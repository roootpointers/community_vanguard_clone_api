from rest_framework import serializers
from accounts.models.user import User

class ChangePasswordSerializer(serializers.Serializer):
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

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        # check email exists
        if not User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"error": "This email is not registered."})

        if password != confirm_password:
            raise serializers.ValidationError({"error": "Password fields didn't match."})
        return attrs
    

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance