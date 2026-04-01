"""Product Service Views"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.db import models
from django.db.models import Q
from .models import Startup, Category, Review, Investor
from .serializers import (StartupSerializer, StartupDetailSerializer, 
                          CategorySerializer, ReviewSerializer, InvestorSerializer)
from .models import StartupOutboxEvent


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'startup-service'})


class CategoryViewSet(viewsets.ModelViewSet):
    """Category CRUD"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class StartupViewSet(viewsets.ModelViewSet):
    """Startup CRUD with filters"""
    queryset = Startup.objects.all()
    permission_classes = [AllowAny]  # Allow anonymous for demo
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StartupDetailSerializer
        return StartupSerializer
    
    def get_queryset(self):
        queryset = Startup.objects.all()
        
        # Filters
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        featured = self.request.query_params.get('featured', None)
        industry = self.request.query_params.get('industry', None)
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search) | Q(description__icontains=search)
            )
        
        if featured == 'true':
            queryset = queryset.filter(featured=True)
            
        if industry:
            queryset = queryset.filter(industry__icontains=industry)
        
        return queryset
    
    def perform_create(self, serializer):
        """Broadcast startup creation via Transactional Outbox"""
        with transaction.atomic():
            startup = serializer.save()
            startup_data = StartupSerializer(startup).data
            StartupOutboxEvent.objects.create(
                event_type='startup_created',
                payload=startup_data
            )
            print(f" [STARTUP-SERVICE] Startup #{startup.id} and its StartupOutboxEvent saved atomically.")
    
    def perform_update(self, serializer):
        """Broadcast startup update via Transactional Outbox"""
        with transaction.atomic():
            startup = serializer.save()
            startup_data = StartupSerializer(startup).data
            StartupOutboxEvent.objects.create(
                event_type='startup_updated',
                payload=startup_data
            )
            print(f" [STARTUP-SERVICE] Startup #{startup.id} update and its StartupOutboxEvent saved atomically.")
    
    def perform_destroy(self, instance):
        """Broadcast startup deletion via Transactional Outbox"""
        with transaction.atomic():
            startup_id = instance.id
            StartupOutboxEvent.objects.create(
                event_type='startup_deleted',
                payload={'id': startup_id}
            )
            instance.delete()
            print(f" [STARTUP-SERVICE] Startup #{startup_id} deletion and its StartupOutboxEvent saved atomically.")
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get startup reviews"""
        startup = self.get_object()
        reviews = startup.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='reviews/summary')
    def reviews_summary(self, request, pk=None):
        """Get startup reviews summary (rating, count)"""
        startup = self.get_object()
        reviews = startup.reviews.all()
        
        if reviews.count() > 0:
            avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
            return Response({
                'startup_id': startup.id,
                'average_rating': round(avg_rating, 1) if avg_rating else 0,
                'count': reviews.count(),
                'ratings_distribution': {
                    '5': reviews.filter(rating=5).count(),
                    '4': reviews.filter(rating=4).count(),
                    '3': reviews.filter(rating=3).count(),
                    '2': reviews.filter(rating=2).count(),
                    '1': reviews.filter(rating=1).count(),
                }
            })
        else:
            return Response({
                'startup_id': startup.id,
                'average_rating': 0,
                'count': 0,
                'ratings_distribution': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
            })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Startup statistics"""
        total_startups = Startup.objects.count()
        featured_startups = Startup.objects.filter(featured=True).count()
        
        return Response({
            'total_startups': total_startups,
            'featured_startups': featured_startups,
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a startup registration"""
        startup = self.get_object()
        with transaction.atomic():
            startup.status = 'APPROVED'
            startup.save()
            StartupOutboxEvent.objects.create(
                event_type='startup_approved',
                payload=StartupSerializer(startup).data
            )
        return Response({'success': True, 'status': 'APPROVED'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a startup registration"""
        startup = self.get_object()
        with transaction.atomic():
            startup.status = 'REJECTED'
            startup.save()
            StartupOutboxEvent.objects.create(
                event_type='startup_rejected',
                payload={'id': startup.id, 'status': 'REJECTED'}
            )
        return Response({'success': True, 'status': 'REJECTED'})


class InvestorViewSet(viewsets.ModelViewSet):
    """Investor profiles"""
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Investor.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset




class ReviewViewSet(viewsets.ModelViewSet):
    """Review CRUD"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Trust BFF - Gateway already validated
    
    def get_queryset(self):
        queryset = Review.objects.all()
        startup_id = self.request.query_params.get('startup') or self.request.query_params.get('product')
        
        if startup_id:
            queryset = queryset.filter(startup_id=startup_id)
        
        return queryset
