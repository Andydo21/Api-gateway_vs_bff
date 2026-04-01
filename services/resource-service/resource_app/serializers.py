from rest_framework import serializers
from .models import EventResource, ResourceReservation
from datetime import timedelta
from django.utils import timezone


class EventResourceSerializer(serializers.ModelSerializer):
    total_quantity = serializers.IntegerField(read_only=True)
    needs_restock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = EventResource
        fields = ['id', 'startup_id', 'startup_name', 'available_quantity', 
                  'reserved_quantity', 'total_quantity', 'reorder_level', 
                  'needs_restock', 'last_restocked', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ResourceReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceReservation
        fields = ['id', 'resource', 'booking_id', 'quantity', 'status', 
                  'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReserveResourceSerializer(serializers.Serializer):
    startup_id = serializers.IntegerField()
    booking_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    expiration_minutes = serializers.IntegerField(default=15, min_value=1, max_value=60)
    
    def validate(self, data):
        try:
            resource = EventResource.objects.get(startup_id=data['startup_id'])
            
            if resource.available_quantity < data['quantity']:
                raise serializers.ValidationError({
                    'quantity': f'Not enough resources. Available: {resource.available_quantity}'
                })
            
            data['resource'] = resource
        except EventResource.DoesNotExist:
            raise serializers.ValidationError({
                'startup_id': 'Startup not found in event resources'
            })
        
        return data
    
    def create(self, validated_data):
        resource = validated_data['resource']
        quantity = validated_data['quantity']
        expiration_minutes = validated_data['expiration_minutes']
        
        # Create reservation
        reservation = ResourceReservation.objects.create(
            resource=resource,
            booking_id=validated_data['booking_id'],
            quantity=quantity,
            status='active',
            expires_at=timezone.now() + timedelta(minutes=expiration_minutes)
        )
        
        # Update resource stock
        resource.available_quantity -= quantity
        resource.reserved_quantity += quantity
        resource.save()
        
        return reservation


class ReleaseResourceSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField(required=False)
    booking_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        if not data.get('reservation_id') and not data.get('booking_id'):
            raise serializers.ValidationError(
                'Either reservation_id or booking_id must be provided'
            )
        return data


class UpdateResourceStockSerializer(serializers.Serializer):
    startup_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    operation = serializers.ChoiceField(choices=['add', 'set', 'subtract'], default='add')
