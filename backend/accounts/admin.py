from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, HuggingFaceToken, UserHFTokenAssignment


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
