"""Admin BFF URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/status/', views.order_status, name='order-status'),
    path('users/', views.users, name='users'),
    path('users/<int:user_id>/ban/', views.user_ban, name='user-ban'),
]
