import uuid
from django.db import models
from accounts.models import User
from .exchange import Exchange


class ExchangeQuote(models.Model):
    """
    Model to store quote requests for exchanges.
    Users can request quotes from exchanges.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name='quotes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exchange_quotes'
    )
    
    # Quote form details
    name = models.CharField(max_length=200)
    email = models.EmailField()
    
    # What do you need? (description)
    description = models.TextField(max_length=500, help_text="What do you need?")
    
    mini_range = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    maxi_range = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Optional file uploads (stored as JSON array of file URLs)
    uploaded_files = models.JSONField(default=list, blank=True, help_text="Uploaded file URLs")
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exchange_quote'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['exchange', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Quote Request from {self.name} to {self.exchange.business_name}"
