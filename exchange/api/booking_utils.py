"""
Utility functions for the booking system.
"""
from datetime import datetime, timedelta, date, time as datetime_time
from django.utils import timezone
from exchange.models import BusinessHours, TimeSlot, Booking


def generate_time_slots_for_exchange(
    exchange,
    start_date,
    end_date,
    slot_duration_minutes=30,
    max_capacity=1
):
    """
    Generate time slots for an exchange based on its business hours.
    
    Args:
        exchange: Exchange instance
        start_date: Start date (date object)
        end_date: End date (date object)
        slot_duration_minutes: Duration of each slot in minutes
        max_capacity: Maximum bookings per slot
    
    Returns:
        dict: {
            'created': int (number of slots created),
            'skipped': int (number already existing),
            'slots': list of created TimeSlot instances
        }
    
    Raises:
        ValueError: If no business hours configured
    """
    business_hours = BusinessHours.objects.filter(
        exchange=exchange,
        is_closed=False
    ).order_by('day_of_week', 'open_time')
    
    if not business_hours.exists():
        raise ValueError(f"No business hours configured for {exchange.business_name}")
    
    created_slots = []
    skipped_count = 0
    current_date = start_date
    slot_duration = timedelta(minutes=slot_duration_minutes)
    
    while current_date <= end_date:
        # Convert weekday() (0=Mon, 6=Sun) to our format (1=Mon, 7=Sun)
        day_of_week = current_date.weekday() + 1
        day_hours = business_hours.filter(day_of_week=day_of_week)
        
        for hours in day_hours:
            current_time = datetime.combine(current_date, hours.open_time)
            end_datetime = datetime.combine(current_date, hours.close_time)
            
            while current_time + slot_duration <= end_datetime:
                slot_start = current_time.time()
                slot_end = (current_time + slot_duration).time()
                
                # Check if slot exists
                existing = TimeSlot.objects.filter(
                    exchange=exchange,
                    date=current_date,
                    start_time=slot_start,
                    end_time=slot_end
                ).first()
                
                if not existing:
                    slot = TimeSlot.objects.create(
                        exchange=exchange,
                        date=current_date,
                        start_time=slot_start,
                        end_time=slot_end,
                        max_capacity=max_capacity
                    )
                    created_slots.append(slot)
                else:
                    skipped_count += 1
                
                current_time += slot_duration
        
        current_date += timedelta(days=1)
    
    return {
        'created': len(created_slots),
        'skipped': skipped_count,
        'slots': created_slots
    }


def get_available_slots_for_date_range(
    exchange,
    start_date,
    end_date=None,
    min_capacity=1
):
    """
    Get available time slots for an exchange within a date range.
    
    Args:
        exchange: Exchange instance or UUID
        start_date: Start date (date object or string)
        end_date: End date (date object or string), optional
        min_capacity: Minimum available capacity required
    
    Returns:
        QuerySet of available TimeSlot instances
    """
    from exchange.models import Exchange
    
    # Handle exchange UUID or instance
    if isinstance(exchange, str):
        from uuid import UUID
        exchange = Exchange.objects.get(uuid=UUID(exchange))
    
    # Handle string dates
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if end_date is None:
        end_date = start_date
    
    queryset = TimeSlot.objects.filter(
        exchange=exchange,
        date__gte=start_date,
        date__lte=end_date,
        is_available=True
    )
    
    # Filter by minimum capacity
    if min_capacity > 0:
        from django.db.models import F
        queryset = queryset.filter(
            current_bookings__lte=F('max_capacity') - min_capacity
        )
    
    return queryset.order_by('date', 'start_time')


def get_slots_by_date(queryset):
    """
    Organize time slots by date.
    
    Args:
        queryset: TimeSlot queryset
    
    Returns:
        dict: {date_string: [slot, slot, ...]}
    """
    slots_by_date = {}
    for slot in queryset:
        date_str = slot.date.isoformat()
        if date_str not in slots_by_date:
            slots_by_date[date_str] = []
        slots_by_date[date_str].append(slot)
    
    return slots_by_date


def check_booking_conflicts(user, time_slot):
    """
    Check if user has any conflicting bookings.
    
    Args:
        user: User instance
        time_slot: TimeSlot instance
    
    Returns:
        bool: True if conflict exists, False otherwise
    """
    conflicting_bookings = Booking.objects.filter(
        user=user,
        time_slot=time_slot,
        status__in=['pending', 'confirmed']
    )
    
    return conflicting_bookings.exists()


def get_user_upcoming_bookings(user, days_ahead=30):
    """
    Get user's upcoming bookings.
    
    Args:
        user: User instance
        days_ahead: Number of days to look ahead (default 30)
    
    Returns:
        QuerySet of Booking instances
    """
    today = timezone.now().date()
    end_date = today + timedelta(days=days_ahead)
    
    return Booking.objects.filter(
        user=user,
        time_slot__date__gte=today,
        time_slot__date__lte=end_date,
        status__in=['pending', 'confirmed']
    ).select_related('exchange', 'time_slot').order_by(
        'time_slot__date',
        'time_slot__start_time'
    )


def get_exchange_bookings_for_date(exchange, booking_date):
    """
    Get all bookings for an exchange on a specific date.
    
    Args:
        exchange: Exchange instance
        booking_date: date object
    
    Returns:
        QuerySet of Booking instances
    """
    return Booking.objects.filter(
        exchange=exchange,
        time_slot__date=booking_date,
        status__in=['pending', 'confirmed']
    ).select_related('user', 'time_slot').order_by('time_slot__start_time')


def cancel_expired_pending_bookings(hours=24):
    """
    Cancel pending bookings that are past their scheduled time.
    
    Args:
        hours: Number of hours past the booking time to consider expired
    
    Returns:
        int: Number of bookings cancelled
    """
    cutoff_datetime = timezone.now() - timedelta(hours=hours)
    cutoff_date = cutoff_datetime.date()
    cutoff_time = cutoff_datetime.time()
    
    # Find expired bookings
    expired_bookings = Booking.objects.filter(
        status='pending',
        time_slot__date__lt=cutoff_date
    ) | Booking.objects.filter(
        status='pending',
        time_slot__date=cutoff_date,
        time_slot__start_time__lt=cutoff_time
    )
    
    count = 0
    for booking in expired_bookings:
        booking.cancel(reason="Automatically cancelled - expired")
        count += 1
    
    return count


def get_booking_statistics(exchange, start_date=None, end_date=None):
    """
    Get booking statistics for an exchange.
    
    Args:
        exchange: Exchange instance
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        dict: Statistics about bookings
    """
    from django.db.models import Count, Q
    
    queryset = Booking.objects.filter(exchange=exchange)
    
    if start_date:
        queryset = queryset.filter(time_slot__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(time_slot__date__lte=end_date)
    
    stats = queryset.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        confirmed=Count('id', filter=Q(status='confirmed')),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled')),
        no_show=Count('id', filter=Q(status='no_show'))
    )
    
    return stats


def is_slot_available(time_slot, check_past=True):
    """
    Check if a time slot is available for booking.
    
    Args:
        time_slot: TimeSlot instance
        check_past: Whether to check if slot is in the past
    
    Returns:
        tuple: (bool, str) - (is_available, reason_if_not)
    """
    if not time_slot.is_available:
        return False, "Slot is marked as unavailable"
    
    if time_slot.current_bookings >= time_slot.max_capacity:
        return False, "Slot is fully booked"
    
    if check_past and time_slot.is_past():
        return False, "Slot is in the past"
    
    return True, "Available"


def bulk_update_slot_capacity(exchange, new_capacity):
    """
    Update max_capacity for all future slots of an exchange.
    
    Args:
        exchange: Exchange instance
        new_capacity: New max_capacity value
    
    Returns:
        int: Number of slots updated
    """
    today = timezone.now().date()
    
    updated = TimeSlot.objects.filter(
        exchange=exchange,
        date__gte=today
    ).update(max_capacity=new_capacity)
    
    # Update availability for all updated slots
    for slot in TimeSlot.objects.filter(exchange=exchange, date__gte=today):
        slot.save()  # This triggers the availability update logic
    
    return updated


def get_next_available_slot(exchange, start_date=None, min_duration_minutes=None):
    """
    Get the next available slot for an exchange.
    
    Args:
        exchange: Exchange instance
        start_date: Optional start date (defaults to today)
        min_duration_minutes: Minimum slot duration required
    
    Returns:
        TimeSlot instance or None
    """
    if start_date is None:
        start_date = timezone.now().date()
    
    queryset = TimeSlot.objects.filter(
        exchange=exchange,
        date__gte=start_date,
        is_available=True
    ).order_by('date', 'start_time')
    
    if min_duration_minutes:
        from django.db.models import F, ExpressionWrapper, fields
        from datetime import datetime
        
        # Filter slots with sufficient duration
        for slot in queryset:
            start_dt = datetime.combine(datetime.today(), slot.start_time)
            end_dt = datetime.combine(datetime.today(), slot.end_time)
            duration = (end_dt - start_dt).total_seconds() / 60
            
            if duration >= min_duration_minutes:
                return slot
        
        return None
    
    return queryset.first()


def create_recurring_business_hours(exchange, template='weekday_9to5'):
    """
    Create business hours from a template.
    
    Args:
        exchange: Exchange instance
        template: Template name ('weekday_9to5', 'weekday_9to6', 'seven_days')
    
    Returns:
        list: Created BusinessHours instances
    """
    templates = {
        'weekday_9to5': [
            {'day_of_week': 1, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(17, 0)},
            {'day_of_week': 2, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(17, 0)},
            {'day_of_week': 3, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(17, 0)},
            {'day_of_week': 4, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(17, 0)},
            {'day_of_week': 5, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(17, 0)},
            {'day_of_week': 6, 'is_closed': True},
            {'day_of_week': 7, 'is_closed': True},
        ],
        'weekday_9to6': [
            {'day_of_week': 1, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(18, 0)},
            {'day_of_week': 2, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(18, 0)},
            {'day_of_week': 3, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(18, 0)},
            {'day_of_week': 4, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(18, 0)},
            {'day_of_week': 5, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(18, 0)},
            {'day_of_week': 6, 'is_closed': True},
            {'day_of_week': 7, 'is_closed': True},
        ],
        'seven_days': [
            {'day_of_week': i, 'open_time': datetime_time(9, 0), 'close_time': datetime_time(17, 0)}
            for i in range(1, 8)
        ]
    }
    
    if template not in templates:
        raise ValueError(f"Unknown template: {template}")
    
    created = []
    for hours_data in templates[template]:
        hours_data['exchange'] = exchange
        hours = BusinessHours.objects.create(**hours_data)
        created.append(hours)
    
    return created
