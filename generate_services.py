#!/usr/bin/env python3
"""
Script to generate complete Django microservices architecture
"""

import os
import shutil

BASE_DIR = r"d:\Django_project\api-gateway_vs_bff"

# Service configurations
SERVICES = {
    'bff': {
        'web-bff': {'port': 3001, 'app_name': 'web_bff'},
        'admin-bff': {'port': 3002, 'app_name': 'admin_bff'},
    },
    'microservices': {
        'user-service': {'port': 4001, 'app_name': 'user_service'},
        'product-service': {'port': 4002, 'app_name': 'product_service'},
        'order-service': {'port': 4003, 'app_name': 'order_service'},
        'payment-service': {'port': 4004, 'app_name': 'payment_service'},
        'inventory-service': {'port': 4005, 'app_name': 'inventory_service'},
        'recommendation-service': {'port': 4006, 'app_name': 'recommendation_service'},
    }
}

def create_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)
    print(f"Created: {path}")

def create_file(path, content):
    """Create file with content"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

def generate_django_service(category, service_name, config):
    """Generate a complete Django service"""
    service_path = os.path.join(BASE_DIR, category, service_name)
    app_name = config['app_name']
    port = config['port']
    
    # Create directories
    create_directory(service_path)
    create_directory(os.path.join(service_path, app_name))
    create_directory(os.path.join(service_path, 'api'))
    
    # manage.py
    manage_py = f'''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{app_name}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''
    create_file(os.path.join(service_path, 'manage.py'), manage_py)
    
    # settings.py
    settings_py = f'''from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-{service_name}-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{app_name}.urls'

TEMPLATES = [{{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {{
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    }},
}}]

WSGI_APPLICATION = '{app_name}.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='ecommerce'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }}
}}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}}

CORS_ALLOW_ALL_ORIGINS = True
'''
    create_file(os.path.join(service_path, app_name, 'settings.py'), settings_py)
    
    # urls.py
    urls_py = f'''from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]
'''
    create_file(os.path.join(service_path, app_name, 'urls.py'), urls_py)
    
    # wsgi.py
    wsgi_py = f'''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{app_name}.settings')
application = get_wsgi_application()
'''
    create_file(os.path.join(service_path, app_name, 'wsgi.py'), wsgi_py)
    
    # __init__.py files
    create_file(os.path.join(service_path, app_name, '__init__.py'), '')
    create_file(os.path.join(service_path, 'api', '__init__.py'), '')
    
    # api/apps.py
    apps_py = '''from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
'''
    create_file(os.path.join(service_path, 'api', 'apps.py'), apps_py)
    
    # api/admin.py
    create_file(os.path.join(service_path, 'api', 'admin.py'), 'from django.contrib import admin\n')
    
    # Dockerfile
    dockerfile = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["sh", "-c", "python manage.py migrate && gunicorn {app_name}.wsgi:application --bind 0.0.0.0:{port}"]
'''
    create_file(os.path.join(service_path, 'Dockerfile'), dockerfile)
    
    # requirements.txt
    requirements = '''Django==5.0.3
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
psycopg2-binary==2.9.9
django-cors-headers==4.3.1
requests==2.31.0
python-decouple==3.8
gunicorn==21.2.0
'''
    create_file(os.path.join(service_path, 'requirements.txt'), requirements)
    
    # .env
    env_content = f'''SECRET_KEY=django-insecure-{service_name}-key
DEBUG=True
DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432
'''
    create_file(os.path.join(service_path, '.env'), env_content)

def main():
    print("Generating Django microservices architecture...")
    print("=" * 60)
    
    # Generate all services
    for category, services in SERVICES.items():
        for service_name, config in services.items():
            print(f"\\nGenerating {service_name}...")
            generate_django_service(category, service_name, config)
    
    print("\\n" + "=" * 60)
    print("✓ All services generated successfully!")
    print("\\nNext steps:")
    print("1. cd into each service directory")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py runserver <port>")

if __name__ == '__main__':
    main()
