"""
Token management models for storing and tracking authentication tokens.
This provides audit trail and ability to revoke tokens.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import hashlib


class AuthToken(models.Model):
    """
    Stores authentication tokens with metadata for security and auditing.
    
    Professional approach:
    - Stores hashed tokens (not plaintext) for security
    - Tracks creation and expiry dates
    - Allows selective token revocation
    - Provides audit trail of user sessions
    - Enables device/session management
    """
    
    TOKEN_TYPE_CHOICES = [
        ('access', 'Access Token'),
        ('refresh', 'Refresh Token'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='auth_tokens'
    )
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPE_CHOICES)
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    jti = models.CharField(max_length=255, unique=True, db_index=True)  # JWT ID
    
    # Session information for auditing
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Token lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    is_revoked = models.BooleanField(default=False)
    
    # Optional: Link refresh and access tokens
    refresh_token = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='access_tokens'
    )
    
    class Meta:
        db_table = 'auth_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'token_type', 'is_revoked']),
            models.Index(fields=['expires_at', 'is_revoked']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.token_type} - {self.jti[:8]}"
    
    @staticmethod
    def hash_token(token):
        """Create a SHA256 hash of the token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def is_expired(self):
        """Check if the token has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the token is valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired()
    
    def revoke(self):
        """
        Revoke this token and all related tokens.
        
        Professional approach on logout:
        - Revoke the refresh token (invalidates the session)
        - Revoke all access tokens created from this refresh token
        - Set revoked_at timestamp for audit trail
        - Keep the records for security auditing
        """
        if not self.is_revoked:
            self.is_revoked = True
            self.revoked_at = timezone.now()
            self.save()
            
            # If this is a refresh token, revoke all its access tokens
            if self.token_type == 'refresh':
                self.access_tokens.filter(is_revoked=False).update(
                    is_revoked=True,
                    revoked_at=timezone.now()
                )
    
    @classmethod
    def revoke_all_user_tokens(cls, user):
        """
        Revoke all tokens for a user (force logout from all devices).
        Useful for security incidents or password changes.
        """
        cls.objects.filter(user=user, is_revoked=False).update(
            is_revoked=True,
            revoked_at=timezone.now()
        )
    
    @classmethod
    def cleanup_expired_tokens(cls, days_to_keep=30):
        """
        Clean up expired and revoked tokens older than specified days.
        Should be run periodically (e.g., daily cron job).
        
        Professional approach:
        - Keep tokens for audit purposes (configurable retention period)
        - Only delete truly old tokens
        - This helps with compliance and security investigations
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        deleted_count = cls.objects.filter(
            models.Q(expires_at__lt=cutoff_date) | models.Q(revoked_at__lt=cutoff_date)
        ).delete()[0]
        return deleted_count
    
    @classmethod
    def get_user_active_sessions(cls, user):
        """
        Get all active sessions (refresh tokens) for a user.
        Useful for displaying "Where you're logged in" feature.
        """
        return cls.objects.filter(
            user=user,
            token_type='refresh',
            is_revoked=False,
            expires_at__gt=timezone.now()
        ).select_related('user')
