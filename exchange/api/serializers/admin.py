from rest_framework import serializers
from exchange.models import Exchange


class ExchangeApproveSerializer(serializers.Serializer):
    """
    Serializer for approving an exchange application.
    """
    pass  # No additional fields required for approval


class ExchangeRejectSerializer(serializers.Serializer):
    """
    Serializer for rejecting an exchange application.
    Requires a reason for rejection.
    """
    rejection_reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1000,
        help_text="Reason for rejecting the exchange application"
    )

    def validate_rejection_reason(self, value):
        """Validate that rejection reason is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason cannot be empty")
        return value.strip()


class AdminExchangeListSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to list exchange applications with rejection reason.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    seller_type_display = serializers.CharField(source='get_seller_type_display', read_only=True)

    class Meta:
        model = Exchange
        fields = [
            'uuid',
            'user_email',
            'business_name',
            'business_ein',
            'seller_type',
            'seller_type_display',
            'category_name',
            'sub_category_name',
            'id_me_verified',
            'status',
            'status_display',
            'rejection_reason',
            'phone',
            'email',
            'website',
            'address',
            'created_at',
            'updated_at',
        ]
