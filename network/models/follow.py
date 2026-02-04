"""
Follow model for Network app
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Follow(models.Model):
    """
    Model representing follower/following relationship between users
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_set',
        help_text="User who is following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers_set',
        help_text="User being followed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'network_follow'
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    def clean(self):
        """Validate that user cannot follow themselves"""
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves")

    def save(self, *args, **kwargs):
        """Override save to call clean()"""
        self.clean()
        super().save(*args, **kwargs)

    @staticmethod
    def is_following(follower, following):
        """Check if follower is following the user"""
        return Follow.objects.filter(
            follower=follower,
            following=following
        ).exists()

    @staticmethod
    def get_followers_count(user):
        """Get count of followers for a user"""
        return Follow.objects.filter(following=user).count()

    @staticmethod
    def get_following_count(user):
        """Get count of users that a user is following"""
        return Follow.objects.filter(follower=user).count()

    @staticmethod
    def get_mutual_followers(user1, user2):
        """Get users who follow both user1 and user2"""
        user1_followers = Follow.objects.filter(following=user1).values_list('follower', flat=True)
        user2_followers = Follow.objects.filter(following=user2).values_list('follower', flat=True)
        mutual_follower_ids = set(user1_followers) & set(user2_followers)
        return settings.AUTH_USER_MODEL.objects.filter(uuid__in=mutual_follower_ids)
