from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Sum, Count
import random
from django.db import transaction
from .models import Payment, FundingOutboxEvent
from .serializers import (
    PaymentSerializer, 
    PaymentCreateSerializer,
    PaymentProcessSerializer,
    PaymentStatusUpdateSerializer
)


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'funding-service'})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'process':
            return PaymentProcessSerializer
        elif self.action == 'update_status':
            return PaymentStatusUpdateSerializer
        return PaymentSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        reference_id = request.query_params.get('reference_id')
        if reference_id:
            queryset = queryset.filter(reference_id=reference_id)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                payment = serializer.save()
                FundingOutboxEvent.objects.create(
                    event_type='payment_initiated',
                    payload=PaymentSerializer(payment).data
                )
            return Response({
                'success': True,
                'message': 'Payment created successfully',
                'data': PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({'success': False, 'errors': serializer.errors}, status=400)
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        payment_id = request.data.get('payment_id')
        if not payment_id:
            return Response({'error': 'payment_id is required'}, status=400)
        
        try:
            payment = Payment.objects.get(id=payment_id)
            if payment.status != 'pending':
                return Response({'error': f'Payment is already {payment.status}'}, status=400)
            
            with transaction.atomic():
                payment.status = 'processing'
                payment.save()
                
                is_successful = random.random() < 0.9
                if is_successful:
                    payment.status = 'completed'
                    payment.error_message = None
                    message = 'Payment processed successfully'
                else:
                    payment.status = 'failed'
                    payment.error_message = 'Insufficient funds'
                    message = 'Payment processing failed'
                
                payment.save()
                
                # Emit event via Outbox
                FundingOutboxEvent.objects.create(
                    event_type=f'payment_{payment.status}',
                    payload=PaymentSerializer(payment).data
                )
            return Response({'success': is_successful, 'message': message, 'data': PaymentSerializer(payment).data})
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        try:
            with transaction.atomic():
                payment = self.get_object()
                if payment.status != 'completed':
                    return Response({'error': 'Only completed payments can be refunded'}, status=400)
                
                payment.status = 'refunded'
                payment.save()
                
                # Emit event via Outbox
                FundingOutboxEvent.objects.create(
                    event_type='payment_refunded',
                    payload=PaymentSerializer(payment).data
                )
            return Response({'success': True, 'data': PaymentSerializer(payment).data})
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_payments = Payment.objects.count()
        status_counts = Payment.objects.values('status').annotate(count=Count('id'))
        total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
        success_rate = (Payment.objects.filter(status='completed').count() / total_payments * 100) if total_payments > 0 else 0
        
        return Response({
            'success': True,
            'data': {
                'total_payments': total_payments,
                'status_breakdown': list(status_counts),
                'total_revenue': float(total_revenue),
                'success_rate': round(success_rate, 2)
            }
        })
