from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pitch-requests', views.PitchRequestViewSet)
router.register(r'pitch-bookings', views.PitchBookingViewSet)
router.register(r'waitlists', views.WaitlistViewSet)
router.register(r'pitch-booking-history', views.PitchBookingHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check),
]
