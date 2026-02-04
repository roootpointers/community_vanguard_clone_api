from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from donation.models import Donation
from donation.api.serializers import DonationSerializer, DonationListSerializer
from donation.api.utils import success_response, error_response, paginated_response


class DonationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing donations.
    
    Provides CRUD operations for donations with search, filter, and ordering capabilities.
    """
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['currency', 'method', 'month', 'year']
    search_fields = ['donor_name', 'donor_email', 'notes']
    ordering_fields = ['created_at', 'amount', 'donor_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action"""
        if self.action == 'list':
            return DonationListSerializer
        return DonationSerializer
    
    def get_queryset(self):
        """
        Optionally restricts the returned donations by filtering against
        a `search` query parameter in the URL.
        """
        queryset = super().get_queryset()
        
        # Custom search across donor name and email
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(donor_name__icontains=search_query) |
                Q(donor_email__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List all donations with standardized response format"""
        queryset = self.filter_queryset(self.get_queryset())
        return paginated_response(
            queryset,
            self.get_serializer_class(),
            request,
        )
    
    def create(self, request, *args, **kwargs):
        """Create a donation with standardized response format"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Donation created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a donation with standardized response format"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Donation retrieved successfully"
        )
    
    def update(self, request, *args, **kwargs):
        """Update a donation with standardized response format"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Donation updated successfully"
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a donation with standardized response format"""
        instance = self.get_object()
        instance.delete()
        return success_response(
            data=None,
            message="Donation deleted successfully",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """
        Get donations grouped by month.
        Query params: year (required)
        """
        year = request.query_params.get('year')
        if not year:
            return error_response(
                message='Year parameter is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            year = int(year)
        except ValueError:
            return error_response(
                message='Year must be a valid integer',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        donations = self.get_queryset().filter(year=year)
        
        # Group by month
        monthly_data = {}
        for month in range(1, 13):
            month_donations = donations.filter(month=month)
            monthly_data[month] = {
                'month': month,
                'count': month_donations.count(),
                'total_amount': sum(d.amount for d in month_donations),
                'donations': DonationListSerializer(month_donations, many=True).data
            }
        
        return success_response(
            data=monthly_data,
            message=f"Donations for year {year} retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def by_donor(self, request):
        """Get donations by donor email"""
        email = request.query_params.get('email')
        if not email:
            return error_response(
                message='Email parameter is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        donations = self.get_queryset().filter(donor_email__iexact=email)
        serializer = self.get_serializer(donations, many=True)
        
        return success_response(
            data={
                'email': email,
                'total_donations': donations.count(),
                'total_amount': float(sum(d.amount for d in donations)),
                'donations': serializer.data
            },
            message=f"Donations for {email} retrieved successfully"
        )
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """
        Bulk delete donations by UUIDs.
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
            message=f'Successfully deleted {deleted_count} donation(s)'
        )
