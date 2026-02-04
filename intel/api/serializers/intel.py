from rest_framework import serializers
from django.core.validators import URLValidator
from intel.models import Intel, IntelMedia
from accounts.api.serializers.user import UserSerializer
from intel.api.serializers.category import IntelCategoryDetailSerializer


class IntelMediaSerializer(serializers.ModelSerializer):
    """Serializer for Intel media files."""
    
    class Meta:
        model = IntelMedia
        fields = ['uuid', 'file_url', 'file_type', 'created_at']
        read_only_fields = ['uuid', 'created_at']


class IntelSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving Intel posts.
    Category accepts UUID for write and returns full object for read.
    """
    media_urls = serializers.ListField(
        child=serializers.CharField(max_length=500),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Array of media file URLs"
    )
    media_files = IntelMediaSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Intel
        fields = [
            'uuid',
            'user',
            'description',
            'category',
            'location',
            'urgency',
            'status',
            'status_display',
            'rejection_reason',
            'likes_count',
            'comments_count',
            'media_urls',
            'media_files',
            'is_liked_by_user',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'user', 'likes_count', 'comments_count', 'created_at', 'updated_at', 'rejection_reason']
    
    def to_representation(self, instance):
        """Customize representation to return nested category object."""
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = IntelCategoryDetailSerializer(instance.category).data
        return representation
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this intel."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def validate_media_urls(self, value):
        """Validate that all media URLs are valid."""
        validator = URLValidator()
        for url in value:
            try:
                validator(url)
            except Exception:
                raise serializers.ValidationError(f"Invalid URL: {url}")
        return value
    
    def create(self, validated_data):
        """Create Intel post with media files."""
        media_urls = validated_data.pop('media_urls', [])

        # Set default status to 'approved' if not provided
        if 'status' not in validated_data:
            validated_data['status'] = 'approved'
        
        # Create the Intel post
        intel = Intel.objects.create(**validated_data)
        
        # Create IntelMedia entries for each URL
        for url in media_urls:
            # Determine file type based on URL extension
            file_type = 'photo'  # default
            if any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm']):
                file_type = 'video'
            
            IntelMedia.objects.create(
                intel=intel,
                file_url=url,
                file_type=file_type
            )
        return intel
    
    def update(self, instance, validated_data):
        """Update Intel post with media files."""
        media_urls = validated_data.pop('media_urls', None)
        
        # Update the Intel post fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If media_urls are provided, replace all media files
        if media_urls is not None:
            # Delete all existing media files for this intel
            instance.media_files.all().delete()
            
            # Create new IntelMedia entries for each URL
            for url in media_urls:
                # Determine file type based on URL extension
                file_type = 'photo'  # default
                if any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm']):
                    file_type = 'video'
                
                IntelMedia.objects.create(
                    intel=instance,
                    file_url=url,
                    file_type=file_type
                )
        
        return instance


class IntelListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing Intel posts.
    """
    user = UserSerializer(read_only=True)
    media_files = IntelMediaSerializer(many=True, read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Intel
        fields = [
            'uuid',
            'user',
            'description',
            'category',
            'location',
            'urgency',
            'status',
            'status_display',
            'rejection_reason',
            'likes_count',
            'comments_count',
            'media_files',
            'is_liked_by_user',
            'created_at',
            'updated_at',
        ]
    
    def to_representation(self, instance):
        """Customize representation to return nested category object."""
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = IntelCategoryDetailSerializer(instance.category).data
        return representation
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this intel."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

