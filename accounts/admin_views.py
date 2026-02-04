from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, UserProfile, UserRole
from intel.models import Intel
from exchange.models import Exchange
from network.models import Follow
from notification.models import Notification


@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with statistics and charts"""
    
    # User Statistics
    total_users = User.objects.filter(is_superuser=False).count()
    active_users = User.objects.filter(is_active=True, is_superuser=False).count()
    staff_users = User.objects.filter(is_staff=True, is_superuser=False).count()
    
    # New users in last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users_30_days = User.objects.filter(
        date_joined__gte=thirty_days_ago,
        is_superuser=False
    ).count()
    
    # Gender Distribution
    gender_stats = UserProfile.objects.values('gender').annotate(
        count=Count('uuid')
    ).order_by('-count')
    
    # Account Type Distribution
    account_type_stats = User.objects.filter(
        is_superuser=False
    ).values('account_type').annotate(
        count=Count('uuid')
    ).order_by('-count')
    
    # Role Distribution
    role_stats = UserRole.objects.values('role').annotate(
        count=Count('uuid')
    ).order_by('-count')
    
    # Profile Completion Stats
    profiles_completed = User.objects.filter(is_profile=True, is_superuser=False).count()
    roles_completed = User.objects.filter(is_role=True, is_superuser=False).count()
    
    # Branch Distribution (Military)
    branch_stats = UserProfile.objects.exclude(
        branch__isnull=True
    ).exclude(
        branch=''
    ).values('branch').annotate(
        count=Count('uuid')
    ).order_by('-count')
    
    # Intel Statistics
    total_intel = Intel.objects.count()
    approved_intel = Intel.objects.filter(status='approved').count()
    
    # Exchange Statistics
    total_exchanges = Exchange.objects.count()
    approved_exchanges = Exchange.objects.filter(status='approved').count()
    
    # Network Statistics
    total_follows = Follow.objects.count()
    
    # Notification Statistics
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    # User Growth (Last 7 days)
    user_growth = []
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        count = User.objects.filter(
            date_joined__date=date.date(),
            is_superuser=False
        ).count()
        user_growth.append({
            'date': date.strftime('%b %d'),
            'count': count
        })
    
    # Education Level Distribution
    education_stats = UserProfile.objects.exclude(
        education__isnull=True
    ).exclude(
        education=''
    ).values('education').annotate(
        count=Count('uuid')
    ).order_by('-count')
    
    context = {
        # User Stats
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'new_users_30_days': new_users_30_days,
        'profiles_completed': profiles_completed,
        'roles_completed': roles_completed,
        
        # Distribution Stats
        'gender_stats': list(gender_stats),
        'account_type_stats': list(account_type_stats),
        'role_stats': list(role_stats),
        'branch_stats': list(branch_stats),
        'education_stats': list(education_stats),
        
        # Content Stats
        'total_intel': total_intel,
        'approved_intel': approved_intel,
        'total_exchanges': total_exchanges,
        'approved_exchanges': approved_exchanges,
        'total_follows': total_follows,
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        
        # Growth Data
        'user_growth': user_growth,
        
        # Percentages
        'active_percentage': round((active_users / total_users * 100) if total_users > 0 else 0, 1),
        'profile_completion_percentage': round((profiles_completed / total_users * 100) if total_users > 0 else 0, 1),
        'role_completion_percentage': round((roles_completed / total_users * 100) if total_users > 0 else 0, 1),
    }
    
    return render(request, 'admin/dashboard.html', context)
