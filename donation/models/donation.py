import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Donation(models.Model):
    """
    Model representing a donation made by a donor.
    """
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('JPY', 'Japanese Yen'),
    ]
    
    METHOD_CHOICES = [
        ('Card', 'Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Paypal', 'Paypal'),
        ('Cash', 'Cash'),
        ('Crypto', 'Cryptocurrency'),
        ('Other', 'Other'),
    ]
    
    donor_name = models.CharField(max_length=255, help_text="Name of the donor")
    donor_email = models.EmailField(help_text="Email address of the donor")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Donation amount"
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="Currency of the donation"
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default='Card',
        help_text="Payment method used"
    )
    month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Month of donation (1-12)"
    )
    year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year of donation"
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['donor_email']),
            models.Index(fields=['currency']),
            models.Index(fields=['month', 'year']),
        ]
    
    def __str__(self):
        return f"{self.donor_name} - {self.currency} {self.amount}"
    
    @property
    def formatted_amount(self):
        """Returns formatted amount with currency symbol"""
        if self.amount is None:
            return "-"
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'CAD': 'C$',
            'AUD': 'A$',
            'JPY': '¥',
        }
        symbol = symbols.get(self.currency, self.currency) if self.currency else ''
        return f"{symbol}{self.amount:,.2f}"
