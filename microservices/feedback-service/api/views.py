from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Feedback, InvestmentInterest
from .serializers import FeedbackSerializer, InvestmentInterestSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    """Investor evaluation reviews"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]

class InvestmentInterestViewSet(viewsets.ModelViewSet):
    """Investor funding interest leads"""
    queryset = InvestmentInterest.objects.all()
    serializer_class = InvestmentInterestSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'feedback-service'})
