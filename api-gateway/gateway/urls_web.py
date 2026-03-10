"""URL configuration for Web BFF routing"""
from django.urls import path, re_path
from .views import WebBFFProxy

urlpatterns = [
    re_path(r'^(?P<path>.*)$', WebBFFProxy.as_view(), name='web-bff-proxy'),
]
