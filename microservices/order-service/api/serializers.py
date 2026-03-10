from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_name', 'price', 'quantity', 'subtotal']
        read_only_fields = ['subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'items', 'total_amount', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'quantity', 'price', 'subtotal']
        read_only_fields = ['subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'total_amount', 'status', 'shipping_address', 
                  'payment_method', 'notes', 'items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    shipping_address = serializers.CharField()
    payment_method = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item")
        
        for item in value:
            required_fields = ['product_id', 'product_name', 'quantity', 'price']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Item missing required field: {field}")
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate total amount
        total_amount = sum(
            float(item['price']) * int(item['quantity']) 
            for item in items_data
        )
        
        # Create order
        order = Order.objects.create(
            user_id=validated_data['user_id'],
            total_amount=total_amount,
            shipping_address=validated_data['shipping_address'],
            payment_method=validated_data['payment_method'],
            notes=validated_data.get('notes', ''),
            status='pending'
        )
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item_data['product_id'],
                product_name=item_data['product_name'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
        
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
