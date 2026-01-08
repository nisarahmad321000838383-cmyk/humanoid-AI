from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re
from .models import HuggingFaceToken, UserHFTokenAssignment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    is_admin = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_admin', 'created_at')
        read_only_fields = ('id', 'role', 'is_admin', 'created_at')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
    
    def validate_password(self, value):
        """
        Validate password meets requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one number
        - At least one special character
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character (!@#$%^&*...)."
            )
        
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        # All registered users have 'user' role by default
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='user'  # Force user role for all registrations
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class HuggingFaceTokenSerializer(serializers.ModelSerializer):
    """Serializer for HuggingFace token management."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    assignment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HuggingFaceToken
        fields = ('id', 'token', 'name', 'is_active', 'created_by', 'created_by_username', 
                  'assignment_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_assignment_count(self, obj):
        """Get count of active assignments for this token."""
        return obj.assignments.filter(is_active=True).count()
    
    def validate_token(self, value):
        """Validate that the token is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Token cannot be empty.")
        return value.strip()
    
    def validate_name(self, value):
        """Validate that the name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value.strip()


class HuggingFaceTokenListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing HuggingFace tokens (without exposing full token)."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    assignment_count = serializers.SerializerMethodField()
    token_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = HuggingFaceToken
        fields = ('id', 'token_preview', 'name', 'is_active', 'created_by_username', 
                  'assignment_count', 'created_at', 'updated_at')
    
    def get_assignment_count(self, obj):
        """Get count of active assignments for this token."""
        return obj.assignments.filter(is_active=True).count()
    
    def get_token_preview(self, obj):
        """Return a preview of the token (first 10 and last 4 characters)."""
        token = obj.token
        if len(token) <= 20:
            return token[:4] + '...' + token[-2:]
        return token[:10] + '...' + token[-4:]


class UserHFTokenAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for HuggingFace token assignments."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    token_name = serializers.CharField(source='hf_token.name', read_only=True)
    
    class Meta:
        model = UserHFTokenAssignment
        fields = ('id', 'user', 'user_username', 'hf_token', 'token_name', 
                  'assigned_at', 'released_at', 'is_active', 'session_identifier')
        read_only_fields = ('id', 'assigned_at', 'released_at')
