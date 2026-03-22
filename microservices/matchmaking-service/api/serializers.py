from rest_framework import serializers
from .models import UserInteraction, StartupSimilarity


class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = ['id', 'user_id', 'startup_id', 'interaction_type', 
                  'weight', 'metadata', 'created_at']
        read_only_fields = ['created_at']


class TrackInteractionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    startup_id = serializers.IntegerField()
    interaction_type = serializers.ChoiceField(choices=UserInteraction.INTERACTION_TYPES)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def create(self, validated_data):
        weight_map = {
            'view': 1.0,
            'click': 2.0,
            'pitch_request': 5.0,
            'like': 2.5,
            'review': 4.0,
        }
        
        interaction = UserInteraction.objects.create(
            user_id=validated_data['user_id'],
            startup_id=validated_data['startup_id'],
            interaction_type=validated_data['interaction_type'],
            weight=weight_map.get(validated_data['interaction_type'], 1.0),
            metadata=validated_data.get('metadata', {})
        )
        
        return interaction


class StartupSimilaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupSimilarity
        fields = ['id', 'startup_id', 'similar_startup_id', 'similarity_score', 'created_at']
        read_only_fields = ['created_at']
