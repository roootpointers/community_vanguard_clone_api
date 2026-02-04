# Booking API Migration - ExchangeAppointment Removed

## Summary
The `ExchangeAppointment` model has been completely removed. The system now uses only the **Booking** model for all appointment/booking functionality.

## What Was Changed

### 1. Models Removed
- ❌ `ExchangeAppointment` model deleted
- ❌ `exchange_appointment` database table dropped
- ✅ Using `Booking` model for all bookings

### 2. API Endpoints Changed

**Old Endpoint (REMOVED):**
```
POST /api/appointments/
```

**New Endpoint (USE THIS):**
```
POST /api/bookings/
```

### 3. Request Format

**New Booking Request:**
```json
{
  "exchange": "f00b8259-058f-4725-94b5-361eec60af41",
  "date": "2026-01-15",
  "start_time": "14:00",
  "end_time": "15:00",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "Optional notes"
}
```

**Response:**
```json
{
  "uuid": "booking-uuid",
  "user": "user-uuid",
  "exchange": "exchange-uuid",
  "time_slot": "auto-created-timeslot-uuid",
  "time_slot_details": {
    "uuid": "timeslot-uuid",
    "date": "2026-01-15",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "available_capacity": 0
  },
  "exchange_name": "Business Name",
  "user_name": "User Full Name",
  "status": "pending",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "Optional notes",
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:00:00Z"
}
```

## Features

### ✅ Dynamic Time Slot Creation
- Time slots are **automatically created** when a booking is made
- No need to pre-generate slots
- Slots are created only when needed

### ✅ Real-Time Availability
Check available slots dynamically:
```
GET /api/time-slots/available_slots/?exchange={uuid}&date=2026-01-15&slot_duration=60
```

Response shows which times are available:
```json
{
  "exchange": "f00b8259-058f-4725-94b5-361eec60af41",
  "business_name": "Tech Repair Shop",
  "date": "2026-01-15",
  "day_of_week": 3,
  "slot_duration_minutes": 60,
  "slots": [
    {
      "start_time": "09:00",
      "end_time": "10:00",
      "is_available": true,
      "available_capacity": 1
    },
    {
      "start_time": "14:00",
      "end_time": "15:00",
      "is_available": false,
      "available_capacity": 0
    }
  ]
}
```

### ✅ Automatic Validation
The system validates:
- ✓ Exchange is open on the requested day
- ✓ Time is within business hours
- ✓ Slot is not in the past
- ✓ Slot has available capacity

### ✅ Booking Statuses
- `pending` - Awaiting confirmation
- `confirmed` - Confirmed by exchange owner
- `cancelled` - Cancelled by user or owner
- `completed` - Service completed
- `no_show` - Customer didn't show up

## Admin Panel

### Viewing Bookings
Navigate to: **Admin → Exchange → Bookings**

Features:
- View all bookings
- Filter by status, date, exchange
- Search by customer name, email, phone
- Bulk actions: Confirm, Complete, Mark as No-Show

### Managing Time Slots
Navigate to: **Admin → Exchange → Time Slots**

Features:
- View all time slots
- See current bookings vs capacity
- Mark slots as available/unavailable
- Filter by date, exchange, availability

## Migration Guide

### For API Users

**Before:**
```javascript
// OLD - Don't use this anymore
POST /api/appointments/
{
  "exchange": "uuid",
  "appointment_date": "2026-01-15",
  "name": "John",
  "email": "john@example.com",
  "time_slots": [...]
}
```

**After:**
```javascript
// NEW - Use this instead
POST /api/bookings/
{
  "exchange": "uuid",
  "date": "2026-01-15",
  "start_time": "14:00",
  "end_time": "15:00",
  "customer_name": "John Doe",
  "customer_email": "john@example.com"
}
```

### For Database Administrators

The migration automatically:
1. Drops the `exchange_appointment` table
2. Keeps all existing `TimeSlot` and `Booking` data
3. No data loss for active bookings

## Complete API Endpoints

### Booking Management
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/` - List user's bookings
- `GET /api/bookings/{uuid}/` - Get booking details
- `POST /api/bookings/{uuid}/cancel/` - Cancel booking
- `GET /api/bookings/upcoming/` - Get upcoming bookings
- `GET /api/bookings/history/` - Get past bookings

### Time Slot Management
- `GET /api/time-slots/available_slots/` - Check availability (dynamic)
- `POST /api/time-slots/generate_slots/` - Pre-generate slots (optional)
- `GET /api/time-slots/` - List time slots
- `GET /api/time-slots/{uuid}/` - Get slot details

### Business Hours
- `GET /api/business-hours/?exchange={uuid}` - Get exchange hours
- `POST /api/business-hours/` - Create business hours
- `PUT /api/business-hours/{uuid}/` - Update business hours

## Example Workflow

```bash
# 1. User checks available times
GET /api/time-slots/available_slots/?exchange=xxx&date=2026-01-16&slot_duration=60

# 2. User creates booking
POST /api/bookings/
{
  "exchange": "xxx",
  "date": "2026-01-16",
  "start_time": "10:00",
  "end_time": "11:00",
  "customer_name": "Jane Smith",
  "customer_email": "jane@example.com"
}

# 3. Check availability again - that slot is now unavailable
GET /api/time-slots/available_slots/?exchange=xxx&date=2026-01-16&slot_duration=60

# 4. User views their bookings
GET /api/bookings/upcoming/

# 5. User cancels if needed
POST /api/bookings/{uuid}/cancel/
{
  "cancellation_reason": "Schedule conflict"
}
```

## Benefits of This Change

1. **Simpler API** - One model, clearer purpose
2. **Better Tracking** - Full booking lifecycle management
3. **Capacity Management** - Built-in capacity tracking
4. **No Duplication** - Single source of truth for bookings
5. **Status Workflow** - Clear booking states
6. **Admin Friendly** - Better admin interface for managing bookings

## Notes

- All old appointment data has been removed
- The Booking model provides richer functionality
- Time slots are managed automatically
- Business hours control when bookings can be made
