from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from accounts.models.user import User
from accounts.api.serializers.user import UserSerializer
from django.shortcuts import get_object_or_404

import logging
logger = logging.getLogger(__name__)


class BannedUsersPagination(PageNumberPagination):
    """Pagination for banned users list"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class BanUserViewSet(viewsets.ViewSet):
    """
    ViewSet for banning and unbanning users.
    Only accessible by admin users (is_staff=True or is_superuser=True).
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['post'], url_path='ban')
    def ban_user(self, request):
        """
        Ban a user by UUID.
        Request body: {"user_uuid": "uuid-string"}
        """
        try:
            user_uuid = request.data.get('user_uuid')
            
            if not user_uuid:
                return Response({
                    'success': False,
                    'message': 'user_uuid is required.',
                    'errors': {'user_uuid': ['This field is required.']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, uuid=user_uuid)
            
            # Prevent banning superusers
            if user.is_superuser:
                return Response({
                    'success': False,
                    'message': 'Cannot ban superuser accounts.',
                    'errors': {'user': ['Superusers cannot be banned.']}
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if user is already banned
            if user.is_banned:
                return Response({
                    'success': False,
                    'message': 'User is already banned.',
                    'data': UserSerializer(user).data
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_banned = True
            user.save()
            
            logger.info(f"User {user.email} was banned by admin {request.user.email}")
            
            return Response({
                'success': True,
                'message': f'User {user.email} has been banned successfully.',
                'data': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error banning user: {str(e)}")
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='unban')
    def unban_user(self, request):
        """
        Unban a user by UUID.
        Request body: {"user_uuid": "uuid-string"}
        """
        try:
            user_uuid = request.data.get('user_uuid')
            
            if not user_uuid:
                return Response({
                    'success': False,
                    'message': 'user_uuid is required.',
                    'errors': {'user_uuid': ['This field is required.']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, uuid=user_uuid)
            
            # Check if user is not banned
            if not user.is_banned:
                return Response({
                    'success': False,
                    'message': 'User is not banned.',
                    'data': UserSerializer(user).data
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_banned = False
            user.save()
            
            logger.info(f"User {user.email} was unbanned by admin {request.user.email}")
            
            return Response({
                'success': True,
                'message': f'User {user.email} has been unbanned successfully.',
                'data': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error unbanning user: {str(e)}")
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='banned-users')
    def list_banned_users(self, request):
        """
        Get paginated list of all banned users.
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 10, max: 100)
        """
        try:
            banned_users = User.objects.filter(is_banned=True, is_superuser=False).order_by('-updated_at')
            
            # Apply pagination
            paginator = BannedUsersPagination()
            paginated_users = paginator.paginate_queryset(banned_users, request)
            serializer = UserSerializer(paginated_users, many=True)
            
            # Return paginated response
            return paginator.get_paginated_response({
                'success': True,
                'message': 'Banned users retrieved successfully.',
                'count': banned_users.count(),
                'results': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error listing banned users: {str(e)}")
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
