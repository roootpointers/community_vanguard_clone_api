from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from blog.models import Blog
from blog.api.serializers import BlogSerializer, BlogListSerializer, UserBlogListSerializer
from blog.api.utils import success_response, error_response, paginated_response


class BlogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts.
    
    Provides CRUD operations for blogs with search, filter, and ordering capabilities.
    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'author', 'is_mission_genesis']
    search_fields = ['title', 'content', 'author']
    ordering_fields = ['created_at', 'views_count', 'title']
    ordering = ['-created_at']
    lookup_field = 'uuid'
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action"""
        if self.action == 'list':
            return BlogListSerializer
        return BlogSerializer
    
    def get_queryset(self):
        """
        Optionally restricts the returned blogs by filtering against
        a `search` query parameter in the URL.
        """
        queryset = super().get_queryset()
        
        # Custom search across title, content and author
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__icontains=search_query)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List all blogs with standardized response format"""
        queryset = self.filter_queryset(self.get_queryset())
        return paginated_response(
            queryset, 
            self.get_serializer_class(), 
            request,
            "Blogs retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        """Create a blog with standardized response format"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Blog created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a blog with standardized response format"""
        instance = self.get_object()
        # Increment view count
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Blog retrieved successfully"
        )
    
    def update(self, request, *args, **kwargs):
        """Update a blog with standardized response format"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Blog updated successfully"
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a blog with standardized response format"""
        instance = self.get_object()
        instance.delete()
        return success_response(
            data=None,
            message="Blog deleted successfully",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def published(self, request):
        """Get all published blogs"""
        blogs = self.get_queryset().filter(status='Published')
        return paginated_response(
            blogs,
            self.get_serializer_class(),
            request,
            "Published blogs retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def mission_genesis(self, request):
        """Get the Mission Genesis blog"""
        try:
            blog = Blog.objects.get(is_mission_genesis=True)
            serializer = self.get_serializer(blog)
            return success_response(
                data=serializer.data,
                message="Mission Genesis blog retrieved successfully"
            )
        except Blog.DoesNotExist:
            return error_response(
                message="No Mission Genesis blog found",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def toggle_mission_genesis(self, request, uuid=None):
        """Toggle Mission Genesis status for a blog"""
        blog = self.get_object()
        blog.is_mission_genesis = not blog.is_mission_genesis
        blog.save()
        
        serializer = self.get_serializer(blog)
        return success_response(
            data=serializer.data,
            message=f"Mission Genesis status {'enabled' if blog.is_mission_genesis else 'disabled'}"
        )
    
    @action(detail=False, methods=['get'])
    def by_author(self, request):
        """Get blogs by author"""
        author = request.query_params.get('author')
        if not author:
            return error_response(
                message='Author parameter is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        blogs = self.get_queryset().filter(author__iexact=author)
        return paginated_response(
            blogs,
            self.get_serializer_class(),
            request,
            f"Blogs by {author} retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular blogs by views"""
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        blogs = self.get_queryset().order_by('-views_count')[:limit]
        serializer = self.get_serializer_class()(blogs, many=True)
        
        return success_response(
            data=serializer.data,
            message="Popular blogs retrieved successfully"
        )
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """
        Bulk delete blogs by UUIDs.
        Body: {"uuids": ["uuid1", "uuid2", "uuid3"]}
        """
        uuids = request.data.get('uuids', [])
        if not uuids:
            return error_response(
                message='UUIDs array is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = self.get_queryset().filter(uuid__in=uuids).delete()[0]
        
        return success_response(
            data={'deleted_count': deleted_count},
            message=f'Successfully deleted {deleted_count} blog(s)'
        )
    
    @action(detail=False, methods=['get'], url_path='user-list')
    def user_list(self, request):
        """
        Get all blogs with full content for user-side display.
        Returns published blogs with complete content (no excerpt).
        """
        blogs = self.filter_queryset(self.get_queryset().filter(status='Published'))
        return paginated_response(
            blogs,
            UserBlogListSerializer,
            request,
            "Blogs retrieved successfully"
        )
