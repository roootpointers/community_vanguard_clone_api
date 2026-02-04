import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from .exchange import Exchange


class ExchangeReview(models.Model):
    """
    Model for customer reviews on exchanges.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exchange_reviews')
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    
    # Review text
    review_text = models.TextField(max_length=500, blank=True, null=True, help_text="Review description")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exchange_reviews'
        ordering = ['-created_at']
        unique_together = ['exchange', 'user']  # One review per user per exchange
        indexes = [
            models.Index(fields=['exchange']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.exchange.business_name} ({self.rating} stars)"
