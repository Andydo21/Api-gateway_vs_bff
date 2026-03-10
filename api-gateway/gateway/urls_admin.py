"""URL configuration for Admin BFF routing"""
from django.urls import path, re_path
from .views import AdminBFFProxy

urlpatterns = [
    re_path(r'^(?P<path>.*)$', AdminBFFProxy.as_view(), name='admin-bff-proxy'),
]
