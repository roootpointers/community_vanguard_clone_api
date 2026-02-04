from rest_framework import serializers
from blog.models import Blog


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for Blog model with full details"""
    
    excerpt = serializers.ReadOnlyField()
    
    class Meta:
        model = Blog
        fields = [
            'uuid',
            'title',
            'slug',
            'content',
            'excerpt',
            'author',
            'status',
            'featured_image',
            'is_mission_genesis',
            'views_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'slug', 'excerpt', 'views_count', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Validate that title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_content(self, value):
        """Validate that content is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()
    
    def validate_author(self, value):
        """Validate that author is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Author cannot be empty.")
        return value.strip()


class BlogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing blogs"""
    
    excerpt = serializers.ReadOnlyField()
    
    class Meta:
        model = Blog
        fields = [
            'uuid',
            'title',
            'excerpt',
            'author',
            'status',
            'is_mission_genesis',
            'views_count',
            'created_at',
        ]
        read_only_fields = fields


class UserBlogListSerializer(serializers.ModelSerializer):
    """Serializer for user-side blog listing with full content"""
    
    class Meta:
        model = Blog
        fields = [
            'uuid',
            'title',
            'content',
            'author',
            'status',
            'featured_image',
            'is_mission_genesis',
            'views_count',
            'created_at',
        ]
        read_only_fields = fields
