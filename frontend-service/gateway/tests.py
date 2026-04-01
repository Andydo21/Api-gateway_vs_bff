from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from .auth_middleware import JWTAuthenticationMiddleware
from .views import ProxyView
import json

class AuthMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda r: JsonResponse({'status': 'ok'})
        self.middleware = JWTAuthenticationMiddleware(self.get_response)

    def test_public_path_allows_access(self):
        # Health check is public
        request = self.factory.get('/health/')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_notification_path_is_public(self):
        # We recently made notifications public for testing
        request = self.factory.get('/notifications/list/')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_protected_path_requires_token(self):
        # Assuming something like /web/orders/ is protected
        request = self.factory.get('/web/orders/')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Authentication required')

class ProxyViewTests(TestCase):
    def test_proxy_view_build_url(self):
        # We can test the build_url logic or if it fails without target_url
        view = ProxyView()
        request = RequestFactory().get('/some-path/')
        response = view.dispatch(request, path='test-path')
        # Should return 500 because target_url is None in base class
        self.assertEqual(response.status_code, 500)
