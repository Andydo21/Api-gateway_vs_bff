"""User Service Views"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import Address
from .serializers import UserSerializer, UserRegistrationSerializer, AddressSerializer

User = get_user_model()


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'user-service'})


@api_view(['POST'])
def register(request):
    """User registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    """User login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if user.banned:
        return Response({'error': 'Account is banned'}, status=status.HTTP_403_FORBIDDEN)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'success': True,
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


class UserViewSet(viewsets.ModelViewSet):
    """User CRUD operations - Trust BFF (no auth needed)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Trust BFF - Gateway already validated
    
    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """User statistics"""
        total_users = User.objects.count()
        banned_users = User.objects.filter(banned=True).count()
        
        return Response({
            'total_users': total_users,
            'banned_users': banned_users,
            'active_users': total_users - banned_users
        })


class AddressViewSet(viewsets.ModelViewSet):
    """Address management - Trust BFF (no auth needed)"""
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]  # Trust BFF - Gateway already validated
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
