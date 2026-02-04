# Exchange Booking System

## Overview

A comprehensive slot-based booking system for the exchange platform, built with Django REST Framework. This system enables exchanges to manage their business hours, generate time slots, and accept bookings from users.

## Features

### ✅ Core Functionality
- **Business Hours Management**: Define operating hours for each day of the week
- **Dynamic Slot Generation**: Automatically create time slots based on business hours
- **Smart Booking System**: Prevent double bookings with database constraints
- **Capacity Management**: Support for multiple bookings per slot
- **Status Tracking**: Complete booking lifecycle management
- **RESTful API**: Clean, well-documented REST endpoints

### ✅ Key Benefits
- **No Double Booking**: Database constraints ensure slot availability
- **Automatic Capacity Updates**: Booking counts update in real-time
- **Past Slot Prevention**: Cannot book slots in the past
- **Flexible Hours**: Support for different hours per day, multiple shifts
- **User-Friendly**: Simple API for both users and exchange owners

## Architecture

### Models

#### 1. BusinessHours
Stores operating hours for each day of the week **as a separate relational model**.

**Important Note:** The Exchange model has a `business_hours` JSONField for legacy/display purposes, but the **BusinessHours model is the source of truth** for managing business hours. Always use the BusinessHours model for creating, updating, and querying business hours.

**Key Fields:**
- `exchange`: ForeignKey to Exchange (related_name='operating_hours')
- `day_of_week`: Integer (0=Monday, 6=Sunday)
- `open_time`: Opening time
- `close_time`: Closing time
- `is_closed`: Boolean flag for non-operating days

**Features:**
- Proper relational database model (not JSON)
- Support for multiple shifts per day
- Validation: close_time must be after open_time
- Unique constraint per exchange, day, and time
- Easy to query, filter, and manage in admin

#### 2. TimeSlot
Represents available booking slots.

**Key Fields:**
- `exchange`: ForeignKey to Exchange
- `date`: Date for the slot
- `start_time`: Slot start time
- `end_time`: Slot end time
- `is_available`: Auto-updated based on capacity
- `max_capacity`: Maximum bookings allowed
- `current_bookings`: Current active bookings

**Features:**
- Auto-generated from business hours
- Automatic availability management
- Capacity tracking
- Unique per exchange, date, and time range

#### 3. Booking
User reservations for time slots.

**Key Fields:**
- `user`: ForeignKey to User (authenticated user)
- `exchange`: ForeignKey to Exchange
- `time_slot`: ForeignKey to TimeSlot
- `status`: Pending, Confirmed, Cancelled, Completed, No Show
- `customer_name`, `customer_email`, `customer_phone`: Contact info
- `notes`: User notes
- `admin_notes`: Internal notes

**Features:**
- Prevents duplicate bookings (unique constraint)
- Automatic time slot capacity updates
- Cancellation tracking with timestamps
- Complete audit trail

## API Endpoints

### Business Hours
- `GET /api/business-hours/` - List all business hours
- `POST /api/business-hours/` - Create business hours
- `POST /api/business-hours/bulk_create/` - Bulk create for multiple days
- `PATCH /api/business-hours/{uuid}/` - Update business hours
- `DELETE /api/business-hours/{uuid}/` - Delete business hours

### Time Slots
- `GET /api/time-slots/available_slots/` - Get available slots (public)
- `POST /api/time-slots/generate_slots/` - Generate slots from business hours
- `GET /api/time-slots/` - List all slots (admin)
- `PATCH /api/time-slots/{uuid}/` - Update slot
- `DELETE /api/time-slots/{uuid}/` - Delete slot

### Bookings
- `POST /api/bookings/` - Create a booking
- `GET /api/bookings/` - List user's bookings
- `GET /api/bookings/upcoming/` - Get upcoming bookings
- `GET /api/bookings/history/` - Get past bookings
- `POST /api/bookings/{uuid}/cancel/` - Cancel a booking
- `PATCH /api/bookings/{uuid}/update_status/` - Update status (admin)

## Setup Guide

### 1. Database Migration

```bash
python manage.py makemigrations exchange
python manage.py migrate exchange
```

### 2. Set Up Business Hours

**Option A: Via API (Bulk)**
```json
POST /api/business-hours/bulk_create/
{
  "exchange": "exchange-uuid",
  "hours": [
    {"day_of_week": 0, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 1, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 2, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 3, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 4, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 5, "is_closed": true},
    {"day_of_week": 6, "is_closed": true}
  ]
}
```

**Option B: Via Django Admin**
1. Go to Exchange > Business Hours
2. Add business hours for each day
3. Mark weekends as closed if needed

### 3. Generate Time Slots

```json
POST /api/time-slots/generate_slots/
{
  "exchange_uuid": "exchange-uuid",
  "start_date": "2024-01-20",
  "end_date": "2024-02-20",
  "slot_duration_minutes": 30,
  "max_capacity": 1
}
```

**Parameters:**
- `slot_duration_minutes`: 15, 30, 60, 90, 120, etc.
- `max_capacity`: 1 for one-on-one, higher for group sessions

### 4. Users Can Now Book!

```json
POST /api/bookings/
{
  "time_slot": "slot-uuid",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "First time visitor"
}
```

## Usage Examples

### Frontend Integration

#### 1. Display Available Slots

```javascript
// Fetch available slots for a week
const response = await fetch(
  `/api/time-slots/available_slots/?exchange=${exchangeId}&date_from=2024-01-20&date_to=2024-01-27`
);
const data = await response.json();

// data.slots is organized by date
{
  "2024-01-20": [
    {
      "uuid": "slot-uuid",
      "start_time": "09:00:00",
      "end_time": "09:30:00",
      "available_capacity": 1
    }
  ]
}
```

#### 2. Create a Booking

```javascript
const booking = await fetch('/api/bookings/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    time_slot: selectedSlotId,
    customer_name: "John Doe",
    customer_email: "john@example.com",
    customer_phone: "+1234567890",
    notes: "First visit"
  })
});
```

#### 3. View User's Upcoming Bookings

```javascript
const upcoming = await fetch('/api/bookings/upcoming/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

#### 4. Cancel a Booking

```javascript
await fetch(`/api/bookings/${bookingId}/cancel/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    cancellation_reason: "Schedule conflict"
  })
});
```

## Admin Management

### Django Admin Features

**Business Hours:**
- View/edit hours by day
- Quick filters by day and exchange
- Bulk operations support

**Time Slots:**
- View all slots with availability
- Filter by date, exchange, availability
- Mark slots as available/unavailable
- See booking count inline

**Bookings:**
- View all bookings with details
- Filter by status, date, exchange
- Bulk confirm/complete/no-show actions
- View customer and time slot details
- Add admin notes

### Exchange Owner View

```javascript
// View bookings for an exchange
const bookings = await fetch(
  `/api/bookings/?view=exchange_bookings&exchange=${exchangeId}`,
  {
    headers: { 'Authorization': 'Bearer ' + token }
  }
);
```

## Best Practices

### 1. Slot Generation Strategy
- Generate slots 1-4 weeks at a time
- Set up a cron job to auto-generate future slots
- Don't generate more than 90 days ahead
- Regenerate periodically to ensure availability

### 2. Capacity Planning
- Use `max_capacity = 1` for appointments
- Use `max_capacity > 1` for classes/group sessions
- Adjust based on business needs

### 3. Status Management
```
New Booking → pending
    ↓
Confirmed by staff → confirmed
    ↓
Service completed → completed

Can be cancelled at any stage (pending or confirmed)
Mark as no_show if customer doesn't arrive
```

### 4. Error Handling
- Always check slot availability before booking
- Handle past slot rejections gracefully
- Show clear error messages to users
- Implement retry logic for race conditions

### 5. Performance Tips
- Use date range filters to limit queries
- Implement pagination for large result sets
- Cache available slots for popular exchanges
- Use database indexes (already configured)

## Database Constraints

### Preventing Double Booking

1. **Unique Constraint**: Prevents same user from booking same slot twice
   ```python
   UniqueConstraint(
       fields=['user', 'time_slot'],
       condition=Q(status__in=['pending', 'confirmed'])
   )
   ```

2. **Capacity Management**: Automatic via model methods
   - `increment_bookings()` when booking created
   - `decrement_bookings()` when booking cancelled
   - `is_available` auto-updates based on capacity

3. **Validation**: Multiple layers
   - Model-level validation
   - Serializer validation
   - Database constraints

## Troubleshooting

### Issue: Slots Not Generating

**Solution:**
1. Verify business hours are configured
2. Check date range (must be ≤ 90 days)
3. Ensure slot_duration_minutes is valid (15-480)
4. Check for existing slots (won't duplicate)

### Issue: Can't Book Slot

**Possible Causes:**
- Slot is in the past
- Slot is fully booked
- User already has booking for this slot
- Time slot doesn't exist

**Check:**
```python
slot = TimeSlot.objects.get(uuid=slot_uuid)
print(f"Available: {slot.is_available}")
print(f"Capacity: {slot.current_bookings}/{slot.max_capacity}")
print(f"Is Past: {slot.is_past()}")
```

### Issue: Capacity Not Updating

**Solution:**
- Ensure using model's `save()` method, not queryset `update()`
- Check that booking status is 'pending' or 'confirmed'
- Use booking's `cancel()` method instead of direct status change

## Testing

### Manual Testing Checklist

- [ ] Create business hours for an exchange
- [ ] Generate slots for a date range
- [ ] Verify slots appear in available_slots endpoint
- [ ] Create a booking
- [ ] Verify slot capacity decremented
- [ ] Try to book same slot again (should fail)
- [ ] Cancel booking
- [ ] Verify slot capacity incremented
- [ ] Try to book past slot (should fail)
- [ ] View upcoming bookings
- [ ] Update booking status in admin

### Sample Test Data

Use Django shell:
```python
from exchange.models import Exchange, BusinessHours, TimeSlot, Booking
from accounts.models import User
from datetime import date, time

# Create business hours
exchange = Exchange.objects.first()
BusinessHours.objects.create(
    exchange=exchange,
    day_of_week=0,
    open_time=time(9, 0),
    close_time=time(17, 0)
)

# Generate slots (via API endpoint recommended)
```

## Future Enhancements

### Planned Features
- [ ] Recurring business hours templates
- [ ] Holiday/exception management
- [ ] Waiting list for fully booked slots
- [ ] Email/SMS notifications
- [ ] Buffer time between slots
- [ ] Minimum advance booking time
- [ ] Maximum advance booking time
- [ ] Booking reminders
- [ ] Analytics dashboard
- [ ] Export bookings to calendar (iCal)

### Configuration Options
- [ ] Cancellation deadline enforcement
- [ ] No-show penalties
- [ ] Booking confirmation requirements
- [ ] Custom booking fields
- [ ] Pricing/payment integration
- [ ] Multiple services per exchange

## Security Considerations

1. **Authentication**: All booking operations require authentication
2. **Authorization**: Users can only:
   - View their own bookings
   - Cancel their own bookings
   - Exchange owners can view/manage their exchange's bookings
3. **Rate Limiting**: Implement rate limiting on booking endpoints
4. **Validation**: Multi-layer validation prevents invalid data
5. **Audit Trail**: All actions are timestamped and logged

## Support & Documentation

- **API Documentation**: See `BOOKING_SYSTEM_API.md`
- **Model Reference**: See model docstrings
- **Examples**: See this README
- **Admin Guide**: Django admin is self-documenting

## Contributing

When adding features:
1. Update models with proper validation
2. Create/update serializers
3. Add API endpoints
4. Update documentation
5. Add tests
6. Update admin interface

## License

Same as parent project.
