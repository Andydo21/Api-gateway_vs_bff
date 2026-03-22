import os
import mimetypes
import logging
import requests
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.conf import settings
from django.views import View


SCHEDULING_SERVICE_URL = getattr(settings, 'SCHEDULING_SERVICE_URL', 'http://scheduling-service:4008')
BOOKING_SERVICE_URL = getattr(settings, 'BOOKING_SERVICE_URL', 'http://booking-service:4009')
MEETING_SERVICE_URL = getattr(settings, 'MEETING_SERVICE_URL', 'http://meeting-service:4010')
FEEDBACK_SERVICE_URL = getattr(settings, 'FEEDBACK_SERVICE_URL', 'http://feedback-service:4011')


class ProxyView(View):
    """Base proxy view to forward requests"""
    
    target_url = None
    timeout = getattr(settings, 'PROXY_TIMEOUT_SECONDS', 10)
    
    def dispatch(self, request, *args, **kwargs):
        if not self.target_url:
            return JsonResponse({'error': 'Target URL not configured'}, status=500)
        
        # Build target URL
        path = kwargs.get('path', '')
        url = f"{self.target_url}/{path}"
        
        # Forward request
        try:
            method = request.method.lower()
            headers = self.get_headers(request)
            cookies = request.COOKIES
            query_params = request.GET
            
            # Prepare request data
            data = None
            json_data = None
            
            if method in ['post', 'put', 'patch']:
                content_type = request.META.get('CONTENT_TYPE', '')
                if 'application/json' in content_type:
                    import json
                    try:
                        json_data = json.loads(request.body) if request.body else None
                    except:
                        data = request.body
                else:
                    data = request.body
            
            if method == 'get':
                response = requests.get(url, headers=headers, params=query_params, cookies=cookies, timeout=self.timeout)
            elif method == 'post':
                response = requests.post(url, headers=headers, json=json_data, data=data, params=query_params, cookies=cookies, timeout=self.timeout)
            elif method == 'put':
                response = requests.put(url, headers=headers, json=json_data, data=data, params=query_params, cookies=cookies, timeout=self.timeout)
            elif method == 'patch':
                response = requests.patch(url, headers=headers, json=json_data, data=data, params=query_params, cookies=cookies, timeout=self.timeout)
            elif method == 'delete':
                response = requests.delete(url, headers=headers, params=query_params, cookies=cookies, timeout=self.timeout)
            else:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
            
            # Return response with cookies
            http_response = HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('content-type', 'application/json')
            )
            
            # Forward Set-Cookie headers
            for cookie in response.cookies:
                http_response.set_cookie(
                    key=cookie.name,
                    value=cookie.value,
                    max_age=cookie.expires,
                    path=cookie.path,
                    domain=cookie.domain,
                    secure=cookie.secure,
                    httponly=cookie.has_nonstandard_attr('HttpOnly'),
                    samesite=cookie.get_nonstandard_attr('SameSite', 'Lax')
                )
            
            return http_response
            
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=502)
    
    def get_headers(self, request):
        """Get headers to forward"""
        headers = {}
        
        # Forward Authorization header (JWT token)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            headers['Authorization'] = auth_header
        
        # Forward user info headers (injected by JWT middleware)
        user_id = request.META.get('HTTP_X_USER_ID')
        if user_id:
            headers['X-User-ID'] = user_id
        
        username = request.META.get('HTTP_X_USERNAME')
        if username:
            headers['X-Username'] = username
        
        email = request.META.get('HTTP_X_EMAIL')
        if email:
            headers['X-Email'] = email
        
        # Forward content type
        content_type = request.META.get('CONTENT_TYPE')
        if content_type:
            headers['Content-Type'] = content_type
        
        return headers


class WebBFFProxy(ProxyView):
    """Proxy to Web BFF"""
    target_url = settings.WEB_BFF_URL


class AdminBFFProxy(ProxyView):
    """Proxy to Admin BFF"""
    target_url = settings.ADMIN_BFF_URL


class NotificationProxy(ProxyView):
    """Proxy to Notification Service"""
    target_url = settings.NOTIFICATION_SERVICE_URL


class SchedulingProxy(ProxyView):
    """Proxy for Scheduling Service (Slots, Availability)"""
    target_url = SCHEDULING_SERVICE_URL

class BookingProxy(ProxyView):
    """Proxy for Booking Service (PitchRequests, Bookings)"""
    target_url = BOOKING_SERVICE_URL

class MeetingProxy(ProxyView):
    """Proxy for Meeting Service (Zoom/Meet)"""
    target_url = MEETING_SERVICE_URL

class FeedbackProxy(ProxyView):
    """Proxy for Feedback Service (Evaluations)"""
    target_url = FEEDBACK_SERVICE_URL


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'api-gateway'
    })


def serve_frontend(request, filename='index.html'):
    """Serve frontend HTML/JS/CSS files from frontend/web directory"""

    # Strip leading 'web/' if present (handle /ui/web/login.html)
    if filename.startswith('web/'):
        filename = filename[4:]  # Remove 'web/' prefix
    
    # Path to frontend/web directory (mounted as volume in Docker at /app/frontend)
    frontend_dir = os.path.join(settings.BASE_DIR, 'frontend', 'web')
    frontend_dir = os.path.abspath(frontend_dir)

    filepath = os.path.join(frontend_dir, filename)

    # Security: prevent path traversal
    if not os.path.abspath(filepath).startswith(frontend_dir):
        raise Http404("Not found")

    if not os.path.exists(filepath):
        # Default to index.html
        filepath = os.path.join(frontend_dir, 'index.html')

    if not os.path.exists(filepath):
        raise Http404("Frontend not found")

    content_type, _ = mimetypes.guess_type(filepath)
    content_type = content_type or 'text/html'
    return FileResponse(open(filepath, 'rb'), content_type=content_type)


def serve_admin_frontend(request, filename='admin.html'):
    """Serve admin frontend HTML/JS/CSS files from frontend/admin directory"""

    # Path to frontend/admin directory
    admin_dir = os.path.join(settings.BASE_DIR, 'frontend', 'admin')
    admin_dir = os.path.abspath(admin_dir)

    filepath = os.path.join(admin_dir, filename)

    # Security: prevent path traversal
    if not os.path.abspath(filepath).startswith(admin_dir):
        raise Http404("Not found")

    if not os.path.exists(filepath):
        # Default to admin.html for SPA-like behavior or if main entry is missing
        filepath = os.path.join(admin_dir, 'admin.html')

    if not os.path.exists(filepath):
        raise Http404("Admin Panel not found")

    content_type, _ = mimetypes.guess_type(filepath)
    content_type = content_type or 'text/html'

    return FileResponse(open(filepath, 'rb'), content_type=content_type)


def home(request):
    """Home page - redirect to frontend"""
    return serve_frontend(request, 'index.html')
