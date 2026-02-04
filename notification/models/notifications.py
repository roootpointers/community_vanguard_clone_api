import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    """
    Notification model to handle various types of notifications for users in the Vanguard app.
    """

    NOTIFICATION_TYPES = [
        # Intel-related notifications
        ('INTEL_COMMENT', 'Intel Comment'),
        ('INTEL_LIKE', 'Intel Like'),
        ('INTEL_STATUS_UPDATE', 'Intel Status Update'),
        
        # Exchange-related notifications
        ('EXCHANGE_APPROVED', 'Exchange Approved'),
        ('EXCHANGE_REJECTED', 'Exchange Rejected'),
        ('EXCHANGE_UNDER_REVIEW', 'Exchange Under Review'),
        
        # System notifications
        ('SYSTEM_UPDATES', 'System Updates'),
        ('WARNINGS_FLAGS', 'Warnings & Flags'),
        ('PROFILE_VERIFICATION', 'Profile Verification'),
        ('ROLE_REQUEST_UPDATE', 'Role Request Update'),
        
        # Document verification notifications
        ('DOCUMENT_APPROVED', 'Document Approved'),
        ('DOCUMENT_REJECTED', 'Document Rejected'),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who will receive this notification"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True,
        help_text="User who triggered this notification (optional for system notifications)"
    )
    
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        help_text="Type of notification"
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Notification title"
    )
    
    message = models.TextField(
        help_text="Notification message content"
    )
    
    # Optional fields for linking to related objects
    related_object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID of the related object (post, comment, etc.)"
    )
    
    related_object_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Type of the related object (post, comment, wink, etc.)"
    )
    
    # Status fields
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read"
    )
    
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was marked as read"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was deleted"
    )
    
    # Additional data (JSON field for flexible data storage)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for the notification"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'is_deleted']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark this notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def soft_delete(self):
        """Soft delete this notification"""
        from django.utils import timezone
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def restore(self):
        """Restore a soft deleted notification"""
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=['is_deleted', 'deleted_at'])
