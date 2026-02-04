from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Sum, Count, Avg
from datetime import datetime, timedelta

from donation.models import Donation, DonationTarget
from donation.api.utils import success_response


class DonationStatsView(APIView):
    """
    API view for donation statistics and analytics.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        """
        Get comprehensive donation statistics.
        Query params:
        - currency: Filter by currency (optional)
        - start_date: Start date for filtering (optional)
        - end_date: End date for filtering (optional)
        """
        queryset = Donation.objects.all()
        
        # Apply filters
        currency = request.query_params.get('currency')
        if currency:
            queryset = queryset.filter(currency=currency)
        
        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Calculate statistics
        total_donations = queryset.count()
        total_amount = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        average_donation = queryset.aggregate(Avg('amount'))['amount__avg'] or 0
        
        # Group by currency
        by_currency = {}
        for curr in ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY']:
            curr_donations = queryset.filter(currency=curr)
            by_currency[curr] = {
                'count': curr_donations.count(),
                'total': float(curr_donations.aggregate(Sum('amount'))['amount__sum'] or 0)
            }
        
        # Group by method
        by_method = {}
        for method in ['Card', 'Bank Transfer', 'Paypal', 'Cash', 'Crypto', 'Other']:
            method_donations = queryset.filter(method=method)
            by_method[method] = {
                'count': method_donations.count(),
                'total': float(method_donations.aggregate(Sum('amount'))['amount__sum'] or 0)
            }
        
        # Recent donations (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_count = queryset.filter(created_at__gte=seven_days_ago).count()
        
        # Top donors
        from django.db.models import Sum
        top_donors = (
            queryset.values('donor_name', 'donor_email')
            .annotate(
                total_donated=Sum('amount'),
                donation_count=Count('id')
            )
            .order_by('-total_donated')[:10]
        )
        
        return success_response(
            data={
                'overview': {
                    'total_donations': total_donations,
                    'total_amount': float(total_amount),
                    'average_donation': float(average_donation),
                    'recent_donations_7_days': recent_count,
                },
                'by_currency': by_currency,
                'by_method': by_method,
                'top_donors': list(top_donors),
            },
            message="Donation statistics retrieved successfully"
        )
