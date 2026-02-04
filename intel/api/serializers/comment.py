from rest_framework import serializers
from intel.models import IntelComment, CommentLike


class CommentLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for comment likes.
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = CommentLike
        fields = ['uuid', 'user', 'comment', 'created_at']
        read_only_fields = ['uuid', 'user', 'created_at']
    
    def get_user(self, obj):
        """Return basic user info."""
        return {
            'uuid': str(obj.user.uuid),
            'full_name': obj.user.full_name,
            'email': obj.user.email,
        }


class IntelCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving comments.
    """
    user = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = IntelComment
        fields = [
            'uuid',
            'user',
            'intel',
            'parent_comment',
            'content',
            'likes_count',
            'replies_count',
            'is_liked_by_user',
            'replies',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'user', 'likes_count', 'replies_count', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        """Return basic user info."""
        return {
            'uuid': str(obj.user.uuid),
            'full_name': obj.user.full_name,
            'email': obj.user.email,
            'profile_photo': obj.user.profile.profile_photo if hasattr(obj.user, 'profile') else None,
        }
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_replies(self, obj):
        """Get replies for this comment (only if it's a parent comment)."""
        if obj.is_reply():
            return None
        
        # Get replies for this comment
        replies = obj.replies.all()[:5]  # Limit to 5 replies initially
        return IntelCommentListSerializer(replies, many=True, context=self.context).data
    
    def validate(self, attrs):
        """Validate comment data."""
        parent_comment = attrs.get('parent_comment')
        intel = attrs.get('intel')
        
        # If parent_comment is provided, ensure it belongs to the same intel
        if parent_comment and parent_comment.intel != intel:
            raise serializers.ValidationError({
                'parent_comment': 'Parent comment must belong to the same intel post.'
            })
        
        # Prevent deeply nested comments (only 1 level of replies allowed)
        if parent_comment and parent_comment.is_reply():
            raise serializers.ValidationError({
                'parent_comment': 'Cannot reply to a reply. Please reply to the parent comment instead.'
            })
        
        return attrs


class IntelCommentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing comments.
    """
    user = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = IntelComment
        fields = [
            'uuid',
            'user',
            'content',
            'likes_count',
            'replies_count',
            'is_liked_by_user',
            'created_at',
            'updated_at',
        ]
    
    def get_user(self, obj):
        """Return basic user info."""
        return {
            'uuid': str(obj.user.uuid),
            'full_name': obj.user.full_name,
            'email': obj.user.email,
            'profile_photo': obj.user.profile.profile_photo if hasattr(obj.user, 'profile') else None,
        }
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
