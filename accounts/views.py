from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    LoginSerializer,
    ChangePasswordSerializer
)


def get_tokens_for_user(user):
    """
    Generate JWT access and refresh tokens for a user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user (user / host / admin).
    POST /api/auth/register/
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        return Response({
            'message': f'Welcome to Eventify, {user.username}!',
            'user': UserSerializer(user).data,
            'tokens': tokens,
        }, status=status.HTTP_201_CREATED)

    return Response({
        'message': 'Registration failed.',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login with username and password.
    Returns JWT tokens on success.
    POST /api/auth/login/
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user:
            tokens = get_tokens_for_user(user)
            return Response({
                'message': f'Welcome back, {user.username}!',
                'user': UserSerializer(user).data,
                'tokens': tokens,
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Invalid username or password.',
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        'message': 'Login failed.',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({
            'message': 'Logged out successfully.'
        }, status=status.HTTP_200_OK)
    except Exception:
        # Even if blacklist fails — still logout cleanly
        return Response({
            'message': 'Logged out successfully.'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get currently logged in user details.
    GET /api/auth/me/
    """
    return Response({
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user's profile.
    PUT /api/auth/profile/update/
    """
    serializer = UserSerializer(
        request.user,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        'message': 'Update failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change current user's password.
    POST /api/auth/password/change/
    """
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        user = request.user

        # Verify old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'message': 'Old password is incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'message': 'Password changed successfully. Please login again.'
        }, status=status.HTTP_200_OK)

    return Response({
        'message': 'Password change failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)