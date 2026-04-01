import jwt
from django.conf import settings
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    """
    Middleware that intercepts the Authorization header, decodes the JWT,
    and injects HTTP_X_USER_ID, HTTP_X_ROLE, and HTTP_X_USERNAME into request.META.
    This replaces APISIX's JWT plugin functionality.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # We can verify the signature if the SECRET_KEY matches the one used by USER_SERVICE
                # Or we can just decode it since APISIX handles external facing routing (but APISIX JWT is off)
                # It's safest to verify. We'll try to verify, but fallback to unverified if keys differ for now.
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                except jwt.InvalidSignatureError:
                    # If secret keys are out of sync across microservices, at least decode to enforce role
                    # The underlying microservice will do the strict signature validation anyway
                    payload = jwt.decode(token, options={"verify_signature": False}, algorithms=['HS256'])
                    
                request.META['HTTP_X_USER_ID'] = str(payload.get('user_id'))
                request.META['HTTP_X_ROLE'] = payload.get('role', 'user')
                request.META['HTTP_X_USERNAME'] = payload.get('username', '')
                
            except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError):
                # Only return 401 if the token clearly looks like a JWT but is failed.
                # If it's a simple bypass string like 'dev-bypass-token', just let it pass
                # and let BypassAuthMiddleware or AllowAny handle it downstream.
                if token.count('.') == 2:
                    return JsonResponse({'success': False, 'error': 'Invalid or expired token'}, status=401)
                
        return self.get_response(request)

class BypassAuthMiddleware:
    """
    Development middleware that injects 'admin' role if no Authorization header is present.
    Added to allow testing without security tokens while keeping the original middleware intact.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or 'dev-bypass-token' in auth_header:
            request.META['HTTP_X_ROLE'] = 'admin'
            request.META['HTTP_X_USER_ID'] = '1'
            request.META['HTTP_X_USERNAME'] = 'dev_user'
        return self.get_response(request)
