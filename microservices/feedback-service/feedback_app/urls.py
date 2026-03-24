from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'investment-interests', views.InvestmentInterestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check),
]
