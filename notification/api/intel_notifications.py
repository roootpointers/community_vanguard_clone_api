"""
Intel-specific notification utilities
Handles all FCM notifications related to Intel operations
"""
import logging
from typing import Optional
from django.contrib.auth import get_user_model
from notification.api.utils import FCMNotificationService
from notification.models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


class IntelNotificationService:
    """
    Service for handling all Intel-related notifications
    """
    
    @staticmethod
    def send_comment_notification(intel, comment, commenter):
        """
        Send notification to intel author when someone comments
        
        Args:
            intel: The Intel object that was commented on
            comment: The comment object
            commenter: The user who created the comment
        """
        try:
            # Validate input parameters
            if not all([intel, comment, commenter]):
                logger.error("Missing required parameters for Intel comment notification")
                return
            
            # Get intel author
            intel_author = intel.user
            
            # Don't send notification if commenter is the author
            if intel_author == commenter:
                logger.info(f"Skipping comment notification - commenter {commenter.username} is the intel author")
                return
            
            # Create notification record in the database
            notification = Notification.objects.create(
                recipient=intel_author,
                sender=commenter,
                notification_type='INTEL_COMMENT',
                title=f"New comment on your intel",
                message=f"{commenter.first_name or commenter.username} commented on your intel report",
                related_object_id=str(comment.uuid),
                related_object_type='intel_comment',
                metadata={
                    'intel_uuid': str(intel.uuid),
                    'comment_uuid': str(comment.uuid),
                    'commenter_uuid': str(commenter.uuid),
                    'intel_description_preview': intel.description[:100] if intel.description else None,
                }
            )
            logger.info(f"Created Intel comment notification for {intel_author.username}")
            
            # Send FCM notification
            IntelNotificationService._send_fcm_comment_notification(
                recipient=intel_author,
                commenter=commenter,
                intel=intel,
                comment=comment
            )
            
        except Exception as e:
            logger.error(f"Error sending Intel comment notification: {e}")

    @staticmethod
    def send_comment_reply_notification(reply_comment, replier):
        """
        Send notification to parent comment owner when someone replies to their comment.
        """
        try:
            if not reply_comment or not replier:
                logger.error("Missing required parameters for Intel reply notification")
                return

            parent_comment = getattr(reply_comment, 'parent_comment', None)
            if not parent_comment:
                return

            recipient = parent_comment.user

            # Don't notify self-replies
            if recipient == replier:
                logger.info(f"Skipping reply notification - replier {replier.username} is the comment owner")
                return

            intel = getattr(reply_comment, 'intel', None)

            # Create notification record
            notification = Notification.objects.create(
                recipient=recipient,
                sender=replier,
                notification_type='INTEL_COMMENT',
                title="New reply to your comment",
                message=f"{replier.first_name or replier.username} replied to your comment",
                related_object_id=str(reply_comment.uuid),
                related_object_type='intel_comment',
                metadata={
                    'intel_uuid': str(intel.uuid) if intel else None,
                    'reply_comment_uuid': str(reply_comment.uuid),
                    'parent_comment_uuid': str(parent_comment.uuid),
                    'replier_uuid': str(replier.uuid),
                }
            )
            logger.info(f"Created Intel comment reply notification for {recipient.username}")

            # Send FCM notification (reuse comment template)
            IntelNotificationService._send_fcm_comment_notification(
                recipient=recipient,
                commenter=replier,
                intel=intel,
                comment=reply_comment
            )

        except Exception as e:
            logger.error(f"Error sending Intel comment reply notification: {e}")
    
    @staticmethod
    def send_like_notification(intel, liker):
        """
        Send notification to intel author when someone likes their post
        
        Args:
            intel: The Intel object that was liked
            liker: The user who liked the intel
        """
        try:
            # Validate input parameters
            if not all([intel, liker]):
                logger.error("Missing required parameters for Intel like notification")
                return
            
            # Get intel author
            intel_author = intel.user
            
            # Don't send notification if liker is the author
            if intel_author == liker:
                logger.info(f"Skipping like notification - liker {liker.username} is the intel author")
                return
            
            # Create notification record in the database
            notification = Notification.objects.create(
                recipient=intel_author,
                sender=liker,
                notification_type='INTEL_LIKE',
                title=f"New like on your intel",
                message=f"{liker.first_name or liker.username} liked your intel report",
                related_object_id=str(intel.uuid),
                related_object_type='intel',
                metadata={
                    'intel_uuid': str(intel.uuid),
                    'liker_uuid': str(liker.uuid),
                    'intel_description_preview': intel.description[:100] if intel.description else None,
                }
            )
            logger.info(f"Created Intel like notification for {intel_author.username}")
            
            # Send FCM notification
            IntelNotificationService._send_fcm_like_notification(
                recipient=intel_author,
                liker=liker,
                intel=intel
            )
            
        except Exception as e:
            logger.error(f"Error sending Intel like notification: {e}")
    
    @staticmethod
    def send_status_update_notification(intel, old_status, new_status):
        """
        Send notification to intel author when status changes
        
        Args:
            intel: The Intel object
            old_status: Previous status
            new_status: New status
        """
        try:
            # Validate input parameters
            if not intel:
                logger.error("Missing intel for status update notification")
                return
            
            intel_author = intel.user
            
            # Create notification record
            notification = Notification.objects.create(
                recipient=intel_author,
                sender=None,  # System notification
                notification_type='INTEL_STATUS_UPDATE',
                title=f"Intel status updated",
                message=f"Your intel report status changed from {old_status} to {new_status}",
                related_object_id=str(intel.uuid),
                related_object_type='intel',
                metadata={
                    'intel_uuid': str(intel.uuid),
                    'old_status': old_status,
                    'new_status': new_status,
                }
            )
            logger.info(f"Created Intel status update notification for {intel_author.username}")
            
            # Send FCM notification
            IntelNotificationService._send_fcm_status_notification(
                recipient=intel_author,
                intel=intel,
                old_status=old_status,
                new_status=new_status
            )
            
        except Exception as e:
            logger.error(f"Error sending Intel status update notification: {e}")
    
    @staticmethod
    def _send_fcm_comment_notification(recipient, commenter, intel, comment):
        """
        Send FCM notification for Intel comment
        """
        try:
            template_name = 'INTEL_COMMENT'
            
            context = {
                'commenter_name': getattr(commenter, 'username', 'Unknown User'),
                'commenter_first_name': getattr(commenter, 'first_name', None) or getattr(commenter, 'username', 'Unknown User'),
                'comment_preview': comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
            }
            
            data = {
                'type': 'intel_comment',
                'commenter_uuid': str(commenter.uuid) if hasattr(commenter, 'uuid') else 'unknown',
                'intel_uuid': str(intel.uuid) if hasattr(intel, 'uuid') else 'unknown',
                'comment_uuid': str(comment.uuid) if hasattr(comment, 'uuid') else 'unknown',
            }
            
            # Try template system first
            try:
                return FCMNotificationService.send_notification_with_template(
                    template_name=template_name,
                    user=recipient,
                    context=context,
                    data=data
                )
            except Exception as template_error:
                logger.warning(f"Template {template_name} not found, using fallback")
            
            # Fallback to direct FCM
            return FCMNotificationService.send_notification_to_user(
                user=recipient,
                title="💬 New Comment on Your Intel",
                body=f"{getattr(commenter, 'first_name', None) or getattr(commenter, 'username', 'Someone')} commented on your intel report",
                data=data,
                icon='comment_icon',
                sound='default',
                priority='normal'
            )
            
        except Exception as e:
            logger.error(f"Failed to send FCM comment notification: {e}")
            return None
    
    @staticmethod
    def _send_fcm_like_notification(recipient, liker, intel):
        """
        Send FCM notification for Intel like
        """
        try:
            template_name = 'INTEL_LIKE'
            
            context = {
                'liker_name': getattr(liker, 'username', 'Unknown User'),
                'liker_first_name': getattr(liker, 'first_name', None) or getattr(liker, 'username', 'Unknown User'),
            }
            
            data = {
                'type': 'intel_like',
                'liker_uuid': str(liker.uuid) if hasattr(liker, 'uuid') else 'unknown',
                'intel_uuid': str(intel.uuid) if hasattr(intel, 'uuid') else 'unknown',
            }
            
            # Try template system first
            try:
                return FCMNotificationService.send_notification_with_template(
                    template_name=template_name,
                    user=recipient,
                    context=context,
                    data=data
                )
            except Exception as template_error:
                logger.warning(f"Template {template_name} not found, using fallback")
            
            # Fallback to direct FCM
            return FCMNotificationService.send_notification_to_user(
                user=recipient,
                title="👍 New Like on Your Intel",
                body=f"{getattr(liker, 'first_name', None) or getattr(liker, 'username', 'Someone')} liked your intel report",
                data=data,
                icon='like_icon',
                sound='default',
                priority='normal'
            )
            
        except Exception as e:
            logger.error(f"Failed to send FCM like notification: {e}")
            return None
    
    @staticmethod
    def _send_fcm_status_notification(recipient, intel, old_status, new_status):
        """
        Send FCM notification for Intel status update
        """
        try:
            template_name = 'INTEL_STATUS_UPDATE'
            
            context = {
                'old_status': old_status,
                'new_status': new_status,
            }
            
            data = {
                'type': 'intel_status_update',
                'intel_uuid': str(intel.uuid) if hasattr(intel, 'uuid') else 'unknown',
                'old_status': old_status,
                'new_status': new_status,
            }
            
            # Try template system first
            try:
                return FCMNotificationService.send_notification_with_template(
                    template_name=template_name,
                    user=recipient,
                    context=context,
                    data=data
                )
            except Exception as template_error:
                logger.warning(f"Template {template_name} not found, using fallback")
            
            # Fallback to direct FCM
            return FCMNotificationService.send_notification_to_user(
                user=recipient,
                title="📋 Intel Status Updated",
                body=f"Your intel report status changed from {old_status} to {new_status}",
                data=data,
                icon='status_icon',
                sound='default',
                priority='normal'
            )
            
        except Exception as e:
            logger.error(f"Failed to send FCM status notification: {e}")
            return None


# Convenience functions for external usage
def send_intel_comment_notification(intel, comment, commenter):
    """Convenience function for sending Intel comment notifications"""
    return IntelNotificationService.send_comment_notification(intel, comment, commenter)


def send_intel_like_notification(intel, liker):
    """Convenience function for sending Intel like notifications"""
    return IntelNotificationService.send_like_notification(intel, liker)


def send_intel_status_update_notification(intel, old_status, new_status):
    """Convenience function for sending Intel status update notifications"""
    return IntelNotificationService.send_status_update_notification(intel, old_status, new_status)


def send_comment_reply_notification(reply_comment, replier):
    """Send notification to parent comment owner when someone replies."""
    return IntelNotificationService.send_comment_reply_notification(reply_comment, replier)
