from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from collections import OrderedDict
import logging

from exchange.models import Exchange, ExchangeVerification
from exchange.api.serializers import (
    ExchangeSerializer,
    ExchangeListSerializer,
    ExchangeVerificationSerializer
)
from exchange.api.pagination import StandardPagination, CategoryGroupedPagination

logger = logging.getLogger(__name__)


class ExchangeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Exchange applications.
    
    All media fields (business_logo, business_background_image, verification_files) 
    are now URL-based. Send URLs instead of file uploads.
    """
    queryset = Exchange.objects.select_related('user').prefetch_related('verifications', 'preview_images').all()
    serializer_class = ExchangeSerializer
    permission_classes = [IsAuthenticated]  # Change to [IsAuthenticated] if auth is required
    parser_classes = [JSONParser]  # Only JSON since all fields are URLs now
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['seller_type', 'status']
    search_fields = ['business_name', 'email', 'mission_statement', 'offers_benefits']
    ordering_fields = ['created_at', 'business_name', 'seller_type']
    ordering = ['-created_at']
    pagination_class = StandardPagination  # DRF's robust pagination
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return ExchangeListSerializer
        return ExchangeSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions and query parameters.
        Admin/staff can see all exchanges. Regular users only see active exchanges.
        Supports: seller_type, category, sub_category
        """
        queryset = super().get_queryset()
        
        # Allow admin/staff to see all exchanges, restrict others to active ones
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(is_active=True)
        
        # Manual filtering for additional flexibility
        seller_type = self.request.query_params.get('seller_type', None)
        category = self.request.query_params.get('category', None)
        sub_category = self.request.query_params.get('sub_category', None)
        status_param = self.request.query_params.get('status', None)
        
        if seller_type:
            queryset = queryset.filter(seller_type=seller_type)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if sub_category:
            queryset = queryset.filter(sub_category=sub_category)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Submit a new exchange application.
        All media fields accept URLs. Supports multiple verification URLs via verification_urls array.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"Validation error in exchange creation: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the exchange
            self.perform_create(serializer)
            
            logger.info(f"Exchange application created: {serializer.data['business_name']}")
            
            return Response({
                'success': True,
                'message': 'Exchange application submitted successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating exchange: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to create exchange application',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """
        List all exchanges grouped by category with robust pagination.
        
        Only shows approved exchanges.
        
        Uses Django's Paginator for reliable pagination with proper edge case handling.
        
        Query params: 
        - seller_type, category, sub_category, search: Filtering
        - page: Page number (default: 1, auto-corrects invalid values)
        - page_size: Items per category per page (default: 10, max: 100)
        
        Returns exchanges organized by category with each category containing:
        - count: Total number of exchanges in that category
        - exchanges: Paginated array of exchange objects
        - page: Current page number
        - page_size: Items per page
        - total_pages: Total pages for this category
        - has_next: Boolean indicating if next page exists
        - has_previous: Boolean indicating if previous page exists
        """
        try:
            queryset = self.filter_queryset(self.get_queryset()).filter(status='approved')
            
            # Use custom pagination class for category grouping
            paginator = CategoryGroupedPagination()
            grouped_data = paginator.paginate_grouped_queryset(queryset, request, view=self)
            
            # Serialize exchanges in each category
            for category, data in grouped_data.items():
                serializer = ExchangeListSerializer(data['exchanges'], many=True)
                data['exchanges'] = serializer.data
            
            return paginator.get_paginated_response(grouped_data, queryset.count())
        
        except Exception as e:
            logger.error(f"Error listing exchanges: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve exchanges',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific exchange details."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'message': 'Exchange retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exchange.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Exchange not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving exchange: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve exchange',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update exchange application. All media fields accept URLs. Only creator or admin can edit."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # Check if user is the creator or admin/staff
            if instance.user != request.user and not (request.user.is_staff or request.user.is_superuser):
                return Response({
                    'success': False,
                    'message': 'You do not have permission to edit this exchange'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if not serializer.is_valid():
                logger.warning(f"Validation error in exchange update: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            
            logger.info(f"Exchange application updated: {serializer.data['business_name']}")
            
            return Response({
                'success': True,
                'message': 'Exchange application updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error updating exchange: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update exchange application',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete exchange application by setting is_active=False. Only creator can delete."""
        try:
            instance = self.get_object()
            
            # Check if user is the creator
            if instance.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to delete this exchange'
                }, status=status.HTTP_403_FORBIDDEN)
            
            org_name = instance.business_name
            
            # Soft delete - set is_active to False instead of deleting
            instance.is_active = False
            instance.save(update_fields=['is_active'])
            
            logger.info(f"Exchange application deactivated: {org_name}")
            
            return Response({
                'success': True,
                'message': 'Exchange application deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error deleting exchange: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to delete exchange application',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='my-exchanges')
    def my_exchanges(self, request):
        """
        Get all exchanges posted by the authenticated user.
        
        Uses DRF's StandardPagination for robust pagination with proper edge case handling.
        
        Query params:
        - page: Page number (default: 1, auto-corrects invalid values)
        - page_size: Items per page (default: 10, max: 100)
        - All standard filters: seller_type, category, sub_category, status, search
        """
        try:
            # Get user's exchanges
            queryset = Exchange.objects.filter(
                user=request.user
            ).select_related('user').prefetch_related('verifications', 'preview_images').order_by('-created_at')
            
            # Apply filters if provided
            queryset = self.filter_queryset(queryset)
            
            # Use DRF's pagination class for robust pagination
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            
            # Serialize paginated data
            serializer = ExchangeListSerializer(paginated_queryset, many=True)
            
            # Return paginated response with enhanced metadata
            response = paginator.get_paginated_response(serializer.data)
            response.data['message'] = 'Your exchanges retrieved successfully'
            
            return response
        
        except Exception as e:
            logger.error(f"Error retrieving user exchanges: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve your exchanges',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_uuid>[^/.]+)')
    def user_exchanges(self, request, user_uuid=None):
        """
        View all exchanges posted by a specific user.
        
        Endpoint: GET /api/exchange/user/{user_uuid}/
        
        Uses DRF's StandardPagination for robust pagination with proper edge case handling.
        
        Query params:
        - page: Page number (default: 1, auto-corrects invalid values)
        - page_size: Items per page (default: 10, max: 100)
        - All standard filters: seller_type, category, sub_category, status, search
        
        Returns only approved exchanges to protect user privacy.
        """
        try:
            from accounts.models import User
            
            # Verify user exists
            try:
                user = User.objects.get(uuid=user_uuid)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get user's approved exchanges (privacy protection)
            # Admin/staff can see all exchanges, others only see approved active ones
            if request.user.is_staff or request.user.is_superuser:
                queryset = Exchange.objects.filter(
                    user=user
                ).select_related('user').prefetch_related('verifications', 'preview_images').order_by('-created_at')
            else:
                queryset = Exchange.objects.filter(
                    user=user,
                    status='approved',
                    is_active=True
                ).select_related('user').prefetch_related('verifications', 'preview_images').order_by('-created_at')
            
            # Apply filters if provided
            queryset = self.filter_queryset(queryset)
            
            # Use DRF's pagination class for robust pagination
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            
            # Serialize paginated data
            serializer = ExchangeListSerializer(paginated_queryset, many=True)
            
            # Return paginated response with enhanced metadata
            response = paginator.get_paginated_response(serializer.data)
            response.data['message'] = f'Exchanges by {user.full_name} retrieved successfully'
            response.data['user'] = {
                'uuid': str(user.uuid),
                'full_name': user.full_name,
                'email': user.email
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Error retrieving user exchanges: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve user exchanges',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
