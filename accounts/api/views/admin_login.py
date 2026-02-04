from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from accounts.api.serializers.admin_login import AdminLoginSerializer
from accounts.api.serializers.user import UserSerializer
from accounts.models.user import User
from accounts.api.permissions import CustomPermission
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

import logging
logger = logging.getLogger(__name__)


class AdminLoginViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admin login functionality.
    Only users with is_staff=True or is_superuser=True can login through this endpoint.
    """
    queryset = User.objects.all()
    permission_classes = [CustomPermission]
    http_method_names = ["post"]

    def admin_login(self, request, *args, **kwargs):
        try:
            serializer = AdminLoginSerializer(data=request.data)
            
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
                    logger.warning(f"Banned admin attempted login: {user.email}")
                    response = {
                        'success': False,
                        'message': 'Your account has been banned. Please contact support.',
                        'errors': {'account': ['This account is banned.']}
                    }
                    return Response(response, status=status.HTTP_403_FORBIDDEN)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Serialize user data
                data = UserSerializer(user).data
                data.update({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                })
                
                logger.info(f"Admin login successful for: {user.email}")
                
                response = {
                    "success": True, 
                    "message": "Admin logged in successfully",
                    "data": data
                }
                return Response(response, status=status.HTTP_200_OK)
            
            # Handle validation errors
            logger.error(f"Admin login validation errors: {serializer.errors}")
            
            # Check if it's an admin privilege error
            if 'error' in serializer.errors and 'Admin privileges required' in str(serializer.errors):
                response = {
                    'success': False,
                    "message": "Access denied. Admin privileges required.",
                    'errors': serializer.errors
                }
                return Response(response, status=status.HTTP_403_FORBIDDEN)
            
            response = {
                'success': False,
                "message": "Invalid credentials.",
                'errors': serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except ValidationError as e:
            logger.error(f"Admin login validation error: {e}")
            response = {
                'success': False,
                'message': str(e),
                'errors': str(e)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Admin login error: {str(e)}", exc_info=True)
            response = {
                'success': False,
                'message': 'Something went wrong.',
                'errors': str(e)
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
