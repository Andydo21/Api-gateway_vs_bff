"""JWT Authentication Middleware for API Gateway"""
import jwt
from django.http import JsonResponse
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthenticationMiddleware:
    """
    Middleware to authenticate JWT tokens at API Gateway level.
    Extracts user info from token and injects into headers for downstream services (BFF).
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = [
        '/health',
        '/web/users/login/',
        '/web/users/register/',
        '/admin/users/login/',
        '/admin/users/register/',
        '/web/products/',  # Browse products without login
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip authentication for public paths
        if self.is_public_path(request.path):
            return self.get_response(request)
        
        # Skip for static files, frontend HTML, and browser requests
        if (request.path.startswith('/static/') or 
            request.path.startswith('/media/') or 
            request.path.startswith('/ui/') or
            request.path == '/favicon.ico' or
            request.path.startswith('/.well-known/')):
            return self.get_response(request)
        
        # Get Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        print(f"🔍 [AUTH] Path: {request.path}")
        print(f"🔍 [AUTH] Authorization header: {auth_header[:50] if auth_header else 'NONE'}...")
        
        if not auth_header.startswith('Bearer '):
            # No token - allow through for endpoints that support guest access
            if self.supports_guest_access(request.path):
                return self.get_response(request)
            
            print(f"❌ [AUTH] No Bearer token found")
            return JsonResponse({
                'error': 'Authentication required',
                'detail': 'No authentication token provided'
            }, status=401)
        
        # Extract token
        token = auth_header.split(' ')[1]
        print(f"🔑 [AUTH] Token extracted: {token[:20]}...{token[-20:]}")
        
        try:
            # Verify token using simplejwt
            print(f"⏳ [AUTH] Validating token...")
            validated_token = UntypedToken(token)
            
            # Extract user info from token
            user_id = validated_token.get('user_id')
            username = validated_token.get('username', '')
            email = validated_token.get('email', '')
            
            print(f"✅ [AUTH] Token valid! user_id={user_id}, username={username}")
            
            # Inject user info into request headers for downstream services
            # BFF services will read these headers instead of verifying token again
            request.META['HTTP_X_USER_ID'] = str(user_id)
            request.META['HTTP_X_USERNAME'] = username
            request.META['HTTP_X_EMAIL'] = email
            
            # Token is valid, proceed with request
            response = self.get_response(request)
            return response
            
        except (InvalidToken, TokenError) as e:
            print(f"❌ [AUTH] JWT validation failed: {type(e).__name__} - {str(e)}")
            return JsonResponse({
                'error': 'Invalid token',
                'detail': str(e)
            }, status=401)
        except Exception as e:
            print(f"❌ [AUTH] Unexpected error: {type(e).__name__} - {str(e)}")
            return JsonResponse({
                'error': 'Authentication failed',
                'detail': str(e)
            }, status=401)
    
    def is_public_path(self, path):
        """Check if path is public (no auth required)"""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False
    
    def supports_guest_access(self, path):
        """Endpoints that work without authentication (very limited)"""
        guest_paths = [
            '/web/products/',  # Browse products only
        ]
        for guest_path in guest_paths:
            if path.startswith(guest_path):
                return True
        return False
