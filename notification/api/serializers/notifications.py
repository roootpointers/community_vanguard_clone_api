from rest_framework import serializers
from django.contrib.auth import get_user_model
from notification.models import Notification

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notification model with sender information
    """
    sender_info = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'uuid',
            'notification_type',
            'title',
            'message',
            'sender_info',
            'related_object_id',
            'related_object_type',
            'is_read',
            'created_at',
            'read_at',
            'time_since_created',
            'metadata'
        ]
        read_only_fields = [
            'uuid',
            'created_at',
            'read_at',
            'sender_info',
            'time_since_created'
        ]
    
    def get_sender_info(self, obj):
        """Get sender information if available (safe against missing profile/photo)."""
        if not obj.sender:
            return None
        sender = obj.sender
        profile_photo = None
        # Try profile relation first; fall back to a direct attribute if ever present
        if hasattr(sender, 'profile') and getattr(sender.profile, 'profile_photo', None):
            profile_photo = sender.profile.profile_photo
        elif hasattr(sender, 'profile_photo'):
            profile_photo = getattr(sender, 'profile_photo')
        return {
            'uuid': sender.uuid,
            'username': sender.username,
            'first_name': sender.first_name,
            'last_name': sender.last_name,
            'profile_photo': profile_photo,
        }
    
    def get_time_since_created(self, obj):
        """
        Get human-readable time since notification was created
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            return f"{diff.days}d ago"
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f"{weeks}w ago"
        else:
            months = diff.days // 30
            return f"{months}mo ago"


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for notification lists
    """
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_profile_photo = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'uuid',
            'notification_type',
            'title',
            'message',
            'sender_username',
            'sender_profile_photo',
            'is_read',
            'metadata',
            'created_at',
            'time_since_created'
        ]
    
    def get_time_since_created(self, obj):
        """
        Get human-readable time since notification was created
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            return f"{diff.days}d ago"
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f"{weeks}w ago"
        else:
            months = diff.days // 30
            return f"{months}mo ago"

    def get_sender_profile_photo(self, obj):
        """Safe accessor for sender profile photo (supports profile relation)."""
        sender = getattr(obj, 'sender', None)
        if not sender:
            return None
        if hasattr(sender, 'profile') and getattr(sender.profile, 'profile_photo', None):
            return sender.profile.profile_photo
        if hasattr(sender, 'profile_photo'):
            return getattr(sender, 'profile_photo')
        return None


class MarkAsReadSerializer(serializers.Serializer):
    """
    Serializer for marking notifications as read
    """
    notification_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of notification UUIDs to mark as read"
    )


class NotificationFilterSerializer(serializers.Serializer):
    """
    Serializer for notification filtering
    """
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPES,
        required=False,
        help_text="Filter by notification type"
    )
    is_read = serializers.BooleanField(
        required=False,
        help_text="Filter by read status"
    )
    date_from = serializers.DateTimeField(
        required=False,
        help_text="Filter notifications from this date"
    )
    date_to = serializers.DateTimeField(
        required=False,
        help_text="Filter notifications to this date"
    )


class CreateNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications (admin/system use)
    """
    recipient_uuid = serializers.UUIDField(write_only=True)
    sender_uuid = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Notification
        fields = [
            'recipient_uuid',
            'sender_uuid',
            'notification_type',
            'title',
            'message',
            'related_object_id',
            'related_object_type',
            'metadata'
        ]
    
    def create(self, validated_data):
        recipient_uuid = validated_data.pop('recipient_uuid')
        sender_uuid = validated_data.pop('sender_uuid', None)
        
        # Remove any recipient or sender fields that might be in validated_data
        validated_data.pop('recipient', None)
        validated_data.pop('sender', None)
        
        try:
            recipient = User.objects.get(uuid=recipient_uuid)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "Recipient user not found"})
        
        sender = None
        if sender_uuid:
            try:
                sender = User.objects.get(uuid=sender_uuid)
            except User.DoesNotExist:
                raise serializers.ValidationError({"error": "Sender user not found"})
        
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            **validated_data
        )
        return notification
