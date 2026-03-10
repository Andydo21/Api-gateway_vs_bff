"""Web BFF URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('home/', views.home_page, name='home'),
    
    # Categories - THỂ HIỆN RÕ BFF PATTERN
    path('categories/', views.category_list, name='category-list'),
    
    # Products
    path('products/', views.product_list, name='product-list'),
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    
    # Reviews - THỂ HIỆN RÕ BFF PATTERN (GET để lấy, POST để tạo)
    path('products/<int:product_id>/reviews/', views.product_reviews, name='get-reviews'),
    path('products/<int:product_id>/reviews/create/', views.create_review, name='create-review'),
    
    # Cart
    path('cart/', views.cart_get, name='cart-get'),
    path('cart/add/', views.cart_add, name='cart-add'),
    path('cart/update/', views.cart_update, name='cart-update'),
    path('cart/remove/', views.cart_remove, name='cart-remove'),
    path('cart/clear/', views.cart_clear, name='cart-clear'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # User Authentication
    path('users/login/', views.user_login, name='user-login'),
    path('users/register/', views.user_register, name='user-register'),
    
    # Orders
    path('orders/', views.order_list, name='order-list'),
    path('orders/create/', views.order_create, name='order-create'),
]
