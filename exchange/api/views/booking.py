from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta, time as datetime_time
from exchange.models import Exchange, BusinessHours, TimeSlot, Booking
from exchange.api.serializers import (
    BusinessHoursSerializer,
    BusinessHoursReadSerializer,
    TimeSlotSerializer,
    TimeSlotAvailableSerializer,
    CreateTimeSlotSerializer,
    BookingSerializer,
    CreateBookingSerializer,
    CancelBookingSerializer,
    BookingStatusUpdateSerializer
)


class BusinessHoursViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing business hours.
    Business hours are managed separately from the Exchange model.
    
    List/Retrieve: Public access
    Create/Update/Delete: Authenticated users (exchange owners)
    """
    queryset = BusinessHours.objects.all()
    serializer_class = BusinessHoursSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """Allow public read access, require authentication for write operations."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter business hours by exchange if provided."""
        queryset = BusinessHours.objects.all()
        exchange_uuid = self.request.query_params.get('exchange', None)
        
        if exchange_uuid:
            queryset = queryset.filter(exchange__uuid=exchange_uuid)
        
        return queryset
    
    def get_serializer_class(self):
        """Use read serializer for list/retrieve actions."""
        if self.action in ['list', 'retrieve']:
            return BusinessHoursReadSerializer
        return BusinessHoursSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_create(self, request):
        """
        Bulk create business hours for an exchange.
        Expected format:
        {
            "exchange": "uuid",
            "hours": [
                {"day_of_week": 0, "open_time": "09:00", "close_time": "17:00"},
                {"day_of_week": 1, "open_time": "09:00", "close_time": "17:00"},
                ...
            ]
        }
        """
        exchange_uuid = request.data.get('exchange')
        hours_data = request.data.get('hours', [])
        
        if not exchange_uuid:
            return Response(
                {'error': 'Exchange UUID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exchange = get_object_or_404(Exchange, uuid=exchange_uuid)
        
        # TODO: Add permission check - only exchange owner should be able to do this
        
        created_hours = []
        errors = []
        
        with transaction.atomic():
            for hour_data in hours_data:
                hour_data['exchange'] = exchange.uuid
                serializer = BusinessHoursSerializer(data=hour_data)
                if serializer.is_valid():
                    serializer.save()
                    created_hours.append(serializer.data)
                else:
                    errors.append({
                        'day_of_week': hour_data.get('day_of_week'),
                        'errors': serializer.errors
                    })
        
        if errors:
            return Response(
                {
                    'created': created_hours,
                    'errors': errors
                },
                status=status.HTTP_207_MULTI_STATUS
            )
        
        return Response(
            {'created': created_hours},
            status=status.HTTP_201_CREATED
        )


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing time slots.
    
    List/Retrieve: Public access (only shows available slots)
    Create/Update/Delete: Authenticated users (exchange owners)
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """Allow public read access for available slots."""
        if self.action in ['list', 'retrieve', 'available_slots']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter time slots based on query parameters."""
        queryset = TimeSlot.objects.select_related('exchange')
        
        # Filter by exchange
        exchange_uuid = self.request.query_params.get('exchange', None)
        if exchange_uuid:
            queryset = queryset.filter(exchange__uuid=exchange_uuid)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Filter by availability (for public view)
        if self.action in ['list', 'available_slots']:
            queryset = queryset.filter(is_available=True)
            # Don't show past slots
            today = timezone.now().date()
            queryset = queryset.filter(date__gte=today)
        
        return queryset.order_by('date', 'start_time')
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action in ['available_slots']:
            return TimeSlotAvailableSerializer
        return TimeSlotSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def available_slots(self, request):
        """
        Dynamically calculate available time slots from BusinessHours.
        No pre-generation required - slots are calculated on-demand.
        
        Query params:
        - exchange: UUID of the exchange (required)
        - date: Specific date (optional, default: today)
        - slot_duration: Duration in minutes (optional, default: 60)
        """
        exchange_uuid = request.query_params.get('exchange')
        if not exchange_uuid:
            return Response(
                {'error': 'Exchange UUID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse date
        date_str = request.query_params.get('date', None)
        slot_duration = int(request.query_params.get('slot_duration', 60))
        
        from datetime import datetime, timedelta, date as dt_date, time as dt_time
        
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = dt_date.today()
        
        # Validate exchange exists
        try:
            exchange = Exchange.objects.get(uuid=exchange_uuid)
        except Exchange.DoesNotExist:
            return Response(
                {'error': 'Exchange not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get day of week (1=Monday to 7=Sunday)
        day_of_week = target_date.weekday() + 1
        
        # Get business hours for this day
        try:
            business_hours = BusinessHours.objects.get(
                exchange=exchange,
                day_of_week=day_of_week
            )
        except BusinessHours.DoesNotExist:
            return Response({
                'exchange': str(exchange.uuid),
                'business_name': exchange.business_name,
                'date': target_date,
                'day_of_week': day_of_week,
                'slots': [],
                'message': 'No business hours defined for this day.'
            })
        
        # Check if closed
        if business_hours.is_closed or not business_hours.open_time or not business_hours.close_time:
            return Response({
                'exchange': str(exchange.uuid),
                'business_name': exchange.business_name,
                'date': target_date,
                'day_of_week': day_of_week,
                'slots': [],
                'message': 'Exchange is closed on this day.'
            })
        
        # Generate time slots dynamically
        slots = []
        current_time = datetime.combine(target_date, business_hours.open_time)
        end_time = datetime.combine(target_date, business_hours.close_time)
        
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=slot_duration)
            if slot_end > end_time:
                break
            
            # Check if this slot exists and is booked
            existing_slot = TimeSlot.objects.filter(
                exchange=exchange,
                date=target_date,
                start_time=current_time.time(),
                end_time=slot_end.time()
            ).first()
            
            is_available = True
            current_bookings = 0
            max_capacity = 1
            
            if existing_slot:
                is_available = existing_slot.is_available
                current_bookings = existing_slot.current_bookings
                max_capacity = existing_slot.max_capacity
            
            slots.append({
                'start_time': current_time.time().strftime('%H:%M'),
                'end_time': slot_end.time().strftime('%H:%M'),
                'is_available': is_available,
                'available_capacity': max_capacity - current_bookings
            })
            
            current_time = slot_end
        
        return Response({
            'exchange': str(exchange.uuid),
            'business_name': exchange.business_name,
            'date': target_date,
            'day_of_week': day_of_week,
            'slot_duration_minutes': slot_duration,
            'slots': slots
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_slots(self, request):
        """
        Generate time slots for a date range based on business hours.
        Expected format:
        {
            "exchange_uuid": "uuid",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "slot_duration_minutes": 30,
            "max_capacity": 1
        }
        """
        serializer = CreateTimeSlotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        exchange = get_object_or_404(Exchange, uuid=data['exchange_uuid'])
        
        # TODO: Add permission check - only exchange owner
        
        # Get business hours for this exchange
        business_hours = BusinessHours.objects.filter(
            exchange=exchange,
            is_closed=False
        ).order_by('day_of_week', 'open_time')
        
        if not business_hours.exists():
            return Response(
                {'error': 'No business hours configured for this exchange.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate slots
        created_slots = []
        current_date = data['start_date']
        slot_duration = timedelta(minutes=data['slot_duration_minutes'])
        
        while current_date <= data['end_date']:
            day_of_week = current_date.weekday()
            
            # Get business hours for this day
            day_hours = business_hours.filter(day_of_week=day_of_week)
            
            for hours in day_hours:
                # Generate slots for this shift
                current_time = datetime.combine(current_date, hours.open_time)
                end_datetime = datetime.combine(current_date, hours.close_time)
                
                while current_time + slot_duration <= end_datetime:
                    slot_start = current_time.time()
                    slot_end = (current_time + slot_duration).time()
                    
                    # Check if slot already exists
                    existing_slot = TimeSlot.objects.filter(
                        exchange=exchange,
                        date=current_date,
                        start_time=slot_start,
                        end_time=slot_end
                    ).first()
                    
                    if not existing_slot:
                        slot = TimeSlot.objects.create(
                            exchange=exchange,
                            date=current_date,
                            start_time=slot_start,
                            end_time=slot_end,
                            max_capacity=data['max_capacity']
                        )
                        created_slots.append(TimeSlotSerializer(slot).data)
                    
                    current_time += slot_duration
            
            current_date += timedelta(days=1)
        
        return Response(
            {
                'message': f'Successfully generated {len(created_slots)} time slots.',
                'slots_created': len(created_slots)
            },
            status=status.HTTP_201_CREATED
        )


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    - List: User's own bookings
    - Create: Book a time slot
    - Retrieve: View booking details
    - Cancel: Cancel a booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        """Return user's bookings or exchange's bookings."""
        user = self.request.user
        queryset = Booking.objects.select_related(
            'user', 'exchange', 'time_slot'
        )
        
        # For update_status action, allow access to bookings on user's exchanges
        if self.action == 'update_status':
            # Get all exchanges owned by this user
            user_exchanges = Exchange.objects.filter(user=user)
            # Return bookings on user's exchanges
            return queryset.filter(exchange__in=user_exchanges)
        
        # Filter by user's own bookings
        view_type = self.request.query_params.get('view', 'my_bookings')
        
        if view_type == 'my_bookings':
            queryset = queryset.filter(user=user)
        elif view_type == 'exchange_bookings':
            # Get bookings for user's exchanges
            exchange_uuid = self.request.query_params.get('exchange')
            if exchange_uuid:
                queryset = queryset.filter(exchange__uuid=exchange_uuid)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'create':
            return CreateBookingSerializer
        elif self.action == 'cancel':
            return CancelBookingSerializer
        elif self.action == 'update_status':
            return BookingStatusUpdateSerializer
        return BookingSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new booking."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'message': 'Validation failed.',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create booking (pass user from request)
            booking = serializer.save(user=request.user)
            
            # Return success response with booking details
            return Response(
                {
                    'success': True,
                    'message': 'Booking created successfully',
                    'data': BookingSerializer(booking).data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exchange.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Exchange not found.',
                    'errors': {
                        'exchange': ['The specified exchange does not exist.']
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except BusinessHours.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Business hours not configured.',
                    'errors': {
                        'date': ['No business hours defined for this day.']
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred while creating the booking.',
                    'errors': {
                        'error': [str(e)]
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, uuid=None):
        """
        Cancel a booking.
        Only the user who made the booking can cancel it.
        """
        booking = self.get_object()
        
        # Check if user owns this booking
        if booking.user != request.user:
            return Response(
                {
                    'success': False,
                    'message': 'You do not have permission to cancel this booking.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status in ['cancelled', 'completed']:
            return Response(
                {
                    'success': False,
                    'message': f'Cannot cancel a {booking.status} booking.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cancellation reason
        serializer = CancelBookingSerializer(data=request.data)
        if serializer.is_valid():
            reason = serializer.validated_data.get('cancellation_reason', None)
            booking.cancel(reason=reason)
            
            return Response(
                {
                    'success': True,
                    'message': 'Booking cancelled successfully',
                    'data': BookingSerializer(booking).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, uuid=None):
        """
        Update booking status.
        Allowed transitions:
        - pending -> approved/rejected
        - approved -> cancelled (via cancel endpoint)
        - any -> no_show
        """
        booking = self.get_object()
        
        serializer = BookingStatusUpdateSerializer(
            booking,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'success': True,
                    'message': 'Booking status updated successfully',
                    'data': BookingSerializer(booking).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def upcoming(self, request):
        """Get user's upcoming bookings."""
        today = timezone.now().date()
        bookings = self.get_queryset().filter(
            time_slot__date__gte=today,
            status__in=['pending', 'confirmed']
        ).order_by('time_slot__date', 'time_slot__start_time')
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def history(self, request):
        """Get user's past bookings."""
        today = timezone.now().date()
        bookings = self.get_queryset().filter(
            time_slot__date__lt=today
        ).order_by('-time_slot__date', '-time_slot__start_time')
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def sent_requests(self, request):
        """
        Get all booking requests sent by the current user.
        These are bookings the user has made on other exchanges.
        
        Query params:
        - status: Filter by booking status (pending, confirmed, cancelled, completed, no_show)
        """
        user = request.user
        
        # Get all bookings created by this user
        bookings = Booking.objects.filter(
            user=user
        ).select_related(
            'exchange', 'time_slot'
        ).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        serializer = BookingSerializer(bookings, many=True)
        
        return Response({
            'success': True,
            'message': 'Sent booking requests retrieved successfully',
            'count': bookings.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def received_requests(self, request):
        """
        Get all booking requests received on the current user's exchanges.
        These are bookings other users have made on exchanges owned by this user.
        
        Query params:
        - exchange: Filter by specific exchange UUID
        - status: Filter by booking status (pending, confirmed, cancelled, completed, no_show)
        """
        user = request.user
        
        # Get all exchanges owned by this user
        user_exchanges = Exchange.objects.filter(user=user)
        
        if not user_exchanges.exists():
            return Response({
                'success': True,
                'message': 'You do not own any exchanges yet.',
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            })
        
        # Get all bookings on user's exchanges
        bookings = Booking.objects.filter(
            exchange__in=user_exchanges
        ).select_related(
            'user', 'exchange', 'time_slot'
        ).order_by('-created_at')
        
        # Filter by specific exchange if provided
        exchange_uuid = request.query_params.get('exchange', None)
        if exchange_uuid:
            bookings = bookings.filter(exchange__uuid=exchange_uuid)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        serializer = BookingSerializer(bookings, many=True)
        
        return Response({
            'success': True,
            'message': 'Received booking requests retrieved successfully',
            'count': bookings.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })
