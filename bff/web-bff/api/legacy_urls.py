from django.urls import path
from . import views

urlpatterns = [
    path('users/login/', views.login, name='legacy-login'),
    path('users/register/', views.register, name='legacy-register'),
    path('pitch-requests/', views.legacy_pitch_requests, name='legacy-pitch-requests'),
]
