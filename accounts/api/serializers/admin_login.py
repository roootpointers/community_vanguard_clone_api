from rest_framework import serializers
from accounts.models.user import User


class AdminLoginSerializer(serializers.Serializer):
    """
    Serializer for admin login endpoint.
    Validates that the user exists, has correct password, and has admin privileges.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Check if email exists
        if not User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({'error': 'Email does not exist.'})

        user = User.objects.get(email__iexact=email)
        
        # Check password is correct
        if not user.check_password(password):
            raise serializers.ValidationError({'error': 'Incorrect password.'})
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError({'error': 'User account is deactivated.'})
        
        # Check if user has admin privileges (staff or superuser)
        if not user.is_staff and not user.is_superuser:
            raise serializers.ValidationError({
                'error': 'Access denied. Admin privileges required.'
            })

        return attrs
