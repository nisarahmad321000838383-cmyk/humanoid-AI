from rest_framework import serializers
from .models_product import Product, ProductImage
import base64
import uuid


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model with base64 encoding."""
    image_base64 = serializers.SerializerMethodField(read_only=True)
    image_upload = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = ProductImage
        fields = (
            'id', 'product', 'image_base64', 'image_upload', 
            'image_filename', 'image_content_type', 'order', 'created_at'
        )
        read_only_fields = ('id', 'product', 'image_filename', 'image_content_type', 'created_at')
    
    def get_image_base64(self, obj):
        """Convert binary image to base64 for frontend display."""
        if obj.image_data:
            return base64.b64encode(obj.image_data).decode('utf-8')
        return None


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with images."""
    images = ProductImageSerializer(many=True, read_only=True)
    images_upload = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        max_length=4,
        min_length=0,
        help_text="List of base64 encoded images (1-4 images, total size <= 1MB)"
    )
    images_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'business', 'product_description', 'images', 'images_upload',
            'images_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'business', 'created_at', 'updated_at', 'images_count')
    
    def get_images_count(self, obj):
        """Get count of images for this product."""
        return obj.images.count()
    
    def validate_product_description(self, value):
        """Validate product description is not empty and has max 10 lines."""
        if not value or not value.strip():
            raise serializers.ValidationError("Product description cannot be empty.")
        
        lines = value.strip().split('\n')
        if len(lines) > 10:
            raise serializers.ValidationError(
                f"Product description must not exceed 10 lines. Current: {len(lines)} lines. "
                f"Please write about product name, price, and specifications in 10 lines."
            )
        
        return value.strip()
    
    def validate_images_upload(self, value):
        """Validate images upload list."""
        if not value:
            return value
        
        # Validate count (1-4 images)
        if len(value) < 1:
            raise serializers.ValidationError(
                "At least 1 image is required per product."
            )
        
        if len(value) > 4:
            raise serializers.ValidationError(
                f"Maximum 4 images allowed per product. You provided {len(value)} images."
            )
        
        # Validate each image and calculate total size
        total_size = 0
        for idx, image_data in enumerate(value):
            if not image_data:
                continue
            
            try:
                # Check if it's a data URL format (data:image/png;base64,...)
                if image_data.startswith('data:'):
                    # Extract the base64 part
                    header, base64_data = image_data.split(',', 1)
                    # Extract content type from header
                    content_type = header.split(':')[1].split(';')[0]
                else:
                    # Assume it's just base64 without header
                    base64_data = image_data
                    content_type = 'image/jpeg'  # Default
                
                # Decode base64 to get actual file size
                decoded_data = base64.b64decode(base64_data)
                image_size = len(decoded_data)
                total_size += image_size
                
                # Validate content type (must be an image)
                if not content_type.startswith('image/'):
                    raise serializers.ValidationError(
                        f"Image {idx + 1}: File must be an image (PNG, JPG, JPEG, GIF, etc.)."
                    )
                
            except Exception as e:
                raise serializers.ValidationError(f"Image {idx + 1}: Invalid image data - {str(e)}")
        
        # Validate total size (must be <= 1MB)
        max_size_bytes = 1024 * 1024  # 1MB
        if total_size > max_size_bytes:
            total_size_mb = total_size / (1024 * 1024)
            raise serializers.ValidationError(
                f"Total size of all images must be less than 1MB. Current total: {total_size_mb:.2f}MB. "
                f"Please compress your images or choose smaller ones."
            )
        
        return value
    
    def validate(self, attrs):
        """Validate the entire product data."""
        # Check max 10 products per business on creation
        if not self.instance:  # Only on creation
            business = attrs.get('business') or (self.context.get('request').user.business if self.context.get('request') else None)
            if business:
                existing_products_count = Product.objects.filter(business=business).count()
                if existing_products_count >= 10:
                    raise serializers.ValidationError({
                        'business': f'Maximum 10 products allowed per business. You already have {existing_products_count} products.'
                    })
        
        # Ensure at least 1 image on creation
        if not self.instance:  # Only on creation
            images_upload = attrs.get('images_upload', [])
            if not images_upload or len(images_upload) == 0:
                raise serializers.ValidationError({
                    'images_upload': 'At least 1 image is required per product.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create product with images and store description in ChromaDB."""
        from chat.chroma_service import chroma_service
        
        images_data = validated_data.pop('images_upload', [])
        business = validated_data['business']
        
        # Generate unique chroma_id for product
        chroma_id = f"product_{business.id}_{uuid.uuid4().hex[:8]}"
        validated_data['chroma_id'] = chroma_id
        
        # Create product in MySQL
        product = Product.objects.create(**validated_data)
        
        # Store product description in ChromaDB
        chroma_service.add_product(
            product_id=chroma_id,
            product_description=product.product_description,
            business_id=business.id,
            username=business.user.username,
            product_db_id=product.id
        )
        
        # Process and create images
        for idx, image_data in enumerate(images_data):
            if not image_data:
                continue
            
            # Parse base64 data
            if image_data.startswith('data:'):
                header, base64_data = image_data.split(',', 1)
                content_type = header.split(':')[1].split(';')[0]
            else:
                base64_data = image_data
                content_type = 'image/jpeg'
            
            decoded_image = base64.b64decode(base64_data)
            
            # Create image
            ProductImage.objects.create(
                product=product,
                image_data=decoded_image,
                image_content_type=content_type,
                image_filename=f"product_{product.id}_image_{idx + 1}",
                order=idx
            )
        
        return product
    
    def update(self, instance, validated_data):
        """Update product with images and update ChromaDB."""
        from chat.chroma_service import chroma_service
        
        images_data = validated_data.pop('images_upload', None)
        
        # Update product description
        if 'product_description' in validated_data:
            instance.product_description = validated_data['product_description']
            instance.save()
            
            # Update in ChromaDB
            chroma_service.add_product(
                product_id=instance.chroma_id,
                product_description=instance.product_description,
                business_id=instance.business.id,
                username=instance.business.user.username,
                product_db_id=instance.id
            )
        
        # Update images if provided
        if images_data is not None:
            # Delete old images
            instance.images.all().delete()
            
            # Create new images
            for idx, image_data in enumerate(images_data):
                if not image_data:
                    continue
                
                # Parse base64 data
                if image_data.startswith('data:'):
                    header, base64_data = image_data.split(',', 1)
                    content_type = header.split(':')[1].split(';')[0]
                else:
                    base64_data = image_data
                    content_type = 'image/jpeg'
                
                decoded_image = base64.b64decode(base64_data)
                
                # Create image
                ProductImage.objects.create(
                    product=instance,
                    image_data=decoded_image,
                    image_content_type=content_type,
                    image_filename=f"product_{instance.id}_image_{idx + 1}",
                    order=idx
                )
        
        return instance


class ProductCreateUpdateSerializer(serializers.Serializer):
    """Simplified serializer for creating/updating products."""
    product_description = serializers.CharField(max_length=2000)
    images = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False,
        max_length=4,
        min_length=1,
        help_text="List of base64 encoded images (1-4 images, total size <= 1MB)"
    )
    
    def validate_product_description(self, value):
        """Validate product description is not empty and has max 10 lines."""
        if not value or not value.strip():
            raise serializers.ValidationError("Product description cannot be empty.")
        
        lines = value.strip().split('\n')
        if len(lines) > 10:
            raise serializers.ValidationError(
                f"Product description must not exceed 10 lines. Current: {len(lines)} lines. "
                f"Please write about product name, price, and specifications in 10 lines."
            )
        
        return value.strip()
    
    def validate_images(self, value):
        """Validate images list."""
        if not value:
            raise serializers.ValidationError("At least 1 image is required per product.")
        
        # Validate count (1-4 images)
        if len(value) < 1:
            raise serializers.ValidationError("At least 1 image is required per product.")
        
        if len(value) > 4:
            raise serializers.ValidationError(
                f"Maximum 4 images allowed per product. You provided {len(value)} images."
            )
        
        # Validate each image and calculate total size
        total_size = 0
        for idx, image_data in enumerate(value):
            if not image_data:
                raise serializers.ValidationError(f"Image {idx + 1}: Empty image data.")
            
            try:
                # Check if it's a data URL format (data:image/png;base64,...)
                if image_data.startswith('data:'):
                    # Extract the base64 part
                    header, base64_data = image_data.split(',', 1)
                    # Extract content type from header
                    content_type = header.split(':')[1].split(';')[0]
                else:
                    # Assume it's just base64 without header
                    base64_data = image_data
                    content_type = 'image/jpeg'  # Default
                
                # Decode base64 to get actual file size
                decoded_data = base64.b64decode(base64_data)
                image_size = len(decoded_data)
                total_size += image_size
                
                # Validate content type (must be an image)
                if not content_type.startswith('image/'):
                    raise serializers.ValidationError(
                        f"Image {idx + 1}: File must be an image (PNG, JPG, JPEG, GIF, etc.)."
                    )
                
            except Exception as e:
                raise serializers.ValidationError(f"Image {idx + 1}: Invalid image data - {str(e)}")
        
        # Validate total size (must be <= 1MB)
        max_size_bytes = 1024 * 1024  # 1MB
        if total_size > max_size_bytes:
            total_size_mb = total_size / (1024 * 1024)
            raise serializers.ValidationError(
                f"Total size of all images must be less than 1MB. Current total: {total_size_mb:.2f}MB. "
                f"Please compress your images or choose smaller ones."
            )
        
        return value
