from rest_framework import serializers
from accounts.models.user import User
from accounts.utils import generate_username

class EmailSignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=128,
        label='Password',
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
    account_type = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'confirm_password', 'account_type']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"error": "This email is already registered."})

        if password != confirm_password:
            raise serializers.ValidationError({"error": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        # Generate a unique username
        username = generate_username(
            validated_data['email'],
            validated_data.get('full_name')
        )
        
        user = User.objects.create_user(
            username=username,
            full_name=validated_data['full_name'],
            email=validated_data['email'].lower(),
            password=validated_data['password'],
            account_type=validated_data['account_type']
        )
        return user
    


class SocialSignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    social_id = serializers.CharField(required=True)
    account_type = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'social_id', 'account_type']

    def validate(self, attrs):
        email = attrs.get('email')
        social_id = attrs.get('social_id')

        if User.objects.filter(social_id=social_id).exists():
            raise serializers.ValidationError({"error": "Social ID already exists."})

        if User.objects.filter(email=email.lower()).exists():
            raise serializers.ValidationError({"error": "This email is already registered."})

        return attrs

    def create(self, validated_data):
        # Generate a unique username
        username = generate_username(
            validated_data['email'],
            validated_data.get('full_name')
        )
        
        user = User.objects.create_user(
            username=username,
            full_name=validated_data['full_name'],
            email=validated_data['email'].lower(),
            social_id=validated_data['social_id'],
            account_type=validated_data['account_type']
        )
        return user
    