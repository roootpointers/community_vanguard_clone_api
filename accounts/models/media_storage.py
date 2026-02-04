import uuid
from django.db import models


class MediaStorage(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('document', 'Document'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    )
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    media = models.FileField(upload_to='media_storage/', blank=True, null=True)
    media_type = models.CharField(max_length=50, choices=MEDIA_TYPE_CHOICES, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Media Storage'

    def __str__(self):
        return str(self.uuid)