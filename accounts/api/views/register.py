from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from accounts.api.serializers.register import (EmailSignupSerializer, SocialSignupSerializer)
from accounts.api.serializers.user import UserSerializer
from accounts.models.user import User
from accounts.api.permissions import CustomPermission
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

import logging
logger = logging.getLogger(__name__)

class UserRegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [CustomPermission]
    http_method_names = ["post"]

    def email_signup(self, request, *args, **kwargs):
        try:
            serializer = EmailSignupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User signed up successfully: {serializer.instance.email}")
                
                # Generate JWT tokens for the newly created user
                refresh = RefreshToken.for_user(serializer.instance)
                user_serializer = UserSerializer(serializer.instance)
                
                # Add tokens to the response data
                data = user_serializer.data
                data.update({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                })
                
                response = {
                    'success': True,
                    'message': 'User created successfully.',
                    'data': data
                }
                return Response(response, status=status.HTTP_201_CREATED)
            logger.error(serializer.errors)
            response = {
                'success': False,
                'message': 'Something went wrong.',
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
        

    def social_signup(self, request, *args, **kwargs):
        try:
            serializer = SocialSignupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User signed up successfully: {serializer.instance.email}")
                
                # Generate JWT tokens for the newly created user
                refresh = RefreshToken.for_user(serializer.instance)
                user_serializer = UserSerializer(serializer.instance)
                
                # Add tokens to the response data
                data = user_serializer.data
                data.update({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                })
                
                response = {
                    'success': True,
                    'message': 'User created successfully.',
                    'data': data
                }
                return Response(response, status=status.HTTP_201_CREATED)
            logger.error(serializer.errors)
            response = {
                'success': False,
                'message': 'Something went wrong.',
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