from rest_framework import serializers
from .models import UserInteraction, ProductSimilarity


class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = ['id', 'user_id', 'product_id', 'interaction_type', 
                  'weight', 'metadata', 'created_at']
        read_only_fields = ['created_at']


class TrackInteractionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    interaction_type = serializers.ChoiceField(choices=UserInteraction.INTERACTION_TYPES)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def create(self, validated_data):
        # Set weight based on interaction type
        weight_map = {
            'view': 1.0,
            'click': 2.0,
            'add_to_cart': 3.0,
            'purchase': 5.0,
            'like': 2.5,
            'review': 4.0,
        }
        
        interaction = UserInteraction.objects.create(
            user_id=validated_data['user_id'],
            product_id=validated_data['product_id'],
            interaction_type=validated_data['interaction_type'],
            weight=weight_map.get(validated_data['interaction_type'], 1.0),
            metadata=validated_data.get('metadata', {})
        )
        
        return interaction


class ProductSimilaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSimilarity
        fields = ['id', 'product_id', 'similar_product_id', 'similarity_score', 'created_at']
        read_only_fields = ['created_at']
