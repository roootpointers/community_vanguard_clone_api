from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count
from notification.models import FCMDeviceCustom, NotificationTemplate, NotificationLog
from notification.api.serializers import (
    FCMDeviceRegistrationSerializer, FCMDeviceSerializer, FCMDeviceUpdateSerializer,
    NotificationTemplateSerializer, SendNotificationSerializer,
    BulkNotificationSerializer
)
from accounts.models.user import User
from notification.api.utils import FCMNotificationService
from notification.api.utils import CommonPagination

import logging
logger = logging.getLogger(__name__)


class FCMDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing FCM devices
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FCMDeviceSerializer
    pagination_class = CommonPagination
    queryset = FCMDeviceCustom.objects.all()
    lookup_field = 'uuid'
    http_method_names = ["post", "get", "put", "patch", "delete"]
    
    
    def create(self, request, *args, **kwargs):
        """Register new device or update existing one"""
        try:
            serializer = FCMDeviceRegistrationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Device registered successfully: {serializer.instance.registration_id}")
                return Response({
                    'success': True,
                    'message': 'Device registered successfully',
                    'data': FCMDeviceSerializer(serializer.instance).data
                }, status=status.HTTP_201_CREATED)
            logger.error(serializer.errors)
            response = {
                'success': False,
                'message': 'Something went wrong.',
                'errors': serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            response = {
                'success': False,
                'message': e.message,
                'errors': str(e)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, *args, **kwargs):
        """List user's devices with pagination"""
        try:
            user = request.user
            queryset = FCMDeviceCustom.objects.filter(user=user)
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = FCMDeviceSerializer(page, many=True)
                paginated_response = self.paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'FCM devices retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = FCMDeviceSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'FCM devices retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing FCM device"""
        try:
            instance = self.get_object()
            serializer = FCMDeviceUpdateSerializer(instance, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Device updated successfully: {serializer.instance.registration_id}")
                return Response({
                    'success': True,
                    'message': 'Device updated successfully',
                    'data': FCMDeviceSerializer(serializer.instance).data
                }, status=status.HTTP_200_OK)
            logger.error(serializer.errors)
            response = {
                'success': False,
                'message': 'Something went wrong.',
                'errors': serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            response = {
                'success': False,
                'message': e.message,
                'errors': str(e)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        """Delete an FCM device"""
        try:
            instance = self.get_object()
            instance.delete()
            logger.info(f"Device deleted successfully: {instance.registration_id}")
            return Response({
                'success': True,
                'message': 'Device deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(e)
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ViewSet):
    """
    ViewSet for sending notifications
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='send')
    def send(self, request):
        """Send custom notification to specific users"""
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        logs = FCMNotificationService.send_notification_to_users(
            user_ids=data['recipient_ids'],
            title=data['title'],
            body=data['body'],
            data=data.get('data', {}),
            icon=data.get('icon'),
            sound=data.get('sound', 'default'),
            priority=data.get('priority', 'normal'),
            click_action=data.get('click_action')
        )
        
        successful_sends = len([log for log in logs if log.status == 'SENT'])
        
        return Response({
            'success': True,
            'message': f'Notification sent to {successful_sends} devices',
            'data': {
                'total_devices': len(logs),
                'successful_sends': successful_sends,
                'failed_sends': len(logs) - successful_sends
            }
        })
    
    @action(detail=False, methods=['post'], url_path='send-bulk')
    def send_bulk(self, request):
        """Send bulk notifications"""
        serializer = BulkNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        logs = FCMNotificationService.send_bulk_notification(
            title=data['title'],
            body=data['body'],
            data=data.get('data', {}),
            icon=data.get('icon'),
            sound=data.get('sound', 'default'),
            priority=data.get('priority', 'normal'),
            user_filters=data.get('user_filters'),
            device_types=data.get('device_types')
        )
        
        successful_sends = len([log for log in logs if log.status == 'SENT'])
        
        return Response({
            'success': True,
            'message': f'Bulk notification sent to {successful_sends} devices',
            'data': {
                'total_devices': len(logs),
                'successful_sends': successful_sends,
                'failed_sends': len(logs) - successful_sends
            }
        })
    
    @action(detail=False, methods=['post'], url_path='test')
    def test_notification(self, request):
        """Send test notification"""
        user = request.user
        
        logs = FCMNotificationService.send_notification_to_user(
            user=user,
            title="🧪 Test Notification",
            body=f"Hello {user.username}! This is a test notification from GoodWink.",
            data={
                'type': 'test',
                'timestamp': str(timezone.now())
            },
            icon='test_icon',
            sound='default',
            priority='normal'
        )
        
        successful_sends = len([log for log in logs if log.status == 'SENT'])
        
        return Response({
            'success': True,
            'message': f'Test notification sent to {successful_sends} of your devices',
            'data': {
                'total_devices': len(logs),
                'successful_sends': successful_sends,
                'failed_sends': len(logs) - successful_sends
            }
        })



class NotificationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notification templates
    """
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = NotificationTemplate.objects.filter(is_active=True)
    
    def list(self, request, *args, **kwargs):
        """List notification templates with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Get template details"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })


class NotificationStatsViewSet(viewsets.ViewSet):
    """
    ViewSet for notification statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='devices')
    def devices(self, request):
        """Get device statistics"""
        stats = FCMNotificationService.get_device_statistics()
        
        # Add user-specific stats
        user_devices = FCMDeviceCustom.objects.filter(user=request.user)
        user_stats = {
            'user_total_devices': user_devices.count(),
            'user_active_devices': user_devices.filter(is_active=True).count(),
            'user_ios_devices': user_devices.filter(type='ios', is_active=True).count(),
            'user_android_devices': user_devices.filter(type='android', is_active=True).count(),
            'user_web_devices': user_devices.filter(type='web', is_active=True).count(),
        }
        
        return Response({
            'success': True,
            'data': {
                'global_stats': stats,
                'user_stats': user_stats
            }
        })
    
    @action(detail=False, methods=['get'], url_path='notifications')
    def notifications(self, request):
        """Get notification statistics"""
        user_logs = NotificationLog.objects.filter(recipient=request.user)
        
        stats = {
            'total_notifications': user_logs.count(),
            'sent_notifications': user_logs.filter(status='SENT').count(),
            'delivered_notifications': user_logs.filter(status='DELIVERED').count(),
            'failed_notifications': user_logs.filter(status='FAILED').count(),
            'clicked_notifications': user_logs.filter(status='CLICKED').count(),
            'recent_notifications': user_logs.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }
        
        # Get notification breakdown by type
        type_breakdown = user_logs.values('data__type').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'success': True,
            'data': {
                'stats': stats,
                'type_breakdown': type_breakdown
            }
        })


class NotificationManagementViewSet(viewsets.ViewSet):
    """
    ViewSet for notification management actions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='cleanup-devices')
    def cleanup_devices(self, request):
        """Cleanup inactive devices"""
        days = request.data.get('days', 30)
        
        try:
            count = FCMNotificationService.cleanup_inactive_devices(days=days)
            
            return Response({
                'success': True,
                'message': f'Cleaned up {count} inactive devices',
                'data': {'deactivated_devices': count}
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Cleanup failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='health-check')
    def health_check(self, request):
        """Health check endpoint"""
        try:
            # Test database connectivity
            device_count = FCMDeviceCustom.objects.count()
            
            # Test basic functionality
            stats = FCMNotificationService.get_device_statistics()
            
            return Response({
                'success': True,
                'message': 'Notification service is healthy',
                'data': {
                    'database_connected': True,
                    'total_devices': device_count,
                    'service_stats': stats
                }
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Health check failed: {str(e)}',
                'data': {'database_connected': False}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
