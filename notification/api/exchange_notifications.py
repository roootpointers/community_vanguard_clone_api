"""
Exchange-specific notification utilities
Handles all FCM notifications related to Exchange operations
"""
import logging
from typing import Optional
from django.contrib.auth import get_user_model
from notification.api.utils import FCMNotificationService
from notification.models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


class ExchangeNotificationService:
    """
    Service for handling all Exchange-related notifications
    """
    
    @staticmethod
    def send_approval_notification(exchange):
        """
        Send notification when an exchange is approved
        
        Args:
            exchange: The Exchange object that was approved
        """
        try:
            # Validate input
            if not exchange:
                logger.error("Missing exchange for approval notification")
                return
            
            if not exchange.user:
                logger.warning(f"No user associated with exchange {exchange.uuid}")
                return
            
            # Create notification record
            notification = Notification.objects.create(
                recipient=exchange.user,
                sender=None,  # System notification
                notification_type='EXCHANGE_APPROVED',
                title=f"Exchange Approved!",
                message=f"Congratulations! Your exchange '{exchange.org_name}' has been approved and is now live.",
                related_object_id=str(exchange.uuid),
                related_object_type='exchange',
                metadata={
                    'exchange_uuid': str(exchange.uuid),
                    'org_name': exchange.org_name,
                    'exchange_type': exchange.exchange_type,
                    'status': 'approved',
                }
            )
            logger.info(f"Created exchange approval notification for {exchange.user.username}")
            
            # Send FCM notification
            ExchangeNotificationService._send_fcm_approval_notification(exchange)
            
        except Exception as e:
            logger.error(f"Error sending exchange approval notification: {e}")
    
    @staticmethod
    def send_rejection_notification(exchange, reason=None):
        """
        Send notification when an exchange is rejected
        
        Args:
            exchange: The Exchange object that was rejected
            reason: Optional reason for rejection
        """
        try:
            # Validate input
            if not exchange:
                logger.error("Missing exchange for rejection notification")
                return
            
            if not exchange.user:
                logger.warning(f"No user associated with exchange {exchange.uuid}")
                return
            
            # Create notification record
            message = f"Your exchange '{exchange.org_name}' has been rejected."
            if reason:
                message += f" Reason: {reason}"
            
            notification = Notification.objects.create(
                recipient=exchange.user,
                sender=None,  # System notification
                notification_type='EXCHANGE_REJECTED',
                title=f"Exchange Rejected",
                message=message,
                related_object_id=str(exchange.uuid),
                related_object_type='exchange',
                metadata={
                    'exchange_uuid': str(exchange.uuid),
                    'org_name': exchange.org_name,
                    'exchange_type': exchange.exchange_type,
                    'status': 'rejected',
                    'reason': reason,
                }
            )
            logger.info(f"Created exchange rejection notification for {exchange.user.username}")
            
            # Send FCM notification
            ExchangeNotificationService._send_fcm_rejection_notification(exchange, reason)
            
        except Exception as e:
            logger.error(f"Error sending exchange rejection notification: {e}")
    
    @staticmethod
    def send_under_review_notification(exchange):
        """
        Send notification when an exchange is submitted for review
        
        Args:
            exchange: The Exchange object under review
        """
        try:
            # Validate input
            if not exchange:
                logger.error("Missing exchange for under review notification")
                return
            
            if not exchange.user:
                logger.warning(f"No user associated with exchange {exchange.uuid}")
                return
            
            # Create notification record
            notification = Notification.objects.create(
                recipient=exchange.user,
                sender=None,  # System notification
                notification_type='EXCHANGE_UNDER_REVIEW',
                title=f"Exchange Submitted for Review",
                message=f"Your exchange '{exchange.org_name}' has been submitted and is under review. We'll notify you once it's reviewed.",
                related_object_id=str(exchange.uuid),
                related_object_type='exchange',
                metadata={
                    'exchange_uuid': str(exchange.uuid),
                    'org_name': exchange.org_name,
                    'exchange_type': exchange.exchange_type,
                    'status': 'under_review',
                }
            )
            logger.info(f"Created exchange under review notification for {exchange.user.username}")
            
            # Send FCM notification
            ExchangeNotificationService._send_fcm_under_review_notification(exchange)
            
        except Exception as e:
            logger.error(f"Error sending exchange under review notification: {e}")
    
    @staticmethod
    def _send_fcm_approval_notification(exchange):
        """
        Send FCM notification for exchange approval
        """
        try:
            template_name = 'EXCHANGE_APPROVED'
            
            context = {
                'org_name': exchange.org_name,
                'exchange_type': exchange.get_exchange_type_display() if exchange.exchange_type else 'Exchange',
            }
            
            data = {
                'type': 'exchange_approved',
                'exchange_uuid': str(exchange.uuid),
                'org_name': exchange.org_name,
                'exchange_type': exchange.exchange_type,
            }
            
            # Try template system first
            try:
                return FCMNotificationService.send_notification_with_template(
                    template_name=template_name,
                    user=exchange.user,
                    context=context,
                    data=data
                )
            except Exception as template_error:
                logger.warning(f"Template {template_name} not found, using fallback")
            
            # Fallback to direct FCM
            return FCMNotificationService.send_notification_to_user(
                user=exchange.user,
                title="🎉 Exchange Approved!",
                body=f"Congratulations! Your exchange '{exchange.org_name}' has been approved and is now live.",
                data=data,
                icon='approval_icon',
                sound='default',
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"Failed to send FCM approval notification: {e}")
            return None
    
    @staticmethod
    def _send_fcm_rejection_notification(exchange, reason=None):
        """
        Send FCM notification for exchange rejection
        """
        try:
            template_name = 'EXCHANGE_REJECTED'
            
            message = f"Your exchange '{exchange.org_name}' has been rejected."
            if reason:
                message += f" Reason: {reason}"
            
            context = {
                'org_name': exchange.org_name,
                'reason': reason or 'Not specified',
            }
            
            data = {
                'type': 'exchange_rejected',
                'exchange_uuid': str(exchange.uuid),
                'org_name': exchange.org_name,
                'exchange_type': exchange.exchange_type,
                'reason': reason,
            }
            
            # Try template system first
            try:
                return FCMNotificationService.send_notification_with_template(
                    template_name=template_name,
                    user=exchange.user,
                    context=context,
                    data=data
                )
            except Exception as template_error:
                logger.warning(f"Template {template_name} not found, using fallback")
            
            # Fallback to direct FCM
            return FCMNotificationService.send_notification_to_user(
                user=exchange.user,
                title="❌ Exchange Rejected",
                body=message,
                data=data,
                icon='rejection_icon',
                sound='default',
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"Failed to send FCM rejection notification: {e}")
            return None
    
    @staticmethod
    def _send_fcm_under_review_notification(exchange):
        """
        Send FCM notification for exchange under review
        """
        try:
            template_name = 'EXCHANGE_UNDER_REVIEW'
            
            context = {
                'org_name': exchange.org_name,
                'exchange_type': exchange.get_exchange_type_display() if exchange.exchange_type else 'Exchange',
            }
            
            data = {
                'type': 'exchange_under_review',
                'exchange_uuid': str(exchange.uuid),
                'org_name': exchange.org_name,
                'exchange_type': exchange.exchange_type,
            }
            
            # Try template system first
            try:
                return FCMNotificationService.send_notification_with_template(
                    template_name=template_name,
                    user=exchange.user,
                    context=context,
                    data=data
                )
            except Exception as template_error:
                logger.warning(f"Template {template_name} not found, using fallback")
            
            # Fallback to direct FCM
            return FCMNotificationService.send_notification_to_user(
                user=exchange.user,
                title="📝 Exchange Under Review",
                body=f"Your exchange '{exchange.org_name}' has been submitted and is under review.",
                data=data,
                icon='review_icon',
                sound='default',
                priority='normal'
            )
            
        except Exception as e:
            logger.error(f"Failed to send FCM under review notification: {e}")
            return None


# Convenience functions for external usage
def send_exchange_approval_notification(exchange):
    """Convenience function for sending exchange approval notifications"""
    return ExchangeNotificationService.send_approval_notification(exchange)


def send_exchange_rejection_notification(exchange, reason=None):
    """Convenience function for sending exchange rejection notifications"""
    return ExchangeNotificationService.send_rejection_notification(exchange, reason)


def send_exchange_under_review_notification(exchange):
    """Convenience function for sending exchange under review notifications"""
    return ExchangeNotificationService.send_under_review_notification(exchange)
