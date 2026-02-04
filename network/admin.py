"""
Admin configuration for Network app
"""
from django.contrib import admin
from network.models import Follow, Report


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin interface for Follow model"""
    list_display = [
        'uuid',
        'follower',
        'following',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'follower__username',
        'follower__email',
        'following__username',
        'following__email'
    ]
    readonly_fields = ['uuid', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Relationship', {
            'fields': ('uuid', 'follower', 'following')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('follower', 'following')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report model"""
    list_display = [
        'uuid',
        'reported_user',
        'reported_by',
        'reason',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'reason', 'created_at', 'updated_at']
    search_fields = [
        'reported_user__username',
        'reported_user__email',
        'reported_by__username',
        'reported_by__email',
        'description'
    ]
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Details', {
            'fields': ('uuid', 'reported_user', 'reported_by', 'reason', 'description')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('reported_user', 'reported_by')
