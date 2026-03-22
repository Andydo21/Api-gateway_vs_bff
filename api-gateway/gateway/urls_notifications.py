from django.urls import path, re_path
from .views import NotificationProxy

urlpatterns = [
    re_path(r'^(?P<path>.*)$', NotificationProxy.as_view(), name='notification-proxy'),
]
