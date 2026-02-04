"""
Follow serializers for Network app
"""
from rest_framework import serializers
from network.models import Follow
from accounts.models import User
from network.api.serializers.user import UserBasicSerializer


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for Follow model with detailed user information
    """
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)
    follower_uuid = serializers.UUIDField(write_only=True, required=False)
    following_uuid = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Follow
        fields = [
            'uuid',
            'follower',
            'following',
            'follower_uuid',
            'following_uuid',
            'created_at',
        ]
        read_only_fields = ['uuid', 'created_at']
    
    def validate(self, attrs):
        """Validate follow relationship"""
        follower_uuid = attrs.get('follower_uuid')
        following_uuid = attrs.get('following_uuid')
        
        # Get follower from context (usually the authenticated user)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            follower = request.user
        elif follower_uuid:
            try:
                follower = User.objects.get(uuid=follower_uuid)
            except User.DoesNotExist:
                raise serializers.ValidationError({"follower_uuid": "User not found"})
        else:
            raise serializers.ValidationError({"follower_uuid": "Follower is required"})
        
        # Get following user
        if not following_uuid:
            raise serializers.ValidationError({"following_uuid": "Following user is required"})
        
        try:
            following = User.objects.get(uuid=following_uuid)
        except User.DoesNotExist:
            raise serializers.ValidationError({"following_uuid": "User not found"})
        
        # Validate user cannot follow themselves
        if follower == following:
            raise serializers.ValidationError("You cannot follow yourself")
        
        # Check if already following
        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("You are already following this user")
        
        attrs['follower'] = follower
        attrs['following'] = following
        
        return attrs
    
    def create(self, validated_data):
        """Create follow relationship"""
        # Remove UUID fields as we already resolved them
        validated_data.pop('follower_uuid', None)
        validated_data.pop('following_uuid', None)
        
        return Follow.objects.create(**validated_data)


class FollowActionSerializer(serializers.Serializer):
    """
    Serializer for follow/unfollow actions
    """
    user_uuid = serializers.UUIDField(required=True, help_text="UUID of user to follow/unfollow")
    
    def validate_user_uuid(self, value):
        """Validate that user exists"""
        try:
            user = User.objects.get(uuid=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        # Check if trying to follow self
        request = self.context.get('request')
        if request and request.user.uuid == value:
            raise serializers.ValidationError("You cannot follow yourself")
        
        return value


class FollowerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing followers with user details
    """
    user = UserBasicSerializer(source='follower', read_only=True)
    is_following_back = serializers.SerializerMethodField()
    
    class Meta:
        model = Follow
        fields = [
            'uuid',
            'user',
            'is_following_back',
            'created_at',
        ]
        read_only_fields = fields
    
    def get_is_following_back(self, obj):
        """Check if the current user is following this follower back"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return Follow.is_following(request.user, obj.follower)
        return False


class FollowingListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing following users with user details
    """
    user = UserBasicSerializer(source='following', read_only=True)
    is_follower = serializers.SerializerMethodField()
    
    class Meta:
        model = Follow
        fields = [
            'uuid',
            'user',
            'is_follower',
            'created_at',
        ]
        read_only_fields = ['uuid', 'created_at']
    
    def get_is_follower(self, obj):
        """Check if the current user is following this user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return Follow.is_following(request.user, obj.following)
        return False
