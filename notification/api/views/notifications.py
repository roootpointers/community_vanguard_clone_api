from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.utils import timezone
from django.db.models import Q
from notification.models import Notification
from notification.api.serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    MarkAsReadSerializer,
    CreateNotificationSerializer
)
import django_filters


class NotificationPagination(PageNumberPagination):
    """
    Custom pagination class for notifications with configurable page size
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class NotificationFilter(django_filters.FilterSet):
    """
    Custom filter for notifications
    """
    notification_type = django_filters.ChoiceFilter(
        choices=Notification.NOTIFICATION_TYPES,
        field_name='notification_type'
    )
    is_read = django_filters.BooleanFilter(field_name='is_read')
    date_from = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    date_to = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Notification
        fields = ['notification_type', 'is_read', 'date_from', 'date_to']


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = NotificationFilter
    ordering_fields = ['created_at', 'is_read']
    ordering = ['-created_at']
    search_fields = ['title', 'message']
    lookup_field = 'uuid'
    pagination_class = NotificationPagination
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        """
        Return notifications for the current user only (not deleted)
        """
        return Notification.objects.filter(
            recipient=self.request.user,
            is_deleted=False
        ).select_related('sender')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return NotificationListSerializer
        elif self.action == 'mark_multiple_as_read':
            return MarkAsReadSerializer
        elif self.action == 'create':
            return CreateNotificationSerializer
        return NotificationSerializer
    
    def perform_create(self, serializer):
        """
        Set the recipient to the current user
        """
        serializer.save(recipient=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to perform soft delete
        """
        notification = self.get_object()
        notification.soft_delete()
        response = {
            "success": True,
            "message": "Notification deleted successfully."
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, uuid=None):
        """
        Mark a single notification as read
        """
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        response = {
            "success": True,
            "message": "Notification marked as read.",
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['patch'])
    def mark_multiple_as_read(self, request):
        """
        Mark multiple notifications as read
        """
        serializer = MarkAsReadSerializer(data=request.data)
        if serializer.is_valid():
            notification_uuids = serializer.validated_data['notification_uuids']
            
            notifications = Notification.objects.filter(
                uuid__in=notification_uuids,
                recipient=request.user,
                is_deleted=False
            )
            
            updated_count = 0
            for notification in notifications:
                if not notification.is_read:
                    notification.mark_as_read()
                    updated_count += 1
            
            response = {
                "success": True,
                "message": f"{updated_count} notifications marked as read",
                "updated_count": updated_count
            }
            return Response(response, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        """
        Mark all unread notifications as read for the current user
        """
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
            is_deleted=False
        )
        
        updated_count = unread_notifications.count()
        
        # Bulk update
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        response = {
            "success": True,
            "message": f"All {updated_count} unread notifications marked as read",
            "updated_count": updated_count
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def delete_multiple(self, request):
        """
        Delete multiple notifications
        """
        notification_uuids = request.data.get('notification_uuids', [])
        
        if not notification_uuids:
            return Response(
                {"error": "notification_uuids is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notifications = Notification.objects.filter(
            uuid__in=notification_uuids,
            recipient=request.user,
            is_deleted=False
        )
        
        deleted_count = 0
        for notification in notifications:
            notification.soft_delete()
            deleted_count += 1
        
        response = {
            "success": True,
            "message": f"{deleted_count} notifications deleted successfully",
            "deleted_count": deleted_count
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def delete_all_read(self, request):
        """
        Delete all read notifications for the current user
        """
        read_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=True,
            is_deleted=False
        )
        
        deleted_count = read_notifications.count()
        
        # Bulk update for soft delete
        read_notifications.update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
        
        response = {
            "success": True,
            "message": f"All {deleted_count} read notifications deleted successfully",
            "deleted_count": deleted_count
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications for the current user
        """
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
            is_deleted=False
        ).count()
        
        response = {
            "success": True,
            "message": "Unread notification count retrieved successfully.",
            "data": {
                "unread_count": unread_count
            }
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get notification summary with counts by type
        """
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_deleted=False
        )
        
        total_count = notifications.count()
        unread_count = notifications.filter(is_read=False).count()
        
        # Count by type
        type_counts = {}
        for notification_type, _ in Notification.NOTIFICATION_TYPES:
            type_count = notifications.filter(
                notification_type=notification_type
            ).count()
            unread_type_count = notifications.filter(
                notification_type=notification_type,
                is_read=False
            ).count()
            
            type_counts[notification_type] = {
                'total': type_count,
                'unread': unread_type_count
            }
        
        response = {
            "success": True,
            "message": "Notification summary retrieved successfully.",
            "data": {
                "total_count": total_count,
                "unread_count": unread_count,
                "type_counts": type_counts
            }
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get notifications grouped by type
        """
        notification_type = request.query_params.get('type')
        
        if not notification_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if notification_type not in dict(Notification.NOTIFICATION_TYPES):
            return Response(
                {"error": "Invalid notification type"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notifications = self.get_queryset().filter(
            notification_type=notification_type
        )
        
        # Apply pagination
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = NotificationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def list(self, request, *args, **kwargs):
        """
        List notifications with pagination and custom response format
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Notifications retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single notification with custom response format
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Notification retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

    def create(self, request, *args, **kwargs):
        """
        Create a new notification with custom response format
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "success": True,
                "message": "Notification created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Validation error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
