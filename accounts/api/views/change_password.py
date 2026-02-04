from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from accounts.api.serializers.change_password import (ChangePasswordSerializer)
from accounts.models.user import User
from accounts.api.permissions import CustomPermission
from django.core.exceptions import ValidationError


import logging
logger = logging.getLogger(__name__)

class ChangePasswordViewSet(viewsets.ModelViewSet):
    """
    ChangePasswordViewSet is a viewset that provides CRUD operations for the User model.
    It allows users to create, retrieve, update, and delete user accounts.
    """
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def change_password(self, request, *args, **kwargs):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.filter(email=serializer.validated_data.get('email')).first()
                user.set_password(serializer.validated_data['password'])
                user.save()
                logger.info(f"Password changed successfully for user: {user.email}")
                response = {
                    'success': True,
                    'message': 'Password changed successfully.',
                    'data': {
                        'username': user.username,
                        'email': user.email
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
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
    