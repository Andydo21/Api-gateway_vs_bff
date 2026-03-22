"""Rate Limiting and Logging Middleware"""
import time
import logging
import json
from collections import defaultdict
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Redis-backed rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests, self.window = self.parse_rate_limit(
            getattr(settings, 'RATE_LIMIT', '100/h')
        )
        
    def __call__(self, request):
        # Skip health check from rate limiting if needed
        if request.path == '/health/':
            return self.get_response(request)

        # Get client IP
        ip = self.get_client_ip(request)
        
        # Check rate limit using Redis (fixed window approach)
        window = self.window
        max_requests = self.max_requests
        
        # Create a unique key for the current window
        # Format: ratelimit:<ip>:<window_timestamp_bucket>
        current_bucket = int(time.time() / window)
        cache_key = f"rl:{ip}:{current_bucket}"
        
        try:
            # Atomic increment
            # If key doesn't exist, it starts at 1 and we set expiry
            count = cache.get(cache_key)
            
            if count is None:
                cache.set(cache_key, 1, timeout=window)
                count = 1
            else:
                if count >= max_requests:
                    logger.warning(f"[RATELIMIT] Limit exceeded for IP: {ip}")
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'retry_after': window
                    }, status=429)
                
                count = cache.incr(cache_key)
            
            # Add headers for transparency
            response = self.get_response(request)
            response['X-RateLimit-Limit'] = str(max_requests)
            response['X-RateLimit-Remaining'] = str(max(0, max_requests - count))
            return response
            
        except Exception as e:
            # Fallback for cache failure (allow request but log error)
            logger.error(f"[RATELIMIT] Cache error: {str(e)}")
            return self.get_response(request)

    def parse_rate_limit(self, rate_limit):
        """Parse RATE_LIMIT in '<count>/<unit>' format, e.g. '100/h'."""
        fallback = (100, 3600)
        try:
            value = str(rate_limit).strip()
            if '/' not in value:
                return fallback

            count_str, unit = value.split('/', 1)
            count = int(count_str)
            unit = unit.strip().lower()

            unit_seconds = {
                's': 1,
                'm': 60,
                'h': 3600,
                'd': 86400,
            }
            window_seconds = unit_seconds.get(unit)
            if not window_seconds or count <= 0:
                return fallback

            return count, window_seconds
        except Exception:
            return fallback
    
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

