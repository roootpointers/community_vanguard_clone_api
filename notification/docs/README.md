# Notification App Documentation - Vanguard Backend

This notification app handles all push notifications and in-app notifications for the Vanguard backend application.

## Overview

The notification system for Vanguard supports:
- **Intel notifications** - Comments, likes, and status updates on intelligence reports
- **Exchange notifications** - Approval, rejection, and review status for exchange applications
- **System notifications** - General system updates, warnings, and profile verification

## Notification Types

### Intel-Related Notifications
- `INTEL_COMMENT` - When someone comments on an intel report
- `INTEL_LIKE` - When someone likes an intel report
- `INTEL_STATUS_UPDATE` - When an intel report status changes (pending → verified → investigating → resolved)

### Exchange-Related Notifications
- `EXCHANGE_APPROVED` - When an exchange application is approved
- `EXCHANGE_REJECTED` - When an exchange application is rejected
- `EXCHANGE_UNDER_REVIEW` - When an exchange application is submitted for review

### System Notifications
- `SYSTEM_UPDATES` - General system announcements and updates
- `WARNINGS_FLAGS` - Account warnings or content flags
- `PROFILE_VERIFICATION` - Profile verification status updates
- `ROLE_REQUEST_UPDATE` - Updates on role upgrade requests (Vendor, Community Support Provider, etc.)

## Models

### Notification
Main notification model that stores all notifications.

**Fields:**
- `uuid` - Unique identifier
- `recipient` - User who receives the notification
- `sender` - User who triggered the notification (optional for system notifications)
- `notification_type` - Type of notification (choices above)
- `title` - Notification title
- `message` - Notification message content
- `related_object_id` - UUID of the related object (intel, exchange, comment, etc.)
- `related_object_type` - Type of related object
- `is_read` - Whether notification has been read
- `is_deleted` - Soft delete flag
- `metadata` - Additional JSON data
- `created_at`, `read_at`, `deleted_at` - Timestamps

### FCMDeviceCustom
Extended FCM device model for push notifications.

**Fields:**
- `uuid` - Unique identifier
- `user` - Associated user
- `device_name` - Device name/model
- `registration_id` - FCM registration token
- `type` - Device type (ios, android, web)
- `active` - Whether device is active

### NotificationTemplate
Predefined templates for notifications.

**Fields:**
- `name` - Unique template name
- `notification_type` - Type of notification
- `title_template` - Template for title with placeholders
- `body_template` - Template for body with placeholders
- `icon`, `sound`, `priority` - Notification settings

### NotificationLog
Logs all sent FCM notifications for tracking.

## Services

### IntelNotificationService
Located in `notification/api/intel_notifications.py`

**Methods:**
- `send_comment_notification(intel, comment, commenter)` - Notify intel author of new comment
- `send_like_notification(intel, liker)` - Notify intel author of new like
- `send_status_update_notification(intel, old_status, new_status)` - Notify intel author of status change

### ExchangeNotificationService
Located in `notification/api/exchange_notifications.py`

**Methods:**
- `send_approval_notification(exchange)` - Notify exchange owner of approval
- `send_rejection_notification(exchange, reason=None)` - Notify exchange owner of rejection
- `send_under_review_notification(exchange)` - Notify exchange owner that application is under review

### FCMNotificationService
Located in `notification/api/utils.py`

Core service for sending FCM push notifications.

**Methods:**
- `send_notification_to_user(user, title, body, data, ...)` - Send to specific user
- `send_notification_with_template(template_name, user, context, data)` - Send using template
- `send_bulk_notification(...)` - Send to multiple users
- `cleanup_inactive_devices(days)` - Remove old inactive devices

## Usage Examples

### Intel Comment Notification

```python
from notification.api.intel_notifications import send_intel_comment_notification

# When a user comments on an intel report
send_intel_comment_notification(
    intel=intel_object,
    comment=comment_object,
    commenter=user
)
```

### Exchange Approval Notification

```python
from notification.api.exchange_notifications import send_exchange_approval_notification

# When an exchange is approved
send_exchange_approval_notification(exchange=exchange_object)
```

### Custom System Notification

```python
from notification.api.notification_utils import NotificationService

# Create a system notification
NotificationService.create_system_notification(
    user_uuid=user.uuid,
    title="System Maintenance",
    message="The system will undergo maintenance tonight from 2-4 AM.",
    metadata={"maintenance_type": "scheduled"}
)
```

## API Endpoints

### List User Notifications
```
GET /api/notifications/
```
Returns paginated list of notifications for authenticated user.

**Query Parameters:**
- `notification_type` - Filter by type
- `is_read` - Filter by read status
- `page` - Page number
- `page_size` - Items per page

### Mark Notification as Read
```
PATCH /api/notifications/{uuid}/mark_as_read/
```

### Mark Multiple as Read
```
POST /api/notifications/mark_multiple_as_read/
Body: {"notification_uuids": ["uuid1", "uuid2", ...]}
```

### Delete Notification (Soft Delete)
```
DELETE /api/notifications/{uuid}/
```

### Get Notification Summary
```
GET /api/notifications/summary/
```
Returns counts by type and unread count.

### Get Unread Count
```
GET /api/notifications/unread_count/
```

## Firebase Configuration

The app uses Firebase Cloud Messaging (FCM) for push notifications. Configuration is in:
- `notification/firebase_config.py` - Firebase initialization
- `notification/firebase_account_file/` - Firebase service account JSON file

## Admin Interface

The notification app includes a comprehensive admin interface at `/admin/notification/` with:
- Notification management with filters
- FCM device management
- Notification template editor
- Notification logs viewer

## Migration Notes

This notification app has been updated from a previous version that supported "wink" notifications (from a different app). All wink-related functionality has been removed and replaced with Vanguard-specific features:
- Intel notifications
- Exchange notifications
- System/role/verification notifications

## Testing

To test notifications:

1. **Register a device:**
```python
from notification.models import FCMDeviceCustom

device = FCMDeviceCustom.objects.create(
    user=user,
    registration_id="your_fcm_token",
    type="android",
    device_name="Test Device"
)
```

2. **Send test notification:**
```python
from notification.api.utils import FCMNotificationService

FCMNotificationService.send_notification_to_user(
    user=user,
    title="Test Notification",
    body="This is a test",
    data={"test": "data"}
)
```

## Development Guidelines

1. **Always create database notification record first** before sending FCM
2. **Use notification services** rather than direct FCM calls
3. **Include metadata** for better tracking and debugging
4. **Check notification settings** before sending (if implemented)
5. **Log all FCM sends** using NotificationLog model
6. **Handle FCM errors gracefully** and deactivate invalid tokens

## Future Enhancements

Potential improvements:
- Notification preferences per user
- Email notifications alongside push notifications
- Notification batching/digests
- Real-time WebSocket notifications
- Analytics dashboard for notification metrics
