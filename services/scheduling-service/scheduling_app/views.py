from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import AvailabilityTemplate, PitchSlot
from .serializers import (
    AvailabilityTemplateSerializer, 
    PitchSlotSerializer, 
    PitchSlotStatusUpdateSerializer
)

class AvailabilityTemplateViewSet(viewsets.ModelViewSet):
    """Availability templates for investors"""
    queryset = AvailabilityTemplate.objects.all()
    serializer_class = AvailabilityTemplateSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_investor(self, request):
        investor_id = request.query_params.get('investor_id')
        if not investor_id:
            return Response({'error': 'investor_id is required'}, status=400)
        templates = AvailabilityTemplate.objects.filter(investor_id=investor_id)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

class PitchSlotViewSet(viewsets.ModelViewSet):
    """Investor availability slots"""
    queryset = PitchSlot.objects.all()
    serializer_class = PitchSlotSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'update_status':
            return PitchSlotStatusUpdateSerializer
        return PitchSlotSerializer

    def get_queryset(self):
        queryset = PitchSlot.objects.all()
        investor_id = self.request.query_params.get('investor_id')
        status_filter = self.request.query_params.get('status')

        if investor_id:
            queryset = queryset.filter(investor_id=investor_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        slot = self.get_object()
        serializer = PitchSlotStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            slot.status = serializer.validated_data['status']
            slot.save()
            return Response({'success': True, 'status': slot.status})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = PitchSlot.objects.count()
        booked = PitchSlot.objects.filter(status='BOOKED').count()
        return Response({
            'total_slots': total,
            'booked_slots': booked,
            'available_slots': total - booked
        })

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'scheduling-service'})
