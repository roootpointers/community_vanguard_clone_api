import uuid
from django.db import models
from accounts.models.profile import UserProfile


class VerificationDocument(models.Model):
    """
    Model for storing multiple verification documents for a user profile.
    Each profile can have multiple verification documents.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='verification_documents'
    )
    document_url = models.CharField(
        max_length=500,
        help_text="URL to the verification document (stored externally like S3/CDN or local path)"
    )
    document_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Type of document (e.g., 'id_card', 'military_id', 'dd214', 'license', etc.)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Verification status of the document"
    )
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for rejection if document is rejected"
    )
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents',
        help_text="Admin user who reviewed this document"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the document was reviewed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_documents'
        verbose_name = 'Verification Document'
        verbose_name_plural = 'Verification Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification Document for {self.profile.user.email} - {self.document_type or 'Unknown'}"
