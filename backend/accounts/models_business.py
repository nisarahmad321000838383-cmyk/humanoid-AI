from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_image_size(image):
    """Validate that image size is less than 200KB."""
    max_size_kb = 200
    if image.size > max_size_kb * 1024:
        raise ValidationError(f'Image size must be less than {max_size_kb}KB. Current size: {image.size / 1024:.2f}KB')


class Business(models.Model):
    """
    Model to store business information for users.
    Business info is converted to embeddings and stored in ChromaDB.
    Business logo is stored in MySQL database.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business',
        help_text='User who owns this business'
    )
    business_info = models.TextField(
        help_text='Business information: name, owner, address, industry (max 10 lines)',
        max_length=2000
    )
    logo = models.BinaryField(
        null=True,
        blank=True,
        help_text='Business logo stored as binary data (max 200KB)'
    )
    logo_filename = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Original filename of the logo'
    )
    logo_content_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='MIME type of the logo (e.g., image/jpeg, image/png)'
    )
    chroma_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Unique ID for ChromaDB document'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'businesses'
        ordering = ['-created_at']
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'
    
    def __str__(self):
        return f"{self.user.username}'s Business"
    
    def clean(self):
        """Validate business info length (max 10 lines)."""
        if self.business_info:
            lines = self.business_info.strip().split('\n')
            if len(lines) > 10:
                raise ValidationError({
                    'business_info': f'Business info must not exceed 10 lines. Current: {len(lines)} lines.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
