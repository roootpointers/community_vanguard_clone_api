from rest_framework.routers import SimpleRouter
from .views.fcm import (
    FCMDeviceViewSet, NotificationViewSet as FCMNotificationViewSet,
    NotificationTemplateViewSet, NotificationStatsViewSet, NotificationManagementViewSet
)
from .views.notifications import NotificationViewSet

from django.urls import path, include

router = SimpleRouter()
router.register("api/devices", FCMDeviceViewSet, basename="devices")
router.register("api/templates", NotificationTemplateViewSet, basename="templates")
router.register("api/notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    # Router URLs - includes standard CRUD operations
    path("", include(router.urls)),
    
    # FCM Notification sending endpoints (using FCMNotificationViewSet)
    path('api/fcm/send/', FCMNotificationViewSet.as_view({'post': 'send'}), name='send_fcm_notification'),
    path('api/fcm/send-bulk/', FCMNotificationViewSet.as_view({'post': 'send_bulk'}), name='send_bulk_fcm_notification'),
    path('api/fcm/test/', FCMNotificationViewSet.as_view({'post': 'test_notification'}), name='test_fcm_notification'),
    
    # Statistics endpoints
    path('api/stats/devices/', NotificationStatsViewSet.as_view({'get': 'devices'}), name='device_stats'),
    path('api/stats/notifications/', NotificationStatsViewSet.as_view({'get': 'notifications'}), name='notification_stats'),
    
    # Management endpoints
    path('api/management/cleanup/', NotificationManagementViewSet.as_view({'post': 'cleanup_devices'}), name='cleanup_devices'),
    path('api/management/health/', NotificationManagementViewSet.as_view({'get': 'health_check'}), name='health_check'),
]