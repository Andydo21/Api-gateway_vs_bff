"""Web BFF Views - Aggregates data from multiple microservices"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
from functools import wraps
from decouple import config

# Microservice URLs
USER_SERVICE = config('USER_SERVICE_URL', default='http://user-service:4001')
STARTUP_SERVICE = config('STARTUP_SERVICE_URL', default='http://startup-service:4002')
SCHEDULING_SERVICE = config('SCHEDULING_SERVICE_URL', default='http://scheduling-service:4008')
BOOKING_SERVICE = config('BOOKING_SERVICE_URL', default='http://booking-service:4009')
MEETING_SERVICE = config('MEETING_SERVICE_URL', default='http://meeting-service:4010')
FEEDBACK_SERVICE = config('FEEDBACK_SERVICE_URL', default='http://feedback-service:4011')
FUNDING_SERVICE = config('FUNDING_SERVICE_URL', default='http://funding-service:4004')
RESOURCE_SERVICE = config('RESOURCE_SERVICE_URL', default='http://resource-service:4005')
NOTIFICATION_SERVICE = config('NOTIFICATION_SERVICE_URL', default='http://notification-service:4007')

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

@api_view(['GET'])
@permission_classes([AllowAny])
def home_page(request):
    """Aggregate homepage data"""
    try:
        startups_res = requests.get(
            f'{STARTUP_SERVICE}/startups/',
            headers={'Accept': 'application/json'},
            timeout=5,
        )
        startups = startups_res.json() if startups_res.status_code == 200 else []

        # Handle paginated response
        if isinstance(startups, dict) and 'results' in startups:
            startups = startups['results']

        # Extract unique categories from startup data
        seen = set()
        categories = []
        for s in startups:
            cat = s.get('industry') or s.get('category_name')
            if cat and cat not in seen:
                seen.add(cat)
                categories.append({'id': cat, 'name': cat})

        return Response({
            'success': True,
            'data': {
                'featuredStartups': startups,
                'categories': categories,
            },
            'featured_startups': startups,
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Proxy login request to User Service"""
    try:
        res = requests.post(f'{USER_SERVICE}/login/', json=request.data, timeout=5)
        try:
            data = res.json()
            return Response(data, status=res.status_code)
        except:
            return Response({'success': False, 'message': res.text}, status=res.status_code)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Proxy registration request to User Service"""
    try:
        res = requests.post(f'{USER_SERVICE}/register/', json=request.data, timeout=5)
        try:
            return Response(res.json(), status=res.status_code)
        except:
            return Response({'success': False, 'message': res.text}, status=res.status_code)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def startup_detail(request, startup_id):
    """Proxy startup detail request"""
    try:
        res = requests.get(f'{STARTUP_SERVICE}/startups/{startup_id}/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@role_required(['admin'])
def approve_startup(request, startup_id):
    try:
        res = requests.post(f'{STARTUP_SERVICE}/startups/{startup_id}/approve/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@role_required(['admin'])
def reject_startup(request, startup_id):
    try:
        res = requests.post(f'{STARTUP_SERVICE}/startups/{startup_id}/reject/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def investor_profile(request):
    return Response({'message': 'Investor profile proxy - Not implemented'}, status=200)

@api_view(['POST'])
@role_required(['startup', 'admin', 'investor', 'user']) # Allow any authenticated role for now, or just require token
def submit_pitch_request(request):
    """Proxy to booking-service to submit a pitch request"""
    try:
        response = requests.post(f"{BOOKING_SERVICE}/api/pitch-requests/", json=request.data, timeout=5)
        response.raise_for_status()
        return Response({'success': True, 'data': response.json(), 'id': response.json().get('id')})
    except requests.exceptions.RequestException as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@role_required(['startup', 'admin', 'investor', 'user'])
def list_pitch_requests(request):
    """Proxy to booking-service to get pitch requests"""
    try:
        # Optionally filter by startup_id if provided
        params = request.query_params
        response = requests.get(f"{BOOKING_SERVICE}/api/pitch-requests/", params=params, timeout=5)
        response.raise_for_status()
        
        # booking-service might return heavily paginated data or just a list
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        return Response({'success': True, 'data': results})
    except requests.exceptions.RequestException as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@role_required(['admin', 'investor'])
def approve_pitch_request(request, request_id):
    """Proxy to booking-service to approve a pitch request"""
    try:
        response = requests.post(f"{BOOKING_SERVICE}/api/pitch-requests/{request_id}/approve/", timeout=5)
        response.raise_for_status()
        return Response({'success': True, 'data': response.json()})
    except requests.exceptions.RequestException as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@role_required(['admin', 'investor'])
def reject_pitch_request(request, request_id):
    """Proxy to booking-service to reject a pitch request"""
    try:
        response = requests.post(f"{BOOKING_SERVICE}/api/pitch-requests/{request_id}/reject/", timeout=5)
        response.raise_for_status()
        return Response({'success': True, 'data': response.json()})
    except requests.exceptions.RequestException as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_pitch_slots(request):
    try:
        res = requests.get(
            f'{SCHEDULING_SERVICE}/pitch-slots/',
            headers={'Accept': 'application/json'},
            timeout=5,
        )
        try:
            payload = res.json()
        except ValueError:
            payload = {
                'error': 'Invalid upstream response from scheduling-service',
                'upstream_status': res.status_code,
                'upstream_body': res.text[:500],
            }
            return Response(payload, status=502)

        return Response(payload, status=res.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST', 'PATCH'])
@permission_classes([AllowAny])
def book_pitch_slot(request, slot_id):
    try:
        payload = {'status': 'BOOKED'}
        if isinstance(getattr(request, 'data', None), dict):
            payload.update({k: v for k, v in request.data.items() if k != 'status'})

        # scheduling-service exposes DRF action: /pitch-slots/{id}/update_status/
        res = requests.patch(
            f'{SCHEDULING_SERVICE}/pitch-slots/{slot_id}/update_status/',
            headers={'Accept': 'application/json'},
            json=payload,
            timeout=5,
        )

        try:
            body = res.json()
        except ValueError:
            body = {
                'error': 'Invalid upstream response from scheduling-service',
                'upstream_status': res.status_code,
                'upstream_body': res.text[:500],
            }
            return Response(body, status=502)

        if res.status_code in (200, 202):
            return Response({'success': True, 'slot_id': slot_id, 'result': body}, status=200)

        return Response(body, status=res.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_meetings(request):
    try:
        res = requests.get(
            f'{MEETING_SERVICE}/meetings/',
            headers={'Accept': 'application/json'},
            timeout=5,
        )
        try:
            payload = res.json()
        except ValueError:
            payload = {
                'error': 'Invalid upstream response from meeting-service',
                'upstream_status': res.status_code,
                'upstream_body': res.text[:500],
            }
            return Response(payload, status=502)

        return Response(payload, status=res.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_feedback(request):
    try:
        payload = dict(request.data) if hasattr(request.data, 'items') else {}

        # Frontend currently sends "booking"; normalize to backend schema "booking_id".
        if 'booking_id' not in payload and 'booking' in payload:
            payload['booking_id'] = payload.pop('booking')

        # Fallback to gateway identity when investor_id is not explicitly provided.
        if not payload.get('investor_id'):
            investor_id = request.META.get('HTTP_X_USER_ID')
            if investor_id:
                payload['investor_id'] = investor_id

        if not payload.get('booking_id'):
            return Response({'error': 'booking_id is required'}, status=400)
        if not payload.get('investor_id'):
            return Response({'error': 'investor_id is required'}, status=400)

        res = requests.post(
            f'{FEEDBACK_SERVICE}/feedbacks/',
            headers={'Accept': 'application/json'},
            json=payload,
            timeout=5,
        )

        try:
            body = res.json()
        except ValueError:
            body = {
                'error': 'Invalid upstream response from feedback-service',
                'upstream_status': res.status_code,
                'upstream_body': res.text[:500],
            }
            return Response(body, status=502)

        return Response(body, status=res.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_feedbacks(request):
    try:
        res = requests.get(
            f'{FEEDBACK_SERVICE}/feedbacks/',
            headers={'Accept': 'application/json'},
            params=request.GET,
            timeout=5,
        )

        try:
            body = res.json()
        except ValueError:
            body = {
                'error': 'Invalid upstream response from feedback-service',
                'upstream_status': res.status_code,
                'upstream_body': res.text[:500],
            }
            return Response(body, status=502)

        return Response(body, status=res.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
