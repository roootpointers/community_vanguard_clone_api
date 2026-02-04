from django.contrib import admin
from notification.models import FCMDeviceCustom, NotificationTemplate, NotificationLog
from notification.models.notifications import Notification


admin.site.register(FCMDeviceCustom)
admin.site.register(NotificationTemplate)
admin.site.register(NotificationLog)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'recipient', 
        'sender', 
        'notification_type', 
        'is_read', 
        'is_deleted',
        'created_at'
    ]
    list_filter = [
        'notification_type', 
        'is_read', 
        'is_deleted', 
        'created_at'
    ]
    search_fields = [
        'title', 
        'message', 
        'recipient__username', 
        'sender__username'
    ]
    readonly_fields = [
        'uuid', 
        'created_at', 
        'read_at', 
        'deleted_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'title', 'message', 'notification_type')
        }),
        ('Users', {
            'fields': ('recipient', 'sender')
        }),
        ('Related Objects', {
            'fields': ('related_object_id', 'related_object_type')
        }),
        ('Status', {
            'fields': ('is_read', 'is_deleted', 'read_at', 'deleted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'sender')
