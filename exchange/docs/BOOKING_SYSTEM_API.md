# Booking System API Documentation

## Overview

The booking system allows exchanges to manage their availability and accept bookings from users. It consists of three main components:

1. **Business Hours** - Define when the exchange is open for business
2. **Time Slots** - Available booking slots generated from business hours
3. **Bookings** - User reservations for specific time slots

---

## API Endpoints

### Base URL
All endpoints are prefixed with `/exchange/`

---

## 1. Business Hours Management

**Note:** Business hours can also be created automatically when creating an exchange. See [CREATE_EXCHANGE_WITH_BUSINESS_HOURS.md](CREATE_EXCHANGE_WITH_BUSINESS_HOURS.md) for details.

### 1.1 List Business Hours

**Endpoint:** `GET /api/business-hours/`

**Description:** Get all business hours, optionally filtered by exchange.

**Query Parameters:**
- `exchange` (optional) - UUID of the exchange to filter by

**Response:**
```json
[
  {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "day_of_week": 0,
    "day_name": "Monday",
    "open_time": "09:00:00",
    "close_time": "17:00:00",
    "is_closed": false
  },
  {
    "uuid": "550e8400-e29b-41d4-a716-446655440001",
    "day_of_week": 1,
    "day_name": "Tuesday",
    "open_time": "09:00:00",
    "close_time": "17:00:00",
    "is_closed": false
  }
]
```

**Status Codes:**
- `200 OK` - Success

---

### 1.2 Create Business Hours

**Endpoint:** `POST /api/business-hours/`

**Authentication:** Required

**Description:** Create a new business hours entry for an exchange.

**Request Body:**
```json
{
  "exchange": "550e8400-e29b-41d4-a716-446655440000",
  "day_of_week": 0,
  "open_time": "09:00",
  "close_time": "17:00",
  "is_closed": false
}
```

**Response:**
```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440002",
  "exchange": "550e8400-e29b-41d4-a716-446655440000",
  "day_of_week": 0,
  "day_name": "Monday",
  "open_time": "09:00:00",
  "close_time": "17:00:00",
  "is_closed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `201 Created` - Business hours created successfully
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Authentication required

**Validation Rules:**
- `close_time` must be after `open_time`
- `day_of_week` must be 0-6 (Monday-Sunday)
- If `is_closed` is false, both `open_time` and `close_time` are required

---

### 1.3 Bulk Create Business Hours

**Endpoint:** `POST /api/business-hours/bulk_create/`

**Authentication:** Required

**Description:** Create multiple business hours entries at once.

**Request Body:**
```json
{
  "exchange": "550e8400-e29b-41d4-a716-446655440000",
  "hours": [
    {
      "day_of_week": 0,
      "open_time": "09:00",
      "close_time": "17:00",
      "is_closed": false
    },
    {
      "day_of_week": 1,
      "open_time": "09:00",
      "close_time": "17:00",
      "is_closed": false
    },
    {
      "day_of_week": 6,
      "is_closed": true
    }
  ]
}
```

**Response:**
```json
{
  "created": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440003",
      "day_of_week": 0,
      "day_name": "Monday",
      "open_time": "09:00:00",
      "close_time": "17:00:00",
      "is_closed": false
    }
  ]
}
```

**Status Codes:**
- `201 Created` - All entries created successfully
- `207 Multi-Status` - Some entries created, some failed
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Authentication required

---

### 1.4 Update Business Hours

**Endpoint:** `PUT/PATCH /api/business-hours/{uuid}/`

**Authentication:** Required

**Description:** Update existing business hours.

**Request Body:**
```json
{
  "open_time": "08:00",
  "close_time": "18:00"
}
```

**Status Codes:**
- `200 OK` - Updated successfully
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Business hours not found

---

### 1.5 Delete Business Hours

**Endpoint:** `DELETE /api/business-hours/{uuid}/`

**Authentication:** Required

**Description:** Delete a business hours entry.

**Status Codes:**
- `204 No Content` - Deleted successfully
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Business hours not found

---

## 2. Time Slots Management

### 2.1 List Available Slots

**Endpoint:** `GET /api/time-slots/available_slots/`

**Description:** Get available time slots for an exchange.

**Query Parameters:**
- `exchange` (required) - UUID of the exchange
- `date_from` (optional) - Start date (YYYY-MM-DD)
- `date_to` (optional) - End date (YYYY-MM-DD)

**Example:** `GET /api/time-slots/available_slots/?exchange=550e8400-e29b-41d4-a716-446655440000&date_from=2024-01-20&date_to=2024-01-27`

**Response:**
```json
{
  "exchange": "550e8400-e29b-41d4-a716-446655440000",
  "slots": {
    "2024-01-20": [
      {
        "uuid": "650e8400-e29b-41d4-a716-446655440000",
        "date": "2024-01-20",
        "start_time": "09:00:00",
        "end_time": "09:30:00",
        "available_capacity": 1
      },
      {
        "uuid": "650e8400-e29b-41d4-a716-446655440001",
        "date": "2024-01-20",
        "start_time": "09:30:00",
        "end_time": "10:00:00",
        "available_capacity": 1
      }
    ],
    "2024-01-21": [
      {
        "uuid": "650e8400-e29b-41d4-a716-446655440002",
        "date": "2024-01-21",
        "start_time": "09:00:00",
        "end_time": "09:30:00",
        "available_capacity": 1
      }
    ]
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Missing required parameters

---

### 2.2 Generate Time Slots

**Endpoint:** `POST /api/time-slots/generate_slots/`

**Authentication:** Required

**Description:** Automatically generate time slots based on business hours.

**Request Body:**
```json
{
  "exchange_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "start_date": "2024-01-20",
  "end_date": "2024-01-27",
  "slot_duration_minutes": 30,
  "max_capacity": 1
}
```

**Field Descriptions:**
- `exchange_uuid` - UUID of the exchange
- `start_date` - First date to generate slots for
- `end_date` - Last date to generate slots for
- `slot_duration_minutes` - Duration of each slot (15-480 minutes)
- `max_capacity` - Maximum bookings allowed per slot (default: 1)

**Response:**
```json
{
  "message": "Successfully generated 140 time slots.",
  "slots_created": 140
}
```

**Status Codes:**
- `201 Created` - Slots generated successfully
- `400 Bad Request` - Invalid parameters or no business hours configured
- `401 Unauthorized` - Authentication required

**Validation Rules:**
- `end_date` must be on or after `start_date`
- Date range cannot exceed 90 days
- `slot_duration_minutes` must be between 15 and 480
- Exchange must have business hours configured

**Notes:**
- Only generates slots for days with configured business hours
- Skips slots that already exist
- Automatically creates slots within business hours only

---

### 2.3 List Time Slots (Admin)

**Endpoint:** `GET /api/time-slots/`

**Authentication:** Required

**Description:** Get all time slots with full details (admin view).

**Query Parameters:**
- `exchange` (optional) - Filter by exchange UUID
- `date_from` (optional) - Filter from date
- `date_to` (optional) - Filter to date

**Response:**
```json
[
  {
    "uuid": "650e8400-e29b-41d4-a716-446655440000",
    "exchange": "550e8400-e29b-41d4-a716-446655440000",
    "date": "2024-01-20",
    "start_time": "09:00:00",
    "end_time": "09:30:00",
    "is_available": true,
    "max_capacity": 1,
    "current_bookings": 0,
    "available_capacity": 1,
    "is_past": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Authentication required

---

### 2.4 Update Time Slot

**Endpoint:** `PUT/PATCH /api/time-slots/{uuid}/`

**Authentication:** Required

**Description:** Update a time slot (e.g., change capacity or availability).

**Request Body:**
```json
{
  "max_capacity": 2,
  "is_available": true
}
```

**Status Codes:**
- `200 OK` - Updated successfully
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Time slot not found

---

### 2.5 Delete Time Slot

**Endpoint:** `DELETE /api/time-slots/{uuid}/`

**Authentication:** Required

**Description:** Delete a time slot (only if no active bookings).

**Status Codes:**
- `204 No Content` - Deleted successfully
- `400 Bad Request` - Cannot delete slot with active bookings
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Time slot not found

---

## 3. Bookings Management

### 3.1 Create Booking

**Endpoint:** `POST /api/bookings/`

**Authentication:** Required

**Description:** Book a time slot.

**Request Body:**
```json
{
  "time_slot": "650e8400-e29b-41d4-a716-446655440000",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "First time visitor"
}
```

**Response:**
```json
{
  "uuid": "750e8400-e29b-41d4-a716-446655440000",
  "user": "450e8400-e29b-41d4-a716-446655440000",
  "exchange": "550e8400-e29b-41d4-a716-446655440000",
  "time_slot": "650e8400-e29b-41d4-a716-446655440000",
  "time_slot_details": {
    "uuid": "650e8400-e29b-41d4-a716-446655440000",
    "date": "2024-01-20",
    "start_time": "09:00:00",
    "end_time": "09:30:00",
    "available_capacity": 0
  },
  "exchange_name": "ABC Services",
  "user_name": "John Doe",
  "status": "pending",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "First time visitor",
  "cancelled_at": null,
  "cancellation_reason": null,
  "admin_notes": null,
  "created_at": "2024-01-15T10:45:00Z",
  "updated_at": "2024-01-15T10:45:00Z"
}
```

**Status Codes:**
- `201 Created` - Booking created successfully
- `400 Bad Request` - Invalid data or slot unavailable
- `401 Unauthorized` - Authentication required

**Validation Rules:**
- Time slot must be available
- Time slot cannot be in the past
- User cannot book the same slot twice (unless previous booking is cancelled)

**Notes:**
- User is automatically set from the authenticated user
- Exchange is automatically set from the time slot
- Booking status starts as "pending"
- Time slot capacity is automatically decremented

---

### 3.2 List My Bookings

**Endpoint:** `GET /api/bookings/`

**Authentication:** Required

**Description:** Get all bookings for the authenticated user.

**Query Parameters:**
- `view` (optional) - "my_bookings" (default) or "exchange_bookings"
- `exchange` (optional) - Filter by exchange UUID (for exchange_bookings view)
- `status` (optional) - Filter by status (pending, confirmed, cancelled, completed, no_show)

**Response:**
```json
[
  {
    "uuid": "750e8400-e29b-41d4-a716-446655440000",
    "user": "450e8400-e29b-41d4-a716-446655440000",
    "exchange": "550e8400-e29b-41d4-a716-446655440000",
    "time_slot": "650e8400-e29b-41d4-a716-446655440000",
    "time_slot_details": {
      "uuid": "650e8400-e29b-41d4-a716-446655440000",
      "date": "2024-01-20",
      "start_time": "09:00:00",
      "end_time": "09:30:00",
      "available_capacity": 0
    },
    "exchange_name": "ABC Services",
    "user_name": "John Doe",
    "status": "pending",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1234567890",
    "notes": "First time visitor",
    "created_at": "2024-01-15T10:45:00Z",
    "updated_at": "2024-01-15T10:45:00Z"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Authentication required

---

### 3.3 Get Booking Details

**Endpoint:** `GET /api/bookings/{uuid}/`

**Authentication:** Required

**Description:** Get details of a specific booking.

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Booking not found

---

### 3.4 Get Upcoming Bookings

**Endpoint:** `GET /api/bookings/upcoming/`

**Authentication:** Required

**Description:** Get user's upcoming bookings (pending or confirmed, future dates only).

**Response:**
```json
[
  {
    "uuid": "750e8400-e29b-41d4-a716-446655440000",
    "time_slot_details": {
      "date": "2024-01-20",
      "start_time": "09:00:00",
      "end_time": "09:30:00"
    },
    "exchange_name": "ABC Services",
    "status": "confirmed",
    "customer_name": "John Doe"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Authentication required

---

### 3.5 Get Booking History

**Endpoint:** `GET /api/bookings/history/`

**Authentication:** Required

**Description:** Get user's past bookings.

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Authentication required

---

### 3.6 Cancel Booking

**Endpoint:** `POST /api/bookings/{uuid}/cancel/`

**Authentication:** Required

**Description:** Cancel a booking. Only the user who created the booking can cancel it.

**Request Body:**
```json
{
  "cancellation_reason": "Schedule conflict"
}
```

**Response:**
```json
{
  "uuid": "750e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "cancelled_at": "2024-01-15T11:00:00Z",
  "cancellation_reason": "Schedule conflict",
  "time_slot_details": {
    "uuid": "650e8400-e29b-41d4-a716-446655440000",
    "date": "2024-01-20",
    "start_time": "09:00:00",
    "end_time": "09:30:00",
    "available_capacity": 1
  }
}
```

**Status Codes:**
- `200 OK` - Cancelled successfully
- `400 Bad Request` - Cannot cancel (already cancelled or completed)
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Not the booking owner
- `404 Not Found` - Booking not found

**Notes:**
- Time slot capacity is automatically incremented
- `cancelled_at` timestamp is set automatically
- Cannot cancel already cancelled or completed bookings

---

### 3.7 Update Booking Status (Admin)

**Endpoint:** `PATCH /api/bookings/{uuid}/update_status/`

**Authentication:** Required (Exchange Owner/Admin)

**Description:** Update booking status. For exchange owners/admins only.

**Request Body:**
```json
{
  "status": "confirmed",
  "admin_notes": "Confirmed via phone call"
}
```

**Status Choices:**
- `pending` - Initial state
- `confirmed` - Booking confirmed
- `completed` - Service completed
- `no_show` - Customer didn't show up

**Response:**
```json
{
  "uuid": "750e8400-e29b-41d4-a716-446655440000",
  "status": "confirmed",
  "admin_notes": "Confirmed via phone call",
  "updated_at": "2024-01-15T11:15:00Z"
}
```

**Status Codes:**
- `200 OK` - Updated successfully
- `400 Bad Request` - Invalid status transition
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Not authorized
- `404 Not Found` - Booking not found

**Validation Rules:**
- Cannot change status of cancelled bookings
- Cannot change status of completed bookings

---

## Status Flow

### Booking Status Lifecycle

```
pending → confirmed → completed
   ↓
cancelled (can happen from pending or confirmed)
```

### Time Slot Availability

- `is_available = true` when `current_bookings < max_capacity`
- `is_available = false` when `current_bookings >= max_capacity`
- Automatically updates when bookings are created or cancelled

---

## Error Responses

All error responses follow this format:

```json
{
  "field_name": [
    "Error message 1",
    "Error message 2"
  ]
}
```

Or for general errors:

```json
{
  "error": "Error message"
}
```

Common status codes:
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Common Use Cases

### Setting Up Business Hours

1. Create business hours for each operating day
2. Use bulk_create for efficiency
3. Mark non-operating days as `is_closed: true`

### Generating Slots for a Month

1. Ensure business hours are configured
2. Call `POST /api/time-slots/generate_slots/` with date range
3. System automatically creates slots based on business hours

### Making a Booking

1. Get available slots: `GET /api/time-slots/available_slots/?exchange={uuid}&date_from={date}`
2. Select a slot
3. Create booking: `POST /api/bookings/` with slot UUID

### Managing Bookings

**For Users:**
- View upcoming: `GET /api/bookings/upcoming/`
- View history: `GET /api/bookings/history/`
- Cancel: `POST /api/bookings/{uuid}/cancel/`

**For Exchange Owners:**
- View all bookings: `GET /api/bookings/?view=exchange_bookings&exchange={uuid}`
- Update status: `PATCH /api/bookings/{uuid}/update_status/`

---

## Best Practices

1. **Slot Generation**
   - Generate slots in reasonable batches (1-4 weeks at a time)
   - Regenerate periodically for future availability
   - Don't generate too far in advance (max 90 days)

2. **Capacity Management**
   - Set `max_capacity > 1` for group sessions
   - Set `max_capacity = 1` for one-on-one appointments

3. **Status Management**
   - Use `pending` for new bookings requiring confirmation
   - Move to `confirmed` once verified
   - Mark as `completed` after service delivery
   - Use `no_show` for tracking purposes

4. **Cancellation Policy**
   - Implement cancellation deadlines in your frontend
   - Store cancellation reasons for analytics
   - Consider sending notifications on cancellation

5. **Performance**
   - Use date range filters to limit queries
   - Filter by exchange UUID when possible
   - Use pagination for large result sets

---

## Notes

- All timestamps are in UTC
- All dates use ISO 8601 format (YYYY-MM-DD)
- Time fields accept HH:MM or HH:MM:SS format
- UUIDs are used for all primary keys
- Database constraints prevent double booking
- Time slot capacity is managed automatically
