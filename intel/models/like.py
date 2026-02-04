import uuid
from django.db import models
from django.conf import settings
from intel.models.intel import Intel


class IntelLike(models.Model):
    """
    Model for tracking likes on Intel posts.
    A user can like an intel post only once.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intel_likes'
    )
    intel = models.ForeignKey(
        Intel,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'intel']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['intel', '-created_at']),
            models.Index(fields=['user']),
        ]
        verbose_name = 'Intel Like'
        verbose_name_plural = 'Intel Likes'
    
    def __str__(self):
        return f"{self.user.email} liked Intel {self.intel.uuid}"
