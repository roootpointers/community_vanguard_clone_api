from rest_framework import serializers
from accounts.models.user import User
from accounts.models.profile import UserProfile
from accounts.models.role import UserRole
from accounts.models.interest import Interest
from accounts.api.serializers.role import UserRoleSerializer
from accounts.api.serializers.interest import InterestListSerializer
from accounts.api.serializers.preferred_contribution_path import PreferredContributionPathListSerializer
from accounts.api.serializers.affiliation import AffiliationListSerializer
from network.models.follow import Follow


class UserSerializer(serializers.ModelSerializer):
    # Profile fields
    birth_date = serializers.DateField(source='profile.birth_date', read_only=True, allow_null=True)
    gender = serializers.CharField(source='profile.gender', read_only=True, allow_null=True)
    profile_photo = serializers.CharField(source='profile.profile_photo', read_only=True, allow_null=True)
    branch = serializers.CharField(source='profile.branch', read_only=True, allow_null=True)
    rank = serializers.CharField(source='profile.rank', read_only=True, allow_null=True)
    mos_afsc = serializers.CharField(source='profile.mos_afsc', read_only=True, allow_null=True)
    location = serializers.CharField(source='profile.location', read_only=True, allow_null=True)
    interests = serializers.SerializerMethodField()
    preferred_contribution_path = serializers.SerializerMethodField()
    affiliation = serializers.SerializerMethodField()
    id_me_verified = serializers.BooleanField(source='profile.id_me_verified', read_only=True, default=False)
    is_document_verified = serializers.SerializerMethodField()
    education = serializers.CharField(source='profile.education', read_only=True, allow_null=True)
    degree = serializers.CharField(source='profile.degree', read_only=True, allow_null=True)
    military_civilian_skills = serializers.JSONField(source='profile.military_civilian_skills', read_only=True, allow_null=True)
    certifications = serializers.CharField(source='profile.certifications', read_only=True, allow_null=True)
    ets = serializers.CharField(source='profile.ets', read_only=True, allow_null=True)
    family_status = serializers.CharField(source='profile.family_status', read_only=True, allow_null=True)
    role = serializers.SerializerMethodField()
    profile_stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'uuid',
            'email',
            'social_id',
            'full_name',
            'role',
            'birth_date',
            'gender',
            'profile_photo',
            'account_type',
            'is_profile',
            'is_role',
            'branch',
            'rank',
            'mos_afsc',
            'location',
            'interests',
            'preferred_contribution_path',
            'affiliation',
            'id_me_verified',
            'is_document_verified',
            'education',
            'degree',
            'military_civilian_skills',
            'certifications',
            'ets',
            'family_status',
            'profile_stats',
            'is_banned',
            'created_at',
            'updated_at',
        ]

    def get_role(self, obj):
        """
        Retrieve the user's role if it exists.
        """
        try:
            role_obj = UserRole.objects.get(user=obj)
            serializer = UserRoleSerializer(role_obj)
            return serializer.data
        except UserRole.DoesNotExist:
            return None
    
    def get_interests(self, obj):
        """
        Retrieve the user's interests if profile exists.
        """
        if hasattr(obj, 'profile'):
            interests = obj.profile.interests.all()
            return InterestListSerializer(interests, many=True).data
        return []
    
    def get_preferred_contribution_path(self, obj):
        """
        Retrieve the user's preferred contribution path if profile exists.
        """
        if hasattr(obj, 'profile') and obj.profile.preferred_contribution_path:
            return PreferredContributionPathListSerializer(obj.profile.preferred_contribution_path).data
        return None
    
    def get_affiliation(self, obj):
        """
        Retrieve the user's affiliation if profile exists.
        """
        if hasattr(obj, 'profile') and obj.profile.affiliation:
            return AffiliationListSerializer(obj.profile.affiliation).data
        return None
    
    def get_is_document_verified(self, obj):
        """
        Check if the profile has verification documents uploaded.
        """
        if hasattr(obj, 'profile'):
            return obj.profile.is_document_verified
        return False

    def get_profile_stats(self, obj):
        """
        Retrieve profile statistics such as counts of intel, exchanges, followers, and following.
        """
        request = self.context.get('request')
        stats = {
            'intel_count': obj.intels.count(),
            'exchange_count': obj.exchanges.count(),
            'followers_count': Follow.get_followers_count(obj),
            'following_count': Follow.get_following_count(obj),
            'is_following': False,
            'is_follower': False,
        }
        
        # Check relationship with requesting user
        if request and request.user.is_authenticated and request.user != obj:
            stats['is_following'] = Follow.is_following(request.user, obj)
            stats['is_follower'] = Follow.is_following(obj, request.user)
        
        return stats

    def to_representation(self, instance):
        """
        Customize representation to handle missing profile gracefully.
        """
        representation = super().to_representation(instance)
        
        # If profile doesn't exist, set profile fields to None
        if not hasattr(instance, 'profile'):
            profile_fields = [
                'birth_date', 'gender', 'profile_photo', 'branch', 'rank', 
                'mos_afsc', 'location', 'preferred_contribution_path',
                'affiliation', 'education', 'degree', 'military_civilian_skills',
                'certifications', 'ets', 'family_status'
            ]
            for field in profile_fields:
                representation[field] = None
            representation['id_me_verified'] = False
            representation['is_document_verified'] = False
            representation['interests'] = []
        
        # Add created_at and updated_at from profile if exists
        try:
            representation['created_at'] = instance.profile.created_at
            representation['updated_at'] = instance.profile.updated_at
        except (UserProfile.DoesNotExist, AttributeError):
            representation['created_at'] = instance.created_at
            representation['updated_at'] = instance.updated_at
        
        return representation
