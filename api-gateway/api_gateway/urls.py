"""
URL configuration for API Gateway project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from gateway.views import home, serve_frontend

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('web/', include('gateway.urls_web')),
    path('admin-panel/', include('gateway.urls_admin')),
    path('health/', include('gateway.urls_health')),

    # Serve frontend HTML files
    # Truy cập: http://localhost:8000/ui/ hoặc http://localhost:8000/ui/web/index.html
    path('ui/', serve_frontend, name='frontend-home'),
    re_path(r'^ui/(?P<filename>[\w\-/]+\.html)$', serve_frontend, name='frontend-file'),
]
