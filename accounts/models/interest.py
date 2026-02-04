import uuid
from django.db import models


class Interest(models.Model):
    """
    Interest model for storing user interests/hobbies.
    Users can select multiple interests during profile setup.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Name of the interest (e.g., Aviation, Medical, Technology)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interests'
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'
        ordering = ['name']

    def __str__(self):
        return self.name
