from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'resources', views.EventResourceViewSet)
router.register(r'resource-reservations', views.ResourceReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check),
]
