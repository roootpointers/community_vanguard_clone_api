"""
Report serializers for Network app
"""
from rest_framework import serializers
from network.models import Report
from accounts.models import User
from network.api.serializers.user import UserBasicSerializer


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Report model with user information
    """
    reported_user = UserBasicSerializer(read_only=True)
    reported_by = UserBasicSerializer(read_only=True)
    reported_user_uuid = serializers.UUIDField(write_only=True, required=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Report
        fields = [
            'uuid',
            'reported_user',
            'reported_by',
            'reported_user_uuid',
            'reason',
            'reason_display',
            'description',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'uuid',
            'reported_by',
            'status',
            'created_at',
            'updated_at',
            'reason_display',
            'status_display',
        ]

    def validate_reported_user_uuid(self, value):
        """Validate that user exists"""
        try:
            user = User.objects.get(uuid=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value

    def validate(self, attrs):
        """Validate report data"""
        request = self.context.get('request')
        reported_user_uuid = attrs.get('reported_user_uuid')

        # Check if trying to report self
        if request and request.user.uuid == reported_user_uuid:
            raise serializers.ValidationError("You cannot report yourself")

        # Check if already reported this user
        if Report.objects.filter(
            reported_user__uuid=reported_user_uuid,
            reported_by=request.user,
            status__in=['pending', 'reviewed']
        ).exists():
            raise serializers.ValidationError("You have already reported this user")

        return attrs

    def create(self, validated_data):
        """Create report"""
        request = self.context.get('request')
        reported_user_uuid = validated_data.pop('reported_user_uuid')

        try:
            reported_user = User.objects.get(uuid=reported_user_uuid)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        report = Report.objects.create(
            reported_user=reported_user,
            reported_by=request.user,
            **validated_data
        )
        return report


class ReportListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing reports (admin view)
    """
    reported_user = UserBasicSerializer(read_only=True)
    reported_by = UserBasicSerializer(read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Report
        fields = [
            'uuid',
            'reported_user',
            'reported_by',
            'reason',
            'reason_display',
            'description',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ReportStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating report status (admin only)
    """
    status = serializers.ChoiceField(
        choices=['pending', 'resolved', 'dismissed'],
        required=True,
        help_text="New status for the report"
    )
