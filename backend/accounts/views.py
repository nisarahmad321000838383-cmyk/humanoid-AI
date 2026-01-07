from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.db.models import Q
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserSerializer,
    HuggingFaceTokenSerializer,
    HuggingFaceTokenListSerializer,
    UserHFTokenAssignmentSerializer
)
from .permissions import IsAdminUser
from .models import HuggingFaceToken, UserHFTokenAssignment
import random

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    All registered users automatically get 'user' role.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response = Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
        
        # Set tokens in HTTP-only cookies
        self._set_token_cookies(response, str(refresh.access_token), str(refresh))
        
        return response
    
    def _set_token_cookies(self, response, access_token, refresh_token):
        """Set JWT tokens in secure HTTP-only cookies."""
        from django.conf import settings
        
        # Access token cookie
        response.set_cookie(
            key='access_token',
            value=access_token,
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path='/',
        )
        
        # Refresh token cookie
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path='/',
        )


class CheckAvailabilityView(generics.GenericAPIView):
    """
    API endpoint to check if username or email is available.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        
        response_data = {}
        
        if username:
            username_exists = User.objects.filter(username=username).exists()
            response_data['username_available'] = not username_exists
            if username_exists:
                response_data['username_message'] = 'This username is already taken. Please try another one.'
        
        if email:
            email_exists = User.objects.filter(email=email).exists()
            response_data['email_available'] = not email_exists
            if email_exists:
                response_data['email_message'] = 'This email is already taken. Please try another one.'
        
        return Response(response_data, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login.
    Validates role from backend and assigns HuggingFace token.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'User account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Assign HuggingFace token for this session
        # Use the refresh token's jti (JWT ID) as session identifier
        session_id = str(refresh['jti'])
        self._assign_hf_token(user, session_id)
        
        response = Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
        
        # Set tokens in HTTP-only cookies
        self._set_token_cookies(response, str(refresh.access_token), str(refresh))
        
        return response
    
    def _set_token_cookies(self, response, access_token, refresh_token):
        """Set JWT tokens in secure HTTP-only cookies."""
        from django.conf import settings
        
        # Access token cookie
        response.set_cookie(
            key='access_token',
            value=access_token,
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path='/',
        )
        
        # Refresh token cookie
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path='/',
        )
    
    def _assign_hf_token(self, user, session_id):
        """
        Assign an available HuggingFace token to the user for this session.
        Uses round-robin selection among available tokens.
        """
        # Get all active HF tokens
        available_tokens = HuggingFaceToken.objects.filter(is_active=True)
        
        if not available_tokens.exists():
            # No tokens available, will use fallback in settings
            return None
        
        # Find the token with the least active assignments (load balancing)
        token_usage = []
        for token in available_tokens:
            active_count = token.assignments.filter(is_active=True).count()
            token_usage.append((token, active_count))
        
        # Sort by usage and pick the least used one
        token_usage.sort(key=lambda x: x[1])
        selected_token = token_usage[0][0]
        
        # Create assignment
        UserHFTokenAssignment.objects.create(
            user=user,
            hf_token=selected_token,
            session_identifier=session_id,
            is_active=True
        )
        
        return selected_token


class CurrentUserView(generics.RetrieveAPIView):
    """
    API endpoint to get current authenticated user.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class TokenRefreshView(generics.GenericAPIView):
    """
    Custom token refresh view that reads refresh token from cookies
    and returns new access token in cookies.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            
            # Get refresh token from cookie
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token not found'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Validate and refresh the token
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            
            response = Response({
                'message': 'Token refreshed successfully'
            }, status=status.HTTP_200_OK)
            
            # Set new access token in cookie
            from django.conf import settings
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
                path='/',
            )
            
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout (blacklist refresh token and release HF token).
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            # Get refresh token from cookie instead of request body
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                
                # Release HuggingFace token assignment for this session
                session_id = str(token['jti'])
                self._release_hf_token(request.user, session_id)
                
                token.blacklist()
            
            response = Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
            
            # Clear the cookies
            response.delete_cookie('access_token', path='/')
            response.delete_cookie('refresh_token', path='/')
            
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _release_hf_token(self, user, session_id):
        """
        Release the HuggingFace token assignment for this session.
        """
        UserHFTokenAssignment.objects.filter(
            user=user,
            session_identifier=session_id,
            is_active=True
        ).update(
            is_active=False,
            released_at=timezone.now()
        )


class HuggingFaceTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing HuggingFace tokens.
    Only admin users can access these endpoints.
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = HuggingFaceToken.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HuggingFaceTokenListSerializer
        return HuggingFaceTokenSerializer
    
    def perform_create(self, serializer):
        """Automatically set the created_by field to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Toggle the is_active status of a token.
        """
        token = self.get_object()
        token.is_active = not token.is_active
        token.save()
        
        serializer = self.get_serializer(token)
        return Response({
            'message': f'Token {"activated" if token.is_active else "deactivated"} successfully',
            'token': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about token usage.
        """
        total_tokens = HuggingFaceToken.objects.count()
        active_tokens = HuggingFaceToken.objects.filter(is_active=True).count()
        total_assignments = UserHFTokenAssignment.objects.filter(is_active=True).count()
        
        return Response({
            'total_tokens': total_tokens,
            'active_tokens': active_tokens,
            'inactive_tokens': total_tokens - active_tokens,
            'active_assignments': total_assignments
        })


class UserHFTokenAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing HuggingFace token assignments.
    Admin users can view all assignments.
    Regular users can only view their own assignments.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserHFTokenAssignmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            # Admin can see all assignments
            return UserHFTokenAssignment.objects.all()
        else:
            # Regular users can only see their own assignments
            return UserHFTokenAssignment.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current active HF token assignment for the logged-in user.
        """
        assignment = UserHFTokenAssignment.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('hf_token').first()
        
        if assignment:
            serializer = self.get_serializer(assignment)
            return Response(serializer.data)
        else:
            return Response({
                'message': 'No active HuggingFace token assigned'
            }, status=status.HTTP_404_NOT_FOUND)
