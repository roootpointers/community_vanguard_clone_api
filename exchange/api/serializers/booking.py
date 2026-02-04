from rest_framework import serializers
from exchange.models import BusinessHours, TimeSlot, Booking, Exchange
from datetime import datetime, timedelta, time as datetime_time


class BusinessHoursSerializer(serializers.ModelSerializer):
    """Serializer for BusinessHours model."""
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessHours
        fields = [
            'uuid',
            'exchange',
            'day_of_week',
            'day_name',
            'open_time',
            'close_time',
            'is_closed',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_day_name(self, obj):
        """Get the readable day name."""
        days = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
        return days.get(obj.day_of_week, '')
    
    def validate(self, data):
        """Validate business hours."""
        if not data.get('is_closed'):
            if not data.get('open_time') or not data.get('close_time'):
                raise serializers.ValidationError(
                    "Open time and close time are required when not closed."
                )
            if data['close_time'] <= data['open_time']:
                raise serializers.ValidationError(
                    "Close time must be after open time."
                )
        return data


class BusinessHoursReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for BusinessHours (no exchange field in response)."""
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessHours
        fields = [
            'uuid',
            'day_of_week',
            'day_name',
            'open_time',
            'close_time',
            'is_closed'
        ]
    
    def get_day_name(self, obj):
        """Get the readable day name."""
        days = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
        return days.get(obj.day_of_week, '')


class TimeSlotSerializer(serializers.ModelSerializer):
    """
    Serializer for TimeSlot model.
    """
    is_past = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = [
            'uuid',
            'exchange',
            'date',
            'start_time',
            'end_time',
            'is_available',
            'max_capacity',
            'current_bookings',
            'available_capacity',
            'is_past',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'current_bookings', 'created_at', 'updated_at']
    
    def get_is_past(self, obj):
        """Check if slot is in the past."""
        return obj.is_past()
    
    def get_available_capacity(self, obj):
        """Get remaining available slots."""
        return obj.max_capacity - obj.current_bookings


class TimeSlotAvailableSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for available time slots (public view).
    """
    available_capacity = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = [
            'uuid',
            'date',
            'start_time',
            'end_time',
            'available_capacity'
        ]
    
    def get_available_capacity(self, obj):
        """Get remaining available slots."""
        return obj.max_capacity - obj.current_bookings


class CreateTimeSlotSerializer(serializers.Serializer):
    """
    Serializer to generate time slots for a date range.
    """
    exchange_uuid = serializers.UUIDField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    slot_duration_minutes = serializers.IntegerField(
        required=True,
        min_value=15,
        max_value=480,
        help_text="Duration of each slot in minutes (15-480)"
    )
    max_capacity = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text="Maximum bookings per slot"
    )
    
    def validate(self, data):
        """Validate date range."""
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                "End date must be on or after start date."
            )
        
        # Limit to 90 days
        date_diff = (data['end_date'] - data['start_date']).days
        if date_diff > 90:
            raise serializers.ValidationError(
                "Date range cannot exceed 90 days."
            )
        
        return data


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    """
    time_slot_details = TimeSlotAvailableSerializer(source='time_slot', read_only=True)
    exchange_name = serializers.CharField(source='exchange.business_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'uuid',
            'user',
            'exchange',
            'time_slot',
            'time_slot_details',
            'exchange_name',
            'user_name',
            'status',
            'customer_name',
            'customer_email',
            'customer_phone',
            'notes',
            'cancelled_at',
            'cancellation_reason',
            'admin_notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'uuid',
            'cancelled_at',
            'created_at',
            'updated_at'
        ]
    
    def validate_time_slot(self, value):
        """Validate time slot availability."""
        if not value.is_available:
            raise serializers.ValidationError(
                "This time slot is no longer available."
            )
        
        if value.is_past():
            raise serializers.ValidationError(
                "Cannot book a time slot in the past."
            )
        
        return value
    
    def validate(self, data):
        """Validate booking data."""
        # Ensure exchange matches time slot's exchange
        if 'time_slot' in data and 'exchange' in data:
            if data['time_slot'].exchange != data['exchange']:
                raise serializers.ValidationError(
                    "Exchange does not match the selected time slot."
                )
        
        return data


class CreateBookingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating bookings (accepts date/time directly).
    Time slot is auto-created if it doesn't exist.
    """
    exchange = serializers.UUIDField(write_only=True)
    date = serializers.DateField(write_only=True)
    start_time = serializers.TimeField(write_only=True)
    end_time = serializers.TimeField(write_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'exchange',
            'date',
            'start_time',
            'end_time',
            'customer_name',
            'customer_email',
            'customer_phone',
            'notes'
        ]
    
    def validate(self, data):
        """Validate booking data and check availability."""
        from datetime import datetime
        
        # Validate times
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })
        
        # Check if date/time is in the past
        slot_datetime = datetime.combine(data['date'], data['start_time'])
        if slot_datetime < datetime.now():
            raise serializers.ValidationError({
                'date': 'Cannot book a time slot in the past.'
            })
        
        # Validate exchange exists
        try:
            exchange = Exchange.objects.get(uuid=data['exchange'])
        except Exchange.DoesNotExist:
            raise serializers.ValidationError({
                'exchange': 'Exchange not found.'
            })
        
        # Check if user already has a booking today on this exchange
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            existing_booking = Booking.objects.filter(
                user=user,
                exchange=exchange,
                time_slot__date=data['date'],
                status__in=['pending', 'approved']
            ).exists()
            
            if existing_booking:
                raise serializers.ValidationError({
                    'date': 'You already have a booking on this exchange for this day.'
                })
        
        # Check if exchange is open on this day/time
        day_of_week = data['date'].weekday() + 1
        
        try:
            business_hours = BusinessHours.objects.get(
                exchange=exchange,
                day_of_week=day_of_week
            )
        except BusinessHours.DoesNotExist:
            raise serializers.ValidationError({
                'date': 'No business hours defined for this day.'
            })
        
        # Check if closed or time is outside business hours
        if business_hours.is_closed:
            raise serializers.ValidationError({
                'date': f'Exchange is closed on {business_hours.get_day_of_week_display()}.'
            })
        
        if not business_hours.open_time or not business_hours.close_time:
            raise serializers.ValidationError({
                'date': 'Business hours not properly configured for this day.'
            })
        
        if data['start_time'] < business_hours.open_time or data['end_time'] > business_hours.close_time:
            raise serializers.ValidationError({
                'start_time': f'Time must be within business hours ({business_hours.open_time.strftime("%H:%M")} - {business_hours.close_time.strftime("%H:%M")}).'
            })
        
        # Store for use in create()
        data['_exchange_obj'] = exchange
        
        return data
    
    def create(self, validated_data):
        """Create booking with auto-created time slot."""
        from django.db import transaction
        
        # User is passed from view via save(user=request.user)
        user = validated_data.pop('user', None)
        if not user:
            raise serializers.ValidationError('User is required.')
        
        exchange_obj = validated_data.pop('_exchange_obj')
        validated_data.pop('exchange')
        date = validated_data.pop('date')
        start_time = validated_data.pop('start_time')
        end_time = validated_data.pop('end_time')
        
        # Extract customer data
        customer_name = validated_data.pop('customer_name')
        customer_email = validated_data.pop('customer_email')
        customer_phone = validated_data.pop('customer_phone', '')
        notes = validated_data.pop('notes', '')
        
        with transaction.atomic():
            # Get or create the time slot
            time_slot, created = TimeSlot.objects.get_or_create(
                exchange=exchange_obj,
                date=date,
                start_time=start_time,
                end_time=end_time,
                defaults={
                    'max_capacity': 1,
                    'current_bookings': 0,
                    'is_available': True
                }
            )
            
            # Check if slot has capacity
            if time_slot.current_bookings >= time_slot.max_capacity:
                raise serializers.ValidationError({
                    'time_slot': 'This time slot has reached maximum capacity.'
                })
            
            # Create the booking
            booking = Booking.objects.create(
                user=user,
                exchange=exchange_obj,
                time_slot=time_slot,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                notes=notes,
                status='pending'
            )
            
            return booking


class CancelBookingSerializer(serializers.Serializer):
    """
    Serializer for cancelling a booking.
    """
    cancellation_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating booking status (admin only).
    """
    
    class Meta:
        model = Booking
        fields = ['status', 'admin_notes']
    
    def validate_status(self, value):
        """Validate status transitions."""
        instance = self.instance
        
        if instance.status == 'cancelled' and value != 'cancelled':
            raise serializers.ValidationError(
                "Cannot change status of a cancelled booking."
            )
        
        if instance.status == 'completed' and value != 'completed':
            raise serializers.ValidationError(
                "Cannot change status of a completed booking."
            )
        
        return value
