import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
# Define choices for account_type and profile_type
# Choices are used to limit the values that can be assigned to these fields
# This is useful for data integrity and validation
ACCOUNT_TYPE = (
    ('email', 'Email'),
    ('google', 'Google'),
    ('apple', 'Apple'),
)


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser and includes additional fields.
    This model is used to manage user accounts in the application.
    """
    # Define custom fields for the User model
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    social_id = models.CharField(max_length=255, null=True, blank=True)
    account_type = models.CharField(max_length=15, choices=ACCOUNT_TYPE, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    is_profile = models.BooleanField(default=False, null=True, blank=True, help_text="Indicates if the user has completed their profile")
    is_role = models.BooleanField(default=False, null=True, blank=True, help_text="Indicates if the user has a role assigned")
    is_profile_completed = models.BooleanField(default=False, help_text="Indicates if the user has completed the profile setup")
    is_banned = models.BooleanField(default=False, help_text="Indicates if the user is banned from logging in")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override the save method to set the username to the email address
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    # Define the string representation of the User model
    def __str__(self):
        return f"{self.email} - {self.account_type}"
