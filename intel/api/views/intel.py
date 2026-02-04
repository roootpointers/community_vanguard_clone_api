from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet
from django.db.models import Q
import logging

from intel.models import Intel, IntelMedia
from intel.api.serializers import IntelSerializer, IntelListSerializer

logger = logging.getLogger(__name__)


class IntelFilterSet(FilterSet):
    """Custom FilterSet for Intel with flexible date filtering."""
    
    class Meta:
        model = Intel
        fields = ['urgency', 'status']


class IntelPagination(PageNumberPagination):
    """Pagination for Intel posts."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IntelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Intel posts.
    
    Supports creating intel with multiple media URLs, listing with filters,
    and retrieving individual intel posts.
    """
    queryset = Intel.objects.select_related('user', 'category').prefetch_related('media_files', 'likes').all()
    serializer_class = IntelSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    pagination_class = IntelPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = IntelFilterSet
    search_fields = ['description', 'location']
    ordering_fields = ['created_at', 'likes_count', 'comments_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset with manual handling for category UUID and date formats."""
        queryset = super().get_queryset()
        
        # Manual filtering for category UUID
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__uuid=category)
        
        # Handle simple date format (YYYY-MM-DD) for created_at
        created_at = self.request.query_params.get('created_at')
        if created_at:
            queryset = queryset.filter(created_at__date=created_at)
        
        # Handle simple date format (YYYY-MM-DD) for updated_at
        updated_at = self.request.query_params.get('updated_at')
        if updated_at:
            queryset = queryset.filter(updated_at__date=updated_at)
        
        return queryset
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return IntelListSerializer
        return IntelSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        """
        Create a new intel post with optional media files.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Set the user
            intel = serializer.save(user=request.user)
            
            logger.info(f"Intel post created by {request.user.email}: {intel.uuid}")
            
            # Return full intel data
            response_serializer = IntelSerializer(intel, context={'request': request})
            
            return Response({
                'success': True,
                'message': 'Intel post created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating intel post: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to create intel post',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """
        List all intel posts with pagination and filtering.
        Only shows approved intel posts.
        
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        - search: Search in description, location
        - urgency: Filter by urgency (low, medium, high)
        - status: Filter by status (under_review, approved, rejected)
        - created_at: Filter by creation date (YYYY-MM-DD format)
        - updated_at: Filter by last updated date (YYYY-MM-DD format)
        - ordering: Sort by created_at, likes_count, comments_count (prefix with - for descending)
        
        Returns paginated list of intel posts.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Intel posts retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Intel posts retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error listing intel posts: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve intel posts',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific intel post details."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'message': 'Intel post retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Intel.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Intel post not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving intel post: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve intel post',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update intel post. Only creator can edit."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # Check if user is the creator
            if instance.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to edit this intel post'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            logger.info(f"Intel post updated: {instance.uuid}")
            
            return Response({
                'success': True,
                'message': 'Intel post updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error updating intel post: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update intel post',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete intel post. Only creator can delete."""
        try:
            instance = self.get_object()
            
            # Check if user is the creator
            if instance.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to delete this intel post'
                }, status=status.HTTP_403_FORBIDDEN)
            
            self.perform_destroy(instance)
            
            logger.info(f"Intel post deleted: {instance.uuid}")
            
            return Response({
                'success': True,
                'message': 'Intel post deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error deleting intel post: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to delete intel post',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='my-intels')
    def my_intels(self, request):
        """
        Get all intel posts created by the authenticated user.
        
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        - search: Search in description, location
        - urgency: Filter by urgency (low, medium, high)
        - status: Filter by status (under_review, approved, rejected)
        - created_at: Filter by creation date (YYYY-MM-DD format)
        - updated_at: Filter by last updated date (YYYY-MM-DD format)
        - ordering: Sort by created_at, likes_count, comments_count (prefix with - for descending)
        
        Returns paginated list of your intel posts.
        """
        try:
            queryset = Intel.objects.filter(
                user=request.user
            ).select_related('user', 'category').prefetch_related('media_files', 'likes').order_by('-created_at')
            
            queryset = self.filter_queryset(queryset)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = IntelListSerializer(page, many=True, context={'request': request})
                response = self.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Your intel posts retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = IntelListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': 'Your intel posts retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error retrieving user intel posts: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve your intel posts',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_uuid>[^/.]+)')
    def user_intels(self, request, user_uuid=None):
        """
        Get all intel posts created by a specific user.
        
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        - search: Search in description, location
        - urgency: Filter by urgency (low, medium, high)
        - status: Filter by status (under_review, approved, rejected)
        - created_at: Filter by creation date (YYYY-MM-DD format)
        - updated_at: Filter by last updated date (YYYY-MM-DD format)
        - ordering: Sort by created_at, likes_count, comments_count (prefix with - for descending)
        
        Returns paginated list of intel posts by the specified user.
        """
        try:
            from accounts.models.user import User
            
            # Get the user
            try:
                user = User.objects.get(uuid=user_uuid)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            queryset = Intel.objects.filter(
                user=user
            ).select_related('user', 'category').prefetch_related('media_files', 'likes').order_by('-created_at')
            
            queryset = self.filter_queryset(queryset)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = IntelListSerializer(page, many=True, context={'request': request})
                response = self.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': f'Intel posts by {user.full_name or user.email} retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = IntelListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': f'Intel posts by {user.full_name or user.email} retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error retrieving user intel posts: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve user intel posts',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)