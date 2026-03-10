"""Admin BFF Views - Admin panel functionality"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests
from decouple import config

# Microservice URLs
USER_SERVICE = config('USER_SERVICE_URL', default='http://localhost:4001')
PRODUCT_SERVICE = config('PRODUCT_SERVICE_URL', default='http://localhost:4002')
ORDER_SERVICE = config('ORDER_SERVICE_URL', default='http://localhost:4003')


def get_user_from_gateway(request):
    """
    Get user info from API Gateway headers.
    BFF trusts Gateway - no JWT verification needed.
    
    Returns: (user_id, username) or (None, None)
    """
    user_id = request.META.get('HTTP_X_USER_ID')
    username = request.META.get('HTTP_X_USERNAME', '')
    
    if user_id:
        return int(user_id), username
    
    return None, None


@api_view(['GET'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def health_check(request):
    return Response({'status': 'healthy', 'service': 'admin-bff'})


@api_view(['GET'])
@permission_classes([AllowAny])  # BFF trusts Gateway - admin check at Gateway
def dashboard(request):
    """Admin dashboard - aggregate statistics"""
    # Gateway already enforced admin auth - just read user_id
    user_id, _ = get_user_from_gateway(request)
    try:
        products_stats = requests.get(f'{PRODUCT_SERVICE}/products/stats/', timeout=5)
        orders_stats = requests.get(f'{ORDER_SERVICE}/orders/stats/', timeout=5)
        users_stats = requests.get(f'{USER_SERVICE}/users/stats/', timeout=5)
        
        return Response({
            'success': True,
            'data': {
                'products': products_stats.json() if products_stats.status_code == 200 else {},
                'orders': orders_stats.json() if orders_stats.status_code == 200 else {},
                'users': users_stats.json() if users_stats.status_code == 200 else {}
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def products(request):
    """Manage products"""
    try:
        if request.method == 'GET':
            params = request.GET.dict()
            response = requests.get(f'{PRODUCT_SERVICE}/products/', params=params, timeout=5)
            return Response(response.json(), status=response.status_code)
        
        elif request.method == 'POST':
            response = requests.post(f'{PRODUCT_SERVICE}/products/', json=request.data, timeout=5)
            return Response(response.json(), status=response.status_code)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def product_detail(request, product_id):
    """Update or delete product"""
    try:
        if request.method == 'PUT':
            response = requests.put(f'{PRODUCT_SERVICE}/products/{product_id}/', json=request.data, timeout=5)
            return Response(response.json(), status=response.status_code)
        
        elif request.method == 'DELETE':
            response = requests.delete(f'{PRODUCT_SERVICE}/products/{product_id}/', timeout=5)
            return Response(response.json() if response.content else {'success': True}, status=response.status_code)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def orders(request):
    """List all orders"""
    try:
        params = request.GET.dict()
        response = requests.get(f'{ORDER_SERVICE}/orders/', params=params, timeout=5)
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def order_status(request, order_id):
    """Update order status"""
    try:
        response = requests.put(f'{ORDER_SERVICE}/orders/{order_id}/', json=request.data, timeout=5)
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def users(request):
    """List all users"""
    try:
        params = request.GET.dict()
        response = requests.get(f'{USER_SERVICE}/users/', params=params, timeout=5)
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])  # BFF trusts Gateway
def user_ban(request, user_id):
    """Ban/Unban user"""
    try:
        response = requests.put(f'{USER_SERVICE}/users/{user_id}/', json=request.data, timeout=5)
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
