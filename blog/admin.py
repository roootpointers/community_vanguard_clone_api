from django.contrib import admin
from django.utils.html import format_html
from blog.models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """Admin interface for Blog model"""
    
    list_display = [
        'title',
        'author',
        'colored_status',
        'mission_genesis_badge',
        'views_count',
        'created_at',
    ]
    list_filter = [
        'status',
        'is_mission_genesis',
        'created_at',
        'author',
    ]
    search_fields = [
        'title',
        'content',
        'author',
    ]
    readonly_fields = [
        'uuid',
        'slug',
        'views_count',
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Content', {
            'fields': ('content', 'featured_image')
        }),
        ('Settings', {
            'fields': ('is_mission_genesis',)
        }),
        ('Metadata', {
            'fields': ('uuid', 'views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    
    def colored_status(self, obj):
        """Display status with color"""
        colors = {
            'Published': 'green',
            'Draft': 'orange',
            'Archived': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status
        )
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'
    
    def mission_genesis_badge(self, obj):
        """Display Mission Genesis badge"""
        if obj.is_mission_genesis:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">✓ Mission Genesis</span>'
            )
        return '-'
    mission_genesis_badge.short_description = 'Special Status'
    mission_genesis_badge.admin_order_field = 'is_mission_genesis'
    
    def save_model(self, request, obj, form, change):
        """Override save to handle Mission Genesis logic"""
        super().save_model(request, obj, form, change)
    
    actions = ['make_published', 'make_draft', 'make_archived', 'set_mission_genesis']
    
    def make_published(self, request, queryset):
        """Bulk action to publish blogs"""
        updated = queryset.update(status='Published')
        self.message_user(request, f'{updated} blog(s) marked as Published.')
    make_published.short_description = "Mark selected blogs as Published"
    
    def make_draft(self, request, queryset):
        """Bulk action to mark as draft"""
        updated = queryset.update(status='Draft')
        self.message_user(request, f'{updated} blog(s) marked as Draft.')
    make_draft.short_description = "Mark selected blogs as Draft"
    
    def make_archived(self, request, queryset):
        """Bulk action to archive blogs"""
        updated = queryset.update(status='Archived')
        self.message_user(request, f'{updated} blog(s) marked as Archived.')
    make_archived.short_description = "Mark selected blogs as Archived"
    
    def set_mission_genesis(self, request, queryset):
        """Set one blog as Mission Genesis"""
        if queryset.count() > 1:
            self.message_user(request, 'You can only set one blog as Mission Genesis at a time.', level='error')
            return
        
        blog = queryset.first()
        if blog:
            # Remove Mission Genesis from all blogs
            Blog.objects.filter(is_mission_genesis=True).update(is_mission_genesis=False)
            # Set selected blog as Mission Genesis
            blog.is_mission_genesis = True
            blog.save()
            self.message_user(request, f'"{blog.title}" set as Mission Genesis blog.')
    set_mission_genesis.short_description = "Set as Mission Genesis blog"
