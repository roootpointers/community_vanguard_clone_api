from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from donation.models import Donation, DonationTarget


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """Admin interface for Donation model"""
    
    list_display = [
        'donor_name',
        'donor_email',
        'colored_amount',
        'currency',
        'method',
        'donation_date',
        'created_at',
    ]
    list_filter = [
        'currency',
        'method',
        'month',
        'year',
        'created_at',
    ]
    search_fields = [
        'donor_name',
        'donor_email',
        'notes',
    ]
    readonly_fields = [
        'formatted_amount',
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('Donor Information', {
            'fields': ('donor_name', 'donor_email')
        }),
        ('Donation Details', {
            'fields': ('amount', 'currency', 'method', 'formatted_amount')
        }),
        ('Date Information', {
            'fields': ('month', 'year', 'created_at', 'updated_at')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    
    def colored_amount(self, obj):
        """Display amount with color based on value"""
        if obj.amount is None:
            return '-'
        color = 'green' if obj.amount >= 1000 else 'blue' if obj.amount >= 100 else 'black'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.formatted_amount
        )
    colored_amount.short_description = 'Amount'
    colored_amount.admin_order_field = 'amount'
    
    def donation_date(self, obj):
        """Display month and year as a formatted date"""
        if obj.month and obj.year:
            month_names = [
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            ]
            month_name = month_names[obj.month - 1] if 1 <= obj.month <= 12 else str(obj.month)
            return f"{month_name} {obj.year}"
        return "-"
    donation_date.short_description = 'Donation Period'
    
    def get_queryset(self, request):
        """Add total amount to changelist"""
        qs = super().get_queryset(request)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist"""
        extra_context = extra_context or {}
        
        # Calculate totals by currency
        totals = {}
        for currency in ['USD', 'EUR', 'GBP']:
            total = Donation.objects.filter(currency=currency).aggregate(Sum('amount'))['amount__sum']
            if total:
                totals[currency] = total
        
        extra_context['donation_totals'] = totals
        return super().changelist_view(request, extra_context)


@admin.register(DonationTarget)
class DonationTargetAdmin(admin.ModelAdmin):
    """Admin interface for DonationTarget model"""
    
    list_display = [
        'get_period',
        'target_display',
        'collected_display',
        'progress_bar',
        'currency',
        'created_at',
    ]
    list_filter = [
        'year',
        'currency',
    ]
    search_fields = [
        'description',
    ]
    readonly_fields = [
        'get_month_name',
        'get_collected_amount',
        'get_progress_percentage',
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('Target Period', {
            'fields': ('month', 'year', 'get_month_name')
        }),
        ('Target Details', {
            'fields': ('target_amount', 'currency', 'description')
        }),
        ('Progress', {
            'fields': ('get_collected_amount', 'get_progress_percentage'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-year', '-month']
    list_per_page = 25
    
    def get_period(self, obj):
        """Display formatted period"""
        return f"{obj.get_month_name()} {obj.year}"
    get_period.short_description = 'Period'
    get_period.admin_order_field = 'month'
    
    def target_display(self, obj):
        """Display target amount with currency symbol"""
        if obj.target_amount is None:
            return '-'
        symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'CAD': 'C$', 'AUD': 'A$', 'JPY': '¥'}
        symbol = symbols.get(obj.currency, obj.currency) if obj.currency else ''
        return f"{symbol}{obj.target_amount:,.2f}"
    target_display.short_description = 'Target'
    target_display.admin_order_field = 'target_amount'
    
    def collected_display(self, obj):
        """Display collected amount with currency symbol"""
        collected = obj.get_collected_amount()
        if collected is None:
            collected = 0
        symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'CAD': 'C$', 'AUD': 'A$', 'JPY': '¥'}
        symbol = symbols.get(obj.currency, obj.currency) if obj.currency else ''
        return f"{symbol}{collected:,.2f}"
    collected_display.short_description = 'Collected'
    
    def progress_bar(self, obj):
        """Display progress as a visual bar"""
        progress = obj.get_progress_percentage()
        color = 'green' if progress >= 75 else 'orange' if progress >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-weight: bold;">'
            '{}%'
            '</div>'
            '</div>',
            min(progress, 100),
            color,
            round(progress, 1)
        )
    progress_bar.short_description = 'Progress'
