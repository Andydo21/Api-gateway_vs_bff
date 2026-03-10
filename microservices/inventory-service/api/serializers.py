from rest_framework import serializers
from .models import Inventory, Reservation
from datetime import timedelta
from django.utils import timezone


class InventorySerializer(serializers.ModelSerializer):
    total_quantity = serializers.IntegerField(read_only=True)
    needs_restock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product_id', 'product_name', 'available_quantity', 
                  'reserved_quantity', 'total_quantity', 'reorder_level', 
                  'needs_restock', 'last_restocked', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'inventory', 'order_id', 'quantity', 'status', 
                  'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReserveInventorySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    expiration_minutes = serializers.IntegerField(default=15, min_value=1, max_value=60)
    
    def validate(self, data):
        try:
            inventory = Inventory.objects.get(product_id=data['product_id'])
            
            if inventory.available_quantity < data['quantity']:
                raise serializers.ValidationError({
                    'quantity': f'Not enough inventory. Available: {inventory.available_quantity}'
                })
            
            data['inventory'] = inventory
        except Inventory.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': 'Product not found in inventory'
            })
        
        return data
    
    def create(self, validated_data):
        inventory = validated_data['inventory']
        quantity = validated_data['quantity']
        expiration_minutes = validated_data['expiration_minutes']
        
        # Create reservation
        reservation = Reservation.objects.create(
            inventory=inventory,
            order_id=validated_data['order_id'],
            quantity=quantity,
            status='active',
            expires_at=timezone.now() + timedelta(minutes=expiration_minutes)
        )
        
        # Update inventory
        inventory.available_quantity -= quantity
        inventory.reserved_quantity += quantity
        inventory.save()
        
        return reservation


class ReleaseInventorySerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField(required=False)
    order_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        if not data.get('reservation_id') and not data.get('order_id'):
            raise serializers.ValidationError(
                'Either reservation_id or order_id must be provided'
            )
        return data


class UpdateStockSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    operation = serializers.ChoiceField(choices=['add', 'set'])
