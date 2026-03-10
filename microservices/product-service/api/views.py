"""Product Service Views"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.db import models
from django.db.models import Q
from .models import Product, Category, Review
from .serializers import (ProductSerializer, ProductDetailSerializer, 
                          CategorySerializer, ReviewSerializer)


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'product-service'})


class CategoryViewSet(viewsets.ModelViewSet):
    """Category CRUD"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    """Product CRUD with filters"""
    queryset = Product.objects.all()
    permission_classes = [AllowAny]  # Allow anonymous for demo
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filters
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        featured = self.request.query_params.get('featured', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Limit
        limit = self.request.query_params.get('limit', None)
        if limit:
            queryset = queryset[:int(limit)]
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get product reviews"""
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='reviews/summary')
    def reviews_summary(self, request, pk=None):
        """Get product reviews summary (rating, count)"""
        product = self.get_object()
        reviews = product.reviews.all()
        
        if reviews.count() > 0:
            avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
            return Response({
                'product_id': product.id,
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
                'product_id': product.id,
                'average_rating': 0,
                'count': 0,
                'ratings_distribution': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
            })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Product statistics"""
        total_products = Product.objects.count()
        featured_products = Product.objects.filter(featured=True).count()
        total_stock = Product.objects.aggregate(total=models.Sum('stock'))['total'] or 0
        
        return Response({
            'total_products': total_products,
            'featured_products': featured_products,
            'total_stock': total_stock
        })


class ReviewViewSet(viewsets.ModelViewSet):
    """Review CRUD"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Trust BFF - Gateway already validated
    
    def get_queryset(self):
        queryset = Review.objects.all()
        product_id = self.request.query_params.get('product', None)
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset
