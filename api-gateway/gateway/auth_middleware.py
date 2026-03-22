"""JWT Authentication Middleware for API Gateway"""
import logging
import re
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    """
    Middleware to authenticate JWT tokens at API Gateway level.
    Extracts user info from token and injects into headers for downstream services (BFF).
    """
    
    # Public routes that don't require authentication.
    # Each rule supports optional method restrictions to avoid broad path bypasses.
    PUBLIC_ROUTE_RULES = [
        (None, re.compile(r'^/health/?$')),
        ('POST', re.compile(r'^/web/users/login/?$')),
        ('POST', re.compile(r'^/web/users/register/?$')),
        ('POST', re.compile(r'^/admin-panel/users/login/?$')),
        ('POST', re.compile(r'^/admin-panel/users/register/?$')),
        ('GET', re.compile(r'^/web/home/?$')),
        ('GET', re.compile(r'^/web/categories/?$')),
        ('GET', re.compile(r'^/web/products/?$')),
        ('GET', re.compile(r'^/web/products/\d+/?$')),
        ('GET', re.compile(r'^/web/products/\d+/reviews/?$')),
        (None, re.compile(r'^/notifications/.*$')),
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip authentication for public paths
        if self.is_public_path(request.path, request.method):
            return self.get_response(request)
        
        # Skip for static files, frontend HTML, and browser requests
        if (request.path.startswith('/static/') or 
            request.path.startswith('/media/') or 
            request.path.startswith('/ui/') or
            request.path.startswith('/admin/') or
            request.path == '/favicon.ico' or
            request.path.startswith('/.well-known/')):
            return self.get_response(request)
        
        # Get Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        logger.debug("[AUTH] Path=%s, has_auth_header=%s", request.path, bool(auth_header))
        
        if not auth_header.startswith('Bearer '):
            logger.info("[AUTH] Missing Bearer token for path=%s", request.path)
            return JsonResponse({
                'error': 'Authentication required',
                'detail': 'No authentication token provided'
            }, status=401)
        
        # Extract token
        token = auth_header.split(' ')[1]
        try:
            # Verify token using simplejwt
            validated_token = UntypedToken(token)
            
            # Extract user info from token
            user_id = validated_token.get('user_id')
            username = validated_token.get('username', '')
            email = validated_token.get('email', '')
            role = validated_token.get('role', 'user')
            
            logger.debug("[AUTH] Token validated for user_id=%s, role=%s", user_id, role)
            
            # Inject user info into request headers for downstream services
            # BFF services will read these headers instead of verifying token again
            request.META['HTTP_X_USER_ID'] = str(user_id)
            request.META['HTTP_X_USERNAME'] = username
            request.META['HTTP_X_EMAIL'] = email
            request.META['HTTP_X_ROLE'] = role
            
            # Token is valid, proceed with request
            response = self.get_response(request)
            return response
            
        except (InvalidToken, TokenError) as e:
            logger.warning("[AUTH] JWT validation failed: %s - %s", type(e).__name__, str(e))
            return JsonResponse({
                'error': 'Invalid token',
                'detail': str(e)
            }, status=401)
        except Exception as e:
            logger.exception("[AUTH] Unexpected authentication error")
            return JsonResponse({
                'error': 'Authentication failed',
                'detail': str(e)
            }, status=401)
    
    def is_public_path(self, path, method):
        """Check if path is public (no auth required)."""
        return self.matches_public_route(path, method)

    def matches_public_route(self, path, method):
        for allowed_method, pattern in self.PUBLIC_ROUTE_RULES:
            method_matches = allowed_method is None or method == allowed_method
            if method_matches and pattern.match(path):
                return True
        return False
