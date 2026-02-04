from rest_framework import serializers
from accounts.models.user import User
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.api.serializers.user import UserSerializer


class EmailLoginSerializer(serializers.Serializer):
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

        # check email exists
        if not User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({'error': 'Email does not exist.'})

        user = User.objects.get(email__iexact=email)
        # check password is correct
        if not user.check_password(password):
            raise serializers.ValidationError({'error': 'Incorrect password.'})
        
        # if user is inactive
        if not user.is_active:
            raise serializers.ValidationError({'error': 'User account is deactivated.'})

        return attrs


class SocialLoginSerializer(serializers.Serializer):
    social_id = serializers.CharField(required=True, max_length=255)
    account_type = serializers.CharField(required=True)

    def validate_account_type(self, value):
        valid_account_types = ['google', 'apple']
        if value not in valid_account_types:
            raise serializers.ValidationError({'error': f"Account type must be one of {valid_account_types}."})
        return value

    def validate_social_id(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError({'error': "Social ID cannot be empty."})
        return value.strip()

    def validate(self, attrs):
        social_id = attrs.get('social_id')
        account_type = attrs.get('account_type')

        # Check if user exists with the provided social credentials
        user = User.objects.filter(
            social_id=social_id, 
            account_type=account_type
        ).first()

        if not user:
            # Return special response for new users
            attrs['is_new_user'] = True
            attrs['user'] = None
            return attrs

        # Check if user account is active
        if not user.is_active:
            raise serializers.ValidationError({
                'error': ['User account is deactivated.']
            })

        # Check if user is not deleted
        # if user.is_deleted:
        #     raise serializers.ValidationError({
        #         'error': ['User account has been deleted.']
        #     })

        # Store user in validated data for easy access
        attrs['user'] = user
        attrs['is_new_user'] = False
        
        return attrs

    def get_response_data(self):
        """
        Generate response data with tokens and user information.
        """
        if self.validated_data.get('is_new_user'):
            return {
                'success': True,
                'message': 'User not found for provided social credentials. Please signup.',
                'data': {
                    'is_new_user': True,
                }
            }

        user = self.validated_data.get('user')
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Serialize user data
        user_data = UserSerializer(user).data
        user_data.update({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'is_new_user': False
        })

        return {
            'success': True,
            'message': 'User logged in successfully.',
            'data': user_data
        }