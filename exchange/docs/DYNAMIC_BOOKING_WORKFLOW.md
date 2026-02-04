# Dynamic Booking Workflow (No Slot Generation Required)

## Overview
This system allows users to book appointments **directly** without pre-generating time slots. Time slots are created automatically when bookings are made, and availability is calculated dynamically from business hours.

## Workflow

### 1. Create Exchange with Operating Hours
When creating an exchange, include `operating_hours` to automatically create business hours.

**Endpoint:** `POST /api/exchanges/`

**Request:**
```json
{
  "business_name": "Tech Repair Shop",
  "description": "Professional electronics repair",
  "operating_hours": [
    {
      "day_of_week": 1,
      "open_time": "09:00",
      "close_time": "17:00",
      "is_closed": false
    },
    {
      "day_of_week": 2,
      "open_time": "09:00",
      "close_time": "17:00",
      "is_closed": false
    },
    {
      "day_of_week": 3,
      "open_time": "09:00",
      "close_time": "17:00",
      "is_closed": false
    },
    {
      "day_of_week": 4,
      "open_time": "09:00",
      "close_time": "17:00",
      "is_closed": false
    },
    {
      "day_of_week": 5,
      "open_time": "09:00",
      "close_time": "17:00",
      "is_closed": false
    },
    {
      "day_of_week": 6,
      "is_closed": true
    },
    {
      "day_of_week": 7,
      "is_closed": true
    }
  ]
}
```

**Response:**
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "business_name": "Tech Repair Shop",
  "description": "Professional electronics repair",
  "operating_hours": [
    {
      "uuid": "...",
      "day_of_week": 1,
      "day_name": "Monday",
      "open_time": "09:00:00",
      "close_time": "17:00:00",
      "is_closed": false
    },
    // ... more days
  ]
}
```

### 2. Check Available Time Slots (Dynamic Calculation)
Get available time slots for a specific date without generating anything.

**Endpoint:** `GET /api/time-slots/available_slots/`

**Query Parameters:**
- `exchange` (required): UUID of the exchange
- `date` (optional): Specific date (YYYY-MM-DD), defaults to today
- `slot_duration` (optional): Duration in minutes, defaults to 60

**Example Request:**
```
GET /api/time-slots/available_slots/?exchange=123e4567-e89b-12d3-a456-426614174000&date=2024-01-15&slot_duration=30
```

**Response:**
```json
{
  "exchange": "123e4567-e89b-12d3-a456-426614174000",
  "business_name": "Tech Repair Shop",
  "date": "2024-01-15",
  "day_of_week": 1,
  "slot_duration_minutes": 30,
  "slots": [
    {
      "start_time": "09:00",
      "end_time": "09:30",
      "is_available": true,
      "available_capacity": 1
    },
    {
      "start_time": "09:30",
      "end_time": "10:00",
      "is_available": true,
      "available_capacity": 1
    },
    {
      "start_time": "10:00",
      "end_time": "10:30",
      "is_available": false,
      "available_capacity": 0
    },
    // ... more slots until 17:00
  ]
}
```

### 3. Create a Booking (Auto-Creates Time Slot)
Book an appointment by providing date and time directly. The system will:
1. Validate the exchange is open at that time
2. Create the time slot if it doesn't exist
3. Create the booking

**Endpoint:** `POST /api/bookings/`

**Request:**
```json
{
  "exchange": "123e4567-e89b-12d3-a456-426614174000",
  "date": "2024-01-15",
  "start_time": "14:00",
  "end_time": "15:00",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "Need laptop screen repair"
}
```

**Response:**
```json
{
  "uuid": "booking-uuid-here",
  "user": "user-uuid",
  "exchange": "123e4567-e89b-12d3-a456-426614174000",
  "time_slot": "time-slot-uuid-auto-created",
  "time_slot_details": {
    "uuid": "time-slot-uuid-auto-created",
    "date": "2024-01-15",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "available_capacity": 0
  },
  "exchange_name": "Tech Repair Shop",
  "user_name": "John Doe",
  "status": "pending",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "Need laptop screen repair",
  "created_at": "2024-01-10T12:00:00Z",
  "updated_at": "2024-01-10T12:00:00Z"
}
```

## Key Features

### ✅ No Pre-Generation Required
- No need to call `generate_slots` endpoint
- Slots are created automatically when bookings are made
- Available slots are calculated on-demand from business hours

### ✅ Real-Time Availability
- When you query `available_slots`, it:
  1. Reads business hours for that day
  2. Calculates all possible time slots
  3. Checks existing bookings
  4. Returns availability status

### ✅ Automatic Validation
- System validates:
  - Exchange is open on the requested day
  - Time is within business hours
  - Slot is not in the past
  - Slot has available capacity

### ✅ Conflict Prevention
- Database constraints prevent double bookings
- Time slot capacity is tracked automatically
- Bookings decrement capacity when created
- Cancelled bookings restore capacity

## Day of Week Reference

| Number | Day       |
|--------|-----------|
| 1      | Monday    |
| 2      | Tuesday   |
| 3      | Wednesday |
| 4      | Thursday  |
| 5      | Friday    |
| 6      | Saturday  |
| 7      | Sunday    |

## Error Handling

### Invalid Date/Time
```json
{
  "date": ["Cannot book a time slot in the past."]
}
```

### Outside Business Hours
```json
{
  "start_time": ["Time must be within business hours (09:00 - 17:00)."]
}
```

### Exchange Closed
```json
{
  "date": ["Exchange is closed on Saturday."]
}
```

### No Capacity
```json
{
  "time_slot": ["This time slot has reached maximum capacity."]
}
```

## Optional: Generate Slots in Advance

If you still want to pre-generate time slots (for performance or other reasons), you can use:

**Endpoint:** `POST /api/time-slots/generate_slots/`

**Request:**
```json
{
  "exchange_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "start_date": "2024-01-15",
  "end_date": "2024-01-31",
  "slot_duration_minutes": 30,
  "max_capacity": 1
}
```

This is optional and only useful if you want to:
- Pre-populate slots for better performance
- Set different capacities for different time periods
- Block out specific times in advance

## Complete Example Flow

```bash
# 1. Create exchange with operating hours
POST /api/exchanges/
{
  "business_name": "My Business",
  "operating_hours": [...]
}

# 2. User checks availability for tomorrow
GET /api/time-slots/available_slots/?exchange=xxx&date=2024-01-16&slot_duration=60

# 3. User books a slot
POST /api/bookings/
{
  "exchange": "xxx",
  "date": "2024-01-16",
  "start_time": "10:00",
  "end_time": "11:00",
  "customer_name": "Jane Smith",
  "customer_email": "jane@example.com"
}

# 4. Check availability again - the booked slot shows as unavailable
GET /api/time-slots/available_slots/?exchange=xxx&date=2024-01-16&slot_duration=60
```

## Summary

**Before (Old Workflow):**
1. Create Exchange with operating_hours
2. **Generate time slots** ← Extra step
3. View available slots
4. Book appointment

**Now (New Workflow):**
1. Create Exchange with operating_hours
2. View available slots ← Calculated dynamically
3. Book appointment ← Auto-creates slot

The system is now **simpler and more dynamic**, removing the need for manual slot generation while maintaining all booking functionality.
