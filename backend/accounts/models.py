from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role for access control'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'


class HuggingFaceToken(models.Model):
    """
    Model to store HuggingFace API access tokens.
    Only admin users can create/manage these tokens.
    """
    token = models.CharField(
        max_length=500,
        unique=True,
        help_text='HuggingFace API access token'
    )
    name = models.CharField(
        max_length=100,
        help_text='Friendly name for this token'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this token is available for assignment'
    )
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='created_hf_tokens',
        help_text='Admin user who created this token'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'huggingface_tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"


class UserHFTokenAssignment(models.Model):
    """
    Model to track HuggingFace token assignments to users per login session.
    A new token is assigned on each login, and released on logout or token expiry.
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='hf_token_assignments'
    )
    hf_token = models.ForeignKey(
        HuggingFaceToken,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this assignment is currently active'
    )
    session_identifier = models.CharField(
        max_length=255,
        help_text='Identifier for the login session (e.g., refresh token jti)',
        db_index=True
    )
    
    class Meta:
        db_table = 'user_hf_token_assignments'
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_identifier']),
        ]
    
    def __str__(self):
        status = 'Active' if self.is_active else 'Released'
        return f"{self.user.username} - {self.hf_token.name} - {status}"
# Re-export AuthToken from models_token
from .models_token import AuthToken

__all__ = ['User', 'HuggingFaceToken', 'UserHFTokenAssignment', 'AuthToken']
