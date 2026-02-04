from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import models
import logging

from intel.models import Intel
from intel.api.permissions import IsAdminUser
from intel.api.serializers.admin import (
    IntelApproveSerializer,
    IntelRejectSerializer,
    AdminIntelListSerializer
)
from intel.api.serializers import IntelSerializer
from notification.api.intel_notifications import (
    send_intel_status_update_notification,
)

logger = logging.getLogger(__name__)


class AdminIntelPagination(PageNumberPagination):
    """Pagination for admin intel list."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class AdminIntelViewSet(viewsets.ViewSet):
    """
    Admin-only ViewSet for managing Intel posts.
    
    Provides endpoints for:
    - Listing all intel posts (with filters)
    - Approving intel posts
    - Rejecting intel posts with reason
    """
    permission_classes = [IsAdminUser]
    pagination_class = AdminIntelPagination

    def get_queryset(self):
        """Get base queryset with related data."""
        return Intel.objects.select_related('user', 'category').prefetch_related('media_files').all()

    def list(self, request):
        """
        List all intel posts with admin-specific details.
        Supports filtering by status, urgency, and search.
        """
        try:
            queryset = self.get_queryset()
            
            # Apply filters
            status_filter = request.query_params.get('status')
            urgency_filter = request.query_params.get('urgency')
            search = request.query_params.get('search')
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if urgency_filter:
                queryset = queryset.filter(urgency=urgency_filter)
            if search:
                queryset = queryset.filter(
                    models.Q(description__icontains=search) |
                    models.Q(location__icontains=search) |
                    models.Q(user__email__icontains=search)
                )
            
            # Order by created_at descending
            queryset = queryset.order_by('-created_at')
            
            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = AdminIntelListSerializer(page, many=True)
                response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Intel posts retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = AdminIntelListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Intel posts retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Admin: Error listing intel posts: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve intel posts',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Get detailed information about a specific intel post.
        """
        try:
            intel = Intel.objects.select_related('user', 'category').prefetch_related('media_files').get(uuid=pk)
            serializer = IntelSerializer(intel, context={'request': request})
            
            # Add rejection reason to response if available
            data = serializer.data
            data['rejection_reason'] = intel.rejection_reason
            
            return Response({
                'success': True,
                'message': 'Intel post retrieved successfully',
                'data': data
            }, status=status.HTTP_200_OK)
        
        except Intel.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Intel post not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error retrieving intel post: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve intel post',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve an intel post.
        Changes status to 'approved' and clears any rejection reason.
        
        POST /api/admin-intel/{uuid}/approve/
        """
        try:
            intel = Intel.objects.get(uuid=pk)
            old_status = intel.get_status_display()
            
            # Validate request data
            serializer = IntelApproveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update intel status
            intel.status = 'approved'
            intel.rejection_reason = None  # Clear rejection reason if any
            intel.save()
            
            # Notify intel owner about status change
            try:
                send_intel_status_update_notification(
                    intel=intel,
                    old_status=old_status,
                    new_status=intel.get_status_display()
                )
            except Exception as notify_err:
                logger.warning(f"Failed to send intel approval notification for {intel.uuid}: {notify_err}")
            
            logger.info(f"Intel {intel.uuid} approved by admin {request.user.email}")
            
            return Response({
                'success': True,
                'message': 'Intel post approved successfully',
                'data': {
                    'uuid': str(intel.uuid),
                    'status': intel.status,
                    'status_display': intel.get_status_display()
                }
            }, status=status.HTTP_200_OK)
        
        except Intel.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Intel post not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error approving intel post: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to approve intel post',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject an intel post with a reason.
        Changes status to 'rejected' and saves the rejection reason.
        
        POST /api/admin-intel/{uuid}/reject/
        Request body: { "rejection_reason": "Reason for rejection" }
        """
        try:
            intel = Intel.objects.get(uuid=pk)
            old_status = intel.get_status_display()
            
            # Validate request data
            serializer = IntelRejectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update intel status and rejection reason
            intel.status = 'rejected'
            intel.rejection_reason = serializer.validated_data['rejection_reason']
            intel.save()
            
            # Notify intel owner about status change
            try:
                send_intel_status_update_notification(
                    intel=intel,
                    old_status=old_status,
                    new_status=intel.get_status_display()
                )
            except Exception as notify_err:
                logger.warning(f"Failed to send intel rejection notification for {intel.uuid}: {notify_err}")
            
            logger.info(f"Intel {intel.uuid} rejected by admin {request.user.email}: {intel.rejection_reason}")
            
            return Response({
                'success': True,
                'message': 'Intel post rejected successfully',
                'data': {
                    'uuid': str(intel.uuid),
                    'status': intel.status,
                    'status_display': intel.get_status_display(),
                    'rejection_reason': intel.rejection_reason
                }
            }, status=status.HTTP_200_OK)
        
        except Intel.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Intel post not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error rejecting intel post: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to reject intel post',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_review(self, request):
        """
        Get all intel posts that are pending review (status = 'under_review').
        
        GET /api/admin-intel/pending/
        """
        try:
            queryset = self.get_queryset().filter(status='under_review').order_by('-created_at')
            
            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = AdminIntelListSerializer(page, many=True)
                response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Pending intel posts retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = AdminIntelListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Pending intel posts retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Admin: Error retrieving pending intel posts: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve pending intel posts',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
