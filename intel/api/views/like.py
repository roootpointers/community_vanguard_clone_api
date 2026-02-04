from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
import logging

from intel.models import Intel, IntelLike
from intel.api.serializers import IntelLikeSerializer
from notification.api.intel_notifications import send_intel_like_notification

logger = logging.getLogger(__name__)


class IntelLikeViewSet(viewsets.ViewSet):
    """
    ViewSet for managing likes on Intel posts.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_like(self, request):
        """
        Toggle like on an intel post.
        If user has liked, remove the like. If not liked, add a like.
        
        Request body:
        {
            "intel_uuid": "uuid-string"
        }
        """
        try:
            intel_uuid = request.data.get('intel_uuid')
            
            if not intel_uuid:
                return Response({
                    'success': False,
                    'message': 'intel_uuid is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                intel = Intel.objects.get(uuid=intel_uuid)
            except Intel.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Intel post not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user already liked this post
            existing_like = IntelLike.objects.filter(user=request.user, intel=intel).first()
            
            if existing_like:
                # Unlike
                existing_like.delete()
                intel.likes_count = max(0, intel.likes_count - 1)
                intel.save(update_fields=['likes_count'])
                
                logger.info(f"User {request.user.email} unliked intel {intel.uuid}")
                
                return Response({
                    'success': True,
                    'message': 'Intel post unliked successfully',
                    'data': {
                        'is_liked': False,
                        'likes_count': intel.likes_count
                    }
                }, status=status.HTTP_200_OK)
            else:
                # Like
                like = IntelLike.objects.create(user=request.user, intel=intel)
                intel.likes_count += 1
                intel.save(update_fields=['likes_count'])
                
                # Notify intel owner about the like (skips if liker is author inside helper)
                try:
                    send_intel_like_notification(intel=intel, liker=request.user)
                except Exception as notify_err:
                    logger.warning(f"Failed to send intel like notification for {intel.uuid}: {notify_err}")
                
                logger.info(f"User {request.user.email} liked intel {intel.uuid}")
                
                return Response({
                    'success': True,
                    'message': 'Intel post liked successfully',
                    'data': {
                        'is_liked': True,
                        'likes_count': intel.likes_count,
                        'like_uuid': str(like.uuid)
                    }
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error toggling intel like: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to toggle like',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='(?P<intel_uuid>[^/.]+)/list')
    def list_likes(self, request, intel_uuid=None):
        """
        Get list of users who liked an intel post.
        """
        try:
            try:
                intel = Intel.objects.get(uuid=intel_uuid)
            except Intel.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Intel post not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            likes = IntelLike.objects.filter(intel=intel).select_related('user').order_by('-created_at')
            serializer = IntelLikeSerializer(likes, many=True)
            
            return Response({
                'success': True,
                'message': 'Likes retrieved successfully',
                'count': likes.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error listing intel likes: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve likes',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
