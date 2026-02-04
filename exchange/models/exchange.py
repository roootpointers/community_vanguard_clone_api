import uuid
from django.db import models
from accounts.models import User
from .category import Category, SubCategory


class Exchange(models.Model):
    """
    Exchange model for organizations/businesses applying to join the exchange platform.
    """
    
    SELLER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('community_support_provider', 'Community Support Provider'),
    ]
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exchanges', null=True, blank=True)
    
    # Business Information
    business_name = models.CharField(max_length=255)
    business_ein = models.CharField(max_length=50, blank=True, null=True, help_text="Business EIN Number")
    seller_type = models.CharField(max_length=50, choices=SELLER_TYPE_CHOICES, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='exchanges', null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, related_name='exchanges', null=True, blank=True)
    
    # Verification
    id_me_verified = models.BooleanField(default=False, help_text="ID.me verification status")
    manual_verification_doc = models.CharField(max_length=255, blank=True, null=True, help_text="Manually uploaded verification document")
    
    # Business Media
    business_logo = models.CharField(max_length=255, blank=True, null=True)
    business_background_image = models.CharField(max_length=255, blank=True, null=True)
    
    # Mission Statement / Description
    mission_statement = models.TextField(blank=True, null=True, help_text="Mission Statement or Description")
    
    # Contact & Location
    address = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Phone Number")
    email = models.EmailField(blank=True, null=True, help_text="Email Address")
    website = models.URLField(blank=True, null=True, help_text="Website (optional)")
    
    # Offers & Benefits
    offers_benefits = models.TextField(blank=True, null=True, help_text="Offers and Benefits description")
    
    # Business Hours (stored as JSON)
    business_hours = models.JSONField(default=dict, blank=True, help_text="Business hours for each day of the week")
    
    # Social Media Links (Optional)
    facebook = models.URLField(blank=True, null=True)
    facebook_enabled = models.BooleanField(default=False)
    twitter = models.URLField(blank=True, null=True)
    twitter_enabled = models.BooleanField(default=False)
    instagram = models.URLField(blank=True, null=True)
    instagram_enabled = models.BooleanField(default=False)
    linkedin = models.URLField(blank=True, null=True)
    linkedin_enabled = models.BooleanField(default=False)
    
    # Status
    STATUS_CHOICES = [
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='under_review')
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason provided by admin if exchange is rejected"
    )

    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exchanges'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_type']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.business_name} - {self.get_seller_type_display()}"


class ExchangePreviewImage(models.Model):
    """
    Model for storing multiple preview images for exchanges.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, related_name='preview_images')
    image_url = models.CharField(max_length=255, help_text="Preview image URL")
    order = models.IntegerField(default=0, help_text="Display order")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exchange_preview_images'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Preview Image for {self.exchange.business_name}"


class ExchangeVerification(models.Model):
    """
    Model for storing verification documents/images for exchanges.
    Supports multiple files per exchange.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, related_name='verifications', null=True, blank=True)
    verification_file = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)  # 'photo' or 'document'
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exchange_verifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification for {self.exchange.business_name}"
