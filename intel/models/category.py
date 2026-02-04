import uuid
from django.db import models


class IntelCategory(models.Model):
    """
    Category model for Intel posts.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., Security, Infrastructure, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Intel Category'
        verbose_name_plural = 'Intel Categories'
    
    def __str__(self):
        return self.name
