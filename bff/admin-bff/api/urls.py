"""Admin BFF URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('startups/', views.startups, name='startups'),
    path('startups/<int:startup_id>/', views.startup_detail, name='startup-detail'),
    path('pitch-slots/', views.pitch_slots, name='pitch-slots'),
    path('pitch-slots/<int:slot_id>/status/', views.pitch_slot_status, name='pitch-slot-status'),
    path('users/', views.users, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user-detail'),
    path('users/<int:user_id>/ban/', views.user_ban, name='user-ban'),
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/update/', views.inventory_update, name='inventory-update'),
]
