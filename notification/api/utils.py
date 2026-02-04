import logging
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice
from rest_framework.pagination import PageNumberPagination
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from notification.models import FCMDeviceCustom, NotificationTemplate, NotificationLog

User = get_user_model()
logger = logging.getLogger(__name__)

PAGINATION_ITEM_PER_PAGE = 10

class CommonPagination(PageNumberPagination):
    page_size = PAGINATION_ITEM_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 500


class FCMNotificationService:
    """
    Service class for handling FCM notifications
    """
    
    @staticmethod
    def send_notification_to_user(
        user,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        icon: Optional[str] = None,
        sound: str = 'default',
        priority: str = 'normal',
        click_action: Optional[str] = None,
        template: Optional[NotificationTemplate] = None
    ) -> List[NotificationLog]:
        """
        Send notification to a specific user on all their devices
        """
        devices = FCMDeviceCustom.objects.filter(user=user)
        notification_logs = []
        
        for device in devices:
            log = FCMNotificationService._send_to_device(
                device=device,
                title=title,
                body=body,
                data=data,
                icon=icon,
                sound=sound,
                priority=priority,
                click_action=click_action,
                template=template
            )
            notification_logs.append(log)
        
        return notification_logs
    
    @staticmethod
    def send_notification_to_users(
        user_ids: List[int],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        icon: Optional[str] = None,
        sound: str = 'default',
        priority: str = 'normal',
        click_action: Optional[str] = None,
        template: Optional[NotificationTemplate] = None
    ) -> List[NotificationLog]:
        """
        Send notification to multiple users
        """
        users = User.objects.filter(id__in=user_ids)
        notification_logs = []
        
        for user in users:
            logs = FCMNotificationService.send_notification_to_user(
                user=user,
                title=title,
                body=body,
                data=data,
                icon=icon,
                sound=sound,
                priority=priority,
                click_action=click_action,
                template=template
            )
            notification_logs.extend(logs)
        
        return notification_logs
    
    @staticmethod
    def send_bulk_notification(
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        icon: Optional[str] = None,
        sound: str = 'default',
        priority: str = 'normal',
        user_filters: Optional[Dict[str, Any]] = None,
        device_types: Optional[List[str]] = None,
        template: Optional[NotificationTemplate] = None
    ) -> List[NotificationLog]:
        """
        Send bulk notification to users based on filters
        """
        # Build user queryset
        user_queryset = User.objects.all()
        if user_filters:
            user_queryset = user_queryset.filter(**user_filters)
        
        # Build device queryset
        device_queryset = FCMDeviceCustom.objects.filter(
            user__in=user_queryset,
            active=True
        )
        
        if device_types:
            device_queryset = device_queryset.filter(type__in=device_types)
        
        notification_logs = []
        
        # Send in batches to avoid overwhelming the service
        batch_size = 500
        devices = device_queryset.select_related('user')
        
        for i in range(0, devices.count(), batch_size):
            batch_devices = devices[i:i + batch_size]
            
            for device in batch_devices:
                log = FCMNotificationService._send_to_device(
                    device=device,
                    title=title,
                    body=body,
                    data=data,
                    icon=icon,
                    sound=sound,
                    priority=priority,
                    template=template
                )
                notification_logs.append(log)
        
        return notification_logs
    
    @staticmethod
    def send_notification_with_template(
        template_name: str,
        user,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> List[NotificationLog]:
        """
        Send notification using a predefined template
        """
        try:
            template = NotificationTemplate.objects.get(name=template_name, is_active=True)
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Notification template '{template_name}' not found")
            return []
        
        # Replace template variables
        context = context or {}
        title = template.title_template.format(**context)
        body = template.body_template.format(**context)
        
        return FCMNotificationService.send_notification_to_user(
            user=user,
            title=title,
            body=body,
            data=data,
            icon=template.icon,
            sound=template.sound,
            priority=template.priority,
            template=template
        )
    
    @staticmethod
    def _send_to_device(
        device: FCMDeviceCustom,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        icon: Optional[str] = None,
        sound: str = 'default',
        priority: str = 'normal',
        click_action: Optional[str] = None,
        template: Optional[NotificationTemplate] = None
    ) -> NotificationLog:
        """
        Send notification to a specific device
        """
        # Create notification log
        log = NotificationLog.objects.create(
            recipient=device.user,
            device=device,
            template=template,
            title=title,
            body=body,
            data=data or {}
        )
        
        try:
            # Prepare notification data
            notification_data = data or {}
            
            # Build the message
            if device.type == 'ios':
                # iOS specific message
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                alert=messaging.ApsAlert(
                                    title=title,
                                    body=body
                                ),
                                sound=sound,
                                badge=1
                            ),
                            custom_data=notification_data
                        )
                    ),
                    token=device.registration_id
                )
            else:
                # Android/Web message
                android_config = messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        title=title,
                        body=body,
                        icon=icon,
                        sound=sound,
                        click_action=click_action
                    ),
                    priority=priority
                )
                
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data={str(k): str(v) for k, v in notification_data.items()},
                    android=android_config,
                    token=device.registration_id
                )
            
            # Send the message
            response = messaging.send(message)
            
            # Update log with success
            log.status = 'SENT'
            log.firebase_message_id = response
            log.sent_at = timezone.now()
            log.save()
            
            logger.info(f"Notification sent successfully to {device.user.username}: {response}")
            
        except FirebaseError as e:
            # Handle Firebase errors
            log.status = 'FAILED'
            log.error_message = str(e)
            log.save()
            
            # If token is invalid, deactivate device
            if 'registration-token-not-registered' in str(e).lower():
                device.deactivate()
                logger.warning(f"Deactivated invalid device for user {device.user.username}")
            
            logger.error(f"Firebase error sending notification: {e}")
            
        except Exception as e:
            # Handle other errors
            log.status = 'FAILED'
            log.error_message = str(e)
            log.save()
            
            logger.error(f"Error sending notification: {e}")
        
        return log
    
    @staticmethod
    def cleanup_inactive_devices(days: int = 30):
        """
        Remove devices that haven't been active for specified days
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        inactive_devices = FCMDeviceCustom.objects.filter(
            updated_at__lt=cutoff_date,
            active=True
        )
        
        count = inactive_devices.count()
        inactive_devices.update(active=False)
        
        logger.info(f"Deactivated {count} inactive devices")
        return count
    
    @staticmethod
    def get_device_statistics():
        """
        Get device statistics
        """
        total_devices = FCMDeviceCustom.objects.count()
        active_devices = FCMDeviceCustom.objects.filter(active=True).count()
        ios_devices = FCMDeviceCustom.objects.filter(type='ios', active=True).count()
        android_devices = FCMDeviceCustom.objects.filter(type='android', active=True).count()
        web_devices = FCMDeviceCustom.objects.filter(type='web', active=True).count()
        
        return {
            'total_devices': total_devices,
            'active_devices': active_devices,
            'ios_devices': ios_devices,
            'android_devices': android_devices,
            'web_devices': web_devices,
            'inactive_devices': total_devices - active_devices
        }


# Convenience functions for common notification types in Vanguard app
def send_intel_comment_notification(commenter, intel_author, intel_uuid: str, comment_uuid: str):
    """Send notification when someone comments on an intel report"""
    return FCMNotificationService.send_notification_with_template(
        template_name='INTEL_COMMENT',
        user=intel_author,
        context={
            'commenter_name': commenter.username,
            'commenter_first_name': getattr(commenter, 'first_name', commenter.username)
        },
        data={
            'type': 'intel_comment',
            'commenter_uuid': str(commenter.uuid),
            'intel_uuid': str(intel_uuid),
            'comment_uuid': str(comment_uuid)
        }
    )


def send_intel_like_notification(liker, intel_author, intel_uuid: str):
    """Send notification when someone likes an intel report"""
    return FCMNotificationService.send_notification_with_template(
        template_name='INTEL_LIKE',
        user=intel_author,
        context={
            'liker_name': liker.username,
            'liker_first_name': getattr(liker, 'first_name', liker.username)
        },
        data={
            'type': 'intel_like',
            'liker_uuid': str(liker.uuid),
            'intel_uuid': str(intel_uuid)
        }
    )


def send_intel_status_notification(intel_author, intel_uuid: str, old_status: str, new_status: str):
    """Send notification when intel report status changes"""
    return FCMNotificationService.send_notification_with_template(
        template_name='INTEL_STATUS_UPDATE',
        user=intel_author,
        context={
            'old_status': old_status,
            'new_status': new_status
        },
        data={
            'type': 'intel_status_update',
            'intel_uuid': str(intel_uuid),
            'old_status': old_status,
            'new_status': new_status
        }
    )


def send_exchange_approval_notification(exchange_owner, exchange_uuid: str, org_name: str):
    """Send notification when exchange is approved"""
    return FCMNotificationService.send_notification_with_template(
        template_name='EXCHANGE_APPROVED',
        user=exchange_owner,
        context={
            'org_name': org_name
        },
        data={
            'type': 'exchange_approved',
            'exchange_uuid': str(exchange_uuid),
            'org_name': org_name
        }
    )


def send_exchange_rejection_notification(exchange_owner, exchange_uuid: str, org_name: str, reason: str = None):
    """Send notification when exchange is rejected"""
    return FCMNotificationService.send_notification_with_template(
        template_name='EXCHANGE_REJECTED',
        user=exchange_owner,
        context={
            'org_name': org_name,
            'reason': reason or 'Not specified'
        },
        data={
            'type': 'exchange_rejected',
            'exchange_uuid': str(exchange_uuid),
            'org_name': org_name,
            'reason': reason
        }
    )