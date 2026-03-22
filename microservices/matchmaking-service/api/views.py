from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Sum, Count
from collections import defaultdict
from django.db import transaction
from .models import UserInteraction, StartupSimilarity, MatchmakingOutboxEvent
from .serializers import (
    UserInteractionSerializer,
    TrackInteractionSerializer,
    StartupSimilaritySerializer
)


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'matchmaking-service'})

class RecommendationViewSet(viewsets.ViewSet):
    """
    ViewSet for startup recommendations
    """
    
    @action(detail=False, methods=['post'])
    def track(self, request):
        """Track user interaction with a startup"""
        serializer = TrackInteractionSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                interaction = serializer.save()
                
                # Emit event via Outbox
                MatchmakingOutboxEvent.objects.create(
                    event_type='interaction_tracked',
                    payload=UserInteractionSerializer(interaction).data
                )
                
            return Response({
                'success': True,
                'message': 'Interaction tracked successfully',
                'data': UserInteractionSerializer(interaction).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def for_user(self, request):
        """Get personalized startup recommendations for a user (investor)"""
        user_id = request.query_params.get('user_id')
        limit = int(request.query_params.get('limit', 10))
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        
        user_interactions = UserInteraction.objects.filter(user_id=user_id).order_by('-created_at')[:50]
        
        if not user_interactions:
            return self._get_popular_startups(limit)
        
        startup_scores = defaultdict(float)
        interacted_startups = set()
        
        for interaction in user_interactions:
            interacted_startups.add(interaction.startup_id)
            similarities = StartupSimilarity.objects.filter(startup_id=interaction.startup_id).order_by('-similarity_score')[:20]
            
            for sim in similarities:
                if sim.similar_startup_id not in interacted_startups:
                    score = interaction.weight * sim.similarity_score
                    startup_scores[sim.similar_startup_id] += score
        
        recommended_startups = sorted(startup_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        recommendations = [{'startup_id': sid, 'score': score, 'reason': 'based_on_activity'} for sid, score in recommended_startups]
        
        return Response({'success': True, 'data': {'user_id': user_id, 'recommendations': recommendations}})
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        limit = int(request.query_params.get('limit', 10))
        return self._get_popular_startups(limit)

    def _get_popular_startups(self, limit):
        popular_startups = UserInteraction.objects.values('startup_id').annotate(
            interaction_count=Count('id'),
            total_weight=Sum('weight')
        ).order_by('-total_weight')[:limit]
        
        recommendations = [
            {
                'startup_id': item['startup_id'],
                'interaction_count': item['interaction_count'],
                'score': float(item['total_weight']),
                'reason': 'popular'
            }
            for item in popular_startups
        ]
        
        return Response({'success': True, 'data': {'recommendations': recommendations}})

class InteractionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        startup_id = request.query_params.get('startup_id')
        if startup_id:
            queryset = queryset.filter(startup_id=startup_id)
            
        serializer = self.get_serializer(queryset[:100], many=True)
        return Response({'success': True, 'data': serializer.data})
