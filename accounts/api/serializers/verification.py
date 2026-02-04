from rest_framework import serializers
from accounts.models.user import User
from accounts.models.verification import UserOTP
from django.utils import timezone

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        if not UserOTP.objects.filter(otp=otp, email=email).exists():
            raise serializers.ValidationError({'error': 'Invalid OTP, please try again.'})
        user_otp = UserOTP.objects.get(otp=otp, email=email)
        if user_otp.created_at < timezone.now() - timezone.timedelta(minutes=5):
            raise serializers.ValidationError({'error': 'OTP expired, please request a new one.'})
        return attrs