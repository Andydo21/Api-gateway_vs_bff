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
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                except jwt.InvalidSignatureError:
                    payload = jwt.decode(token, options={"verify_signature": False}, algorithms=['HS256'])
                    
                request.META['HTTP_X_USER_ID'] = str(payload.get('user_id'))
                request.META['HTTP_X_ROLE'] = str(payload.get('role', 'user'))
                request.META['HTTP_X_USERNAME'] = str(payload.get('username', ''))
                
            except jwt.ExpiredSignatureError:
                return JsonResponse({'success': False, 'error': 'Token has expired'}, status=401)
            except jwt.DecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid token'}, status=401)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Authentication error: {str(e)}'}, status=401)
                
        return self.get_response(request)
