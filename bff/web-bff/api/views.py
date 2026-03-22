"""Web BFF Views - Aggregates data from multiple microservices"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
from decouple import config

# Microservice URLs
from functools import wraps

# Microservice URLs
USER_SERVICE = config('USER_SERVICE_URL', default='http://localhost:4001')
STARTUP_SERVICE = config('STARTUP_SERVICE_URL', default='http://localhost:4002')
SCHEDULING_SERVICE = config('SCHEDULING_SERVICE_URL', default='http://localhost:4008')
BOOKING_SERVICE = config('BOOKING_SERVICE_URL', default='http://localhost:4009')
MEETING_SERVICE = config('MEETING_SERVICE_URL', default='http://localhost:4010')
FEEDBACK_SERVICE = config('FEEDBACK_SERVICE_URL', default='http://localhost:4011')
FUNDING_SERVICE = config('FUNDING_SERVICE_URL', default='http://localhost:4004')
RESOURCE_SERVICE = config('RESOURCE_SERVICE_URL', default='http://localhost:4005')
NOTIFICATION_SERVICE = config('NOTIFICATION_SERVICE_URL', default='http://localhost:4006')

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(request, *args, **kwargs):
            role = request.META.get('HTTP_X_ROLE', 'user')
            if role not in allowed_roles:
                return Response(
                    {'success': False, 'error': f'Unauthorized. {allowed_roles} role required.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            return f(request, *args, **kwargs)
        return decorated_function
    return decorator

def get_user_from_gateway(request):
    """Get user info from API Gateway headers."""
    user_id = request.META.get('HTTP_X_USER_ID')
    username = request.META.get('HTTP_X_USERNAME', '')
    role = request.META.get('HTTP_X_ROLE', 'user')
    if user_id: return int(user_id), username, role
    return None, None, None

@api_view(['GET'])
@permission_classes([AllowAny])
def home_page(request):
    """Aggregate homepage data"""
    try:
        startups_res = requests.get(f'{STARTUP_SERVICE}/startups/?featured=true&limit=12', timeout=5)
        categories_res = requests.get(f'{STARTUP_SERVICE}/categories/', timeout=5)
        return Response({
            'success': True,
            'data': {
                'featuredStartups': startups_res.json() if startups_res.status_code == 200 else [],
                'categories': categories_res.json() if categories_res.status_code == 200 else []
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def startup_detail(request, startup_id):
    try:
        startup_res = requests.get(f'{STARTUP_SERVICE}/startups/{startup_id}/', timeout=5)
        if startup_res.status_code != 200: return Response({'error': 'Not found'}, status=404)
        
        reviews_res = requests.get(f'{STARTUP_SERVICE}/startups/{startup_id}/reviews/', timeout=3)
        return Response({
            'success': True,
            'startup': startup_res.json(),
            'reviews': reviews_res.json() if reviews_res.status_code == 200 else []
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# ===== INVESTOR PROFILE =====

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def investor_profile(request):
    user_id, _, _ = get_user_from_gateway(request)
    if not user_id: return Response({'error': 'Auth required'}, status=401)
    
    try:
        if request.method == 'GET':
            res = requests.get(f'{STARTUP_SERVICE}/investors/', params={'user_id': user_id}, timeout=5)
            data = res.json()
            return Response({'success': True, 'profile': data[0] if data else None})
        else:
            data = request.data.copy()
            data['user_id'] = user_id
            res = requests.post(f'{STARTUP_SERVICE}/investors/', json=data, timeout=5)
            return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

# ===== PITCHING WORKFLOW =====

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_pitch_request(request):
    user_id, _, _ = get_user_from_gateway(request)
    if not user_id: return Response({'error': 'Auth required'}, status=401)
    try:
        data = request.data.copy()
        res = requests.post(f'{BOOKING_SERVICE}/pitch-requests/', json=data, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_pitch_requests(request):
    user_id, _, _ = get_user_from_gateway(request)
    if not user_id: return Response({'error': 'Auth required'}, status=401)
    try:
        res = requests.get(f'{BOOKING_SERVICE}/pitch-requests/', params={'user_id': user_id}, timeout=5)
        if res.status_code == 200:
            return Response({'success': True, 'data': res.json()})
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_pitch_slots(request):
    try:
        params = request.query_params.dict()
        res = requests.get(f'{SCHEDULING_SERVICE}/pitch-slots/', params=params, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def book_pitch_slot(request, slot_id):
    try:
        data = {'status': 'BOOKED'}
        res = requests.patch(f'{SCHEDULING_SERVICE}/pitch-slots/{slot_id}/update_status/', json=data, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_pitch_booking(request, slot_id):
    user_id, _, _ = get_user_from_gateway(request)
    if not user_id: return Response({'error': 'Auth required'}, status=401)
    try:
        res = requests.post(f'{BOOKING_SERVICE}/pitch-bookings/', json={
            'pitch_slot_id': slot_id,
            'pitch_request_id': request.data.get('pitch_request_id'),
            'user_id': user_id
        }, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_meetings(request):
    try:
        res = requests.get(f'{MEETING_SERVICE}/meetings/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_feedback(request):
    try:
        res = requests.post(f'{FEEDBACK_SERVICE}/feedbacks/', json=request.data, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@role_required(['admin'])
def approve_pitch_request(request, request_id):
    """Handle approval of a pitch request (Admin only)"""
    try:
        res = requests.post(f'{BOOKING_SERVICE}/pitch-requests/{request_id}/approve/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@role_required(['admin'])
def reject_pitch_request(request, request_id):
    """Handle rejection of a pitch request (Admin only)"""
    try:
        res = requests.post(f'{BOOKING_SERVICE}/pitch-requests/{request_id}/reject/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@role_required(['admin'])
def approve_startup(request, startup_id):
    """Handle startup registration approval (Admin only)"""
    try:
        res = requests.post(f'{STARTUP_SERVICE}/startups/{startup_id}/approve/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@role_required(['admin'])
def reject_startup(request, startup_id):
    """Handle startup registration rejection (Admin only)"""
    try:
        res = requests.post(f'{STARTUP_SERVICE}/startups/{startup_id}/reject/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)
