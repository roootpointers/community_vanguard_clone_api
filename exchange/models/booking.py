import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from .exchange import Exchange


class TimeSlot(models.Model):
    """
    Model to represent time slots for bookings.
    Generated dynamically based on business hours and slot duration.
    """
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    date = models.DateField(help_text="Date for this time slot")
    start_time = models.TimeField(help_text="Start time of the slot")
    end_time = models.TimeField(help_text="End time of the slot")
    is_available = models.BooleanField(
        default=True,
        help_text="Whether this slot is available for booking"
    )
    max_capacity = models.IntegerField(
        default=1,
        help_text="Maximum number of bookings allowed for this slot"
    )
    current_bookings = models.IntegerField(
        default=0,
        help_text="Current number of active bookings for this slot"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'time_slots'
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['exchange', 'date', 'is_available']),
            models.Index(fields=['date', 'start_time']),
        ]
        # Ensure unique slots per exchange, date, and time
        unique_together = ['exchange', 'date', 'start_time', 'end_time']
    
    def clean(self):
        """Validate slot times and capacity."""
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({
                    'end_time': 'End time must be after start time.'
                })
        
        if self.max_capacity < 1:
            raise ValidationError({
                'max_capacity': 'Max capacity must be at least 1.'
            })
        
        if self.current_bookings < 0:
            raise ValidationError({
                'current_bookings': 'Current bookings cannot be negative.'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        # Auto-update availability based on capacity
        if self.current_bookings >= self.max_capacity:
            self.is_available = False
        elif self.current_bookings < self.max_capacity:
            self.is_available = True
        super().save(*args, **kwargs)
    
    def is_past(self):
        """Check if the time slot is in the past."""
        slot_datetime = datetime.combine(self.date, self.start_time)
        return slot_datetime < datetime.now()
    
    def increment_bookings(self):
        """Increment the booking count and update availability."""
        self.current_bookings += 1
        if self.current_bookings >= self.max_capacity:
            self.is_available = False
        self.save()
    
    def decrement_bookings(self):
        """Decrement the booking count and update availability."""
        if self.current_bookings > 0:
            self.current_bookings -= 1
            if self.current_bookings < self.max_capacity:
                self.is_available = True
            self.save()
    
    def __str__(self):
        return f"{self.exchange.business_name} - {self.date} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


class Booking(models.Model):
    """
    Model to store bookings made by users for specific time slots.
    Ensures no double booking through database constraints and model validation.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    # Booking details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Additional notes or special requests"
    )
    
    # Cancellation tracking
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for admin/exchange owner"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['exchange', 'status']),
            models.Index(fields=['time_slot', 'status']),
            models.Index(fields=['created_at']),
        ]
        # Prevent a user from booking the same slot multiple times
        # (unless previously cancelled)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'time_slot'],
                condition=models.Q(status__in=['pending', 'confirmed']),
                name='unique_active_booking_per_user_slot'
            )
        ]
    
    def clean(self):
        """Validate booking before saving."""
        # Check if time slot is available
        if self.time_slot and not self.time_slot.is_available:
            if not self.pk:  # Only check for new bookings
                raise ValidationError({
                    'time_slot': 'This time slot is no longer available.'
                })
        
        # Check if time slot is in the past (only for new bookings)
        if self.time_slot and self.time_slot.is_past():
            if not self.pk:  # Only check for new bookings
                raise ValidationError({
                    'time_slot': 'Cannot book a time slot in the past.'
                })
        
        # Ensure exchange matches time slot's exchange
        if self.time_slot and self.exchange:
            if self.time_slot.exchange != self.exchange:
                raise ValidationError({
                    'exchange': 'Exchange does not match the time slot.'
                })
    
    def save(self, *args, **kwargs):
        # Use _state.adding to check if this is a new object (more reliable than pk check for UUIDs)
        is_new = self._state.adding
        old_status = None
        
        if not is_new:
            try:
                old_status = Booking.objects.get(pk=self.pk).status
            except Booking.DoesNotExist:
                # Edge case: pk is set but object doesn't exist in DB
                is_new = True
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update time slot booking count
        if is_new and self.status in ['pending', 'confirmed']:
            self.time_slot.increment_bookings()
        elif not is_new and old_status in ['pending', 'confirmed'] and self.status == 'cancelled':
            self.time_slot.decrement_bookings()
            if not self.cancelled_at:
                self.cancelled_at = timezone.now()
                super().save(update_fields=['cancelled_at'])
    
    def cancel(self, reason=None):
        """Cancel the booking."""
        if self.status in ['cancelled', 'completed']:
            raise ValidationError(f'Cannot cancel a {self.status} booking.')
        
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        if reason:
            self.cancellation_reason = reason
        self.save()
    
    def confirm(self):
        """Confirm the booking."""
        if self.status != 'pending':
            raise ValidationError('Only pending bookings can be confirmed.')
        self.status = 'confirmed'
        self.save()
    
    def complete(self):
        """Mark booking as completed."""
        if self.status != 'confirmed':
            raise ValidationError('Only confirmed bookings can be marked as completed.')
        self.status = 'completed'
        self.save()
    
    def __str__(self):
        return f"{self.customer_name} - {self.exchange.business_name} on {self.time_slot.date}"
