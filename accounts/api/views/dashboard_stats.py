from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from accounts.models.user import User
from intel.models import Intel
from exchange.models import Exchange

import logging
logger = logging.getLogger(__name__)


class DashboardStatsAPIView(APIView):
    """
    API endpoint for admin dashboard statistics.
    Returns aggregated data for:
    - Total users count
    - Total intel (coalitions) count
    - Total exchanges count
    - New user sign-ups per week/month (for charts)
    
    Only accessible by admin users (is_staff=True or is_superuser=True).
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """
        GET /api/accounts/dashboard-stats/
        
        Returns dashboard statistics for admin panel.
        """
        try:
            # Total counts
            total_users = User.objects.filter(is_superuser=False).count()
            total_intel = Intel.objects.count()
            total_exchanges = Exchange.objects.count()
            
            # Active users
            active_users = User.objects.filter(is_active=True, is_superuser=False).count()
            
            # New users statistics
            now = timezone.now()
            
            # This week (last 7 days)
            week_ago = now - timedelta(days=7)
            new_users_this_week = User.objects.filter(
                date_joined__gte=week_ago,
                is_superuser=False
            ).count()
            
            # This month (last 30 days)
            month_ago = now - timedelta(days=30)
            new_users_this_month = User.objects.filter(
                date_joined__gte=month_ago,
                is_superuser=False
            ).count()
            
            # Weekly sign-ups data (last 12 weeks for chart)
            weekly_signups = []
            for i in range(11, -1, -1):
                week_start = now - timedelta(weeks=i+1)
                week_end = now - timedelta(weeks=i)
                count = User.objects.filter(
                    date_joined__gte=week_start,
                    date_joined__lt=week_end,
                    is_superuser=False
                ).count()
                weekly_signups.append({
                    'period': week_end.strftime('%b %d'),
                    'count': count
                })
            
            # Monthly sign-ups data (last 7 months for chart)
            monthly_signups = []
            for i in range(6, -1, -1):
                # Calculate the start and end of each month period
                month_end = now - timedelta(days=30*i)
                month_start = month_end - timedelta(days=30)
                count = User.objects.filter(
                    date_joined__gte=month_start,
                    date_joined__lt=month_end,
                    is_superuser=False
                ).count()
                monthly_signups.append({
                    'period': month_end.strftime('%b'),
                    'count': count
                })
            
            # Status breakdown for intel
            intel_status = Intel.objects.values('status').annotate(
                count=Count('uuid')
            ).order_by('-count')
            
            # Status breakdown for exchanges
            exchange_status = Exchange.objects.values('status').annotate(
                count=Count('uuid')
            ).order_by('-count')
            
            response_data = {
                'success': True,
                'message': 'Dashboard statistics retrieved successfully.',
                'data': {
                    'overview': {
                        'total_users': total_users,
                        'total_coalitions': total_intel,  # Intel count labeled as coalitions
                        'total_exchanges': total_exchanges,
                        'active_users': active_users,
                        'new_users_this_week': new_users_this_week,
                        'new_users_this_month': new_users_this_month
                    },
                    'signups': {
                        'weekly': weekly_signups,
                        'monthly': monthly_signups
                    },
                    'intel_breakdown': {
                        'by_status': list(intel_status)
                    },
                    'exchange_breakdown': {
                        'by_status': list(exchange_status)
                    }
                }
            }
            
            logger.info(f"Dashboard stats retrieved by admin: {request.user.email}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving dashboard stats: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Something went wrong while retrieving dashboard statistics.',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)