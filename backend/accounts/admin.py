from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, HuggingFaceToken, UserHFTokenAssignment, AuthToken, Business


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


@admin.register(HuggingFaceToken)
class HuggingFaceTokenAdmin(admin.ModelAdmin):
    """Admin configuration for HuggingFace Token model."""
    
    list_display = ('name', 'is_active', 'created_by', 'created_at', 'assignment_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'assignment_count')
    
    fieldsets = (
        ('Token Information', {'fields': ('name', 'token', 'is_active')}),
        ('Metadata', {'fields': ('created_by', 'created_at', 'updated_at', 'assignment_count')}),
    )
    
    def assignment_count(self, obj):
        """Display count of active assignments."""
        return obj.assignments.filter(is_active=True).count()
    assignment_count.short_description = 'Active Assignments'


@admin.register(UserHFTokenAssignment)
class UserHFTokenAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for User HF Token Assignment model."""
    
    list_display = ('user', 'hf_token', 'is_active', 'assigned_at', 'released_at')
    list_filter = ('is_active', 'assigned_at', 'released_at')
    search_fields = ('user__username', 'hf_token__name', 'session_identifier')
    ordering = ('-assigned_at',)
    readonly_fields = ('assigned_at', 'released_at')
    
    fieldsets = (
        ('Assignment Information', {'fields': ('user', 'hf_token', 'is_active')}),
        ('Session Information', {'fields': ('session_identifier',)}),
        ('Timestamps', {'fields': ('assigned_at', 'released_at')}),
    )


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    """Admin interface for AuthToken model."""
    list_display = ['user', 'token_type', 'jti_short', 'created_at', 'expires_at', 'is_revoked', 'is_valid']
    list_filter = ['token_type', 'is_revoked', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'jti', 'ip_address']
    readonly_fields = ['token_hash', 'jti', 'created_at', 'expires_at', 'revoked_at', 'ip_address', 'user_agent']
    date_hierarchy = 'created_at'
    
    def jti_short(self, obj):
        """Display shortened JTI for readability."""
        return obj.jti[:16] + '...' if len(obj.jti) > 16 else obj.jti
    jti_short.short_description = 'JWT ID'
    
    def is_valid(self, obj):
        """Display if token is currently valid."""
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'
    
    actions = ['revoke_tokens', 'cleanup_expired']
    
    def revoke_tokens(self, request, queryset):
        """Admin action to revoke selected tokens."""
        count = 0
        for token in queryset:
            token.revoke()
            count += 1
        self.message_user(request, f"Successfully revoked {count} token(s).")
    revoke_tokens.short_description = "Revoke selected tokens"
    
    def cleanup_expired(self, request, queryset):
        """Admin action to delete old expired/revoked tokens."""
        count = AuthToken.cleanup_expired_tokens(days_to_keep=30)
        self.message_user(request, f"Successfully cleaned up {count} expired token(s).")
    cleanup_expired.short_description = "Cleanup expired tokens (30+ days old)"


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    """Admin configuration for Business model."""
    
    list_display = ('user', 'get_business_preview', 'has_logo', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'business_info', 'chroma_id')
    ordering = ('-created_at',)
    readonly_fields = ('chroma_id', 'created_at', 'updated_at', 'logo_preview')
    
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Business Information', {'fields': ('business_info',)}),
        ('Logo Information', {'fields': ('logo_filename', 'logo_content_type', 'logo_preview')}),
        ('Metadata', {'fields': ('chroma_id', 'created_at', 'updated_at')}),
    )
    
    def get_business_preview(self, obj):
        """Display first 50 characters of business info."""
        return obj.business_info[:50] + '...' if len(obj.business_info) > 50 else obj.business_info
    get_business_preview.short_description = 'Business Info'
    
    def has_logo(self, obj):
        """Display if business has a logo."""
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'Has Logo'
    
    def logo_preview(self, obj):
        """Display logo preview if available."""
        if obj.logo:
            import base64
            from django.utils.html import format_html
            logo_base64 = base64.b64encode(obj.logo).decode('utf-8')
            return format_html(
                '<img src="data:{};base64,{}" style="max-width: 200px; max-height: 200px;" />',
                obj.logo_content_type or 'image/jpeg',
                logo_base64
            )
        return "No logo"
    logo_preview.short_description = 'Logo Preview'
