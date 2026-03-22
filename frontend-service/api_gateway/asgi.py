import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from channels.http import AsgiHandler

from gateway.consumers import WebSocketProxyConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_gateway.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/notifications/<str:user_id>/", WebSocketProxyConsumer.as_asgi()),
        ])
    ),
})
