from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from collections import defaultdict
from .models import UserInteraction, ProductSimilarity
from .serializers import (
    UserInteractionSerializer,
    TrackInteractionSerializer,
    ProductSimilaritySerializer
)


class RecommendationViewSet(viewsets.ViewSet):
    """
    ViewSet for product recommendations
    """
    
    @action(detail=False, methods=['post'])
    def track(self, request):
        """Track user interaction with a product"""
        serializer = TrackInteractionSerializer(data=request.data)
        
        if serializer.is_valid():
            interaction = serializer.save()
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
        """Get personalized recommendations for a user"""
        user_id = request.query_params.get('user_id')
        limit = int(request.query_params.get('limit', 10))
        
        if not user_id:
            return Response({
                'success': False,
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's interaction history
        user_interactions = UserInteraction.objects.filter(
            user_id=user_id
        ).order_by('-created_at')[:50]  # Last 50 interactions
        
        if not user_interactions:
            # Return popular products if no history
            return self._get_popular_products(limit)
        
        # Calculate product scores based on interactions
        product_scores = defaultdict(float)
        interacted_products = set()
        
        for interaction in user_interactions:
            interacted_products.add(interaction.product_id)
            
            # Find similar products
            similarities = ProductSimilarity.objects.filter(
                product_id=interaction.product_id
            ).order_by('-similarity_score')[:20]
            
            for sim in similarities:
                if sim.similar_product_id not in interacted_products:
                    # Score = interaction weight * similarity score
                    score = interaction.weight * sim.similarity_score
                    product_scores[sim.similar_product_id] += score
        
        # Sort by score and get top N
        recommended_products = sorted(
            product_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        recommendations = [
            {
                'product_id': product_id,
                'score': score,
                'reason': 'based_on_your_activity'
            }
            for product_id, score in recommended_products
        ]
        
        # If not enough recommendations, add popular products
        if len(recommendations) < limit:
            popular = self._get_popular_products(limit - len(recommendations))
            for item in popular['data']['recommendations']:
                if item['product_id'] not in [r['product_id'] for r in recommendations]:
                    recommendations.append(item)
        
        return Response({
            'success': True,
            'data': {
                'user_id': user_id,
                'recommendations': recommendations
            }
        })
    
    @action(detail=False, methods=['get'])
    def similar(self, request):
        """Get similar products to a given product"""
        product_id = request.query_params.get('product_id')
        limit = int(request.query_params.get('limit', 10))
        
        if not product_id:
            return Response({
                'success': False,
                'error': 'product_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get similar products
        similarities = ProductSimilarity.objects.filter(
            product_id=product_id
        ).order_by('-similarity_score')[:limit]
        
        recommendations = [
            {
                'product_id': sim.similar_product_id,
                'similarity_score': sim.similarity_score,
                'reason': 'similar_to_viewed'
            }
            for sim in similarities
        ]
        
        return Response({
            'success': True,
            'data': {
                'product_id': product_id,
                'recommendations': recommendations
            }
        })
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular products"""
        limit = int(request.query_params.get('limit', 10))
        return self._get_popular_products(limit)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending products (popular in last 7 days)"""
        from django.utils import timezone
        from datetime import timedelta
        
        limit = int(request.query_params.get('limit', 10))
        days = int(request.query_params.get('days', 7))
        
        # Get interactions from last N days
        since_date = timezone.now() - timedelta(days=days)
        
        trending_products = UserInteraction.objects.filter(
            created_at__gte=since_date
        ).values('product_id').annotate(
            interaction_count=Count('id'),
            total_weight=Sum('weight')
        ).order_by('-total_weight')[:limit]
        
        recommendations = [
            {
                'product_id': item['product_id'],
                'interaction_count': item['interaction_count'],
                'score': float(item['total_weight']),
                'reason': 'trending'
            }
            for item in trending_products
        ]
        
        return Response({
            'success': True,
            'data': {
                'period': f'last_{days}_days',
                'recommendations': recommendations
            }
        })
    
    @action(detail=False, methods=['post'])
    def compute_similarities(self, request):
        """
        Compute product similarities based on user interactions
        (This would be run periodically as a background job)
        """
        # Get all user interactions
        interactions = UserInteraction.objects.all()
        
        # Build user-product matrix
        user_products = defaultdict(set)
        for interaction in interactions:
            user_products[interaction.user_id].add(interaction.product_id)
        
        # Calculate similarities using collaborative filtering
        product_pairs = defaultdict(int)
        product_counts = defaultdict(int)
        
        for user_id, products in user_products.items():
            products_list = list(products)
            for i, product1 in enumerate(products_list):
                product_counts[product1] += 1
                for product2 in products_list[i+1:]:
                    pair = tuple(sorted([product1, product2]))
                    product_pairs[pair] += 1
        
        # Calculate Jaccard similarity and save
        similarities_created = 0
        for (product1, product2), co_occurrence in product_pairs.items():
            count1 = product_counts[product1]
            count2 = product_counts[product2]
            
            # Jaccard similarity
            similarity = co_occurrence / (count1 + count2 - co_occurrence)
            
            if similarity > 0.1:  # Only save if similarity > threshold
                # Save both directions
                ProductSimilarity.objects.update_or_create(
                    product_id=product1,
                    similar_product_id=product2,
                    defaults={'similarity_score': similarity}
                )
                ProductSimilarity.objects.update_or_create(
                    product_id=product2,
                    similar_product_id=product1,
                    defaults={'similarity_score': similarity}
                )
                similarities_created += 2
        
        return Response({
            'success': True,
            'message': f'Computed {similarities_created} product similarities'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get recommendation statistics"""
        total_interactions = UserInteraction.objects.count()
        unique_users = UserInteraction.objects.values('user_id').distinct().count()
        unique_products = UserInteraction.objects.values('product_id').distinct().count()
        total_similarities = ProductSimilarity.objects.count()
        
        # Interaction breakdown
        interaction_breakdown = UserInteraction.objects.values('interaction_type').annotate(
            count=Count('id')
        )
        
        return Response({
            'success': True,
            'data': {
                'total_interactions': total_interactions,
                'unique_users': unique_users,
                'unique_products': unique_products,
                'total_similarities': total_similarities,
                'interaction_breakdown': list(interaction_breakdown)
            }
        })
    
    def _get_popular_products(self, limit):
        """Helper method to get popular products"""
        popular_products = UserInteraction.objects.values('product_id').annotate(
            interaction_count=Count('id'),
            total_weight=Sum('weight')
        ).order_by('-total_weight')[:limit]
        
        recommendations = [
            {
                'product_id': item['product_id'],
                'interaction_count': item['interaction_count'],
                'score': float(item['total_weight']),
                'reason': 'popular'
            }
            for item in popular_products
        ]
        
        return Response({
            'success': True,
            'data': {
                'recommendations': recommendations
            }
        })


class InteractionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user interactions"""
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer
    
    def list(self, request):
        """Get all interactions with optional filtering"""
        queryset = self.get_queryset()
        
        # Filter by user
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by product
        product_id = request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by interaction type
        interaction_type = request.query_params.get('interaction_type')
        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)
        
        # Limit results
        limit = request.query_params.get('limit', 100)
        queryset = queryset[:int(limit)]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
