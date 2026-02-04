"""
Report model for Network app
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


REPORT_REASON_CHOICES = (
    ('harassment', 'Harassment'),
    ('hate_speech', 'Hate Speech'),
    ('spam', 'Spam'),
    ('inappropriate_content', 'Inappropriate Content'),
    ('impersonation', 'Impersonation'),
    ('scam', 'Scam'),
    ('other', 'Other'),
)

REPORT_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('resolved', 'Resolved'),
    ('dismissed', 'Dismissed'),
)


class Report(models.Model):
    """
    Model for reporting users for violations
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_received',
        help_text="User being reported"
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_made',
        help_text="User making the report"
    )
    reason = models.CharField(
        max_length=50,
        choices=REPORT_REASON_CHOICES,
        help_text="Reason for reporting"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed description of the violation"
    )
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS_CHOICES,
        default='pending',
        help_text="Status of the report"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'network_report'
        unique_together = ('reported_user', 'reported_by')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reported_user', '-created_at']),
            models.Index(fields=['reported_by', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Report: {self.reported_user.username} reported by {self.reported_by.username} - {self.get_reason_display()}"

    def clean(self):
        """Validate that user cannot report themselves"""
        if self.reported_user == self.reported_by:
            raise ValidationError("Users cannot report themselves")

    def save(self, *args, **kwargs):
        """Override save to call clean()"""
        self.clean()
        super().save(*args, **kwargs)
