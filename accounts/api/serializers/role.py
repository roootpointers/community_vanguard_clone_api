from rest_framework import serializers
from accounts.models.role import UserRole
from accounts.models.user import User
from datetime import datetime
import json


class CreateUserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and managing user roles.
    Handles validation for vendor and community support provider roles.
    """
    # Read-only fields from related User model
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'uuid',
            'email',
            'full_name',
            'role',
            'business_name',
            'business_ein',
            'business_type',
            'organization_name',
            'organization_mission',
            'tax_document',
            'is_nonprofit_confirmed',
            'is_verified',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'uuid',
            'created_at',
            'updated_at',
        ]
    
    def validate_role(self, value):
        """
        Validate that the role is valid.
        """
        valid_roles = ['customer', 'vendor', 'community_support_provider']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return value
    
    def validate(self, attrs):
        """
        Object-level validation based on role type.
        """
        role = attrs.get('role')
        
        # Vendor-specific validation
        if role == 'vendor':
            # Require business information
            if not attrs.get('business_name'):
                raise serializers.ValidationError({
                    'business_name': 'Business name is required for vendor role.'
                })
        
        # Community Support Provider-specific validation
        elif role == 'community_support_provider':
            # Require organization information
            if not attrs.get('organization_name'):
                raise serializers.ValidationError({
                    'organization_name': 'Organization name is required for community support provider role.'
                })
            
            # Check non-profit confirmation
            if not attrs.get('is_nonprofit_confirmed'):
                raise serializers.ValidationError({
                    'is_nonprofit_confirmed': 'Please confirm that your organization is a registered non-profit.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user role.
        """
        user = self.context['request'].user
        
        # Check if user already has a role entry
        existing_role = UserRole.objects.filter(user=user).first()
        
        if existing_role:
            raise serializers.ValidationError(
                "You already have a role record. Use update endpoint to modify it."
            )
        
        validated_data['user'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update existing user role.
        """
        return super().update(instance, validated_data)


class UserRoleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserRole
        fields = [
            'uuid',
            'role',
            'business_name',
            'business_ein',
            'business_type',
            'organization_name',
            'organization_mission',
            'tax_document',
            'is_nonprofit_confirmed',
            'is_verified',
            'created_at',
            'updated_at',
        ]
