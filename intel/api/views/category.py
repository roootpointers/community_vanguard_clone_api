from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404

from intel.models import IntelCategory
from intel.api.serializers.category import IntelCategorySerializer

import logging
logger = logging.getLogger(__name__)


class IntelCategoryPagination(PageNumberPagination):
    """Pagination for Intel Categories"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class IntelCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Intel Categories with full CRUD operations.
    
    Permissions:
    - List and retrieve: Any authenticated user
    - Create, update, delete: Admin only
    
    Endpoints:
    - GET /api/intel-category/ - List all categories (paginated)
    - POST /api/intel-category/ - Create new category (admin only)
    - GET /api/intel-category/{uuid}/ - Retrieve specific category
    - PUT /api/intel-category/{uuid}/ - Update category (admin only)
    - PATCH /api/intel-category/{uuid}/ - Partial update (admin only)
    - DELETE /api/intel-category/{uuid}/ - Delete category (admin only)
    """
    queryset = IntelCategory.objects.all()
    serializer_class = IntelCategorySerializer
    pagination_class = IntelCategoryPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """Admin only for create, update, delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """
        List all intel categories with pagination.
        Supports search and ordering.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Intel categories retrieved successfully.',
                'count': queryset.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing intel categories: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve intel categories.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific intel category by UUID."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'message': 'Intel category retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except IntelCategory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Intel category not found.',
                'errors': {'uuid': ['Category with this UUID does not exist.']}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving intel category: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve intel category.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Create a new intel category (Admin only)."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                self.perform_create(serializer)
                logger.info(f"Intel category created: {serializer.data['name']} by {request.user.email}")
                
                return Response({
                    'success': True,
                    'message': 'Intel category created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Failed to create intel category.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating intel category: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create intel category.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update an intel category (Admin only)."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                self.perform_update(serializer)
                logger.info(f"Intel category updated: {serializer.data['name']} by {request.user.email}")
                
                return Response({
                    'success': True,
                    'message': 'Intel category updated successfully.',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': 'Failed to update intel category.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except IntelCategory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Intel category not found.',
                'errors': {'uuid': ['Category with this UUID does not exist.']}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating intel category: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to update intel category.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Partially update an intel category (Admin only)."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an intel category (Admin only)."""
        try:
            instance = self.get_object()
            category_name = instance.name
            
            # Check if category is being used by any intel posts
            intel_count = instance.intels.count()
            if intel_count > 0:
                return Response({
                    'success': False,
                    'message': f'Cannot delete category. It is being used by {intel_count} intel post(s).',
                    'errors': {'category': [f'This category is associated with {intel_count} intel post(s).']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_destroy(instance)
            logger.info(f"Intel category deleted: {category_name} by {request.user.email}")
            
            return Response({
                'success': True,
                'message': 'Intel category deleted successfully.',
                'data': {'name': category_name}
            }, status=status.HTTP_200_OK)
            
        except IntelCategory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Intel category not found.',
                'errors': {'uuid': ['Category with this UUID does not exist.']}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting intel category: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to delete intel category.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
