from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Feedback, InvestmentInterest, FeedbackOutboxEvent
from .serializers import FeedbackSerializer, InvestmentInterestSerializer
from django.db import transaction

class FeedbackViewSet(viewsets.ModelViewSet):
    """Investor evaluation reviews"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        with transaction.atomic():
            feedback = serializer.save()
            FeedbackOutboxEvent.objects.create(
                event_type='feedback_submitted',
                payload=FeedbackSerializer(feedback).data
            )

class InvestmentInterestViewSet(viewsets.ModelViewSet):
    """Investor funding interest leads"""
    queryset = InvestmentInterest.objects.all()
    serializer_class = InvestmentInterestSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        with transaction.atomic():
            interest = serializer.save()
            FeedbackOutboxEvent.objects.create(
                event_type='investment_interest_tracked',
                payload=InvestmentInterestSerializer(interest).data
            )

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'feedback-service'})
