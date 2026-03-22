"""Admin BFF Views - Admin panel functionality"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests
from decouple import config

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
def dashboard(request):
    """Admin dashboard statistics"""
    try:
        users_res = requests.get(f"{USER_SERVICE}/users/", timeout=5)
        startups_res = requests.get(f"{STARTUP_SERVICE}/startups/", timeout=5)
        pitching_res = requests.get(f"{BOOKING_SERVICE}/pitch-requests/", timeout=5)
        users_stats = requests.get(f'{USER_SERVICE}/users/stats/', timeout=5)
        scheduling_stats = requests.get(f'{SCHEDULING_SERVICE}/pitch-slots/', timeout=5)
        
        return Response({
            'success': True,
            'data': {
                'pitch_slots': pitch_slots_stats.json() if pitch_slots_stats.status_code == 200 else {},
                'users': users_stats.json() if users_stats.status_code == 200 else {}
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def startups(request):
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
def pitch_slots(request):
    try:
        res = requests.get(f'{SCHEDULING_SERVICE}/pitch-slots/', params=request.GET.dict(), timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def pitch_slot_status(request, slot_id):
    """Update pitch slot status (Approve/Reject)"""
    try:
        res = requests.patch(f'{SCHEDULING_SERVICE}/pitch-slots/{slot_id}/update_status/', json=request.data, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def users(request):
    try:
        res = requests.get(f'{USER_SERVICE}/users/', params=request.GET.dict(), timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_detail(request, user_id):
    try:
        res = requests.get(f'{USER_SERVICE}/users/{user_id}/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([AllowAny])
def user_ban(request, user_id):
    try:
        res = requests.put(f'{USER_SERVICE}/users/{user_id}/', json=request.data, timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)


