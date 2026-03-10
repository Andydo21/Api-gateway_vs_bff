"""Web BFF Views - Aggregates data from multiple microservices"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import requests
from decouple import config

# Microservice URLs
USER_SERVICE = config('USER_SERVICE_URL', default='http://localhost:4001')
PRODUCT_SERVICE = config('PRODUCT_SERVICE_URL', default='http://localhost:4002')
ORDER_SERVICE = config('ORDER_SERVICE_URL', default='http://localhost:4003')
PAYMENT_SERVICE = config('PAYMENT_SERVICE_URL', default='http://localhost:4004')
INVENTORY_SERVICE = config('INVENTORY_SERVICE_URL', default='http://localhost:4005')
RECOMMENDATION_SERVICE = config('RECOMMENDATION_SERVICE_URL', default='http://localhost:4006')


def get_user_from_gateway(request):
    """
    Get user info from API Gateway headers.
    API Gateway validates JWT and injects user info into headers.
    BFF trusts these headers (Gateway-to-BFF communication is internal).
    
    Returns: (user_id, username) or (None, None) if not authenticated
    """
    user_id = request.META.get('HTTP_X_USER_ID')
    username = request.META.get('HTTP_X_USERNAME', '')
    
    if user_id:
        return int(user_id), username
    
    return None, None


def require_auth(request):
    """
    Check if request is authenticated via Gateway.
    Returns (user_id, None) if authenticated, (None, error_response) if not.
    """
    user_id, username = get_user_from_gateway(request)
    
    if not user_id:
        return None, Response(
            {'success': False, 'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return user_id, None


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy', 'service': 'web-bff'})


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 15)  # Cache for 15 minutes
def home_page(request):
    """
    Homepage - BFF PATTERN: Aggregate data từ NHIỀU microservices
    Frontend chỉ gọi 1 API → BFF gọi nhiều services → Trả về 1 response
    """
    try:
        print('=' * 70)
        print('🏠 [BFF] Nhận request GET /home/ từ API Gateway')
        print('🎯 [BFF PATTERN] Bắt đầu AGGREGATE data từ nhiều microservices...')
        print('=' * 70)
        
        # Parallel requests to multiple services
        print('[BFF → PRODUCT-SERVICE] GET /products/?featured=true&limit=12')
        products_response = requests.get(f'{PRODUCT_SERVICE}/products/?featured=true&limit=12', timeout=5)
        
        print('[BFF → PRODUCT-SERVICE] GET /categories/')
        categories_response = requests.get(f'{PRODUCT_SERVICE}/categories/', timeout=5)
        
        # Get recommendations if user is authenticated
        recommendations = []
        user_id = request.META.get('HTTP_X_USER_ID')
        if user_id:
            print(f'[BFF → RECOMMENDATION-SERVICE] GET /recommendations/?userId={user_id}')
            try:
                rec_response = requests.get(
                    f'{RECOMMENDATION_SERVICE}/recommendations/',
                    params={'userId': user_id},
                    timeout=5
                )
                if rec_response.status_code == 200:
                    recommendations = rec_response.json()
                    print(f'  Nhận {len(recommendations)} recommendations')
            except:
                print('  Recommendation Service không available')
        
        # 2️⃣ Process responses
        featured_products = products_response.json() if products_response.status_code == 200 else []
        categories = categories_response.json() if categories_response.status_code == 200 else []
        
        # Enrich products with REVIEWS (aggregate thêm data từ microservice)
        print(f'[BFF] Enriching {min(len(featured_products), 3)} products với reviews...')
        reviews_fetched = 0
        for idx, product in enumerate(featured_products[:3]):  # Chỉ lấy 3 products đầu
            try:
                print(f'  [BFF → PRODUCT-SERVICE] GET /products/{product["id"]}/reviews/summary/')
                review_response = requests.get(
                    f'{PRODUCT_SERVICE}/products/{product["id"]}/reviews/summary/',
                    timeout=1
                )
                if review_response.status_code == 200:
                    review_data = review_response.json()
                    product['rating'] = review_data.get('average_rating', 0)
                    product['review_count'] = review_data.get('count', 0)
                    reviews_fetched += 1
            except:
                product['rating'] = 0
                product['review_count'] = 0
        print(f'   ✅ Đã fetch reviews cho {reviews_fetched} products')
        
        print('=' * 70)
        print(f'✅ [BFF] AGGREGATION hoàn tất:')
        print(f'   📦 Featured Products: {len(featured_products)} items')
        print(f'   📂 Categories: {len(categories)} items')
        print(f'   💬 Reviews: {reviews_fetched} products enriched')
        print(f'   ⭐ Recommendations: {len(recommendations)} items')
        print(f'🎯 [BFF PATTERN] Đã gọi {3 + reviews_fetched + (1 if user_id else 0)} microservice APIs!')
        print(f'   → Trả về 1 RESPONSE duy nhất cho Frontend!')
        print('=' * 70)
        
        return Response({
            'success': True,
            'data': {
                'banners': [
                    {
                        'id': 1,
                        'title': 'Summer Sale',
                        'description': 'Up to 50% off on selected items',
                        'image': '/static/images/summer-sale.jpg'
                    },
                    {
                        'id': 2,
                        'title': 'New Arrivals',
                        'description': 'Check out our latest products',
                        'image': '/static/images/new-arrivals.jpg'
                    }
                ],
                'featuredProducts': featured_products,
                'categories': categories,
                'recommendations': recommendations[:8]
            },
            # Metadata để thể hiện BFF pattern
            'bff_info': {
                'pattern': 'BFF Aggregation',
                'services_called': ['product-service', 'recommendation-service'] if user_id else ['product-service'],
                'api_endpoints_called': [
                    'GET /products/ (featured)',
                    'GET /categories/',
                    f'GET /products/{{id}}/reviews/summary/ (x{reviews_fetched})'
                ] + (['GET /recommendations/'] if user_id else []),
                'total_api_calls': 2 + reviews_fetched + (1 if user_id else 0),
                'message': f'Frontend gọi 1 API → BFF gọi {2 + reviews_fetched + (1 if user_id else 0)} microservice APIs → Trả về 1 response'
            }
        })
    except Exception as e:
        print(f'❌ [BFF] Lỗi khi aggregate data: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 5)  # Cache for 5 minutes
def product_list(request):
    """Product listing - Aggregates products with categories and reviews"""
    try:
        # 1. Get products from Product Service
        params = request.GET.dict()
        products_response = requests.get(f'{PRODUCT_SERVICE}/products/', params=params, timeout=5)
        
        if products_response.status_code != 200:
            return Response({'error': 'Failed to fetch products'}, status=products_response.status_code)
        
        products = products_response.json()
        
        # 2. Get categories from Product Service (parallel request)
        try:
            categories_response = requests.get(f'{PRODUCT_SERVICE}/categories/', timeout=3)
            categories = categories_response.json() if categories_response.status_code == 200 else []
        except:
            categories = []
        
        # 3. Enrich products with review data (only for first 10 to avoid timeout)
        enriched_products = []
        for idx, product in enumerate(products):
            # Only fetch reviews for first 10 products to avoid timeout
            if idx < 10:
                try:
                    reviews_response = requests.get(
                        f'{PRODUCT_SERVICE}/products/{product["id"]}/reviews/summary/', 
                        timeout=1
                    )
                    if reviews_response.status_code == 200:
                        review_data = reviews_response.json()
                        product['rating'] = review_data.get('average_rating', 4.5)
                        product['review_count'] = review_data.get('count', 0)
                    else:
                        product['rating'] = 4.5
                        product['review_count'] = 0
                except:
                    product['rating'] = 4.5
                    product['review_count'] = 0
            else:
                product['rating'] = 4.5
                product['review_count'] = 0
            
            enriched_products.append(product)
        
        # 4. Return aggregated data from BFF
        return Response({
            'success': True,
            'products': enriched_products,
            'categories': categories,
            'total': len(enriched_products),
            'bff_info': {
                'aggregated_from': ['product-service', 'review-service', 'category-service'],
                'services_called': 2 + min(len(products), 10),  # products + categories + reviews
                'source': 'web-bff'
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@cache_page(60 * 10)  # Cache for 10 minutes
@permission_classes([AllowAny])
def product_detail(request, product_id):
    """Product detail - aggregates product, inventory, and reviews"""
    try:
        product_response = requests.get(f'{PRODUCT_SERVICE}/products/{product_id}/', timeout=5)
        
        if product_response.status_code != 200:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        product = product_response.json()
        
        # Get inventory
        inventory_response = requests.get(f'{INVENTORY_SERVICE}/inventory/{product_id}/', timeout=5)
        inventory = inventory_response.json() if inventory_response.status_code == 200 else {}
        
        # Get reviews
        reviews_response = requests.get(f'{PRODUCT_SERVICE}/products/{product_id}/reviews/', timeout=5)
        reviews = reviews_response.json() if reviews_response.status_code == 200 else []
        
        # Get reviews summary
        summary_response = requests.get(f'{PRODUCT_SERVICE}/products/{product_id}/reviews/summary/', timeout=5)
        reviews_summary = summary_response.json() if summary_response.status_code == 200 else {}
        
        return Response({
            'success': True,
            'product': product,
            'reviews': reviews,
            'reviews_summary': reviews_summary
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def create_review(request, product_id):
    """Create product review - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, username = get_user_from_gateway(request)
    
    try:
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create review in Product Service
        review_data = {
            'product': product_id,
            'user_id': user_id,
            'username': username or 'Khách hàng',  # Send username for display
            'rating': int(rating),
            'comment': comment
        }
        
        review_response = requests.post(
            f'{PRODUCT_SERVICE}/reviews/',
            json=review_data,
            timeout=5
        )
        
        if review_response.status_code == 201:
            review = review_response.json()
            return Response({
                'success': True,
                'review': review,
                'message': 'Đánh giá của bạn đã được gửi!'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Failed to create review', 'details': review_response.text}, status=review_response.status_code)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # BFF trusts Gateway - no DRF auth needed
def cart(request):
    """Cart management - OLD endpoints (not used)"""
    # In production, use Redis or database
    # For demo, use session
    if request.method == 'GET':
        cart_data = request.session.get('cart', {'items': [], 'total': 0})
        return Response({'success': True, 'data': cart_data})
    
    elif request.method == 'POST':
        product_id = request.data.get('product_id') or request.data.get('productId')
        quantity = request.data.get('quantity', 1)
        action = request.data.get('action', 'add')
        
        cart_data = request.session.get('cart', {'items': [], 'total': 0})
        
        # Handle remove action
        if action == 'remove':
            cart_data['items'] = [item for item in cart_data['items'] if item['product_id'] != product_id]
        else:
            # Get product info from Product Service
            try:
                product_response = requests.get(f'{PRODUCT_SERVICE}/products/{product_id}/', timeout=5)
                if product_response.status_code != 200:
                    return Response({'success': False, 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
                
                product = product_response.json()
                price = float(product.get('price', 0))
                name = product.get('name', 'Unknown Product')
            except Exception as e:
                return Response({'success': False, 'message': f'Error fetching product: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Check if product already in cart
            existing_item = next((item for item in cart_data['items'] if item['product_id'] == product_id), None)
            
            if action == 'update':
                if existing_item:
                    existing_item['quantity'] = quantity
                else:
                    cart_data['items'].append({
                        'product_id': product_id,
                        'name': name,
                        'quantity': quantity,
                        'price': price
                    })
            else:  # add
                if existing_item:
                    existing_item['quantity'] += quantity
                else:
                    cart_data['items'].append({
                        'product_id': product_id,
                        'name': name,
                        'quantity': quantity,
                        'price': price
                    })
        
        # Recalculate total
        cart_data['total'] = sum(item['price'] * item['quantity'] for item in cart_data['items'])
        
        request.session['cart'] = cart_data
        request.session.modified = True
        return Response({'success': True, 'data': cart_data})


@api_view(['POST'])
@permission_classes([AllowAny])  # BFF trusts Gateway - no DRF auth needed
def checkout(request):
    """Checkout - orchestrates order, payment, and inventory (OLD - not used)"""
    try:
        items = request.data.get('items', [])
        shipping_address = request.data.get('shippingAddress')
        payment_method = request.data.get('paymentMethod')
        
        # Step 1: Reserve inventory
        for item in items:
            inv_response = requests.post(
                f'{INVENTORY_SERVICE}/inventory/reserve/',
                json={'productId': item['productId'], 'quantity': item['quantity']},
                timeout=5
            )
            if inv_response.status_code != 201:
                return Response({'error': 'Insufficient inventory'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 2: Create order
        order_response = requests.post(
            f'{ORDER_SERVICE}/orders/',
            json={
                'userId': request.user.id,
                'items': items,
                'shippingAddress': shipping_address
            },
            timeout=5
        )
        
        if order_response.status_code != 201:
            return Response({'error': 'Failed to create order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        order = order_response.json()
        
        # Step 3: Process payment
        payment_response = requests.post(
            f'{PAYMENT_SERVICE}/payment/',
            json={
                'orderId': order['id'],
                'amount': order['total'],
                'method': payment_method
            },
            timeout=5
        )
        
        if payment_response.status_code != 201:
            # Rollback: cancel order
            requests.put(f'{ORDER_SERVICE}/orders/{order["id"]}/', json={'status': 'cancelled'})
            return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Clear cart
        request.session['cart'] = {'items': [], 'total': 0}
        
        return Response({
            'success': True,
            'data': {
                'order': order,
                'payment': payment_response.json()
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== USER AUTHENTICATION ENDPOINTS =====

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login - forwards to User Service"""
    try:
        response = requests.post(
            f'{USER_SERVICE}/login/',
            json=request.data,
            timeout=5
        )
        data = response.json()
        
        if response.status_code == 200:
            # Return token for frontend
            return Response({
                'success': True,
                'token': data.get('tokens', {}).get('access'),
                'refresh': data.get('tokens', {}).get('refresh'),
                'user': data.get('user')
            })
        else:
            return Response(data, status=response.status_code)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    """User registration - forwards to User Service"""
    try:
        response = requests.post(
            f'{USER_SERVICE}/register/',
            json=request.data,
            timeout=5
        )
        data = response.json()
        
        if response.status_code == 201:
            return Response({
                'success': True,
                'token': data.get('tokens', {}).get('access'),
                'refresh': data.get('tokens', {}).get('refresh'),
                'user': data.get('user')
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(data, status=response.status_code)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== CART ENDPOINTS =====

@api_view(['GET'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def cart_get(request):
    """Get user's cart - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, _ = get_user_from_gateway(request)
    
    try:
        response = requests.get(
            f'{ORDER_SERVICE}/cart/',
            params={'user_id': user_id},
            timeout=5
        )
        
        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(response.json(), status=response.status_code)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def cart_add(request):
    """Add item to cart - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, _ = get_user_from_gateway(request)
    
    try:
        product_id = request.data.get('product_id')
        product_name = request.data.get('product_name')
        price = request.data.get('price')
        quantity = request.data.get('quantity', 1)

        if not all([product_id, product_name, price]):
            return Response(
                {'success': False, 'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = requests.post(
            f'{ORDER_SERVICE}/cart/',
            json={
                'user_id': user_id,
                'product_id': product_id,
                'product_name': product_name,
                'price': price,
                'quantity': quantity
            },
            timeout=5
        )
        if response.status_code in [200, 201]:
            return Response(response.json())
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def cart_update(request):
    """Update cart item quantity - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, _ = get_user_from_gateway(request)
    
    try:
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not all([product_id, quantity is not None]):
            return Response(
                {'success': False, 'error': 'Thiếu user_id, product_id hoặc quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = requests.patch(
            f'{ORDER_SERVICE}/cart/update_item/',
            json={'user_id': user_id, 'product_id': product_id, 'quantity': quantity},
            timeout=5
        )
        if response.status_code == 200:
            return Response(response.json())
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def cart_remove(request):
    """Remove item from cart - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, _ = get_user_from_gateway(request)
    
    try:
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'success': False, 'error': 'Thiếu user_id hoặc product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response = requests.delete(
            f'{ORDER_SERVICE}/cart/remove_item/',
            params={'user_id': user_id, 'product_id': product_id},
            timeout=5
        )
        if response.status_code == 200:
            return Response(response.json())
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def cart_clear(request):
    """Clear cart - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, _ = get_user_from_gateway(request)
    
    try:
        response = requests.delete(
            f'{ORDER_SERVICE}/cart/clear/',
            params={'user_id': user_id},
            timeout=5
        )
        if response.status_code == 200:
            return Response(response.json())
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== ORDER ENDPOINTS =====

@api_view(['GET'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def order_list(request):
    """Get user's orders - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, _ = get_user_from_gateway(request)
    
    try:
        response = requests.get(
            f'{ORDER_SERVICE}/orders/',
            params={'user_id': user_id},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            # Order Service returns {success: True, data: [orders]}
            orders = data.get('data', []) if isinstance(data, dict) else data
            return Response({
                'success': True,
                'orders': orders
            })
        else:
            return Response({'error': 'Failed to fetch orders'}, status=response.status_code)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def order_create(request):
    """Create new order - Gateway already enforced auth"""
    # Gateway validated JWT and injected X-User-ID - just read it
    user_id, _ = get_user_from_gateway(request)
    
    try:
        items = request.data.get('items', [])
        
        if not items:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total from provided items (frontend already has price info)
        total = 0
        order_items = []
        
        for item in items:
            product_id = item.get('product_id')
            product_name = item.get('product_name', 'Unknown Product')
            quantity = item.get('quantity', 1)
            price = float(item.get('price', 0))
            
            if not product_id:
                return Response({'error': 'Missing product_id in items'}, status=status.HTTP_400_BAD_REQUEST)
            
            order_items.append({
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'price': price
            })
            
            total += price * quantity
        
        # Create order with required fields for Order Service
        order_data = {
            'user_id': user_id,
            'items': order_items,
            'shipping_address': request.data.get('shipping_address', 'Default Address'),
            'payment_method': request.data.get('payment_method', 'COD'),
            'notes': request.data.get('notes', '')
        }
        
        order_response = requests.post(
            f'{ORDER_SERVICE}/orders/',
            json=order_data,
            timeout=5
        )
        
        if order_response.status_code == 201:
            order = order_response.json()
            
            return Response({
                'success': True,
                'order': order,
                'message': 'Order created successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Failed to create order', 'details': order_response.text}, status=order_response.status_code)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== CATEGORIES ENDPOINT - THỂ HIỆN RÕ BFF PATTERN =====

@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 15)  # Cache 15 phút
def category_list(request):
    """
    Get all categories - Forward to Product Service
    THỂ HIỆN: Frontend gọi riêng API categories qua Gateway → BFF → Product Service
    """
    try:
        print('📂 [BFF] Nhận request GET /categories/ từ Gateway')
        print('📂 [BFF → PRODUCT-SERVICE] Forward request đến Product Service')
        
        response = requests.get(f'{PRODUCT_SERVICE}/categories/', timeout=5)
        
        if response.status_code == 200:
            categories = response.json()
            print(f'✅ [BFF] Nhận {len(categories)} categories từ Product Service')
            
            return Response({
                'success': True,
                'categories': categories,
                'source': 'web-bff',
                'upstream': 'product-service'
            })
        else:
            return Response(
                {'success': False, 'error': 'Failed to fetch categories'}, 
                status=response.status_code
            )
    
    except Exception as e:
        print(f'❌ [BFF] Lỗi khi gọi Product Service: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 5)  # Cache 5 phút
def product_reviews(request, product_id):
    """
    Get reviews for a product - Forward to Product Service
    THỂ HIỆN: Frontend gọi riêng API reviews qua Gateway → BFF → Product Service
    """
    try:
        print(f'⭐ [BFF] Nhận request GET /products/{product_id}/reviews/ từ Gateway')
        print(f'⭐ [BFF → PRODUCT-SERVICE] Forward request đến Product Service')
        
        # Get reviews list
        reviews_response = requests.get(
            f'{PRODUCT_SERVICE}/products/{product_id}/reviews/', 
            timeout=5
        )
        
        # Get reviews summary (rating, count)
        summary_response = requests.get(
            f'{PRODUCT_SERVICE}/products/{product_id}/reviews/summary/', 
            timeout=5
        )
        
        reviews = reviews_response.json() if reviews_response.status_code == 200 else []
        summary = summary_response.json() if summary_response.status_code == 200 else {}
        
        print(f'✅ [BFF] Nhận {len(reviews)} reviews từ Product Service')
        
        return Response({
            'success': True,
            'reviews': reviews,
            'average_rating': summary.get('average_rating', 0),
            'count': summary.get('count', 0),
            'ratings_distribution': summary.get('ratings_distribution', {}),
            'source': 'web-bff',
            'upstream': 'product-service'
        })
    
    except Exception as e:
        print(f'❌ [BFF] Lỗi khi gọi Product Service: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
