from django.contrib.auth import get_user_model
from notification.models import Notification
from typing import Optional, Dict, Any

User = get_user_model()


class NotificationService:
    """
    Service class for creating and managing notifications
    """
    
    @staticmethod
    def create_notification(
        recipient_uuid: str,
        notification_type: str,
        title: str,
        message: str,
        sender_uuid: Optional[str] = None,
        related_object_id: Optional[str] = None,
        related_object_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Create a new notification
        
        Args:
            recipient_uuid: UUID of the user who will receive the notification
            notification_type: Type of notification (from NOTIFICATION_TYPES)
            title: Notification title
            message: Notification message
            sender_uuid: UUID of the user who triggered the notification (optional)
            related_object_id: ID of related object (post, comment, etc.)
            related_object_type: Type of related object
            metadata: Additional data as dictionary
            
        Returns:
            Created Notification instance
            
        Raises:
            ValueError: If recipient or sender not found
        """
        try:
            recipient = User.objects.get(uuid=recipient_uuid)
        except User.DoesNotExist:
            raise ValueError(f"Recipient with UUID {recipient_uuid} not found")
        
        sender = None
        if sender_uuid:
            try:
                sender = User.objects.get(uuid=sender_uuid)
            except User.DoesNotExist:
                raise ValueError(f"Sender with UUID {sender_uuid} not found")
        
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            metadata=metadata or {}
        )
        
        return notification
    
    @staticmethod
    def create_intel_comment_notification(intel_owner_uuid: str, commenter_uuid: str, 
                                  intel_id: str, comment_id: str):
        """Create an Intel comment notification"""
        try:
            commenter = User.objects.get(uuid=commenter_uuid)
            title = "New comment on your intel"
            message = f"{commenter.username} commented on your intel report"
            
            return NotificationService.create_notification(
                recipient_uuid=intel_owner_uuid,
                notification_type='INTEL_COMMENT',
                title=title,
                message=message,
                sender_uuid=commenter_uuid,
                related_object_id=comment_id,
                related_object_type="intel_comment",
                metadata={"intel_id": intel_id}
            )
        except User.DoesNotExist:
            raise ValueError("Commenter user not found")
    
    @staticmethod
    def create_intel_like_notification(intel_owner_uuid: str, liker_uuid: str, intel_id: str):
        """Create an Intel like notification"""
        try:
            liker = User.objects.get(uuid=liker_uuid)
            title = "New like on your intel"
            message = f"{liker.username} liked your intel report"
            
            return NotificationService.create_notification(
                recipient_uuid=intel_owner_uuid,
                notification_type='INTEL_LIKE',
                title=title,
                message=message,
                sender_uuid=liker_uuid,
                related_object_id=intel_id,
                related_object_type="intel"
            )
        except User.DoesNotExist:
            raise ValueError("Liker user not found")
    
    @staticmethod
    def create_intel_status_notification(intel_owner_uuid: str, intel_id: str, 
                                        old_status: str, new_status: str):
        """Create an Intel status update notification"""
        title = "Intel status updated"
        message = f"Your intel report status changed from {old_status} to {new_status}"
        
        return NotificationService.create_notification(
            recipient_uuid=intel_owner_uuid,
            notification_type='INTEL_STATUS_UPDATE',
            title=title,
            message=message,
            related_object_id=intel_id,
            related_object_type="intel",
            metadata={"old_status": old_status, "new_status": new_status}
        )
    
    @staticmethod
    def create_exchange_approval_notification(exchange_owner_uuid: str, exchange_id: str, org_name: str):
        """Create an Exchange approval notification"""
        title = "Exchange Approved!"
        message = f"Congratulations! Your exchange '{org_name}' has been approved and is now live."
        
        return NotificationService.create_notification(
            recipient_uuid=exchange_owner_uuid,
            notification_type='EXCHANGE_APPROVED',
            title=title,
            message=message,
            related_object_id=exchange_id,
            related_object_type="exchange",
            metadata={"org_name": org_name, "status": "approved"}
        )
    
    @staticmethod
    def create_exchange_rejection_notification(exchange_owner_uuid: str, exchange_id: str, 
                                               org_name: str, reason: Optional[str] = None):
        """Create an Exchange rejection notification"""
        title = "Exchange Rejected"
        message = f"Your exchange '{org_name}' has been rejected."
        if reason:
            message += f" Reason: {reason}"
        
        return NotificationService.create_notification(
            recipient_uuid=exchange_owner_uuid,
            notification_type='EXCHANGE_REJECTED',
            title=title,
            message=message,
            related_object_id=exchange_id,
            related_object_type="exchange",
            metadata={"org_name": org_name, "status": "rejected", "reason": reason}
        )
    
    @staticmethod
    def create_exchange_review_notification(exchange_owner_uuid: str, exchange_id: str, org_name: str):
        """Create an Exchange under review notification"""
        title = "Exchange Submitted for Review"
        message = f"Your exchange '{org_name}' has been submitted and is under review."
        
        return NotificationService.create_notification(
            recipient_uuid=exchange_owner_uuid,
            notification_type='EXCHANGE_UNDER_REVIEW',
            title=title,
            message=message,
            related_object_id=exchange_id,
            related_object_type="exchange",
            metadata={"org_name": org_name, "status": "under_review"}
        )
    
    @staticmethod
    def create_warning_notification(user_uuid: str, warning_type: str, reason: str):
        """Create a warning/flag notification"""
        title = "Account Warning"
        message = f"Your account has received a warning for: {reason}"
        
        return NotificationService.create_notification(
            recipient_uuid=user_uuid,
            notification_type='warnings_flags',
            title=title,
            message=message,
            metadata={"warning_type": warning_type, "reason": reason}
        )
    
    @staticmethod
    def create_system_notification(user_uuid: str, title: str, message: str, 
                                 metadata: Optional[Dict[str, Any]] = None):
        """Create a system notification"""
        return NotificationService.create_notification(
            recipient_uuid=user_uuid,
            notification_type='system_updates',
            title=title,
            message=message,
            metadata=metadata
        )
    
    @staticmethod
    def create_verification_notification(user_uuid: str, verification_type: str, 
                                       status: str, reason: Optional[str] = None):
        """Create a verification notification"""
        notification_type = 'PROFILE_VERIFICATION'  # For Vanguard app, we only have profile verification
        
        if status == 'approved':
            title = f"{verification_type.title()} Verification Approved"
            message = f"Your {verification_type} verification has been approved!"
        elif status == 'rejected':
            title = f"{verification_type.title()} Verification Rejected"
            message = f"Your {verification_type} verification was rejected. {reason or ''}"
        else:
            title = f"{verification_type.title()} Verification Update"
            message = f"Your {verification_type} verification status has been updated to: {status}"
        
        return NotificationService.create_notification(
            recipient_uuid=user_uuid,
            notification_type=notification_type,
            title=title,
            message=message,
            metadata={
                "verification_type": verification_type,
                "status": status,
                "reason": reason
            }
        )
    
    @staticmethod
    def create_role_request_notification(user_uuid: str, role: str, status: str, reason: Optional[str] = None):
        """Create a role request update notification"""
        if status == 'approved':
            title = f"Role Request Approved"
            message = f"Your request to become a {role} has been approved!"
        elif status == 'rejected':
            title = f"Role Request Rejected"
            message = f"Your request to become a {role} was rejected. {reason or ''}"
        else:
            title = f"Role Request Update"
            message = f"Your {role} request status has been updated to: {status}"
        
        return NotificationService.create_notification(
            recipient_uuid=user_uuid,
            notification_type='ROLE_REQUEST_UPDATE',
            title=title,
            message=message,
            metadata={
                "role": role,
                "status": status,
                "reason": reason
            }
        )
    
    @staticmethod
    def mark_notifications_as_read(notification_uuids: list, user_uuid: str) -> int:
        """
        Mark multiple notifications as read for a specific user
        
        Args:
            notification_uuids: List of notification UUIDs
            user_uuid: UUID of the user (for security)
            
        Returns:
            Number of notifications marked as read
        """
        try:
            user = User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            raise ValueError("User not found")
        
        notifications = Notification.objects.filter(
            uuid__in=notification_uuids,
            recipient=user,
            is_read=False,
            is_deleted=False
        )
        
        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1
        
        return count
    
    @staticmethod
    def delete_notifications(notification_uuids: list, user_uuid: str) -> int:
        """
        Soft delete multiple notifications for a specific user
        
        Args:
            notification_uuids: List of notification UUIDs
            user_uuid: UUID of the user (for security)
            
        Returns:
            Number of notifications deleted
        """
        try:
            user = User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            raise ValueError("User not found")
        
        notifications = Notification.objects.filter(
            uuid__in=notification_uuids,
            recipient=user,
            is_deleted=False
        )
        
        count = 0
        for notification in notifications:
            notification.soft_delete()
            count += 1
        
        return count
    
    @staticmethod
    def get_unread_count(user_uuid: str) -> int:
        """Get count of unread notifications for a user"""
        try:
            user = User.objects.get(uuid=user_uuid)
            return Notification.objects.filter(
                recipient=user,
                is_read=False,
                is_deleted=False
            ).count()
        except User.DoesNotExist:
            return 0
