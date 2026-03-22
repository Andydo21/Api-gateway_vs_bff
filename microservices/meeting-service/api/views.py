from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Meeting
from .serializers import MeetingSerializer

class MeetingViewSet(viewsets.ModelViewSet):
    """Orchestration for pitch sessions (Zoom/Meet)"""
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'meeting-service'})
