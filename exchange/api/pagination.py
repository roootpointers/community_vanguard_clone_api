"""
Custom pagination classes for Exchange API.
Uses Django REST Framework's built-in pagination for robustness.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardPagination(PageNumberPagination):
    """
    Standard pagination class used across Exchange endpoints.
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object with enhanced metadata.
        """
        return Response(OrderedDict([
            ('success', True),
            ('message', 'Data retrieved successfully'),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('results', data)
        ]))


class CategoryGroupedPagination(PageNumberPagination):
    """
    Custom pagination for category-grouped exchanges.
    Paginates within each category group.
    
    Query parameters:
    - page: Page number per category (default: 1)
    - page_size: Items per category per page (default: 10, max: 100)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def paginate_grouped_queryset(self, queryset, request, view=None):
        """
        Paginate queryset grouped by category.
        
        Returns:
            OrderedDict: Categories with paginated exchanges
        """
        from django.db.models import Q
        
        self.request = request
        self.page_size = self.get_page_size(request)
        
        if not self.page_size:
            return None
        
        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            self.page_number = int(page_number)
        except (TypeError, ValueError):
            self.page_number = 1
        
        grouped_data = OrderedDict()
        
        # Get all unique categories (excluding null)
        categories = queryset.exclude(
            category__isnull=True
        ).values_list('category__name', 'category').distinct().order_by('category__name')
        
        # For each category, get paginated exchanges
        for category_name, category_id in categories:
            category_exchanges = queryset.filter(category=category_id).order_by('-created_at')
            
            # Use Django Paginator for robust pagination
            from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
            
            paginator = Paginator(category_exchanges, self.page_size)
            
            try:
                page_obj = paginator.page(self.page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            
            grouped_data[category_name] = {
                'count': paginator.count,
                'page': page_obj.number,
                'page_size': self.page_size,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'exchanges': list(page_obj)  # Will be serialized by the view
            }
        
        # Handle exchanges with no category
        no_category_exchanges = queryset.filter(
            category__isnull=True
        ).order_by('-created_at')
        
        if no_category_exchanges.exists():
            from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
            
            paginator = Paginator(no_category_exchanges, self.page_size)
            
            try:
                page_obj = paginator.page(self.page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            
            grouped_data['Uncategorized'] = {
                'count': paginator.count,
                'page': page_obj.number,
                'page_size': self.page_size,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'exchanges': list(page_obj)
            }
        
        return grouped_data
    
    def get_paginated_response(self, grouped_data, total_exchanges):
        """
        Return response for grouped pagination.
        
        Args:
            grouped_data: OrderedDict with category groups
            total_exchanges: Total number of exchanges across all categories
        """
        return Response(OrderedDict([
            ('success', True),
            ('message', 'Exchanges grouped by category retrieved successfully'),
            ('data', grouped_data),
            ('total_categories', len(grouped_data)),
            ('total_exchanges', total_exchanges),
            ('current_page', self.page_number),
            ('page_size', self.page_size)
        ]))
