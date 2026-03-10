from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
import random
from .models import Payment
from .serializers import (
    PaymentSerializer, 
    PaymentCreateSerializer,
    PaymentProcessSerializer,
    PaymentStatusUpdateSerializer
)


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
        """Get all payments with optional filtering"""
        queryset = self.get_queryset()
        
        # Filter by user
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by order
        order_id = request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """Get payment details"""
        try:
            payment = self.get_object()
            serializer = self.get_serializer(payment)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create new payment"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            payment = serializer.save()
            return Response({
                'success': True,
                'message': 'Payment created successfully',
                'data': PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process a payment (simulation)"""
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response({
                'success': False,
                'error': 'payment_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            if payment.status != 'pending':
                return Response({
                    'success': False,
                    'error': f'Payment is already {payment.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update to processing
            payment.status = 'processing'
            payment.save()
            
            # Simulate payment processing (90% success rate)
            is_successful = random.random() < 0.9
            
            if is_successful:
                payment.status = 'completed'
                payment.error_message = None
                message = 'Payment processed successfully'
            else:
                payment.status = 'failed'
                payment.error_message = 'Insufficient funds or card declined'
                message = 'Payment processing failed'
            
            payment.save()
            
            return Response({
                'success': is_successful,
                'message': message,
                'data': PaymentSerializer(payment).data
            })
            
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a payment"""
        try:
            payment = self.get_object()
            
            if payment.status != 'completed':
                return Response({
                    'success': False,
                    'error': 'Only completed payments can be refunded'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            payment.status = 'refunded'
            payment.save()
            
            return Response({
                'success': True,
                'message': 'Payment refunded successfully',
                'data': PaymentSerializer(payment).data
            })
            
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update payment status"""
        try:
            payment = self.get_object()
            serializer = PaymentStatusUpdateSerializer(data=request.data)
            
            if serializer.is_valid():
                payment.status = serializer.validated_data['status']
                
                if 'error_message' in serializer.validated_data:
                    payment.error_message = serializer.validated_data['error_message']
                
                payment.save()
                
                return Response({
                    'success': True,
                    'message': 'Payment status updated',
                    'data': PaymentSerializer(payment).data
                })
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payment statistics"""
        total_payments = Payment.objects.count()
        
        # Payments by status
        status_counts = Payment.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Total revenue
        total_revenue = Payment.objects.filter(
            status='completed'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Success rate
        completed_count = Payment.objects.filter(status='completed').count()
        success_rate = (completed_count / total_payments * 100) if total_payments > 0 else 0
        
        return Response({
            'success': True,
            'data': {
                'total_payments': total_payments,
                'status_breakdown': list(status_counts),
                'total_revenue': float(total_revenue),
                'success_rate': round(success_rate, 2)
            }
        })
