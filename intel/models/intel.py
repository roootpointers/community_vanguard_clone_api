import uuid
from django.db import models
from django.conf import settings


class Intel(models.Model):
    """
    Intel model represents ground truth intelligence reports.
    """
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intels'
    )
    description = models.TextField(
        help_text="Detailed description of the intel report"
    )
    category = models.ForeignKey(
        'IntelCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='intels',
        help_text="Category of the intel"
    )
    location = models.CharField(
        max_length=255,
        help_text="Location where the intel was observed"
    )
    urgency = models.CharField(
        max_length=10,
        choices=URGENCY_CHOICES,
        default='low',
        help_text="Urgency level of the intel"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='under_review',
        help_text="Current status of the intel"
    )
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason provided by admin if intel is rejected"
    )
    
    # Counts for performance
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['urgency']),
        ]
        verbose_name = 'Intel'
        verbose_name_plural = 'Intels'
    
    def __str__(self):
        return f"Intel by {self.user.email} - {self.category.name if self.category else 'No Category'}"


class IntelMedia(models.Model):
    """
    Model for storing multiple media files (photos/videos) for an Intel.
    """
    FILE_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
    ]
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intel = models.ForeignKey(
        Intel,
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    file_url = models.CharField(
        max_length=500,
        help_text="URL to the media file (stored externally like S3/CDN)"
    )
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        help_text="Type of media file"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Intel Media'
        verbose_name_plural = 'Intel Media'
    
    def __str__(self):
        return f"{self.file_type} for Intel {self.intel.uuid}"
