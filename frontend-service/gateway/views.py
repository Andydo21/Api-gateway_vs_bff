import os
import mimetypes
import logging
import requests
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.conf import settings
from django.views import View



def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'api-gateway'
    })


def serve_frontend(request, filename='index.html'):
    """Serve frontend HTML/JS/CSS files from frontend/web directory"""

    # Strip leading 'web/' if present (handle /ui/web/login.html)
    if filename.startswith('web/'):
        filename = filename[4:]  # Remove 'web/' prefix
    
    # Path to frontend/web directory (mounted as volume in Docker at /app/frontend)
    frontend_dir = os.path.join(settings.BASE_DIR, 'frontend', 'web')
    frontend_dir = os.path.abspath(frontend_dir)

    filepath = os.path.join(frontend_dir, filename)

    # Security: prevent path traversal
    if not os.path.abspath(filepath).startswith(frontend_dir):
        raise Http404("Not found")

    if not os.path.exists(filepath):
        # Default to index.html
        filepath = os.path.join(frontend_dir, 'index.html')

    if not os.path.exists(filepath):
        raise Http404("Frontend not found")

    content_type, _ = mimetypes.guess_type(filepath)
    content_type = content_type or 'text/html'
    return FileResponse(open(filepath, 'rb'), content_type=content_type)


def serve_admin_frontend(request, filename='admin.html'):
    """Serve admin frontend HTML/JS/CSS files from frontend/admin directory"""

    # Path to frontend/admin directory
    admin_dir = os.path.join(settings.BASE_DIR, 'frontend', 'admin')
    admin_dir = os.path.abspath(admin_dir)

    filepath = os.path.join(admin_dir, filename)

    # Security: prevent path traversal
    if not os.path.abspath(filepath).startswith(admin_dir):
        raise Http404("Not found")

    if not os.path.exists(filepath):
        # Default to admin.html for SPA-like behavior or if main entry is missing
        filepath = os.path.join(admin_dir, 'admin.html')

    if not os.path.exists(filepath):
        raise Http404("Admin Panel not found")

    content_type, _ = mimetypes.guess_type(filepath)
    content_type = content_type or 'text/html'

    return FileResponse(open(filepath, 'rb'), content_type=content_type)


def home(request):
    """Home page - redirect to frontend"""
    return serve_frontend(request, 'index.html')
