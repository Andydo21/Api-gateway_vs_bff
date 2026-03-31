from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
from functools import wraps
from decouple import config
from .utils import startup_breaker, user_breaker, booking_breaker
import pybreaker

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
    """Aggregate homepage data with Circuit Breaker and Fallback"""
    startups = []
    service_status = "healthy"

    try:
        # Use breaker.call() for maximum reliability across versions
        res = startup_breaker.call(
            requests.get,
            f'{STARTUP_SERVICE}/startups/',
            headers={'Accept': 'application/json'},
            timeout=3
        )
        
        if res.status_code == 200:
            startups = res.json()
            if isinstance(startups, dict) and 'results' in startups:
                startups = startups['results']
        else:
            startups = []

    except (pybreaker.CircuitBreakerError, requests.RequestException) as e:
        # Fallback: Return empty list instead of 500
        startups = []
        service_status = "degraded"
        print(f"DEBUG: Startup Service Breaker tripped or Error: {str(e)}")

    # Extract unique categories from startup data
    seen = set()
    categories = []
    for s in startups:
        # Safety check if startups is not a list of dicts
        if not isinstance(s, dict): continue
        cat = s.get('industry') or s.get('category_name')
        if cat and cat not in seen:
            seen.add(cat)
            categories.append({'id': cat, 'name': cat})

    # Aggregate health from User Service as well
    user_service_status = "healthy"
    try:
        user_res = requests.get(f'{USER_SERVICE}/health/', timeout=2)
        if user_res.status_code != 200:
            user_service_status = "unhealthy"
    except:
        user_service_status = "unavailable"

    return Response({
        'success': True,
        'data': {
            'featuredStartups': startups,
            'categories': categories,
            'service_status': {
                'startup_service': service_status,
                'user_service': user_service_status,
                'overall': "healthy" if service_status == "healthy" and user_service_status == "healthy" else "degraded"
            }
        },
        'featured_startups': startups,
    })

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
    """BFF for single startup detail aggregation (Startup + Owner + Reviews)"""
    try:
        # 1. Fetch startup basic info
        res = requests.get(f'{STARTUP_SERVICE}/startups/{startup_id}/', timeout=5)
        if res.status_code != 200:
            return Response(res.json(), status=res.status_code)
        
        startup_data = res.json()
        
        # 2. Aggregate: Fetch Owner info from User Service
        owner_id = startup_data.get('user_id') or startup_data.get('owner_id')
        if owner_id:
            try:
                user_res = requests.get(f'{USER_SERVICE}/users/{owner_id}/', timeout=2)
                if user_res.status_code == 200:
                    startup_data['owner_details'] = user_res.json()
            except:
                startup_data['owner_details'] = None
        
        # 3. Aggregate: Fetch Reviews
        reviews = []
        try:
            rev_res = requests.get(f'{STARTUP_SERVICE}/startups/{startup_id}/reviews/', timeout=2)
            if rev_res.status_code == 200:
                reviews = rev_res.json()
        except:
            pass

        return Response({
            'success': True,
            'startup': startup_data,
            'reviews': reviews
        })
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def startup_reviews(request, startup_id):
    """Proxy startup reviews request"""
    try:
        res = requests.get(f'{STARTUP_SERVICE}/startups/{startup_id}/reviews/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def startup_reviews_summary(request, startup_id):
    """Proxy startup reviews summary request"""
    try:
        res = requests.get(f'{STARTUP_SERVICE}/startups/{startup_id}/reviews/summary/', timeout=5)
        return Response(res.json(), status=res.status_code)
    except Exception as e: return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@role_required(['founder', 'admin', 'user'])  # Basic user can also register a startup to become a founder
def create_startup(request):
    """Proxy startup creation request to Startup Service"""
    try:
        payload = request.data.copy()
        # Automatically set user_id from Gateway headers
        user_id = request.META.get('HTTP_X_USER_ID')
        if user_id:
            payload['user_id'] = user_id
            
        res = requests.post(f'{STARTUP_SERVICE}/startups/', json=payload, timeout=5)
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

@api_view(['POST'])
@role_required(['admin', 'investor'])
def book_pitch_slot(request, slot_id):
    """
    Orchestrate pitch booking using booking-service (Saga entry).
    This creates a PitchBooking record which then triggers a Saga event to:
    1. Reserve the slot in scheduling-service
    2. (Optional) Notify the founder
    """
    try:
        # Expecting pitch_request_id in payload
        pitch_request_id = request.data.get('pitch_request_id')
        if not pitch_request_id:
            return Response({'error': 'pitch_request_id is required'}, status=400)
            
        payload = {
            'pitch_request': pitch_request_id,
            'pitch_slot_id': slot_id,
            'status': 'INITIALIZED' # Triggers Saga
        }

        # Create booking in booking-service
        # booking-service is on 8002
        res = requests.post(f'{BOOKING_SERVICE}/api/pitch-bookings/', json=payload, timeout=5)
        
        if res.status_code == 201:
            return Response({
                'success': True, 
                'message': 'Booking initiated. The slot will be reserved shortly via Saga.',
                'data': res.json()
            }, status=201)
            
        return Response(res.json(), status=res.status_code)
        
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

@api_view(['GET', 'POST'])
@role_required(['investor', 'admin'])
def list_create_availability_templates(request):
    """Proxy to scheduling-service for investor availability templates"""
    try:
        # Resolve investor_id (priority: query_param > header_x_user_id)
        investor_id = request.query_params.get('investor_id')
        if not investor_id:
            investor_id = request.META.get('HTTP_X_USER_ID')
            
        if request.method == 'GET':
            res = requests.get(f'{SCHEDULING_SERVICE}/availability-templates/by_investor/?investor_id={investor_id}', timeout=5)
            return Response(res.json(), status=res.status_code)
            
        elif request.method == 'POST':
            payload = request.data.copy()
            # Ensure investor is set to the current user if not explicitly provided
            if 'investor' not in payload:
                payload['investor'] = investor_id
                
            res = requests.post(f'{SCHEDULING_SERVICE}/availability-templates/', json=payload, timeout=5)
            return Response(res.json(), status=res.status_code)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)
