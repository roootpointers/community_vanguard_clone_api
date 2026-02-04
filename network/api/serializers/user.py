"""
User serializer for Network app
"""
from rest_framework import serializers
from accounts.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user information for follower/following lists
    """
    full_name = serializers.CharField(read_only=True)
    profile_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'uuid',
            'username',
            'email',
            'full_name',
            'first_name',
            'last_name',
            'profile_photo',
        ]
        read_only_fields = fields
    
    def get_profile_photo(self, obj):
        """Get profile photo URL"""
        if hasattr(obj, 'profile') and obj.profile.profile_photo:
            return obj.profile.profile_photo
        return None
