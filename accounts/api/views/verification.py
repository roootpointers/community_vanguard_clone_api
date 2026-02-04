from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from accounts.models.user import User
from accounts.models.verification import UserOTP
from accounts.api.serializers.verification import VerifyOtpSerializer
from accounts.api.serializers.user import UserSerializer
from accounts.api.utils import send_verification_email

class VerificationViewSet(viewsets.GenericViewSet):
    """
    VerificationViewSet is responsible for handling all verification-related operations
    such as sending OTP, verifying OTP, etc.
    """
    permission_classes = [AllowAny]      
    @action(detail=False, methods=['post'], url_path='send-otp-code')
    def send_otp(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            if not email:
                error = {
                    "success": False,
                    "message": "Email is required.",
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
                
            # Delete existing OTPs for this email
            UserOTP.objects.filter(email=email).delete()
            
            # Send verification email
            # send_verification_email(email, 'Your SeizeIT OTP Verification')
            # static OTP for testing purposes
            otp = '123456'
            
            # Save OTP in UserOTP model
            UserOTP.objects.create(email=email, otp=otp)
            
            response = {
                "success": True,
                "message": "OTP sent successfully.",
                "data": {
                    "email": email,
                    "otp": otp # In production, do not return OTP in response
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {
                "success": False,
                "message": "Something went wrong.",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request, *args, **kwargs):
        try:
            serializer = VerifyOtpSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {
                    "success": False,
                    "message": "Something went wrong.",
                    "errors": e.args[0]
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.data['email']
            otp = serializer.data['otp']
            
            # Optionally delete the OTP after verification
            UserOTP.objects.filter(otp=otp, email=email).delete()
            
            response = {
                "success": True,
                "message": "OTP verified successfully.",
                "data": {
                    "email": email
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {
                "success": False,
                "message": "Something went wrong.",
                "errors": e.args[0]
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
