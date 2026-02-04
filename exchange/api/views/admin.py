from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
import logging

from exchange.models import Exchange
from intel.api.permissions import IsAdminUser
from exchange.api.serializers import ExchangeListSerializer
from exchange.api.serializers.admin import (
    ExchangeApproveSerializer,
    ExchangeRejectSerializer,
    AdminExchangeListSerializer
)

logger = logging.getLogger(__name__)


class AdminExchangePagination(PageNumberPagination):
    """Pagination for admin exchange list."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class AdminExchangeViewSet(viewsets.ViewSet):
    """
    Admin-only ViewSet for managing Exchange applications.
    
    Provides endpoints for:
    - Listing all exchange applications (with filters)
    - Retrieving specific exchange details
    """
    permission_classes = [IsAdminUser]
    pagination_class = AdminExchangePagination

    def get_queryset(self):
        """Get base queryset with related data."""
        return Exchange.objects.select_related('user', 'category', 'sub_category').prefetch_related('verifications', 'preview_images').all()

    def list(self, request):
        """
        List all exchange applications with admin-specific details.
        Supports filtering by status, seller_type, category, and search.
        
        GET /api/admin-exchange/
        
        Query Parameters:
        - status: Filter by status (under_review, approved, rejected)
        - seller_type: Filter by seller type
        - category: Filter by category UUID
        - sub_category: Filter by sub-category UUID
        - search: Search in business_name, email, mission_statement
        - page: Page number
        - page_size: Items per page (default: 50, max: 200)
        """
        try:
            queryset = self.get_queryset()
            
            # Apply filters
            status_filter = request.query_params.get('status')
            seller_type_filter = request.query_params.get('seller_type')
            category_filter = request.query_params.get('category')
            sub_category_filter = request.query_params.get('sub_category')
            search = request.query_params.get('search')
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if seller_type_filter:
                queryset = queryset.filter(seller_type=seller_type_filter)
            if category_filter:
                queryset = queryset.filter(category__uuid=category_filter)
            if sub_category_filter:
                queryset = queryset.filter(sub_category__uuid=sub_category_filter)
            if search:
                queryset = queryset.filter(
                    models.Q(business_name__icontains=search) |
                    models.Q(email__icontains=search) |
                    models.Q(mission_statement__icontains=search) |
                    models.Q(user__email__icontains=search)
                )
            
            # Order by created_at descending
            queryset = queryset.order_by('-created_at')
            
            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ExchangeListSerializer(page, many=True)
                response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Exchange retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = ExchangeListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Exchange retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Admin: Error listing exchanges: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve exchanges',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Get detailed information about a specific exchange application.
        
        GET /api/admin-exchange/{uuid}/
        """
        try:
            from exchange.api.serializers import ExchangeSerializer
            
            exchange = Exchange.objects.select_related('user', 'category', 'sub_category').prefetch_related('verifications', 'preview_images').get(uuid=pk)
            serializer = ExchangeSerializer(exchange, context={'request': request})
            
            # Add rejection reason to response if available
            data = serializer.data
            data['rejection_reason'] = exchange.rejection_reason
            
            return Response({
                'success': True,
                'message': 'Exchange retrieved successfully',
                'data': data
            }, status=status.HTTP_200_OK)
        
        except Exchange.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Exchange not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error retrieving exchange: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve exchange',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_review(self, request):
        """
        Get all exchanges that are pending review (status = 'under_review').
        
        GET /api/admin-exchange/pending/
        """
        try:
            queryset = self.get_queryset().filter(status='under_review').order_by('-created_at')
            
            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ExchangeListSerializer(page, many=True)
                response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Exchange retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = ExchangeListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Exchange retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Admin: Error retrieving pending exchanges: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve pending exchanges',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='approved')
    def approved(self, request):
        """
        Get all approved exchanges.
        
        GET /api/admin-exchange/approved/
        """
        try:
            queryset = self.get_queryset().filter(status='approved').order_by('-created_at')
            
            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ExchangeListSerializer(page, many=True)
                response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Exchange retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = ExchangeListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Exchange retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Admin: Error retrieving approved exchanges: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve approved exchanges',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='rejected')
    def rejected(self, request):
        """
        Get all rejected exchanges.
        
        GET /api/admin-exchange/rejected/
        """
        try:
            queryset = self.get_queryset().filter(status='rejected').order_by('-created_at')
            
            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ExchangeListSerializer(page, many=True)
                response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Exchange retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = ExchangeListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Exchange retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Admin: Error retrieving rejected exchanges: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve rejected exchanges',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve an exchange application.
        Changes status to 'approved' and clears any rejection reason.
        
        POST /api/admin-exchange/{uuid}/approve/
        """
        try:
            exchange = Exchange.objects.get(uuid=pk)
            
            # Validate request data
            serializer = ExchangeApproveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update exchange status
            exchange.status = 'approved'
            exchange.rejection_reason = None  # Clear rejection reason if any
            exchange.save()
            
            logger.info(f"Exchange {exchange.uuid} approved by admin {request.user.email}")
            
            return Response({
                'success': True,
                'message': 'Exchange application approved successfully',
                'data': {
                    'uuid': str(exchange.uuid),
                    'status': exchange.status,
                    'status_display': exchange.get_status_display()
                }
            }, status=status.HTTP_200_OK)
        
        except Exchange.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Exchange not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error approving exchange: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to approve exchange',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject an exchange application with a reason.
        Changes status to 'rejected' and saves the rejection reason.
        
        POST /api/admin-exchange/{uuid}/reject/
        Request body: { "rejection_reason": "Reason for rejection" }
        """
        try:
            exchange = Exchange.objects.get(uuid=pk)
            
            # Validate request data
            serializer = ExchangeRejectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update exchange status and rejection reason
            exchange.status = 'rejected'
            exchange.rejection_reason = serializer.validated_data['rejection_reason']
            exchange.save()
            
            logger.info(f"Exchange {exchange.uuid} rejected by admin {request.user.email}: {exchange.rejection_reason}")
            
            return Response({
                'success': True,
                'message': 'Exchange application rejected successfully',
                'data': {
                    'uuid': str(exchange.uuid),
                    'status': exchange.status,
                    'status_display': exchange.get_status_display(),
                    'rejection_reason': exchange.rejection_reason
                }
            }, status=status.HTTP_200_OK)
        
        except Exchange.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Exchange not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error rejecting exchange: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to reject exchange',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
