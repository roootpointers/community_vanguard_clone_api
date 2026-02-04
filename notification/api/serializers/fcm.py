from rest_framework import serializers
from fcm_django.models import FCMDevice
from notification.models import FCMDeviceCustom, NotificationTemplate, NotificationLog


class FCMDeviceRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for FCM device registration
    """
    registration_id = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=['ios', 'android', 'web'], required=True)
    device_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    class Meta:
        model = FCMDeviceCustom
        fields = [
            'registration_id', 'type', 'device_name', 'device_id'
        ]
        extra_kwargs = {
            'registration_id': {'required': True},
            'type': {'required': True},
        }

    # def validate(self, attrs):
    #     """
    #     Validate that the registration_id is unique for the user.
    #     """
    #     user = self.context['request'].user
    #     if FCMDeviceCustom.objects.filter(user=user, registration_id=attrs['registration_id']).exists():
    #         raise serializers.ValidationError({"error": "This registration ID is already registered for this user."})
    #     return attrs
    
    def create(self, validated_data):
        """
        Create a new FCM device instance.
        """
        user = self.context['request'].user
        # delete existing device if it exists
        FCMDeviceCustom.objects.filter(user=user).delete()
        FCMDeviceCustom.objects.filter(registration_id=validated_data['registration_id']).delete()
        # Create the new device
        return FCMDeviceCustom.objects.create(user=user, **validated_data)
    

class FCMDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for FCM device details
    """
    
    class Meta:
        model = FCMDeviceCustom
        fields = [
            'uuid', 'registration_id', 'device_id', 'type', 'device_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class FCMDeviceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating FCM device
    """
    
    class Meta:
        model = FCMDeviceCustom
        fields = [
            'registration_id', 'device_id', 'type', 'device_name'
        ]

    
    def validate(self, attrs):
        """
        Validate the FCM device update data.
        """
        user = self.context['request'].user
        if FCMDeviceCustom.objects.filter(user=user, registration_id=attrs['registration_id']).exists():
            raise serializers.ValidationError({"error": "This registration ID is already registered for this user."})
        return attrs

    def update(self, instance, validated_data):
        """
        Update the FCM device instance.
        """
        instance.registration_id = validated_data.get('registration_id', instance.registration_id)
        instance.device_id = validated_data.get('device_id', instance.device_id)
        instance.type = validated_data.get('type', instance.type)
        instance.device_name = validated_data.get('device_name', instance.device_name)
        instance.save()
        return instance


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for notification templates
    """
    
    class Meta:
        model = NotificationTemplate
        fields = '__all__'


class NotificationLogSerializer(serializers.ModelSerializer):
    """
    Serializer for notification logs
    """
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    device_name = serializers.CharField(source='device.device_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'recipient_username', 'device_name', 'template_name',
            'title', 'body', 'data', 'status', 'firebase_message_id',
            'error_message', 'sent_at', 'delivered_at', 'clicked_at',
            'created_at'
        ]
        read_only_fields = '__all__'


class SendNotificationSerializer(serializers.Serializer):
    """
    Serializer for sending custom notifications
    """
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of user IDs to send notification to"
    )
    title = serializers.CharField(max_length=200)
    body = serializers.CharField()
    data = serializers.JSONField(required=False, default=dict)
    icon = serializers.CharField(required=False)
    sound = serializers.CharField(default='default')
    priority = serializers.ChoiceField(choices=['high', 'normal'], default='normal')
    click_action = serializers.CharField(required=False)
    
    def validate_recipient_ids(self, value):
        """Validate recipient IDs"""
        if not value:
            raise serializers.ValidationError("At least one recipient ID is required")
        return value


class BulkNotificationSerializer(serializers.Serializer):
    """
    Serializer for sending bulk notifications
    """
    title = serializers.CharField(max_length=200)
    body = serializers.CharField()
    data = serializers.JSONField(required=False, default=dict)
    icon = serializers.CharField(required=False)
    sound = serializers.CharField(default='default')
    priority = serializers.ChoiceField(choices=['high', 'normal'], default='normal')
    user_filters = serializers.JSONField(
        required=False, 
        help_text="Filters to apply to users (e.g., {'is_active': True})"
    )
    device_types = serializers.ListField(
        child=serializers.ChoiceField(choices=['ios', 'android', 'web']),
        required=False,
        help_text="Send to specific device types only"
    )
