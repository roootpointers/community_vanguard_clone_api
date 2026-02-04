import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class DonationTarget(models.Model):
    """
    Model representing a donation target/goal for a specific month and year.
    """
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    month = models.IntegerField(
        help_text="Target month (1-12)"
    )
    year = models.IntegerField(
        help_text="Target year"
    )
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Target donation amount"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency of the target"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the target goal"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year']
        indexes = [
            models.Index(fields=['month', 'year']),
        ]
    
    def __str__(self):
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        month_name = month_names[self.month - 1] if 1 <= self.month <= 12 else str(self.month)
        return f"{month_name} {self.year} - {self.currency} {self.target_amount}"
    
    def get_month_name(self):
        """Returns the name of the month"""
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return month_names[self.month - 1] if 1 <= self.month <= 12 else str(self.month)
    
    def get_collected_amount(self):
        """Calculate total collected donations for this target period"""
        from .donation import Donation
        donations = Donation.objects.filter(
            month=self.month,
            year=self.year,
            currency=self.currency
        )
        return sum(d.amount for d in donations)
    
    def get_progress_percentage(self):
        """Calculate progress percentage"""
        collected = self.get_collected_amount()
        if self.target_amount > 0:
            return min((collected / self.target_amount) * 100, 100)
        return 0
