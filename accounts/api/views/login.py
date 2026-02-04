from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from accounts.api.serializers.register import (EmailSignupSerializer, SocialSignupSerializer)
from accounts.api.serializers.login import EmailLoginSerializer, SocialLoginSerializer
from accounts.api.serializers.user import UserSerializer
from accounts.models.user import User
from accounts.api.permissions import CustomPermission
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

import logging
logger = logging.getLogger(__name__)


class UserLoginViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [CustomPermission]
    http_method_names = ["post"]

    def email_login(self, request, *args, **kwargs):
        try:
            serializer = EmailLoginSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.filter(email__iexact=serializer.validated_data.get('email')).first()
                if not user:
                    logger.error(f"User not found after validation for email: {serializer.validated_data.get('email')}")
                    response = {
                        'success': False,
                        'message': 'User not found.',
                        'errors': {'email': ['User does not exist.']}
                    }
                    return Response(response, status=status.HTTP_404_NOT_FOUND)
                
                # Check if user is banned
                if user.is_banned:
                    logger.warning(f"Banned user attempted login: {user.email}")
                    response = {
                        'success': False,
                        'message': 'Your account has been banned. Please contact support.',
                        'errors': {'account': ['This account is banned.']}
                    }
                    return Response(response, status=status.HTTP_403_FORBIDDEN)
                
                refresh = RefreshToken.for_user(user)
                data = UserSerializer(user).data
                data.update({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                })
                response = {"success": True, 
                            "message": "User Logged in Successfully",
                            "data": data}
                return Response(response, status=status.HTTP_200_OK)
            logger.error(serializer.errors)
            response = {
                'success': False,
                "message": "Something went wrong.",
                'errors': serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            response = {
                'success': False,
                'message': e.message,
                'errors': str(e)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
    def social_login(self, request, *args, **kwargs):
        try:
            serializer = SocialLoginSerializer(data=request.data)
            if serializer.is_valid():
                # Check if user is banned (for existing users)
                social_id = serializer.validated_data.get('social_id')
                user = User.objects.filter(social_id=social_id).first()
                if user and user.is_banned:
                    logger.warning(f"Banned user attempted social login: {user.email}")
                    response = {
                        'success': False,
                        'message': 'Your account has been banned. Please contact support.',
                        'errors': {'account': ['This account is banned.']}
                    }
                    return Response(response, status=status.HTTP_403_FORBIDDEN)
                
                # Get response data from serializer
                response_data = serializer.get_response_data()
                
                # Return appropriate status code based on whether user is new or existing
                if response_data['data'].get('is_new_user'):
                    return Response(response_data, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(response_data, status=status.HTTP_200_OK)
            
            # Handle validation errors
            logger.error(serializer.errors)
            response = {
                'success': False,
                'message': 'Invalid social login credentials.',
                'errors': serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Social login error: {str(e)}")
            response = {
                'success': False,
                'message': 'Something went wrong.',
                'errors': str(e)
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)