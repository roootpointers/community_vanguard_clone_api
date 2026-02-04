import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from accounts.models.user import User


# Define choices for gender
GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)


class UserProfile(models.Model):
    """
    UserProfile model that extends the User model with additional profile information.
    This model stores detailed information about users after they complete the signup process.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    birth_date = models.DateField(null=True, blank=True)
    profile_photo = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Military Information
    branch = models.CharField(max_length=20, null=True, blank=True)
    rank = models.CharField(max_length=100, null=True, blank=True)
    mos_afsc = models.CharField(max_length=100, null=True, blank=True, help_text="Military Occupational Specialty / Air Force Specialty Code")
    ets = models.CharField(max_length=100, null=True, blank=True, help_text="Expiration of Term of Service")
    family_status = models.CharField(max_length=100, null=True, blank=True, help_text="Family status or dependents information")
    
    # Location & Interests
    location = models.CharField(max_length=255, null=True, blank=True)
    interests = models.ManyToManyField('Interest', related_name='user_profiles', blank=True, help_text="User's interests and hobbies")
    preferred_contribution_path = models.ForeignKey('PreferredContributionPath', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles', help_text="User's preferred contribution path")
    
    # Affiliation & Verification
    affiliation = models.ForeignKey('Affiliation', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles', help_text="User's affiliation")
    id_me_verified = models.BooleanField(default=False)
    
    # Education & Skills
    education = models.CharField(max_length=20, null=True, blank=True)
    degree = models.CharField(max_length=255, null=True, blank=True)
    military_civilian_skills = models.JSONField(default=list, blank=True, help_text="List of skills (e.g., ['Aviation', 'Medical Training', 'Communication'])")
    certifications = models.TextField(null=True, blank=True)
    
    # Profile completion status
    # is_profile_completed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    @property
    def is_document_verified(self):
        """
        Property to check if the profile has approved verification documents.
        Returns True if at least one verification document is approved.
        """
        return hasattr(self, 'verification_documents') and self.verification_documents.filter(status='approved').exists()
    
    def __str__(self):
        return f"{self.user.email} - Profile"
