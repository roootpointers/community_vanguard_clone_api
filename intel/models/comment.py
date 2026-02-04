import uuid
from django.db import models
from django.conf import settings
from intel.models.intel import Intel


class IntelComment(models.Model):
    """
    Model for comments on Intel posts.
    Supports nested comments (replies) with parent_comment field.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intel_comments'
    )
    intel = models.ForeignKey(
        Intel,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment for nested replies"
    )
    content = models.TextField(
        help_text="Comment text content"
    )
    
    # Counts for performance
    likes_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['intel', '-created_at']),
            models.Index(fields=['parent_comment']),
            models.Index(fields=['user']),
        ]
        verbose_name = 'Intel Comment'
        verbose_name_plural = 'Intel Comments'
    
    def __str__(self):
        if self.parent_comment:
            return f"Reply by {self.user.email} on Intel {self.intel.uuid}"
        return f"Comment by {self.user.email} on Intel {self.intel.uuid}"
    
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent_comment is not None


class CommentLike(models.Model):
    """
    Model for tracking likes on comments.
    A user can like a comment only once.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )
    comment = models.ForeignKey(
        IntelComment,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'comment']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['comment', '-created_at']),
            models.Index(fields=['user']),
        ]
        verbose_name = 'Comment Like'
        verbose_name_plural = 'Comment Likes'
    
    def __str__(self):
        return f"{self.user.email} liked Comment {self.comment.uuid}"
