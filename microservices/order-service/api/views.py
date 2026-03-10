from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Order, OrderItem, Cart, CartItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    CartSerializer, CartItemSerializer
)


class CartViewSet(viewsets.ViewSet):
    """Cart operations"""
    
    def list(self, request):
        """Get user's cart"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        serializer = CartSerializer(cart)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request):
        """Add item to cart"""
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        product_name = request.data.get('product_name')
        price = request.data.get('price')
        quantity = request.data.get('quantity', 1)
        
        if not all([user_id, product_id, product_name, price]):
            return Response({
                'success': False,
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={
                'product_name': product_name,
                'price': price,
                'quantity': quantity
            }
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += int(quantity)
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Item added to cart',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        """Update cart item quantity"""
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        if not all([user_id, product_id, quantity]):
            return Response({
                'success': False,
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart = Cart.objects.get(user_id=user_id)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            
            if int(quantity) <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = int(quantity)
                cart_item.save()
            
            serializer = CartSerializer(cart)
            return Response({
                'success': True,
                'message': 'Cart updated',
                'data': serializer.data
            })
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({
                'success': False,
                'error': 'Item not found in cart'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove item from cart"""
        user_id = request.query_params.get('user_id')
        product_id = request.query_params.get('product_id')
        
        if not all([user_id, product_id]):
            return Response({
                'success': False,
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart = Cart.objects.get(user_id=user_id)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            
            serializer = CartSerializer(cart)
            return Response({
                'success': True,
                'message': 'Item removed from cart',
                'data': serializer.data
            })
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({
                'success': False,
                'error': 'Item not found in cart'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear cart"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart = Cart.objects.get(user_id=user_id)
            cart.items.all().delete()
            
            return Response({
                'success': True,
                'message': 'Cart cleared'
            })
        except Cart.DoesNotExist:
            return Response({
                'success': True,
                'message': 'Cart already empty'
            })


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def list(self, request):
        """Get all orders with optional filtering"""
        queryset = self.get_queryset()
        
        # Filter by user
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Pagination
        limit = request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """Get order details"""
        try:
            order = self.get_object()
            serializer = self.get_serializer(order)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create new order"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            order = serializer.save()
            return Response({
                'success': True,
                'message': 'Order created successfully',
                'data': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update order status"""
        try:
            order = self.get_object()
            serializer = OrderStatusUpdateSerializer(data=request.data)
            
            if serializer.is_valid():
                order.status = serializer.validated_data['status']
                order.save()
                
                return Response({
                    'success': True,
                    'message': 'Order status updated',
                    'data': OrderSerializer(order).data
                })
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def user_orders(self, request):
        """Get orders for a specific user"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orders = Order.objects.filter(user_id=user_id)
        serializer = self.get_serializer(orders, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics"""
        total_orders = Order.objects.count()
        
        # Orders by status
        status_counts = Order.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Total revenue
        total_revenue = Order.objects.filter(
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Recent orders
        recent_orders = Order.objects.all()[:10]
        
        return Response({
            'success': True,
            'data': {
                'total_orders': total_orders,
                'status_breakdown': list(status_counts),
                'total_revenue': float(total_revenue),
                'recent_orders': OrderSerializer(recent_orders, many=True).data
            }
        })
