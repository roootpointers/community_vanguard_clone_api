import uuid
from django.db import models


class Affiliation(models.Model):
    """
    Affiliation model for storing organization/military affiliation options.
    Users can select one affiliation during profile setup.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text="Name of the affiliation")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'affiliations'
        verbose_name = 'Affiliation'
        verbose_name_plural = 'Affiliations'
        ordering = ['name']

    def __str__(self):
        return self.name
