from rest_framework import serializers
from .models import Payment
import uuid


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'user_id', 'amount', 'payment_method', 
                  'status', 'transaction_id', 'payment_details', 'error_message',
                  'created_at', 'updated_at']
        read_only_fields = ['transaction_id', 'created_at', 'updated_at']


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    payment_details = serializers.JSONField(required=False, default=dict)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def create(self, validated_data):
        # Generate transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:16].upper()}"
        
        # Create payment
        payment = Payment.objects.create(
            order_id=validated_data['order_id'],
            user_id=validated_data['user_id'],
            amount=validated_data['amount'],
            payment_method=validated_data['payment_method'],
            payment_details=validated_data.get('payment_details', {}),
            transaction_id=transaction_id,
            status='pending'
        )
        
        return payment


class PaymentProcessSerializer(serializers.Serializer):
    """Serializer for processing a payment"""
    payment_id = serializers.IntegerField()


class PaymentStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating payment status"""
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES)
    error_message = serializers.CharField(required=False, allow_blank=True)
