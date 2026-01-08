from rest_framework import serializers
from .models import Business
import base64


class BusinessSerializer(serializers.ModelSerializer):
    """Serializer for Business model with logo handling."""
    logo_base64 = serializers.SerializerMethodField(read_only=True)
    logo_upload = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Business
        fields = (
            'id', 'user', 'business_info', 'logo_base64', 'logo_upload', 
            'logo_filename', 'logo_content_type', 'chroma_id', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'chroma_id', 'created_at', 'updated_at', 'logo_filename', 'logo_content_type')
    
    def get_logo_base64(self, obj):
        """Convert binary logo to base64 for frontend display."""
        if obj.logo:
            return base64.b64encode(obj.logo).decode('utf-8')
        return None
    
    def validate_business_info(self, value):
        """Validate business info is not empty and has max 10 lines."""
        if not value or not value.strip():
            raise serializers.ValidationError("Business info cannot be empty.")
        
        lines = value.strip().split('\n')
        if len(lines) > 10:
            raise serializers.ValidationError(
                f"Business info must not exceed 10 lines. Current: {len(lines)} lines. "
                f"Please write about your business name, owner, address, and industry in 10 lines."
            )
        
        return value.strip()
    
    def validate_logo_upload(self, value):
        """Validate logo upload (base64 string) and size."""
        if not value:
            return value
        
        try:
            # Check if it's a data URL format (data:image/png;base64,...)
            if value.startswith('data:'):
                # Extract the base64 part
                header, base64_data = value.split(',', 1)
                # Extract content type from header
                content_type = header.split(':')[1].split(';')[0]
            else:
                # Assume it's just base64 without header
                base64_data = value
                content_type = 'image/jpeg'  # Default
            
            # Decode base64 to get actual file size
            decoded_data = base64.b64decode(base64_data)
            file_size_kb = len(decoded_data) / 1024
            
            # Validate size (must be less than 200KB)
            if file_size_kb > 200:
                raise serializers.ValidationError(
                    f"Image size must be less than 200KB. Current size: {file_size_kb:.2f}KB. "
                    f"Please compress your image or choose a smaller one."
                )
            
            # Validate content type (must be an image)
            if not content_type.startswith('image/'):
                raise serializers.ValidationError("File must be an image (PNG, JPG, JPEG, GIF, etc.).")
            
            return value
        except Exception as e:
            raise serializers.ValidationError(f"Invalid image data: {str(e)}")
    
    def create(self, validated_data):
        """Create business with logo and ChromaDB integration."""
        from chat.chroma_service import chroma_service
        import uuid
        
        logo_data = validated_data.pop('logo_upload', None)
        user = validated_data['user']
        
        # Generate unique ChromaDB ID
        chroma_id = f"business_{user.id}_{uuid.uuid4().hex[:8]}"
        validated_data['chroma_id'] = chroma_id
        
        # Process logo if provided
        if logo_data:
            if logo_data.startswith('data:'):
                header, base64_data = logo_data.split(',', 1)
                content_type = header.split(':')[1].split(';')[0]
            else:
                base64_data = logo_data
                content_type = 'image/jpeg'
            
            decoded_logo = base64.b64decode(base64_data)
            validated_data['logo'] = decoded_logo
            validated_data['logo_content_type'] = content_type
            validated_data['logo_filename'] = f"business_logo_{user.username}"
        
        # Create business
        business = Business.objects.create(**validated_data)
        
        # Add to ChromaDB
        chroma_service.add_business(
            business_id=chroma_id,
            business_info=business.business_info,
            username=user.username
        )
        
        return business
    
    def update(self, instance, validated_data):
        """Update business with logo and ChromaDB integration."""
        from chat.chroma_service import chroma_service
        
        logo_data = validated_data.pop('logo_upload', None)
        
        # Process logo if provided
        if logo_data:
            if logo_data.startswith('data:'):
                header, base64_data = logo_data.split(',', 1)
                content_type = header.split(':')[1].split(';')[0]
            else:
                base64_data = logo_data
                content_type = 'image/jpeg'
            
            decoded_logo = base64.b64decode(base64_data)
            instance.logo = decoded_logo
            instance.logo_content_type = content_type
            instance.logo_filename = f"business_logo_{instance.user.username}"
        
        # Update business info
        if 'business_info' in validated_data:
            instance.business_info = validated_data['business_info']
            # Update in ChromaDB
            chroma_service.add_business(
                business_id=instance.chroma_id,
                business_info=instance.business_info,
                username=instance.user.username
            )
        
        instance.save()
        return instance


class BusinessCreateUpdateSerializer(serializers.Serializer):
    """Simplified serializer for creating/updating business."""
    business_info = serializers.CharField(max_length=2000)
    logo = serializers.CharField(required=False, allow_blank=True, help_text="Base64 encoded image data")
    
    def validate_business_info(self, value):
        """Validate business info is not empty and has max 10 lines."""
        if not value or not value.strip():
            raise serializers.ValidationError("Business info cannot be empty.")
        
        lines = value.strip().split('\n')
        if len(lines) > 10:
            raise serializers.ValidationError(
                f"Business info must not exceed 10 lines. Current: {len(lines)} lines. "
                f"Please write about your business name, owner, address, and industry in 10 lines."
            )
        
        return value.strip()
    
    def validate_logo(self, value):
        """Validate logo upload (base64 string) and size."""
        if not value:
            return value
        
        try:
            # Check if it's a data URL format (data:image/png;base64,...)
            if value.startswith('data:'):
                # Extract the base64 part
                header, base64_data = value.split(',', 1)
                # Extract content type from header
                content_type = header.split(':')[1].split(';')[0]
            else:
                # Assume it's just base64 without header
                base64_data = value
                content_type = 'image/jpeg'  # Default
            
            # Decode base64 to get actual file size
            decoded_data = base64.b64decode(base64_data)
            file_size_kb = len(decoded_data) / 1024
            
            # Validate size (must be less than 200KB)
            if file_size_kb > 200:
                raise serializers.ValidationError(
                    f"Image size must be less than 200KB. Current size: {file_size_kb:.2f}KB. "
                    f"Please compress your image or choose a smaller one."
                )
            
            # Validate content type (must be an image)
            if not content_type.startswith('image/'):
                raise serializers.ValidationError("File must be an image (PNG, JPG, JPEG, GIF, etc.).")
            
            return value
        except Exception as e:
            raise serializers.ValidationError(f"Invalid image data: {str(e)}")
