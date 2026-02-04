from django.contrib import admin
from exchange.models import (
    Exchange,
    ExchangeVerification,
    ExchangePreviewImage,
    Category,
    SubCategory,
    ExchangeReview,
    ExchangeQuote,
    BusinessHours,
    TimeSlot,
    Booking
)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 0
    readonly_fields = ['uuid', 'created_at']
    fields = ['name', 'created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcategories_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    inlines = [SubCategoryInline]
    
    fieldsets = (
        ('Category Information', {
            'fields': ('uuid', 'name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def subcategories_count(self, obj):
        """Display count of subcategories."""
        return obj.subcategories.count()
    subcategories_count.short_description = 'SubCategories'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category__name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('SubCategory Information', {
            'fields': ('uuid', 'category', 'name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ExchangeVerificationInline(admin.TabularInline):
    model = ExchangeVerification
    extra = 0
    readonly_fields = ['uuid', 'created_at']
    fields = ['verification_file', 'file_type', 'created_at']


class ExchangePreviewImageInline(admin.TabularInline):
    model = ExchangePreviewImage
    extra = 0
    readonly_fields = ['uuid', 'created_at']
    fields = ['image_url', 'order', 'created_at']
    ordering = ['order']


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = [
        'business_name',
        'seller_type',
        'category',
        'email',
        'status',
        'id_me_verified',
        'created_at'
    ]
    list_filter = ['seller_type', 'status', 'category', 'id_me_verified', 'created_at']
    search_fields = [
        'business_name',
        'business_ein',
        'email',
        'phone',
        'mission_statement',
        'offers_benefits'
    ]
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    inlines = [ExchangeVerificationInline, ExchangePreviewImageInline]
    
    fieldsets = (
        ('Business Information', {
            'fields': (
                'uuid',
                'user',
                'business_name',
                'business_ein',
                'seller_type',
                'category',
                'sub_category'
            )
        }),
        ('Verification', {
            'fields': (
                'id_me_verified',
                'manual_verification_doc',
                'status'
            )
        }),
        ('Business Media', {
            'fields': (
                'business_logo',
                'business_background_image'
            )
        }),
        ('Mission & Offers', {
            'fields': (
                'mission_statement',
                'offers_benefits',
                'business_hours'
            )
        }),
        ('Contact Information', {
            'fields': (
                'address',
                'phone',
                'email',
                'website'
            )
        }),
        ('Social Media', {
            'fields': (
                'facebook',
                'facebook_enabled',
                'twitter',
                'twitter_enabled',
                'instagram',
                'instagram_enabled',
                'linkedin',
                'linkedin_enabled'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_exchanges', 'reject_exchanges', 'mark_pending', 'mark_under_review']
    
    def approve_exchanges(self, request, queryset):
        """Bulk approve selected exchanges."""
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} exchange(s) approved successfully.")
    approve_exchanges.short_description = "Approve selected exchanges"
    
    def reject_exchanges(self, request, queryset):
        """Bulk reject selected exchanges."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} exchange(s) rejected.")
    reject_exchanges.short_description = "Reject selected exchanges"
    
    def mark_pending(self, request, queryset):
        """Mark selected exchanges as pending."""
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} exchange(s) marked as pending review.")
    mark_pending.short_description = "Mark as pending review"
    
    def mark_under_review(self, request, queryset):
        """Mark selected exchanges as under review."""
        updated = queryset.update(status='under_review')
        self.message_user(request, f"{updated} exchange(s) marked as under review.")
    mark_under_review.short_description = "Mark as under review"


@admin.register(ExchangeVerification)
class ExchangeVerificationAdmin(admin.ModelAdmin):
    list_display = ['exchange', 'file_type', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['exchange__business_name']
    readonly_fields = ['uuid', 'created_at']


@admin.register(ExchangePreviewImage)
class ExchangePreviewImageAdmin(admin.ModelAdmin):
    list_display = ['exchange', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['exchange__business_name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['exchange', 'order']


@admin.register(ExchangeReview)
class ExchangeReviewAdmin(admin.ModelAdmin):
    list_display = ['exchange', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['exchange__business_name', 'user__email', 'review_text']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('uuid', 'exchange', 'user', 'rating', 'review_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExchangeQuote)
class ExchangeQuoteAdmin(admin.ModelAdmin):
    list_display = ['name', 'exchange', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'description', 'exchange__business_name', 'user__email']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Quote Information', {
            'fields': ('uuid', 'exchange', 'user', 'name', 'email', 'description', 'mini_range', 'maxi_range', 'uploaded_files')
        }),
        ('Response', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_reviewed', 'mark_quoted', 'reject_quotes']
    
    def mark_reviewed(self, request, queryset):
        """Mark selected quotes as reviewed."""
        updated = queryset.update(status='reviewed')
        self.message_user(request, f"{updated} quote(s) marked as reviewed.")
    mark_reviewed.short_description = "Mark as reviewed"
    
    def mark_quoted(self, request, queryset):
        """Mark selected quotes as quoted."""
        updated = queryset.update(status='quoted')
        self.message_user(request, f"{updated} quote(s) marked as quoted.")
    mark_quoted.short_description = "Mark as quoted"
    
    def reject_quotes(self, request, queryset):
        """Reject selected quotes."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} quote(s) rejected.")
    reject_quotes.short_description = "Reject selected quotes"


# ===== Booking System Admin =====

@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['exchange', 'get_day_name', 'open_time', 'close_time', 'is_closed']
    list_filter = ['day_of_week', 'is_closed', 'created_at']
    search_fields = ['exchange__business_name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['exchange', 'day_of_week', 'open_time']
    
    fieldsets = (
        ('Business Hours', {
            'fields': ('uuid', 'exchange', 'day_of_week', 'open_time', 'close_time', 'is_closed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_day_name(self, obj):
        """Display readable day name."""
        days = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
        return days.get(obj.day_of_week, '')
    get_day_name.short_description = 'Day'
    get_day_name.admin_order_field = 'day_of_week'


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ['uuid', 'user', 'customer_name', 'status', 'created_at']
    fields = ['user', 'customer_name', 'status', 'created_at']
    can_delete = False
    max_num = 0  # Don't allow adding from inline


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = [
        'exchange',
        'date',
        'start_time',
        'end_time',
        'is_available',
        'current_bookings',
        'max_capacity',
        'get_available_capacity'
    ]
    list_filter = ['is_available', 'date', 'exchange', 'created_at']
    search_fields = ['exchange__business_name']
    readonly_fields = ['uuid', 'current_bookings', 'created_at', 'updated_at']
    ordering = ['-date', 'start_time']
    date_hierarchy = 'date'
    inlines = [BookingInline]
    
    fieldsets = (
        ('Time Slot Information', {
            'fields': ('uuid', 'exchange', 'date', 'start_time', 'end_time')
        }),
        ('Capacity & Availability', {
            'fields': ('is_available', 'max_capacity', 'current_bookings')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_unavailable', 'mark_available']
    
    def get_available_capacity(self, obj):
        """Display available capacity."""
        return obj.max_capacity - obj.current_bookings
    get_available_capacity.short_description = 'Available'
    
    def mark_unavailable(self, request, queryset):
        """Mark selected slots as unavailable."""
        updated = queryset.update(is_available=False)
        self.message_user(request, f"{updated} slot(s) marked as unavailable.")
    mark_unavailable.short_description = "Mark as unavailable"
    
    def mark_available(self, request, queryset):
        """Mark selected slots as available (if capacity allows)."""
        count = 0
        for slot in queryset:
            if slot.current_bookings < slot.max_capacity:
                slot.is_available = True
                slot.save()
                count += 1
        self.message_user(request, f"{count} slot(s) marked as available.")
    mark_available.short_description = "Mark as available"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name',
        'exchange',
        'get_booking_date',
        'get_booking_time',
        'status',
        'user',
        'created_at'
    ]
    list_filter = ['status', 'time_slot__date', 'exchange', 'created_at']
    search_fields = [
        'customer_name',
        'customer_email',
        'customer_phone',
        'exchange__business_name',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    readonly_fields = [
        'uuid',
        'user',
        'exchange',
        'time_slot',
        'cancelled_at',
        'created_at',
        'updated_at'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Booking Information', {
            'fields': (
                'uuid',
                'user',
                'exchange',
                'time_slot',
                'status'
            )
        }),
        ('Customer Details', {
            'fields': (
                'customer_name',
                'customer_email',
                'customer_phone',
                'notes'
            )
        }),
        ('Cancellation', {
            'fields': (
                'cancelled_at',
                'cancellation_reason'
            ),
            'classes': ('collapse',)
        }),
        ('Admin', {
            'fields': ('admin_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_bookings', 'complete_bookings', 'mark_no_show']
    
    def get_booking_date(self, obj):
        """Display booking date."""
        return obj.time_slot.date
    get_booking_date.short_description = 'Date'
    get_booking_date.admin_order_field = 'time_slot__date'
    
    def get_booking_time(self, obj):
        """Display booking time range."""
        return f"{obj.time_slot.start_time.strftime('%H:%M')} - {obj.time_slot.end_time.strftime('%H:%M')}"
    get_booking_time.short_description = 'Time'
    
    def confirm_bookings(self, request, queryset):
        """Confirm selected bookings."""
        count = 0
        for booking in queryset.filter(status='pending'):
            booking.status = 'confirmed'
            booking.save()
            count += 1
        self.message_user(request, f"{count} booking(s) confirmed.")
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def complete_bookings(self, request, queryset):
        """Mark selected bookings as completed."""
        count = 0
        for booking in queryset.filter(status='confirmed'):
            booking.status = 'completed'
            booking.save()
            count += 1
        self.message_user(request, f"{count} booking(s) marked as completed.")
    complete_bookings.short_description = "Mark as completed"
    
    def mark_no_show(self, request, queryset):
        """Mark selected bookings as no-show."""
        count = 0
        for booking in queryset.filter(status__in=['pending', 'confirmed']):
            booking.status = 'no_show'
            booking.save()
            count += 1
        self.message_user(request, f"{count} booking(s) marked as no-show.")
    mark_no_show.short_description = "Mark as no-show"

