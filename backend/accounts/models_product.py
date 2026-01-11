from django.db import models
from django.core.exceptions import ValidationError
from .models_business import Business


class Product(models.Model):
    """
    Model to store product information for businesses.
    Each business can have up to 10 products.
    Each product can have 1-4 images with total size <= 1MB.
    Product descriptions are stored in ChromaDB for semantic search.
    Product images are stored in MySQL as binary data.
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='products',
        help_text='Business that owns this product'
    )
    product_description = models.TextField(
        help_text='Product details: name, price, specifications (max 10 lines)',
        max_length=2000
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
        db_table = 'products'
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        # Get first line as product name
        first_line = self.product_description.split('\n')[0][:50]
        return f"{first_line} - {self.business.user.username}"
    
    def clean(self):
        """Validate product description length (max 10 lines)."""
        if self.product_description:
            lines = self.product_description.strip().split('\n')
            if len(lines) > 10:
                raise ValidationError({
                    'product_description': f'Product description must not exceed 10 lines. Current: {len(lines)} lines.'
                })
        
        # Validate max 10 products per business
        if not self.pk:  # Only check on creation
            existing_products_count = Product.objects.filter(business=self.business).count()
            if existing_products_count >= 10:
                raise ValidationError({
                    'business': f'Maximum 10 products allowed per business. You already have {existing_products_count} products.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_total_images_size(self):
        """Calculate total size of all images for this product in bytes."""
        total_size = 0
        for image in self.images.all():
            if image.image_data:
                total_size += len(image.image_data)
        return total_size
    
    def get_images_count(self):
        """Get count of images for this product."""
        return self.images.count()


class ProductImage(models.Model):
    """
    Model to store product images.
    Each product can have 1-4 images.
    Total size of all images per product must be <= 1MB.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text='Product this image belongs to'
    )
    image_data = models.BinaryField(
        help_text='Product image stored as binary data'
    )
    image_filename = models.CharField(
        max_length=255,
        help_text='Original filename of the image'
    )
    image_content_type = models.CharField(
        max_length=100,
        help_text='MIME type of the image (e.g., image/jpeg, image/png)'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order of the image (0-3)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['order', 'created_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        unique_together = [['product', 'order']]
    
    def __str__(self):
        return f"Image {self.order + 1} - {self.product}"
    
    def clean(self):
        """Validate image constraints."""
        # Validate max 4 images per product
        if not self.pk:  # Only check on creation
            existing_images_count = ProductImage.objects.filter(product=self.product).count()
            if existing_images_count >= 4:
                raise ValidationError({
                    'product': f'Maximum 4 images allowed per product. This product already has {existing_images_count} images.'
                })
        
        # Validate total size of all images <= 1MB
        if self.image_data:
            # Calculate total size including this new image
            existing_total_size = self.product.get_total_images_size()
            if self.pk:  # If updating, subtract old size
                try:
                    old_image = ProductImage.objects.get(pk=self.pk)
                    existing_total_size -= len(old_image.image_data) if old_image.image_data else 0
                except ProductImage.DoesNotExist:
                    pass
            
            new_total_size = existing_total_size + len(self.image_data)
            max_size_bytes = 1024 * 1024  # 1MB
            
            if new_total_size > max_size_bytes:
                current_size_mb = new_total_size / (1024 * 1024)
                raise ValidationError({
                    'image_data': f'Total size of all product images must not exceed 1MB. Current total: {current_size_mb:.2f}MB'
                })
        
        # Validate content type
        if self.image_content_type and not self.image_content_type.startswith('image/'):
            raise ValidationError({
                'image_content_type': 'File must be an image (PNG, JPG, JPEG, GIF, etc.).'
            })
        
        # Validate order is between 0 and 3
        if self.order < 0 or self.order > 3:
            raise ValidationError({
                'order': 'Image order must be between 0 and 3.'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
