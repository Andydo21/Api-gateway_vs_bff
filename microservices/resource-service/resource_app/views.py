from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import EventResource, ResourceReservation
from .serializers import (
    EventResourceSerializer,
    ResourceReservationSerializer,
    ReserveResourceSerializer,
    ReleaseResourceSerializer,
    UpdateResourceStockSerializer
)


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'resource-service'})

class EventResourceViewSet(viewsets.ModelViewSet):
    """Management of event resources (Demo booths, equipment)"""
    queryset = EventResource.objects.all()
    serializer_class = EventResourceSerializer
    
    def list(self, request):
        """Get all event resources"""
        queryset = self.get_queryset()
        
        # Filter by startup
        startup_id = request.query_params.get('startup_id')
        if startup_id:
            queryset = queryset.filter(startup_id=startup_id)
        
        # Filter low stock
        low_stock = request.query_params.get('low_stock')
        if low_stock == 'true':
            queryset = [res for res in queryset if res.available_quantity <= res.reorder_level]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """Get resource details for a startup"""
        try:
            if pk.isdigit():
                resource = EventResource.objects.get(id=pk)
            else:
                resource = EventResource.objects.get(startup_id=pk)
            
            serializer = self.get_serializer(resource)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except EventResource.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Resource not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def reserve(self, request):
        """Reserve resource for a booking"""
        serializer = ReserveResourceSerializer(data=request.data)
        
        if serializer.is_valid():
            reservation = serializer.save()
            return Response({
                'success': True,
                'message': 'Resource reserved successfully',
                'data': ResourceReservationSerializer(reservation).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def release(self, request):
        """Release reserved resource"""
        serializer = ReleaseResourceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if 'reservation_id' in serializer.validated_data:
            reservations = ResourceReservation.objects.filter(
                id=serializer.validated_data['reservation_id'],
                status='active'
            )
        else:
            reservations = ResourceReservation.objects.filter(
                booking_id=serializer.validated_data['booking_id'],
                status='active'
            )
        
        if not reservations.exists():
            return Response({
                'success': False,
                'error': 'No active reservations found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        released_count = 0
        for reservation in reservations:
            resource = reservation.resource
            resource.available_quantity += reservation.quantity
            resource.reserved_quantity -= reservation.quantity
            resource.save()
            
            reservation.status = 'released'
            reservation.save()
            released_count += 1
        
        return Response({
            'success': True,
            'message': f'{released_count} reservation(s) released successfully'
        })
    
    @action(detail=False, methods=['post'])
    def fulfill(self, request):
        """Fulfill reserved resource"""
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response({
                'success': False,
                'error': 'booking_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reservations = ResourceReservation.objects.filter(
            booking_id=booking_id,
            status='active'
        )
        
        if not reservations.exists():
            return Response({
                'success': False,
                'error': 'No active reservations found for this booking'
            }, status=status.HTTP_404_NOT_FOUND)
        
        fulfilled_count = 0
        for reservation in reservations:
            resource = reservation.resource
            resource.reserved_quantity -= reservation.quantity
            resource.save()
            
            reservation.status = 'fulfilled'
            reservation.save()
            fulfilled_count += 1
        
        return Response({
            'success': True,
            'message': f'{fulfilled_count} reservation(s) fulfilled successfully'
        })
    
    @action(detail=False, methods=['post'])
    def update_stock(self, request):
        serializer = UpdateResourceStockSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        startup_id = serializer.validated_data['startup_id']
        quantity = serializer.validated_data['quantity']
        operation = serializer.validated_data['operation']
        
        try:
            resource = EventResource.objects.get(startup_id=startup_id)
            if operation == 'add':
                resource.available_quantity += quantity
            elif operation == 'subtract':
                if resource.available_quantity >= quantity:
                    resource.available_quantity -= quantity
                else:
                    return Response({'error': 'Not enough stock'}, status=400)
            else:
                resource.available_quantity = quantity
            
            resource.last_restocked = timezone.now()
            resource.save()
            return Response({'success': True, 'data': EventResourceSerializer(resource).data})
        except EventResource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=404)

class ResourceReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResourceReservation.objects.all()
    serializer_class = ResourceReservationSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        booking_id = request.query_params.get('booking_id')
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
