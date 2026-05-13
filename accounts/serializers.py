from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password validation and user creation.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password',
            'confirm_password', 'role', 'phone'
        ]

    def validate(self, attrs):
        # Check passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })

        # Check email is unique
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'This email is already registered.'
            })

        return attrs

    def create(self, validated_data):
        # Remove confirm_password before creating user
        validated_data.pop('confirm_password')

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user'),
            phone=validated_data.get('phone', '')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user data.
    Safe fields only — no password exposed.
    """

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email',
            'role', 'phone', 'profile_picture', 'created_at'
        ]


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Accepts username and password.
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({
                'new_password': 'New passwords do not match.'
            })
        return attrs