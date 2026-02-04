from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
import logging

from exchange.models import Category, SubCategory
from exchange.api.serializers import (
    CategorySerializer,
    CategoryListSerializer,
    SubCategorySerializer,
    SubCategoryListSerializer
)
from exchange.api.pagination import StandardPagination

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Categories.
    
    List and retrieve are public.
    Create, update, delete require admin permissions.
    """
    queryset = Category.objects.prefetch_related('subcategories').all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = StandardPagination
    
    def get_permissions(self):
        """
        List and retrieve are public.
        Create, update, delete require admin.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def list(self, request, *args, **kwargs):
        """List all categories with pagination."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            
            serializer = self.get_serializer(paginated_queryset, many=True)
            
            response = paginator.get_paginated_response(serializer.data)
            response.data['message'] = 'Categories retrieved successfully'
            
            return response
        
        except Exception as e:
            logger.error(f"Error listing categories: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve categories',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific category with all subcategories."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'message': 'Category retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Category.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Category not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving category: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve category',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Create a new category (admin only)."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                logger.warning(f"Validation error in category creation: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_create(serializer)
            
            logger.info(f"Category created: {serializer.data['name']}")
            
            return Response({
                'success': True,
                'message': 'Category created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to create category',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update category (admin only)."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                logger.warning(f"Validation error in category update: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            
            logger.info(f"Category updated: {serializer.data['name']}")
            
            return Response({
                'success': True,
                'message': 'Category updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update category',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete category (admin only)."""
        try:
            instance = self.get_object()
            category_name = instance.name
            
            self.perform_destroy(instance)
            
            logger.info(f"Category deleted: {category_name}")
            
            return Response({
                'success': True,
                'message': 'Category deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error deleting category: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to delete category',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing SubCategories.
    
    List and retrieve are public.
    Create, update, delete require admin permissions.
    """
    queryset = SubCategory.objects.select_related('category').all()
    serializer_class = SubCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['category__name', 'name']
    pagination_class = StandardPagination
    
    def get_permissions(self):
        """
        List and retrieve are public.
        Create, update, delete require admin.
        """
        if self.action in ['list', 'retrieve', 'by_category']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return SubCategoryListSerializer
        return SubCategorySerializer
    
    def list(self, request, *args, **kwargs):
        """List all subcategories with pagination."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            
            serializer = self.get_serializer(paginated_queryset, many=True)
            
            response = paginator.get_paginated_response(serializer.data)
            response.data['message'] = 'SubCategories retrieved successfully'
            
            return response
        
        except Exception as e:
            logger.error(f"Error listing subcategories: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve subcategories',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific subcategory."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'message': 'SubCategory retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except SubCategory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'SubCategory not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving subcategory: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve subcategory',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Create a new subcategory (admin only)."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                logger.warning(f"Validation error in subcategory creation: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_create(serializer)
            
            logger.info(f"SubCategory created: {serializer.data['name']}")
            
            return Response({
                'success': True,
                'message': 'SubCategory created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating subcategory: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to create subcategory',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update subcategory (admin only)."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                logger.warning(f"Validation error in subcategory update: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            
            logger.info(f"SubCategory updated: {serializer.data['name']}")
            
            return Response({
                'success': True,
                'message': 'SubCategory updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error updating subcategory: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update subcategory',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete subcategory (admin only)."""
        try:
            instance = self.get_object()
            subcategory_name = instance.name
            
            self.perform_destroy(instance)
            
            logger.info(f"SubCategory deleted: {subcategory_name}")
            
            return Response({
                'success': True,
                'message': 'SubCategory deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error deleting subcategory: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to delete subcategory',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='category/(?P<category_uuid>[^/.]+)')
    def by_category(self, request, category_uuid=None):
        """Get all subcategories for a specific category."""
        try:
            # Verify category exists
            try:
                category = Category.objects.get(uuid=category_uuid)
            except Category.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Category not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            queryset = SubCategory.objects.filter(category=category)
            
            serializer = SubCategoryListSerializer(queryset, many=True)
            
            return Response({
                'success': True,
                'message': f'SubCategories for {category.name} retrieved successfully',
                'count': queryset.count(),
                'category': {
                    'uuid': str(category.uuid),
                    'name': category.name
                },
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error retrieving subcategories by category: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve subcategories',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
