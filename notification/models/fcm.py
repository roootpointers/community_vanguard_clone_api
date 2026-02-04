import uuid
from django.db import models
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice

User = get_user_model()


class FCMDeviceCustom(FCMDevice):
    """
    Custom FCM Device model that extends the FCMDevice model to include additional fields.
    This model is used to manage FCM devices in the application.
    """
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device_name = models.CharField(max_length=100, null=True, blank=True, help_text="Device name or model")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FCM Device"
        verbose_name_plural = "FCM Devices"

    def __str__(self):
        return f"{self.device_name or 'Unknown Device'} - {self.user.email if self.user else 'Anonymous'}"
    
    def activate(self):
        """Activate this device"""
        self.active = True
        self.save(update_fields=['active', 'updated_at'])
    
    def deactivate(self):
        """Deactivate this device"""
        self.active = False
        self.save(update_fields=['active', 'updated_at'])


class NotificationTemplate(models.Model):
    """
    Model to store notification templates for different notification types in the Vanguard app
    """
    NOTIFICATION_TYPES = [
        # Intel-related
        ('INTEL_COMMENT', 'Intel Comment'),
        ('INTEL_LIKE', 'Intel Like'),
        ('INTEL_STATUS_UPDATE', 'Intel Status Update'),
        
        # Exchange-related
        ('EXCHANGE_APPROVED', 'Exchange Approved'),
        ('EXCHANGE_REJECTED', 'Exchange Rejected'),
        ('EXCHANGE_UNDER_REVIEW', 'Exchange Under Review'),
        
        # System
        ('SYSTEM', 'System'),
        ('PROFILE_VERIFICATION', 'Profile Verification'),
        ('ROLE_REQUEST_UPDATE', 'Role Request Update'),
    ]

    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title_template = models.CharField(max_length=200, help_text="Template for notification title")
    body_template = models.TextField(help_text="Template for notification body")
    icon = models.CharField(max_length=200, null=True, blank=True, help_text="Icon URL or name")
    sound = models.CharField(max_length=100, default='default', help_text="Sound for notification")
    priority = models.CharField(
        max_length=10, 
        choices=[('high', 'High'), ('normal', 'Normal')], 
        default='normal'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"

    def __str__(self):
        return f"{self.name} - {self.notification_type}"


class NotificationLog(models.Model):
    """
    Model to log all sent notifications for tracking and analytics
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('CLICKED', 'Clicked'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_logs')
    device = models.ForeignKey(FCMDeviceCustom, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(null=True, blank=True, help_text="Additional data sent with notification")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    firebase_message_id = models.CharField(max_length=200, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username} - {self.status}"