from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models.user import User
from accounts.api.serializers.user import UserSerializer
from network.models.follow import Follow
import logging

logger = logging.getLogger(__name__)


class UserPagination(PageNumberPagination):
    """Pagination class for user listing."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    UserViewSet is a viewset that provides CRUD operations for the User model.
    It allows users to create, retrieve, update, and delete user accounts.
    """
    serializer_class = UserSerializer
    queryset = User.objects.select_related('profile').prefetch_related('role_requests').all()
    permission_classes = [AllowAny]
    http_method_names = ["post", "get", "put", "patch", "delete"]
    lookup_field = 'uuid'
    pagination_class = UserPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['email', 'role_requests__role', 'role_requests__is_verified', 'is_active']
    search_fields = ['email', 'full_name', 'profile__branch', 'profile__rank', 'profile__location']
    ordering_fields = ['created_at', 'full_name', 'email']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Set different permissions for different actions.
        List action requires authentication.
        """
        if self.action == 'list':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """
        List all users with pagination and filtering.
        
        Endpoint: GET /api/user/
        
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        - search: Search in email, full_name, branch, rank, location
        - email: Filter by exact email
        - role_requests__role: Filter by role (customer, vendor, community_support_provider)
        - role_requests__is_verified: Filter by verified role (true/false)
        - is_active: Filter by active status (true/false)
        - ordering: Sort by created_at, full_name, email (prefix with - for descending)
        
        Returns paginated list of users with their profiles.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset()).exclude(is_superuser=True).exclude(uuid=request.user.uuid).exclude(is_profile_completed=False)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                
                # Add custom success message
                response.data = {
                    'success': True,
                    'message': 'Users retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }
                return response
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Users retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve users',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='profile', permission_classes=[IsAuthenticated])
    def view_profile(self, request, uuid=None):
        """
        View another user's profile by their UUID.
        
        Endpoint: GET /api/user/{uuid}/profile/
        
        Returns the full user profile including all public information.
        """
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)
            
            return Response({
                'success': True,
                'message': 'User profile retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error retrieving user profile: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve user profile',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='suggested', permission_classes=[IsAuthenticated])
    def suggested_users(self, request):
        """
        Get suggested users that the current user hasn't followed.
        
        Endpoint: GET /api/user/suggested/
        
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        - search: Search in email, full_name, branch, rank, location
        - role_requests__role: Filter by role (customer, vendor, community_support_provider)
        - role_requests__is_verified: Filter by verified role (true/false)
        - is_active: Filter by active status (true/false)
        - ordering: Sort by created_at, full_name, email (prefix with - for descending)
        
        Returns paginated list of users that the current user is not following.
        Excludes superusers, incomplete profiles, and the current user.
        """
        try:
            # Get list of user IDs that current user is already following
            following_ids = Follow.objects.filter(
                follower=request.user
            ).values_list('following_id', flat=True)
            
            # Get users that are not followed by current user
            queryset = self.filter_queryset(
                self.get_queryset()
            ).exclude(
                uuid__in=following_ids
            ).exclude(
                is_superuser=True
            ).exclude(
                uuid=request.user.uuid
            ).exclude(
                is_profile_completed=False
            )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                
                # Add custom success message
                response.data = {
                    'success': True,
                    'message': 'Suggested users retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }
                return response
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Suggested users retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error retrieving suggested users: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve suggested users',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)