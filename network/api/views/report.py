"""
Report ViewSet for Network app
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from network.models import Report
from network.api.serializers import (
    ReportSerializer,
    ReportListSerializer,
    ReportStatusUpdateSerializer,
)
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class ReportPagination(PageNumberPagination):
    """Custom pagination for report lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsAdminUser(permissions.BasePermission):
    """Permission to check if user is admin"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user reports
    
    Endpoints:
    - POST /api/network/reports/create/ - Create a report (authenticated users)
    - GET /api/network/reports/my-reports/ - Get current user's reports
    - GET /api/network/reports/admin-list/ - List all reports (admin only)
    - GET /api/network/reports/user/{user_uuid}/ - Get reports about a user (admin only)
    - PATCH /api/network/reports/{uuid}/update-status/ - Update report status (admin only)
    """
    pagination_class = ReportPagination
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create_report', 'my_reports']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['admin_list', 'user_reports', 'update_status']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_report(self, request):
        """
        Create a new report for a user
        
        Request body:
        {
            "reported_user_uuid": "uuid-of-user-to-report",
            "reason": "harassment|hate_speech|spam|inappropriate_content|impersonation|scam|other",
            "description": "detailed description of the violation (optional)"
        }
        """
        try:
            serializer = ReportSerializer(data=request.data, context={'request': request})
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Validation error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            report = serializer.save()
            
            logger.info(f"User {request.user.username} reported {report.reported_user.username} for {report.get_reason_display()}")
            
            return Response({
                'success': True,
                'message': 'Report submitted successfully',
                'data': ReportSerializer(report, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create report',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='my-reports')
    def my_reports(self, request):
        """
        Get list of reports made by the current user
        Query params: page, page_size, status
        """
        try:
            queryset = Report.objects.filter(reported_by=request.user).select_related('reported_user', 'reported_by')
            
            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ReportListSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Your reports retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = ReportListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': 'Your reports retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
                logger.error(f"Error retrieving user reports: {str(e)}")
                return Response({
                    'success': False,
                    'message': 'Failed to retrieve reports',
                    'errors': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
            """
            Update report status (admin only)
            URL: /api/network/reports/{uuid}/update-status/
    
            Request body:
            {
                "status": "pending|resolved|dismissed"
            }
            """
            try:
                report = get_object_or_404(Report, uuid=pk)
                serializer = ReportStatusUpdateSerializer(data=request.data)
    
                if not serializer.is_valid():
                    return Response({
                        'success': False,
                        'message': 'Validation error',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
    
                report.status = serializer.validated_data['status']
                report.save()
    
                logger.info(f"Admin {request.user.username} updated report {report.uuid} status to {report.status}")
    
                return Response({
                    'success': True,
                    'message': f'Report status updated to {report.get_status_display()}',
                    'data': ReportListSerializer(report, context={'request': request}).data
                }, status=status.HTTP_200_OK)
    
            except Exception as e:
                logger.error(f"Error updating report status: {str(e)}")
                return Response({
                    'success': False,
                    'message': 'Failed to update report status',
                    'errors': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='admin-list')
    def admin_list(self, request):
        """
        Get list of all reports (admin only)
        Query params: page, page_size, status, reason
        """
        try:
            queryset = Report.objects.all().select_related('reported_user', 'reported_by')
            
            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Filter by reason if provided
            reason_filter = request.query_params.get('reason')
            if reason_filter:
                queryset = queryset.filter(reason=reason_filter)
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ReportListSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': 'Reports retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = ReportListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': 'Reports retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving reports: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve reports',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='user')
    def user_reports(self, request, pk=None):
        """
        Get all reports about a specific user (admin only)
        URL: /api/network/reports/{user_uuid}/user/
        """
        try:
            user = get_object_or_404(User, uuid=pk)
            queryset = Report.objects.filter(reported_user=user).select_related('reported_user', 'reported_by')
            
            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ReportListSerializer(page, many=True, context={'request': request})
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                return Response({
                    'success': True,
                    'message': f'Reports about {user.username} retrieved successfully',
                    'count': paginated_response.data['count'],
                    'next': paginated_response.data['next'],
                    'previous': paginated_response.data['previous'],
                    'results': serializer.data
                }, status=status.HTTP_200_OK)
            
            serializer = ReportListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'message': f'Reports about {user.username} retrieved successfully',
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving user reports: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve reports',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
