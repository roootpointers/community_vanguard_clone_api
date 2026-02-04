"""
Follow ViewSet for Network app
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from network.models import Follow
from network.api.serializers import (
    FollowSerializer,
    FollowActionSerializer,
    FollowerListSerializer,
    FollowingListSerializer,
    UserNetworkStatsSerializer,
    UserBasicSerializer
)
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class NetworkPagination(PageNumberPagination):
    """Custom pagination for network lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FollowViewSet(viewsets.ViewSet):
    """
    ViewSet for managing follow relationships
    
    Endpoints:
    - POST /api/network/follow/ - Follow a user
    - POST /api/network/unfollow/ - Unfollow a user
    - GET /api/network/followers/ - Get current user's followers
    - GET /api/network/following/ - Get current user's following
    - GET /api/network/followers/{user_uuid}/ - Get specific user's followers
    - GET /api/network/following/{user_uuid}/ - Get specific user's following
    - GET /api/network/mutual-followers/ - Get mutual followers
    - GET /api/network/stats/ - Get network statistics
    - GET /api/network/stats/{user_uuid}/ - Get specific user's network stats
    - POST /api/network/toggle-follow/ - Toggle follow/unfollow
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NetworkPagination
    
    @action(detail=False, methods=['post'], url_path='follow')
    def follow_user(self, request):
        """
        Follow a user
        
        Request body:
        {
            "user_uuid": "uuid-of-user-to-follow"
        }
        """
        try:
            serializer = FollowActionSerializer(data=request.data, context={'request': request})
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Validation error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_uuid = serializer.validated_data['user_uuid']
            user_to_follow = get_object_or_404(User, uuid=user_uuid)
            
            # Check if already following
            if Follow.is_following(request.user, user_to_follow):
                return Response({
                    'success': False,
                    'message': 'You are already following this user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create follow relationship
            follow = Follow.objects.create(
                follower=request.user,
                following=user_to_follow
            )
            
            logger.info(f"User {request.user.username} followed {user_to_follow.username}")
            
            return Response({
                'success': True,
                'message': f'You are now following {user_to_follow.username}',
                'data': FollowSerializer(follow, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error following user: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to follow user',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='unfollow')
    def unfollow_user(self, request):
        """
        Unfollow a user
        
        Request body:
        {
            "user_uuid": "uuid-of-user-to-unfollow"
        }
        """
        try:
            serializer = FollowActionSerializer(data=request.data, context={'request': request})
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Validation error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_uuid = serializer.validated_data['user_uuid']
            user_to_unfollow = get_object_or_404(User, uuid=user_uuid)
            
            # Check if actually following
            follow = Follow.objects.filter(
                follower=request.user,
                following=user_to_unfollow
            ).first()
            
            if not follow:
                return Response({
                    'success': False,
                    'message': 'You are not following this user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete follow relationship
            follow.delete()
            
            logger.info(f"User {request.user.username} unfollowed {user_to_unfollow.username}")
            
            return Response({
                'success': True,
                'message': f'You have unfollowed {user_to_unfollow.username}'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error unfollowing user: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to unfollow user',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='toggle-follow')
    def toggle_follow(self, request):
        """
        Toggle follow/unfollow for a user
        If following -> unfollow
        If not following -> follow
        
        Request body:
        {
            "user_uuid": "uuid-of-user"
        }
        """
        try:
            serializer = FollowActionSerializer(data=request.data, context={'request': request})
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Validation error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_uuid = serializer.validated_data['user_uuid']
            target_user = get_object_or_404(User, uuid=user_uuid)
            
            # Check if following
            follow = Follow.objects.filter(
                follower=request.user,
                following=target_user
            ).first()
            
            if follow:
                # Unfollow
                follow.delete()
                action_taken = 'unfollowed'
                is_following = False
                logger.info(f"User {request.user.username} unfollowed {target_user.username}")
            else:
                # Follow
                Follow.objects.create(
                    follower=request.user,
                    following=target_user
                )
                action_taken = 'followed'
                is_following = True
                logger.info(f"User {request.user.username} followed {target_user.username}")
            
            return Response({
                'success': True,
                'message': f'You have {action_taken} {target_user.username}',
                'data': {
                    'is_following': is_following,
                    'action': action_taken
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error toggling follow: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to toggle follow',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='followers')
    def list_followers(self, request):
        """
        Get list of current user's followers
        Query params: page, page_size
        """
        try:
            queryset = Follow.objects.filter(following=request.user).select_related('follower')
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = FollowerListSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Followers retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = FollowerListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': 'Followers retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing followers: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve followers',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='following')
    def list_following(self, request):
        """
        Get list of users current user is following
        Query params: page, page_size
        """
        try:
            queryset = Follow.objects.filter(follower=request.user).select_related('following')
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = FollowingListSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Following list retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = FollowingListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': 'Following list retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing following: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve following list',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='followers')
    def user_followers(self, request, pk=None):
        """
        Get list of specific user's followers
        URL: /api/network/{user_uuid}/followers/
        """
        try:
            user = get_object_or_404(User, uuid=pk)
            queryset = Follow.objects.filter(following=user).select_related('follower')
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = FollowerListSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': f'Followers of {user.username} retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = FollowerListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': f'Followers of {user.username} retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing user followers: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve followers',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='following')
    def user_following(self, request, pk=None):
        """
        Get list of users that specific user is following
        URL: /api/network/{user_uuid}/following/
        """
        try:
            user = get_object_or_404(User, uuid=pk)
            queryset = Follow.objects.filter(follower=user).select_related('following')
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = FollowingListSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': f'Following list of {user.username} retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = FollowingListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': f'Following list of {user.username} retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing user following: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve following list',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='mutual-followers')
    def mutual_followers(self, request):
        """
        Get list of mutual followers (users who follow each other)
        """
        try:
            mutual_users = Follow.get_mutual_followers(request.user)
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(mutual_users, request)
            
            if page is not None:
                serializer = UserBasicSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Mutual followers retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = UserBasicSerializer(mutual_users, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': 'Mutual followers retrieved successfully',
                'count': mutual_users.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing mutual followers: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve mutual followers',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def network_stats(self, request):
        """
        Get network statistics for current user
        """
        try:
            followers_count = Follow.get_followers_count(request.user)
            following_count = Follow.get_following_count(request.user)
            
            stats = {
                'followers_count': followers_count,
                'following_count': following_count,
            }
            
            serializer = UserNetworkStatsSerializer(stats)
            
            return Response({
                'success': True,
                'message': 'Network stats retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting network stats: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve network stats',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='stats')
    def user_network_stats(self, request, pk=None):
        """
        Get network statistics for specific user
        URL: /api/network/{user_uuid}/stats/
        """
        try:
            user = get_object_or_404(User, uuid=pk)
            
            followers_count = Follow.get_followers_count(user)
            following_count = Follow.get_following_count(user)
            
            # Check relationship with current user
            is_following = Follow.is_following(request.user, user)
            is_follower = Follow.is_following(user, request.user)
            
            stats = {
                'followers_count': followers_count,
                'following_count': following_count,
                'is_following': is_following,
                'is_follower': is_follower,
            }
            
            serializer = UserNetworkStatsSerializer(stats)
            
            return Response({
                'success': True,
                'message': f'Network stats for {user.username} retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting user network stats: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve network stats',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
