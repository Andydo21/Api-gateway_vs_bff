"""
URL configuration for API Gateway project.
"""
from django.urls import path, include, re_path
from gateway.views import home, serve_frontend, serve_admin_frontend

urlpatterns = [
    path('', home, name='home'),
    path('health/', include('gateway.urls_health')),

    # Serve Admin UI
    path('admin-ui/', serve_admin_frontend, name='admin-ui'),
    re_path(r'^admin-ui/(?P<filename>[\w\-/]+\.html)$', serve_admin_frontend, name='admin-ui-file'),

    # Serve frontend HTML files
    path('ui/', serve_frontend, name='frontend-home'),
    re_path(r'^ui/(?P<filename>[\w\-/]+\.html)$', serve_frontend, name='frontend-file'),
]
