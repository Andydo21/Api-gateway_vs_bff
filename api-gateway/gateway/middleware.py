"""Rate Limiting and Logging Middleware"""
import time
import logging
import json
from collections import defaultdict
from django.http import JsonResponse
from django.conf import settings
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Simple rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = defaultdict(list)
        
    def __call__(self, request):
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Check rate limit
        current_time = time.time()
        window = 3600  # 1 hour
        max_requests = 10000  # Increased for development
        
        # Clean old requests
        self.requests[ip] = [req_time for req_time in self.requests[ip] 
                             if current_time - req_time < window]
        
        # Check limit
        if len(self.requests[ip]) >= max_requests:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'retry_after': window
            }, status=429)
        
        # Add current request
        self.requests[ip].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoggingMiddleware:
    """Enhanced Request/Response logging middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Start timing
        start_time = time.time()
        
        # Log request details
        request_data = self.get_request_data(request)
        logger.info(f"[REQUEST] {request.method} {request.path}", extra={
            'request_data': request_data,
            'timestamp': now().isoformat()
        })
        
        # Process request
        response = self.get_response(request)
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000  # milliseconds
        
        # Log response details
        response_data = self.get_response_data(response, latency)
        logger.info(f"[RESPONSE] {response.status_code} - {latency:.2f}ms", extra={
            'response_data': response_data,
            'latency_ms': latency,
            'status_code': response.status_code,
            'timestamp': now().isoformat()
        })
        
        # Add custom headers
        response['X-Response-Time'] = f"{latency:.2f}ms"
        
        return response
    
    def get_request_data(self, request):
        """Extract request data for logging"""
        data = {
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self.get_client_ip(request),
        }
        
        # Log request body for POST/PUT/PATCH
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.body:
                    body = request.body.decode('utf-8')
                    # Try to parse as JSON
                    try:
                        data['body'] = json.loads(body)
                    except:
                        data['body'] = body[:500]  # Limit body size
            except Exception as e:
                data['body_error'] = str(e)
        
        return data
    
    def get_response_data(self, response, latency):
        """Extract response data for logging"""
        data = {
            'status_code': response.status_code,
            'latency_ms': round(latency, 2),
            'content_type': response.get('Content-Type', ''),
        }
        
        # Log response body for errors or small responses
        if response.status_code >= 400:
            try:
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    try:
                        data['body'] = json.loads(content)
                    except:
                        data['body'] = content[:500]
            except Exception as e:
                data['body_error'] = str(e)
        
        return data
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

