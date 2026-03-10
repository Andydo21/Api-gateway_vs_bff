from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet, ReservationViewSet

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
]
