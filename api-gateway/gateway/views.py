"""Proxy views to forward requests to BFF services"""
import requests
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views import View


class ProxyView(View):
    """Base proxy view to forward requests"""
    
    target_url = None
    
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
                response = requests.get(url, headers=headers, params=request.GET, cookies=cookies)
            elif method == 'post':
                response = requests.post(url, headers=headers, json=json_data, data=data, params=request.GET, cookies=cookies)
            elif method == 'put':
                response = requests.put(url, headers=headers, json=json_data, data=data, cookies=cookies)
            elif method == 'patch':
                response = requests.patch(url, headers=headers, json=json_data, data=data, cookies=cookies)
            elif method == 'delete':
                response = requests.delete(url, headers=headers, cookies=cookies)
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


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'api-gateway'
    })


def serve_frontend(request, filename='index.html'):
    """Serve frontend HTML/JS/CSS files from frontend/web directory"""
    import os
    import mimetypes
    from django.http import FileResponse, Http404

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


def home(request):
    """Home page - redirect to frontend"""
    return serve_frontend(request, 'index.html')
