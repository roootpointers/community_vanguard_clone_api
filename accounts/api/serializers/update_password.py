from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UpdatePasswordSerializer(serializers.Serializer):
    """
    Serializer for password update by authenticated user.
    Requires current password verification.
    """
    current_password = serializers.CharField(
        max_length=128,
        label='Current Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )
    new_password = serializers.CharField(
        max_length=128,
        label='New Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )
    confirm_password = serializers.CharField(
        max_length=128,
        label='Confirm Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

    def validate_current_password(self, value):
        """Verify that the current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validate the new password using Django's password validators."""
        user = self.context['request'].user
        try:
            validate_password(value, user=user)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Validate that new password and confirm password match."""
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        current_password = attrs.get('current_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "New password and confirm password do not match."
            })
        
        # Check if new password is same as current password
        if current_password == new_password:
            raise serializers.ValidationError({
                "new_password": "New password must be different from current password."
            })
        
        return attrs
