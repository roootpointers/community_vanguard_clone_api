from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from donation.models import DonationTarget
from donation.api.serializers import DonationTargetSerializer
from donation.api.utils import success_response, error_response, paginated_response


class DonationTargetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing donation targets.
    
    Provides CRUD operations for donation targets with filter capabilities.
    """
    queryset = DonationTarget.objects.all()
    serializer_class = DonationTargetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['month', 'year', 'currency']
    ordering_fields = ['year', 'month', 'target_amount']
    ordering = ['-year', '-month']
    
    def list(self, request, *args, **kwargs):
        """List all targets with standardized response format"""
        queryset = self.filter_queryset(self.get_queryset())
        return paginated_response(
            queryset, 
            self.get_serializer_class(), 
            request,
            "Donation targets retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        """Create a target with standardized response format"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Donation target created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a target with standardized response format"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Donation target retrieved successfully"
        )
    
    def update(self, request, *args, **kwargs):
        """Update a target with standardized response format"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Donation target updated successfully"
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a target with standardized response format"""
        instance = self.get_object()
        instance.delete()
        return success_response(
            data=None,
            message="Donation target deleted successfully",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_period(self, request):
        """
        Get target for a specific month and year.
        Query params: month, year
        """
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return error_response(
                message='Both month and year parameters are required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return error_response(
                message='Month and year must be valid integers',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target = DonationTarget.objects.get(month=month, year=year)
            serializer = self.get_serializer(target)
            return success_response(
                data=serializer.data,
                message=f"Target for {target.get_month_name()} {year} retrieved successfully"
            )
        except DonationTarget.DoesNotExist:
            return error_response(
                message='No target found for the specified period',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def current_year(self, request):
        """Get all targets for the current year"""
        from datetime import datetime
        year = datetime.now().year
        targets = self.get_queryset().filter(year=year)
        serializer = self.get_serializer(targets, many=True)
        return success_response(
            data=serializer.data,
            message=f"Targets for current year ({year}) retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def progress_tracker(self, request):
        """
        Get progress tracker data for multiple months.
        Query params: months (comma-separated), year
        Example: ?months=1,2,3&year=2024
        """
        months_param = request.query_params.get('months')
        year = request.query_params.get('year')
        
        if not months_param or not year:
            return error_response(
                message='Both months and year parameters are required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            months = [int(m.strip()) for m in months_param.split(',')]
            year = int(year)
        except ValueError:
            return error_response(
                message='Invalid months or year format',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        targets = self.get_queryset().filter(month__in=months, year=year)
        serializer = self.get_serializer(targets, many=True)
        
        # Calculate overall progress
        total_target = sum(t.target_amount for t in targets)
        total_collected = sum(t.get_collected_amount() for t in targets)
        overall_progress = (total_collected / total_target * 100) if total_target > 0 else 0
        
        return success_response(
            data={
                'year': year,
                'months': months,
                'targets': serializer.data,
                'overall': {
                    'total_target': float(total_target),
                    'total_collected': float(total_collected),
                    'progress_percentage': round(overall_progress, 2)
                }
            },
            message="Progress tracker data retrieved successfully"
        )
