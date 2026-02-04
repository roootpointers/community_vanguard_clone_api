from rest_framework import serializers
from accounts.models.profile import UserProfile
from accounts.models.user import User
from accounts.models.role import UserRole
from accounts.models.interest import Interest
from accounts.models.preferred_contribution_path import PreferredContributionPath
from accounts.models.affiliation import Affiliation
from accounts.models.verification_document import VerificationDocument
from accounts.api.serializers.role import UserRoleSerializer
from accounts.api.serializers.interest import InterestListSerializer
from accounts.api.serializers.preferred_contribution_path import PreferredContributionPathListSerializer
from accounts.api.serializers.affiliation import AffiliationListSerializer
from accounts.api.serializers.verification_document import VerificationDocumentSerializer
from network.models.follow import Follow
from datetime import date
import json


class CreateUpdateUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    Handles creation and updates of user profiles with comprehensive validation.
    Manages role selection and all profile fields in a single endpoint.
    """
    # Fields from related User model
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', required=False, allow_blank=True)
    role = serializers.SerializerMethodField()
    account_type = serializers.CharField(source='user.account_type', read_only=True)
    social_id = serializers.CharField(source='user.social_id', read_only=True)
    is_profile = serializers.BooleanField(source='user.is_profile', read_only=True)
    is_role = serializers.BooleanField(source='user.is_role', read_only=True)
    
    # Many-to-many field for interests (accepts list of UUIDs for write, returns full objects for read)
    interests = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Interest.objects.all(),
        required=False,
        allow_null=True
    )
    
    # ForeignKey field for preferred contribution path (accepts UUID for write)
    preferred_contribution_path = serializers.PrimaryKeyRelatedField(
        queryset=PreferredContributionPath.objects.all(),
        required=False,
        allow_null=True
    )
    
    # ForeignKey field for affiliation (accepts UUID for write)
    affiliation = serializers.PrimaryKeyRelatedField(
        queryset=Affiliation.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Verification documents field (accepts list of objects with document_url and optional document_type)
    verification_documents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        write_only=True,
        help_text="List of verification documents. Each document should have 'document_url' and optionally 'document_type'"
    )
    
    # Verification fields
    id_me_verified = serializers.BooleanField(read_only=True)
    is_document_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'uuid',
            'email',
            'full_name',
            'role',
            'birth_date',
            'gender',
            'profile_photo',
            'account_type',
            'social_id',
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
            'verification_documents',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'role', 'email', 'id_me_verified']

    
    def validate_birth_date(self, value):
        """
        Validate that birth date is not in the future and user is at least 18 years old.
        """
        if value:
            today = date.today()
            if value > today:
                raise serializers.ValidationError({'error': "Birth date cannot be in the future."})
            
            # Calculate age
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 18:
                raise serializers.ValidationError({'error': "User must be at least 18 years old."})
            
            if age > 120:
                raise serializers.ValidationError({'error': "Invalid birth date."})

        return value
    
    def validate_military_civilian_skills(self, value):
        """
        Validate that military_civilian_skills is a list.
        """
        if value is not None:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({'error': "Invalid JSON format for skills."})
            
            if not isinstance(value, list):
                raise serializers.ValidationError({'error': "Skills must be a list."})

            # Validate each skill is a string
            for skill in value:
                if not isinstance(skill, str):
                    raise serializers.ValidationError({'error': "Each skill must be a string."})

        return value if value else []
    
    # def validate_id_document(self, value):
    #     """
    #     Validate uploaded ID document file size and type.
    #     """
    #     if value:
    #         # Check file size (max 5MB)
    #         max_size = 5 * 1024 * 1024  # 5MB in bytes
    #         if value.size > max_size:
    #             raise serializers.ValidationError({'error': "File size cannot exceed 5MB."})
            
    #         # Validate file extension
    #         allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
    #         ext = value.name.split('.')[-1].lower()
    #         if ext not in allowed_extensions:
    #             raise serializers.ValidationError(
    #                 f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
    #             )
        
    #     return value
    
    def validate_location(self, value):
        """
        Validate location field is not empty if provided.
        """
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError({'error': "Location cannot be empty."})
        return value
    
    def validate(self, attrs):
        """
        Object-level validation.
        """
        # Handle both 'interest' and 'interests' field names for backward compatibility
        if 'interest' in self.initial_data and 'interests' not in attrs:
            attrs['interests'] = self.initial_data.get('interest')
        
        # If degree is provided, education should also be provided
        if attrs.get('degree') and not attrs.get('education'):
            if not (self.instance and self.instance.education):
                raise serializers.ValidationError({'error': "Education is required if degree is provided."})
        
        # Validate verification documents if provided
        verification_documents = attrs.get('verification_documents', [])
        if verification_documents:
            for idx, doc in enumerate(verification_documents):
                if not isinstance(doc, dict):
                    raise serializers.ValidationError({
                        'verification_documents': f"Document at index {idx} must be an object with 'document_url' field."
                    })
                if 'document_url' not in doc or not doc.get('document_url'):
                    raise serializers.ValidationError({
                        'verification_documents': f"Document at index {idx} must have a 'document_url' field."
                    })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user profile.
        """
        user = self.context['request'].user
        
        # Check if profile already exists
        if hasattr(user, 'profile'):
            raise serializers.ValidationError({'error': "Profile already exists for this user."})
        
        # Extract many-to-many data and verification documents
        interests_data = validated_data.pop('interests', [])
        verification_documents_data = validated_data.pop('verification_documents', [])
        
        validated_data['user'] = user
        instance = super().create(validated_data)
        
        # Set many-to-many relationships
        if interests_data:
            instance.interests.set(interests_data)
        
        # Create verification documents
        if verification_documents_data:
            for doc_data in verification_documents_data:
                VerificationDocument.objects.create(
                    profile=instance,
                    document_url=doc_data.get('document_url'),
                    document_type=doc_data.get('document_type', '')
                )
        
        return instance
    
    def update(self, instance, validated_data):
        """
        Update existing user profile.
        Handles updating both profile fields and related User model fields.
        """
        # Extract user-related data if present
        user_data = validated_data.pop('user', {})
        
        # Extract many-to-many data and verification documents
        interests_data = validated_data.pop('interests', None)
        verification_documents_data = validated_data.pop('verification_documents', None)
        
        # Update User model fields if provided
        if user_data:
            user = instance.user
            if 'full_name' in user_data:
                user.full_name = user_data['full_name']
                user.save(update_fields=['full_name'])
        
        # Update profile fields
        instance = super().update(instance, validated_data)
        
        # Update many-to-many relationships
        if interests_data is not None:
            instance.interests.set(interests_data)
        
        # Handle verification documents
        # If verification_documents is provided, replace all existing documents
        if verification_documents_data is not None:
            # Delete existing verification documents
            instance.verification_documents.all().delete()
            # Create new verification documents
            for doc_data in verification_documents_data:
                VerificationDocument.objects.create(
                    profile=instance,
                    document_url=doc_data.get('document_url'),
                    document_type=doc_data.get('document_type', '')
                )
        
        return instance
    
    def get_role(self, obj):
        """
        Retrieve the user's role if it exists.
        """
        try:
            role_obj = UserRole.objects.get(user=obj.user)
            serializer = UserRoleSerializer(role_obj)
            return serializer.data
        except UserRole.DoesNotExist:
            return None
    
    def get_is_document_verified(self, obj):
        """
        Check if the profile has verification documents uploaded.
        """
        return obj.is_document_verified
    
    def to_representation(self, instance):
        """
        Customize the representation to include nested serializers for related fields.
        """
        representation = super().to_representation(instance)
        
        # Serialize interests as full objects instead of UUIDs
        if instance.interests.exists():
            representation['interests'] = InterestListSerializer(
                instance.interests.all(), many=True
            ).data
        else:
            representation['interests'] = []
        
        # Serialize preferred_contribution_path as full object
        if instance.preferred_contribution_path:
            representation['preferred_contribution_path'] = PreferredContributionPathListSerializer(
                instance.preferred_contribution_path
            ).data
        
        # Serialize affiliation as full object
        if instance.affiliation:
            representation['affiliation'] = AffiliationListSerializer(
                instance.affiliation
            ).data
        
        # Serialize verification documents
        if hasattr(instance, 'verification_documents'):
            representation['verification_documents'] = VerificationDocumentSerializer(
                instance.verification_documents.all(), many=True
            ).data
        else:
            representation['verification_documents'] = []
        
        return representation


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing profiles.
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    account_type = serializers.CharField(source='user.account_type', read_only=True)
    social_id = serializers.CharField(source='user.social_id', read_only=True)
    is_profile = serializers.BooleanField(source='user.is_profile', read_only=True)
    is_role = serializers.BooleanField(source='user.is_role', read_only=True)
    role = serializers.SerializerMethodField()
    profile_stats = serializers.SerializerMethodField()
    interests = InterestListSerializer(many=True, read_only=True)
    preferred_contribution_path = PreferredContributionPathListSerializer(read_only=True)
    affiliation = AffiliationListSerializer(read_only=True)
    verification_documents = VerificationDocumentSerializer(many=True, read_only=True)
    id_me_verified = serializers.BooleanField(read_only=True)
    is_document_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'uuid',
            'email',
            'full_name',
            'account_type',
            'role',
            'birth_date',
            'gender',
            'profile_photo',
            'social_id',
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
            'verification_documents',
            'profile_stats',
            'created_at',
            'updated_at',
        ]

    def get_role(self, obj):
        """
        Retrieve the user's role if it exists.
        """
        try:
            role_obj = UserRole.objects.get(user=obj.user)
            serializer = UserRoleSerializer(role_obj)
            return serializer.data
        except UserRole.DoesNotExist:
            return None
    
    def get_profile_stats(self, obj):
        """
        Get profile statistics including intel count, exchange count, followers count, and following count.
        """
        request = self.context.get('request')
        stats = {
            'intel_count': obj.user.intels.count(),
            'exchange_count': obj.user.exchanges.count(),
            'followers_count': Follow.get_followers_count(obj.user),
            'following_count': Follow.get_following_count(obj.user),
            'is_following': False,
            'is_follower': False,
        }
        
        # Check relationship with requesting user
        if request and request.user.is_authenticated and request.user != obj.user:
            stats['is_following'] = Follow.is_following(request.user, obj.user)
            stats['is_follower'] = Follow.is_following(obj.user, request.user)
        
        return stats
    
    def get_is_document_verified(self, obj):
        """
        Check if the profile has verification documents uploaded.
        """
        return obj.is_document_verified