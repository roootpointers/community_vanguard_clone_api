import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from accounts.models.user import User


# Define choices for role type
ROLE_CHOICES = (
    ('customer', 'Customer (General User)'),
    ('vendor', 'Vendor (Paid Business)'),
    ('community_support_provider', 'Community Support Provider (VSO / Non-Profit)'),
)


class UserRole(models.Model):
    """
    UserRole model for handling user role change/upgrade requests.
    This model is used when users want to become Vendors or Community Support Providers.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_requests')
    
    # Role Information
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        help_text="The role being requested by the user"
    )
    
    # Vendor-specific fields
    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_ein = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Business EIN (Employer Identification Number)"
    )
    business_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Type of business (e.g., Product, Service)"
    )
    
    # Community Support Provider-specific fields
    organization_name = models.CharField(max_length=255, null=True, blank=True)
    organization_mission = models.TextField(null=True, blank=True)

    # Verification Documents
    tax_document = models.CharField(max_length=255, null=True, blank=True)
    is_nonprofit_confirmed = models.BooleanField(
        default=False,
        help_text="Confirmation that organization is a registered non-profit"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Indicates if the role request has been verified and approved"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'role']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role}"
