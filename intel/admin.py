from django.contrib import admin
from intel.models import Intel, IntelMedia, IntelLike, IntelComment, CommentLike, IntelCategory


@admin.register(IntelCategory)
class IntelCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Intel Categories."""
    list_display = ['uuid', 'name', 'created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('uuid', 'name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class IntelMediaInline(admin.TabularInline):
    """Inline admin for Intel media files."""
    model = IntelMedia
    extra = 1
    fields = ['file_url', 'file_type', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Intel)
class IntelAdmin(admin.ModelAdmin):
    """Admin interface for Intel posts."""
    list_display = ['uuid', 'user', 'category', 'location', 'urgency', 'status', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['urgency', 'status', 'created_at', 'category']
    search_fields = ['description', 'location', 'user__email', 'user__full_name', 'category__name']
    readonly_fields = ['uuid', 'likes_count', 'comments_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    inlines = [IntelMediaInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'user', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'location', 'urgency', 'status')
        }),
        ('Statistics', {
            'fields': ('likes_count', 'comments_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_verified', 'mark_as_investigating', 'mark_as_resolved']
    
    def mark_as_verified(self, request, queryset):
        """Mark selected intel posts as verified."""
        count = queryset.update(status='verified')
        self.message_user(request, f'{count} intel post(s) marked as verified.')
    mark_as_verified.short_description = "Mark as Verified"
    
    def mark_as_investigating(self, request, queryset):
        """Mark selected intel posts as investigating."""
        count = queryset.update(status='investigating')
        self.message_user(request, f'{count} intel post(s) marked as investigating.')
    mark_as_investigating.short_description = "Mark as Investigating"
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected intel posts as resolved."""
        count = queryset.update(status='resolved')
        self.message_user(request, f'{count} intel post(s) marked as resolved.')
    mark_as_resolved.short_description = "Mark as Resolved"


@admin.register(IntelMedia)
class IntelMediaAdmin(admin.ModelAdmin):
    """Admin interface for Intel media files."""
    list_display = ['uuid', 'intel', 'file_type', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['intel__uuid', 'file_url']
    readonly_fields = ['uuid', 'created_at']
    ordering = ['-created_at']


@admin.register(IntelLike)
class IntelLikeAdmin(admin.ModelAdmin):
    """Admin interface for Intel likes."""
    list_display = ['uuid', 'user', 'intel', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__full_name', 'intel__uuid']
    readonly_fields = ['uuid', 'created_at']
    ordering = ['-created_at']


@admin.register(IntelComment)
class IntelCommentAdmin(admin.ModelAdmin):
    """Admin interface for Intel comments."""
    list_display = ['uuid', 'user', 'intel', 'is_reply', 'likes_count', 'replies_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__full_name', 'intel__uuid', 'content']
    readonly_fields = ['uuid', 'likes_count', 'replies_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment Info', {
            'fields': ('uuid', 'user', 'intel', 'parent_comment', 'content')
        }),
        ('Statistics', {
            'fields': ('likes_count', 'replies_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Admin interface for Comment likes."""
    list_display = ['uuid', 'user', 'comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__full_name', 'comment__uuid']
    readonly_fields = ['uuid', 'created_at']
    ordering = ['-created_at']


