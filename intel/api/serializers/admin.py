from rest_framework import serializers
from intel.models import Intel


class IntelApproveSerializer(serializers.Serializer):
    """
    Serializer for approving an intel post.
    """
    pass  # No additional fields required for approval


class IntelRejectSerializer(serializers.Serializer):
    """
    Serializer for rejecting an intel post.
    Requires a reason for rejection.
    """
    rejection_reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1000,
        help_text="Reason for rejecting the intel post"
    )

    def validate_rejection_reason(self, value):
        """Validate that rejection reason is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason cannot be empty")
        return value.strip()


class AdminIntelListSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to list intel posts with rejection reason.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Intel
        fields = [
            'uuid',
            'user_email',
            'user_full_name',
            'description',
            'category_name',
            'location',
            'urgency',
            'status',
            'status_display',
            'rejection_reason',
            'likes_count',
            'comments_count',
            'created_at',
            'updated_at',
        ]
