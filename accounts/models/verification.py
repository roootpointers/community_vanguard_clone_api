import uuid
from django.db import models


class UserOTP(models.Model):
    """
    Model for storing OTP (One Time Password) for users.
    This model is used to verify the user's identity during the authentication process.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"