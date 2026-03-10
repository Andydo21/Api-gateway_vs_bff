from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Inventory, Reservation
from .serializers import (
    InventorySerializer,
    ReservationSerializer,
    ReserveInventorySerializer,
    ReleaseInventorySerializer,
    UpdateStockSerializer
)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    
    def list(self, request):
        """Get all inventory items"""
        queryset = self.get_queryset()
        
        # Filter by product
        product_id = request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter low stock
        low_stock = request.query_params.get('low_stock')
        if low_stock == 'true':
            queryset = [inv for inv in queryset if inv.needs_restock]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """Get inventory details for a product"""
        try:
            # Try to get by ID first
            if pk.isdigit():
                inventory = Inventory.objects.get(id=pk)
            else:
                # If not a digit, treat as product_id
                inventory = Inventory.objects.get(product_id=pk)
            
            serializer = self.get_serializer(inventory)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Inventory.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Inventory not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def reserve(self, request):
        """Reserve inventory for an order"""
        serializer = ReserveInventorySerializer(data=request.data)
        
        if serializer.is_valid():
            reservation = serializer.save()
            return Response({
                'success': True,
                'message': 'Inventory reserved successfully',
                'data': ReservationSerializer(reservation).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def release(self, request):
        """Release reserved inventory"""
        serializer = ReleaseInventorySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find reservation(s)
        if 'reservation_id' in serializer.validated_data:
            reservations = Reservation.objects.filter(
                id=serializer.validated_data['reservation_id'],
                status='active'
            )
        else:
            reservations = Reservation.objects.filter(
                order_id=serializer.validated_data['order_id'],
                status='active'
            )
        
        if not reservations.exists():
            return Response({
                'success': False,
                'error': 'No active reservations found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Release reservations
        released_count = 0
        for reservation in reservations:
            inventory = reservation.inventory
            
            # Update inventory
            inventory.available_quantity += reservation.quantity
            inventory.reserved_quantity -= reservation.quantity
            inventory.save()
            
            # Update reservation status
            reservation.status = 'released'
            reservation.save()
            
            released_count += 1
        
        return Response({
            'success': True,
            'message': f'{released_count} reservation(s) released successfully'
        })
    
    @action(detail=False, methods=['post'])
    def fulfill(self, request):
        """Fulfill reserved inventory (mark as completed)"""
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({
                'success': False,
                'error': 'order_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reservations = Reservation.objects.filter(
            order_id=order_id,
            status='active'
        )
        
        if not reservations.exists():
            return Response({
                'success': False,
                'error': 'No active reservations found for this order'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Fulfill reservations
        fulfilled_count = 0
        for reservation in reservations:
            inventory = reservation.inventory
            
            # Reduce reserved quantity (already deducted from available)
            inventory.reserved_quantity -= reservation.quantity
            inventory.save()
            
            # Update reservation status
            reservation.status = 'fulfilled'
            reservation.save()
            
            fulfilled_count += 1
        
        return Response({
            'success': True,
            'message': f'{fulfilled_count} reservation(s) fulfilled successfully'
        })
    
    @action(detail=False, methods=['post'])
    def update_stock(self, request):
        """Update stock quantity"""
        serializer = UpdateStockSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        operation = serializer.validated_data['operation']
        
        try:
            inventory = Inventory.objects.get(product_id=product_id)
            
            if operation == 'add':
                inventory.available_quantity += quantity
            else:  # set
                inventory.available_quantity = quantity
            
            inventory.last_restocked = timezone.now()
            inventory.save()
            
            return Response({
                'success': True,
                'message': 'Stock updated successfully',
                'data': InventorySerializer(inventory).data
            })
            
        except Inventory.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Inventory not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def check_availability(self, request):
        """Check if products are available"""
        products = request.query_params.get('products')  # Format: "product_id:quantity,product_id:quantity"
        
        if not products:
            return Response({
                'success': False,
                'error': 'products parameter is required (format: product_id:quantity,product_id:quantity)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Parse products
            product_list = []
            for item in products.split(','):
                product_id, quantity = item.split(':')
                product_list.append({
                    'product_id': int(product_id),
                    'quantity': int(quantity)
                })
            
            # Check availability
            availability = []
            all_available = True
            
            for item in product_list:
                try:
                    inventory = Inventory.objects.get(product_id=item['product_id'])
                    is_available = inventory.available_quantity >= item['quantity']
                    
                    availability.append({
                        'product_id': item['product_id'],
                        'requested': item['quantity'],
                        'available': inventory.available_quantity,
                        'is_available': is_available
                    })
                    
                    if not is_available:
                        all_available = False
                        
                except Inventory.DoesNotExist:
                    availability.append({
                        'product_id': item['product_id'],
                        'requested': item['quantity'],
                        'available': 0,
                        'is_available': False
                    })
                    all_available = False
            
            return Response({
                'success': True,
                'all_available': all_available,
                'items': availability
            })
            
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid products format'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get inventory statistics"""
        total_products = Inventory.objects.count()
        total_available = sum(inv.available_quantity for inv in Inventory.objects.all())
        total_reserved = sum(inv.reserved_quantity for inv in Inventory.objects.all())
        low_stock_count = sum(1 for inv in Inventory.objects.all() if inv.needs_restock)
        
        return Response({
            'success': True,
            'data': {
                'total_products': total_products,
                'total_available': total_available,
                'total_reserved': total_reserved,
                'low_stock_count': low_stock_count,
                'out_of_stock_count': Inventory.objects.filter(available_quantity=0).count()
            }
        })


class ReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def list(self, request):
        """Get all reservations"""
        queryset = self.get_queryset()
        
        # Filter by order
        order_id = request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
