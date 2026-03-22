from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from .models import PitchRequest, PitchBooking, Waitlist, PitchBookingHistory, BookingOutboxEvent
from .serializers import (
    PitchRequestSerializer, PitchBookingSerializer, 
    CreateBookingSerializer, WaitlistSerializer, 
    PitchBookingHistorySerializer
)

class PitchRequestViewSet(viewsets.ModelViewSet):
    """Startup applications for pitching"""
    queryset = PitchRequest.objects.all()
    serializer_class = PitchRequestSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = PitchRequest.objects.all()
        startup_id = self.request.query_params.get('startup_id')
        if startup_id:
            queryset = queryset.filter(startup_id=startup_id)
        return queryset

    def perform_create(self, serializer):
        with transaction.atomic():
            pitch_request = serializer.save()
            BookingOutboxEvent.objects.create(
                event_type='pitch_request_created',
                payload=PitchRequestSerializer(pitch_request).data
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pitch request"""
        pitch_request = self.get_object()
        with transaction.atomic():
            pitch_request.status = 'APPROVED'
            pitch_request.save()
            BookingOutboxEvent.objects.create(
                event_type='pitch_request_approved',
                payload=PitchRequestSerializer(pitch_request).data
            )
        return Response({'success': True, 'status': 'APPROVED'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pitch request"""
        pitch_request = self.get_object()
        with transaction.atomic():
            pitch_request.status = 'REJECTED'
            pitch_request.save()
            BookingOutboxEvent.objects.create(
                event_type='pitch_request_rejected',
                payload=PitchRequestSerializer(pitch_request).data
            )
        return Response({'success': True, 'status': 'REJECTED'})

class PitchBookingViewSet(viewsets.ModelViewSet):
    """Orchestration for pitch bookings"""
    queryset = PitchBooking.objects.all()
    serializer_class = PitchBookingSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = CreateBookingSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                booking = serializer.save()
                BookingOutboxEvent.objects.create(
                    event_type='pitch_booking_created',
                    payload=PitchBookingSerializer(booking).data
                )
            return Response(PitchBookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'CANCELLED':
            return Response({'error': 'Already cancelled'}, status=400)
            
        with transaction.atomic():
            booking.status = 'CANCELLED'
            booking.save()
            
            # Record in history
            PitchBookingHistory.objects.create(
                booking=booking,
                action='CANCEL',
                old_slot_id=booking.pitch_slot_id
            )
            
            # Emit event for scheduling-service to release slot
            BookingOutboxEvent.objects.create(
                event_type='pitch_booking_cancelled',
                payload={'booking_id': booking.id, 'pitch_slot_id': booking.pitch_slot_id}
            )
            
        return Response({'success': True, 'message': 'Booking cancelled'})

class WaitlistViewSet(viewsets.ModelViewSet):
    queryset = Waitlist.objects.all()
    serializer_class = WaitlistSerializer
    permission_classes = [AllowAny]

class PitchBookingHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PitchBookingHistory.objects.all()
    serializer_class = PitchBookingHistorySerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'booking-service'})
