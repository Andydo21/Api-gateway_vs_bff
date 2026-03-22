"""Admin BFF Views - Admin panel functionality"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests
from decouple import config
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        role = request.META.get('HTTP_X_ROLE', 'user')
        if role != 'admin':
            return Response(
                {'success': False, 'error': 'Unauthorized. Admin role required.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return f(request, *args, **kwargs)
    return decorated_function

# Microservice URLs
# Microservice URLs
USER_SERVICE = config('USER_SERVICE_URL', default='http://localhost:4001')
STARTUP_SERVICE = config('STARTUP_SERVICE_URL', default='http://localhost:4002')
SCHEDULING_SERVICE = config('SCHEDULING_SERVICE_URL', default='http://localhost:4008')
BOOKING_SERVICE = config('BOOKING_SERVICE_URL', default='http://localhost:4009')
MEETING_SERVICE = config('MEETING_SERVICE_URL', default='http://localhost:4010')
FEEDBACK_SERVICE = config('FEEDBACK_SERVICE_URL', default='http://localhost:4011')



def get_user_from_gateway(request):
    """Get user info from API Gateway headers."""
    user_id = request.META.get('HTTP_X_USER_ID')
    username = request.META.get('HTTP_X_USERNAME', '')
    role = request.META.get('HTTP_X_ROLE', 'user')
    if user_id: return int(user_id), username, role
    return None, None, None


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'admin-bff'})


@api_view(['GET'])
@permission_classes([AllowAny])
@admin_required
def dashboard(request):
    """Admin dashboard statistics aggregator"""
    try:
        # Get stats from multiple services
        users_stats = requests.get(f'{USER_SERVICE}/users/stats/', timeout=5).json()
        startup_stats = requests.get(f'{STARTUP_SERVICE}/startups/stats/', timeout=5).json()
        
        # We can also add count for bookings if needed
        # booking_stats = requests.get(f'{BOOKING_SERVICE}/pitch-requests/stats/', timeout=5).json()
        
        return Response({
            'success': True,
            'data': {
                'users': users_stats,
                'startups': startup_stats,
                'system_health': 'All services online'
            }
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def startups(request):
    """List startups (public) or Create (Admin only)"""
    if request.method == 'POST':
        # Apply admin check manually for POST in combined view
        role = request.META.get('HTTP_X_ROLE', 'user')
        if role != 'admin':
            return Response({'error': 'Admin only'}, status=403)
            
    try:
        if request.method == 'GET':
            res = requests.get(f'{STARTUP_SERVICE}/startups/', params=request.GET.dict(), timeout=5)
            return Response(res.json(), status=res.status_code)
        elif request.method == 'POST':
            res = requests.post(f'{STARTUP_SERVICE}/startups/', json=request.data, timeout=5)
            return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])
@admin_required
def startup_detail(request, startup_id):
    try:
        if request.method == 'PUT':
            res = requests.put(f'{STARTUP_SERVICE}/startups/{startup_id}/', json=request.data, timeout=5)
            return Response(res.json(), status=res.status_code)
        elif request.method == 'DELETE':
            res = requests.delete(f'{STARTUP_SERVICE}/startups/{startup_id}/', timeout=5)
            return Response(res.json() if res.content else {'success': True}, status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
@admin_required
def pitch_slots(request):
    try:
        res = requests.get(f'{SCHEDULING_SERVICE}/pitch-slots/', params=request.GET.dict(), timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
@admin_required
def pitch_slot_status(request, slot_id):
    """Update pitch slot status (Approve/Reject)"""
    try:
        res = requests.patch(f'{SCHEDULING_SERVICE}/pitch-slots/{slot_id}/update_status/', json=request.data, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
@admin_required
def users(request):
    try:
        res = requests.get(f'{USER_SERVICE}/users/', params=request.GET.dict(), timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
@admin_required
def user_detail(request, user_id):
    try:
        res = requests.get(f'{USER_SERVICE}/users/{user_id}/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([AllowAny])
@admin_required
def user_ban(request, user_id):
    """Generic update for user (often used for banning)"""
    try:
        res = requests.put(f'{USER_SERVICE}/users/{user_id}/', json=request.data, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@admin_required
def approve_startup(request, startup_id):
    """Approve startup via Startup Service"""
    try:
        res = requests.post(f'{STARTUP_SERVICE}/startups/{startup_id}/approve/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@admin_required
def reject_startup(request, startup_id):
    """Reject startup via Startup Service"""
    try:
        res = requests.post(f'{STARTUP_SERVICE}/startups/{startup_id}/reject/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@admin_required
def block_user(request, user_id):
    """Block user (banned=True)"""
    try:
        res = requests.patch(f'{USER_SERVICE}/users/{user_id}/', json={'banned': True}, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@admin_required
def unblock_user(request, user_id):
    """Unblock user (banned=False)"""
    try:
        res = requests.patch(f'{USER_SERVICE}/users/{user_id}/', json={'banned': False}, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


