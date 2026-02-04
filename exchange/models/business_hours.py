import uuid
from django.db import models
from django.core.exceptions import ValidationError
from datetime import time
from .exchange import Exchange


class BusinessHours(models.Model):
    """
    Model to store business operating hours for each day of the week.
    Supports multiple shifts per day (e.g., morning and evening shifts).
    
    This is the proper relational model for managing business hours.
    The Exchange.business_hours JSONField is for display/legacy purposes.
    """
    
    DAYS_OF_WEEK = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name='operating_hours'
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        help_text="Day of the week (1=Monday, 7=Sunday)"
    )
    open_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Opening time for this shift"
    )
    close_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Closing time for this shift"
    )
    is_closed = models.BooleanField(
        default=False,
        help_text="Mark as closed if the business is not operating on this day"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_hours'
        ordering = ['day_of_week', 'open_time']
        indexes = [
            models.Index(fields=['exchange', 'day_of_week']),
        ]
        verbose_name = 'Business Hours'
        verbose_name_plural = 'Business Hours'
        # Ensure unique constraint for day and shift combination
        unique_together = ['exchange', 'day_of_week', 'open_time']
    
    def clean(self):
        """Validate that close_time is after open_time."""
        if not self.is_closed and self.open_time and self.close_time:
            if self.close_time <= self.open_time:
                raise ValidationError({
                    'close_time': 'Close time must be after open time.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        if self.is_closed:
            return f"{self.exchange.business_name} - {day_name} (Closed)"
        return f"{self.exchange.business_name} - {day_name} ({self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')})"
