import uuid
from django.db import models


class PreferredContributionPath(models.Model):
    """
    PreferredContributionPath model for storing contribution path options.
    Users can select one path during profile setup.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text="Name of the contribution path")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'preferred_contribution_paths'
        verbose_name = 'Preferred Contribution Path'
        verbose_name_plural = 'Preferred Contribution Paths'
        ordering = ['name']

    def __str__(self):
        return self.name
