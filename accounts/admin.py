from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import User, UserOTP, UserProfile, UserRole, MediaStorage, Interest, PreferredContributionPath, Affiliation, VerificationDocument


class CustomUserAdmin(BaseUserAdmin):
    """Custom User Admin to remove password field from display"""
    list_display = ['email', 'full_name', 'account_type', 'is_banned', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'is_banned', 'account_type', 'is_profile', 'is_role']
    search_fields = ['email', 'full_name', 'social_id']
    ordering = ['-date_joined']
    readonly_fields = ['uuid', 'date_joined', 'last_login']
    actions = ['ban_users', 'unban_users']
    
    def get_queryset(self, request):
        """Exclude superusers from the list"""
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=False)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'email', 'full_name', 'social_id', 'account_type')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_banned', 'groups', 'user_permissions'),
        }),
        ('Profile Status', {
            'fields': ('is_profile', 'is_role'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    
    def ban_users(self, request, queryset):
        """Admin action to ban selected users"""
        updated = queryset.update(is_banned=True)
        self.message_user(request, f'{updated} user(s) have been banned.')
    ban_users.short_description = 'Ban selected users'
    
    def unban_users(self, request, queryset):
        """Admin action to unban selected users"""
        updated = queryset.update(is_banned=False)
        self.message_user(request, f'{updated} user(s) have been unbanned.')
    unban_users.short_description = 'Unban selected users'


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'branch', 'rank', 'location', 'id_me_verified', 'created_at']
    list_filter = ['id_me_verified', 'branch', 'gender', 'education']
    search_fields = ['user__email', 'user__full_name', 'location', 'rank', 'affiliation']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    filter_horizontal = ['interests']


class InterestAdmin(admin.ModelAdmin):
    """Admin interface for managing interests"""
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['name']


class PreferredContributionPathAdmin(admin.ModelAdmin):
    """Admin interface for managing preferred contribution paths"""
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['name']


class AffiliationAdmin(admin.ModelAdmin):
    """Admin interface for managing affiliations"""
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['name']


class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'business_name', 'organization_name', 'created_at']
    list_filter = ['role', 'is_nonprofit_confirmed', 'created_at']
    search_fields = [
        'user__email',
        'user__full_name',
        'business_name',
        'organization_name'
    ]
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'user', 'role')
        }),
        ('Vendor Information', {
            'fields': ('business_name', 'business_ein', 'business_type'),
            'classes': ('collapse',),
        }),
        ('Community Support Provider Information', {
            'fields': ('organization_name', 'organization_mission', 'is_nonprofit_confirmed'),
            'classes': ('collapse',),
        }),
        ('Documents', {
            'fields': ('tax_document',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


class MediaStorageAdmin(admin.ModelAdmin):
    """Custom Media Storage Admin with image preview"""
    list_display = ['uuid', 'preview', 'filename', 'media_type', 'size', 'mime_type', 'created_at', 'download_link']
    list_filter = ['media_type', 'created_at']
    search_fields = ['uuid', 'media']
    readonly_fields = ['uuid', 'preview_large', 'created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Media Information', {
            'fields': ('uuid', 'media', 'media_type', 'preview_large')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    def preview(self, obj):
        """Show thumbnail preview in list view"""
        if obj.media:
            file_url = obj.media.url
            # Check if it's an image file
            if file_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                    file_url
                )
            elif file_url.lower().endswith(('.pdf')):
                return format_html('<span style="font-size: 30px;">📄</span>')
            elif file_url.lower().endswith(('.doc', '.docx')):
                return format_html('<span style="font-size: 30px;">📝</span>')
            elif file_url.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                return format_html('<span style="font-size: 30px;">🎥</span>')
            else:
                return format_html('<span style="font-size: 30px;">📁</span>')
        return '-'
    preview.short_description = 'PREVIEW'
    
    def preview_large(self, obj):
        """Show larger preview in detail view"""
        if obj.media:
            file_url = obj.media.url
            if file_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                return format_html(
                    '<img src="{}" style="max-width: 500px; max-height: 500px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                    file_url
                )
        return 'No preview available'
    preview_large.short_description = 'Preview'
    
    def filename(self, obj):
        """Extract and display filename"""
        if obj.media:
            return obj.media.name.split('/')[-1]
        return '-'
    filename.short_description = 'FILENAME'
    
    def size(self, obj):
        """Display file size"""
        if obj.media:
            try:
                size_bytes = obj.media.size
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            except:
                return '-'
        return '-'
    size.short_description = 'SIZE'
    
    def mime_type(self, obj):
        """Display MIME type"""
        if obj.media:
            file_url = obj.media.name.lower()
            if file_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                ext = file_url.split('.')[-1]
                return f"image/{ext}"
            elif file_url.endswith('.pdf'):
                return "application/pdf"
            elif file_url.endswith(('.doc', '.docx')):
                return "application/msword"
            else:
                return "file"
        return '-'
    mime_type.short_description = 'MIME'
    
    def download_link(self, obj):
        """Provide download link"""
        if obj.media:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff; text-decoration: none;">Download</a>',
                obj.media.url
            )
        return '-'
    download_link.short_description = 'DOWNLOAD'


class VerificationDocumentAdmin(admin.ModelAdmin):
    """Admin for VerificationDocument model"""
    list_display = ['uuid', 'profile', 'document_type', 'status', 'reviewed_by', 'document_url_preview', 'created_at']
    list_filter = ['status', 'document_type', 'created_at', 'reviewed_at']
    search_fields = ['profile__user__email', 'document_type', 'document_url']
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'reviewed_at', 'document_url_preview']
    list_per_page = 20
    
    fieldsets = (
        ('Document Information', {
            'fields': ('uuid', 'profile', 'document_url', 'document_url_preview', 'document_type')
        }),
        ('Verification Status', {
            'fields': ('status', 'rejection_reason', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def document_url_preview(self, obj):
        """Display document URL with link"""
        if obj.document_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff; text-decoration: none;">View Document</a>',
                obj.document_url
            )
        return '-'
    document_url_preview.short_description = 'DOCUMENT URL'


# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserOTP)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(MediaStorage, MediaStorageAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(PreferredContributionPath, PreferredContributionPathAdmin)
admin.site.register(Affiliation, AffiliationAdmin)
admin.site.register(VerificationDocument, VerificationDocumentAdmin)