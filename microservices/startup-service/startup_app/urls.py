"""Product Service URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'startups', views.StartupViewSet)
router.register(r'investors', views.InvestorViewSet, basename='investor')


urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('', include(router.urls)),
]
