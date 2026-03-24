"""Admin BFF URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('startups/', views.startups, name='startups'),
    path('startups/<int:startup_id>/', views.startup_detail, name='startup-detail'),
    path('startups/<int:startup_id>/approve/', views.approve_startup, name='startup-approve'),
    path('startups/<int:startup_id>/reject/', views.reject_startup, name='startup-reject'),
    path('pitch-slots/', views.pitch_slots, name='pitch-slots'),
    path('pitch-slots/<int:slot_id>/status/', views.pitch_slot_status, name='pitch-slot-status'),
    path('pitch-requests/', views.pitch_requests, name='pitch-requests'),
    path('pitch-requests/<int:pitch_id>/approve/', views.approve_pitch, name='pitch-approve'),
    path('pitch-requests/<int:pitch_id>/reject/', views.reject_pitch, name='pitch-reject'),
    path('users/', views.users, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user-detail'),
    path('users/<int:user_id>/ban/', views.user_ban, name='user-ban'),
    
    # New Specific Admin Actions
    path('startups/<int:startup_id>/approve/', views.approve_startup, name='approve-startup'),
    path('startups/<int:startup_id>/reject/', views.reject_startup, name='reject-startup'),
    path('users/<int:user_id>/block/', views.block_user, name='block-user'),
    path('users/<int:user_id>/unblock/', views.unblock_user, name='unblock-user'),
]
