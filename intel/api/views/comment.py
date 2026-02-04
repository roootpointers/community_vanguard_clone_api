from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
import logging

from intel.models import Intel, IntelComment, CommentLike
from intel.api.serializers import IntelCommentSerializer, IntelCommentListSerializer, CommentLikeSerializer
from notification.api.intel_notifications import (
    send_intel_comment_notification,
    send_comment_reply_notification,
)

logger = logging.getLogger(__name__)


class CommentPagination(PageNumberPagination):
    """Pagination for comments."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IntelCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on Intel posts.
    Supports nested comments (replies).
    """
    queryset = IntelComment.objects.select_related('user', 'intel', 'parent_comment').all()
    serializer_class = IntelCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return IntelCommentListSerializer
        return IntelCommentSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        """
        Create a new comment or reply on an intel post.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Set the user
            comment = serializer.save(user=request.user)
            
            # Update comment count on intel
            intel = comment.intel
            intel.comments_count = intel.comments.count()
            intel.save(update_fields=['comments_count'])
            
            # Update reply count on parent comment if it's a reply
            if comment.parent_comment:
                parent = comment.parent_comment
                parent.replies_count = parent.replies.count()
                parent.save(update_fields=['replies_count'])

            # Send notifications:
            # - If top-level comment: notify intel owner
            # - If reply: notify parent comment owner
            try:
                if comment.parent_comment:
                    send_comment_reply_notification(reply_comment=comment, replier=request.user)
                else:
                    send_intel_comment_notification(intel=intel, comment=comment, commenter=request.user)
            except Exception as notify_err:
                logger.warning(f"Failed to send comment notification for intel {intel.uuid}: {notify_err}")
            
            logger.info(f"Comment created by {request.user.email} on intel {intel.uuid}")
            
            # Return full comment data
            response_serializer = IntelCommentSerializer(comment, context={'request': request})
            
            return Response({
                'success': True,
                'message': 'Comment posted successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to post comment',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='intel/(?P<intel_uuid>[^/.]+)')
    def list_comments(self, request, intel_uuid=None):
        """
        Get all comments for a specific intel post (top-level comments only).
        """
        try:
            try:
                intel = Intel.objects.get(uuid=intel_uuid)
            except Intel.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Intel post not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get only top-level comments (not replies)
            comments = IntelComment.objects.filter(
                intel=intel,
                parent_comment__isnull=True
            ).select_related('user').prefetch_related('replies').order_by('-created_at')
            
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = IntelCommentSerializer(page, many=True, context={'request': request})
                response = self.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Comments retrieved successfully',
                    'count': response.data.get('count'),
                    'next': response.data.get('next'),
                    'previous': response.data.get('previous'),
                    'results': response.data.get('results')
                }, status=status.HTTP_200_OK)
            
            serializer = IntelCommentSerializer(comments, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': 'Comments retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error listing comments: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve comments',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='replies')
    def list_replies(self, request, pk=None):
        """
        Get all replies for a specific comment.
        """
        try:
            comment = self.get_object()
            
            replies = IntelComment.objects.filter(
                parent_comment=comment
            ).select_related('user').order_by('created_at')
            
            serializer = IntelCommentListSerializer(replies, many=True, context={'request': request})
            
            return Response({
                'success': True,
                'message': 'Replies retrieved successfully',
                'count': replies.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error listing replies: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve replies',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update comment. Only creator can edit."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # Check if user is the creator
            if instance.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to edit this comment'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            logger.info(f"Comment updated: {instance.uuid}")
            
            return Response({
                'success': True,
                'message': 'Comment updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error updating comment: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update comment',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete comment. Only creator can delete."""
        try:
            instance = self.get_object()
            
            # Check if user is the creator
            if instance.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to delete this comment'
                }, status=status.HTTP_403_FORBIDDEN)
            
            intel = instance.intel
            parent_comment = instance.parent_comment
            
            self.perform_destroy(instance)
            
            # Update counts
            intel.comments_count = intel.comments.count()
            intel.save(update_fields=['comments_count'])
            
            if parent_comment:
                parent_comment.replies_count = parent_comment.replies.count()
                parent_comment.save(update_fields=['replies_count'])
            
            logger.info(f"Comment deleted: {instance.uuid}")
            
            return Response({
                'success': True,
                'message': 'Comment deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error deleting comment: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to delete comment',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentLikeViewSet(viewsets.ViewSet):
    """
    ViewSet for managing likes on comments.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_like(self, request):
        """
        Toggle like on a comment.
        If user has liked, remove the like. If not liked, add a like.
        
        Request body:
        {
            "comment_uuid": "uuid-string"
        }
        """
        try:
            comment_uuid = request.data.get('comment_uuid')
            
            if not comment_uuid:
                return Response({
                    'success': False,
                    'message': 'comment_uuid is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                comment = IntelComment.objects.get(uuid=comment_uuid)
            except IntelComment.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Comment not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user already liked this comment
            existing_like = CommentLike.objects.filter(user=request.user, comment=comment).first()
            
            if existing_like:
                # Unlike
                existing_like.delete()
                comment.likes_count = max(0, comment.likes_count - 1)
                comment.save(update_fields=['likes_count'])
                
                logger.info(f"User {request.user.email} unliked comment {comment.uuid}")
                
                return Response({
                    'success': True,
                    'message': 'Comment unliked successfully',
                    'data': {
                        'is_liked': False,
                        'likes_count': comment.likes_count
                    }
                }, status=status.HTTP_200_OK)
            else:
                # Like
                like = CommentLike.objects.create(user=request.user, comment=comment)
                comment.likes_count += 1
                comment.save(update_fields=['likes_count'])
                
                logger.info(f"User {request.user.email} liked comment {comment.uuid}")
                
                return Response({
                    'success': True,
                    'message': 'Comment liked successfully',
                    'data': {
                        'is_liked': True,
                        'likes_count': comment.likes_count,
                        'like_uuid': str(like.uuid)
                    }
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error toggling comment like: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to toggle like',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
