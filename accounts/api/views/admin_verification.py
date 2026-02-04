from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db import models
from accounts.models.verification_document import VerificationDocument
from accounts.models.user import User
from accounts.models.profile import UserProfile
from accounts.api.serializers.verification_document import (
    VerificationDocumentSerializer,
    VerificationDocumentApproveSerializer,
    VerificationDocumentRejectSerializer
)
from notification.api.notification_utils import NotificationService
import logging

logger = logging.getLogger(__name__)


class AdminVerificationDocumentPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class AdminVerificationDocumentViewSet(viewsets.ViewSet):
    """
    Admin-only ViewSet for managing verification documents.
    
    Provides endpoints for:
    - Listing all verification documents (with filters)
    - Retrieving specific document details
    - Approving documents
    - Rejecting documents with reason
    """
    permission_classes = [IsAdminUser]
    pagination_class = AdminVerificationDocumentPagination

    def get_queryset(self):
        """Get base queryset with related data."""
        return VerificationDocument.objects.select_related(
            'profile__user', 'reviewed_by'
        ).all()

    def list(self, request):
        """
        List all verification documents with admin-specific details.
        Supports filtering by status and search.
        
        GET /api/admin-verification-documents/
        
        Query Parameters:
        - status: Filter by status (pending, approved, rejected)
        - search: Search in user email, document_type
        - page: Page number
        - page_size: Items per page (default: 50, max: 200)
        """
        try:
            queryset = self.get_queryset()
            
            # Apply filters
            status_filter = request.query_params.get('status')
            search = request.query_params.get('search')
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if search:
                queryset = queryset.filter(
                    models.Q(profile__user__email__icontains=search) |
                    models.Q(document_type__icontains=search)
                )
            
            # Order by created_at descending
            queryset = queryset.order_by('-created_at')
            
            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = VerificationDocumentSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = VerificationDocumentSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Verification documents retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Admin: Error listing verification documents: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve verification documents',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific verification document.
        
        GET /api/admin-verification-documents/{uuid}/
        """
        try:
            document = VerificationDocument.objects.select_related(
                'profile__user', 'reviewed_by'
            ).get(uuid=pk)
            
            serializer = VerificationDocumentSerializer(document)
            return Response({
                'success': True,
                'message': 'Verification document retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except VerificationDocument.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Verification document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error retrieving verification document: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve verification document',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve verification documents for a user.
        Approves all pending documents for the user and sends notification.
        
        POST /api/admin-verification-documents/{user_uuid}/approve/
        """
        try:
            user = User.objects.get(uuid=pk)
            profile = UserProfile.objects.get(user=user)
            documents = VerificationDocument.objects.filter(profile=profile, status='pending')
            
            if not documents.exists():
                return Response({
                    'success': False,
                    'message': 'No pending verification documents found for this user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate request data
            serializer = VerificationDocumentApproveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update all pending documents status
            approved_count = 0
            approved_documents = []
            for document in documents:
                document.status = 'approved'
                document.rejection_reason = None
                document.reviewed_by = request.user
                document.reviewed_at = timezone.now()
                document.save()
                approved_count += 1
                approved_documents.append({
                    'uuid': str(document.uuid),
                    'document_type': document.document_type
                })
            
            # Send notification to user
            try:
                NotificationService.create_notification(
                    recipient_uuid=str(user.uuid),
                    notification_type='DOCUMENT_APPROVED',
                    title='Verification Documents Approved',
                    message=f'{approved_count} verification document(s) have been approved.',
                    sender_uuid=str(request.user.uuid),
                    related_object_id=str(profile.uuid),
                    related_object_type='verification_document',
                    metadata={
                        'approved_count': approved_count,
                        'documents': approved_documents
                    }
                )
            except Exception as notify_err:
                logger.warning(f"Failed to send document approval notification for user {user.uuid}: {notify_err}")
            
            logger.info(f"{approved_count} verification document(s) approved for user {user.email} by admin {request.user.email}")
            
            return Response({
                'success': True,
                'message': f'{approved_count} verification document(s) approved successfully',
                'data': {
                    'user_uuid': str(user.uuid),
                    'approved_count': approved_count,
                    'documents': approved_documents,
                    'reviewed_by': request.user.email,
                    'reviewed_at': timezone.now().isoformat()
                }
            }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error approving verification documents: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to approve verification documents',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject verification documents for a user with reason.
        Rejects all pending documents for the user and sends notification.
        
        POST /api/admin-verification-documents/{user_uuid}/reject/
        
        Body:
        {
            "rejection_reason": "Reason for rejection"
        }
        """
        try:
            user = User.objects.get(uuid=pk)
            profile = UserProfile.objects.get(user=user)
            documents = VerificationDocument.objects.filter(profile=profile, status='pending')
            
            if not documents.exists():
                return Response({
                    'success': False,
                    'message': 'No pending verification documents found for this user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate request data
            serializer = VerificationDocumentRejectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            rejection_reason = serializer.validated_data.get('rejection_reason', '')
            
            # Update all pending documents status
            rejected_count = 0
            rejected_documents = []
            for document in documents:
                document.status = 'rejected'
                document.rejection_reason = rejection_reason
                document.reviewed_by = request.user
                document.reviewed_at = timezone.now()
                document.save()
                rejected_count += 1
                rejected_documents.append({
                    'uuid': str(document.uuid),
                    'document_type': document.document_type
                })
            
            # Send notification to user
            try:
                NotificationService.create_notification(
                    recipient_uuid=str(user.uuid),
                    notification_type='DOCUMENT_REJECTED',
                    title='Verification Documents Rejected',
                    message=f'{rejected_count} verification document(s) have been rejected. Reason: {rejection_reason}',
                    sender_uuid=str(request.user.uuid),
                    related_object_id=str(profile.uuid),
                    related_object_type='verification_document',
                    metadata={
                        'rejected_count': rejected_count,
                        'documents': rejected_documents,
                        'rejection_reason': rejection_reason
                    }
                )
            except Exception as notify_err:
                logger.warning(f"Failed to send document rejection notification for user {user.uuid}: {notify_err}")
            
            logger.info(f"{rejected_count} verification document(s) rejected for user {user.email} by admin {request.user.email}")
            
            return Response({
                'success': True,
                'message': f'{rejected_count} verification document(s) rejected successfully',
                'data': {
                    'user_uuid': str(user.uuid),
                    'rejected_count': rejected_count,
                    'documents': rejected_documents,
                    'rejection_reason': rejection_reason,
                    'reviewed_by': request.user.email,
                    'reviewed_at': timezone.now().isoformat()
                }
            }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin: Error rejecting verification documents: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to reject verification documents',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
