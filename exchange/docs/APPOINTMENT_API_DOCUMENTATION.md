# Exchange Appointment Booking API Documentation

## Overview

The Appointment Booking API allows users to book appointments with exchanges. Users fill out a booking form with their details, select date and time slots, and submit the appointment request. Exchange owners can view and manage appointment bookings.

---

## Base URL

```
/api/appointments/
```

---

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Create Appointment Booking

**Endpoint:** `POST /api/appointments/`

**Description:** Submit a new appointment booking for an exchange.

**Authentication:** Required

**Request Body:**

```json
{
  "exchange": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "appointment_date": "2025-12-15",
  "time_slots": [
    {
      "day": "Wednesday",
      "start_time": "10:00 AM",
      "end_time": "12:00 AM",
      "selected": true
    },
    {
      "day": "Friday",
      "start_time": "12:00 PM",
      "end_time": "02:00 PM",
      "selected": true
    },
    {
      "day": "Saturday",
      "start_time": "12:00 PM",
      "end_time": "02:00 PM",
      "selected": false
    }
  ],
  "notes": "I would like to discuss partnership opportunities"
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exchange` | UUID | Yes | UUID of the exchange to book appointment with |
| `name` | String | Yes | Full name of the person booking |
| `email` | Email | Yes | Email address for contact |
| `appointment_date` | Date | Yes | Preferred date for appointment (YYYY-MM-DD) |
| `time_slots` | Array | Yes | Array of time slot objects with selection status |
| `notes` | String | No | Additional notes or requirements (max 500 chars) |

**Time Slot Object Structure:**

```json
{
  "day": "Wednesday",           // Day name
  "start_time": "10:00 AM",    // Start time (12-hour format)
  "end_time": "12:00 AM",      // End time (12-hour format)
  "selected": true             // Selection status (boolean)
}
```

**Response (201 Created):**

```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "exchange": "exchange-uuid",
  "user": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "appointment_date": "2025-12-15",
  "time_slots": [
    {
      "day": "Wednesday",
      "start_time": "10:00 AM",
      "end_time": "12:00 AM",
      "selected": true
    },
    {
      "day": "Friday",
      "start_time": "12:00 PM",
      "end_time": "02:00 PM",
      "selected": true
    }
  ],
  "status": "pending",
  "notes": "I would like to discuss partnership opportunities",
  "created_at": "2025-12-03T10:30:00Z",
  "updated_at": "2025-12-03T10:30:00Z"
}
```

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/appointments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "exchange-uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "appointment_date": "2025-12-15",
    "time_slots": [
      {
        "day": "Wednesday",
        "start_time": "10:00 AM",
        "end_time": "12:00 AM",
        "selected": true
      }
    ],
    "notes": "Partnership discussion"
  }'
```

**Validation Rules:**

- Name cannot be empty
- Email must be valid format
- Appointment date must be in the future
- At least one time slot must be provided
- Selected time slots must have day, start_time, and end_time
- Time slots must be a valid array of objects

**Error Responses:**

```json
// 400 Bad Request - Invalid date
{
  "appointment_date": {
    "error": "Appointment date must be in the future."
  }
}

// 400 Bad Request - Missing time slots
{
  "time_slots": {
    "error": "At least one time slot must be selected."
  }
}

// 400 Bad Request - Invalid time slot structure
{
  "time_slots": {
    "error": "Time slot missing required field: day"
  }
}

// 404 Not Found - Exchange not found
{
  "exchange": "Invalid pk \"invalid-uuid\" - object does not exist."
}
```

---

### 2. List All Appointments

**Endpoint:** `GET /api/appointments/`

**Description:** Retrieve all appointments (filtered by user role).

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | String | Filter by status: pending, approved, rejected |
| `exchange` | UUID | Filter by exchange UUID |
| `page` | Integer | Page number for pagination |

**Permissions:**
- Regular users see only their own appointments
- Exchange owners see appointments for their exchanges
- Staff/superusers see all appointments

**Response (200 OK):**

```json
{
  "count": 50,
  "next": "http://localhost:8000/api/appointments/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "appointment-uuid",
      "exchange": "exchange-uuid",
      "exchange_name": "Veteran's Auto Shop",
      "exchange_logo": "https://example.com/logo.png",
      "user": "user-uuid",
      "user_name": "John Doe",
      "name": "John Doe",
      "email": "john@example.com",
      "appointment_date": "2025-12-15",
      "time_slots": [...],
      "status": "pending",
      "created_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

**cURL Example:**

```bash
# List all appointments
curl -X GET http://localhost:8000/api/appointments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/appointments/?status=pending" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by exchange
curl -X GET "http://localhost:8000/api/appointments/?exchange=exchange-uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3. Get Specific Appointment

**Endpoint:** `GET /api/appointments/{uuid}/`

**Description:** Retrieve details of a specific appointment.

**Authentication:** Required

**Response (200 OK):**

```json
{
  "uuid": "appointment-uuid",
  "exchange": "exchange-uuid",
  "user": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "appointment_date": "2025-12-15",
  "time_slots": [
    {
      "day": "Wednesday",
      "start_time": "10:00 AM",
      "end_time": "12:00 AM",
      "selected": true
    }
  ],
  "status": "pending",
  "notes": "Partnership discussion",
  "created_at": "2025-12-03T10:30:00Z",
  "updated_at": "2025-12-03T10:30:00Z"
}
```

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/appointments/{uuid}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 4. Update Appointment

**Endpoint:** `PATCH /api/appointments/{uuid}/`

**Description:** Update appointment details (name, email, date, time slots, notes).

**Authentication:** Required

**Permissions:** Only the appointment creator can update

**Request Body (Partial Update):**

```json
{
  "appointment_date": "2025-12-20",
  "notes": "Updated notes"
}
```

**Response (200 OK):**

```json
{
  "uuid": "appointment-uuid",
  "exchange": "exchange-uuid",
  "user": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "appointment_date": "2025-12-20",
  "time_slots": [...],
  "status": "pending",
  "notes": "Updated notes",
  "created_at": "2025-12-03T10:30:00Z",
  "updated_at": "2025-12-03T15:45:00Z"
}
```

**cURL Example:**

```bash
curl -X PATCH http://localhost:8000/api/appointments/{uuid}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_date": "2025-12-20",
    "notes": "Updated notes"
  }'
```

---

### 5. Delete Appointment

**Endpoint:** `DELETE /api/appointments/{uuid}/`

**Description:** Delete/cancel an appointment.

**Authentication:** Required

**Permissions:** Only the appointment creator can delete

**Response (204 No Content):**

No response body.

**cURL Example:**

```bash
curl -X DELETE http://localhost:8000/api/appointments/{uuid}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 6. Get My Appointments

**Endpoint:** `GET /api/appointments/my-appointments/`

**Description:** Retrieve all appointments created by the current user.

**Authentication:** Required

**Response (200 OK):**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "uuid": "appointment-uuid",
      "exchange": "exchange-uuid",
      "exchange_name": "Veteran's Auto Shop",
      "exchange_logo": "https://example.com/logo.png",
      "user": "user-uuid",
      "user_name": "John Doe",
      "name": "John Doe",
      "email": "john@example.com",
      "appointment_date": "2025-12-15",
      "time_slots": [...],
      "status": "pending",
      "created_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/appointments/my-appointments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 7. Get Exchange Appointments

**Endpoint:** `GET /api/appointments/exchange-appointments/`

**Description:** Retrieve all appointments for exchanges owned by the current user (for exchange owners).

**Authentication:** Required

**Permissions:** Only exchange owners can access

**Response (200 OK):**

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "uuid": "appointment-uuid",
      "exchange": "exchange-uuid",
      "exchange_name": "My Veteran Business",
      "exchange_logo": "https://example.com/logo.png",
      "user": "customer-user-uuid",
      "user_name": "Jane Smith",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "appointment_date": "2025-12-15",
      "time_slots": [...],
      "status": "pending",
      "created_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/appointments/exchange-appointments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 8. Update Appointment Status

**Endpoint:** `PATCH /api/appointments/{uuid}/update_status/`

**Description:** Update the status of an appointment (approve/reject).

**Authentication:** Required

**Permissions:**
- Exchange owners can update status for their exchanges
- Staff/superusers can update any appointment
- Regular users can only cancel their own appointments

**Request Body:**

```json
{
  "status": "approved"
}
```

**Valid Status Values:**
- `pending` - Initial status
- `approved` - Appointment confirmed by exchange owner
- `rejected` - Appointment declined by exchange owner

**Response (200 OK):**

```json
{
  "uuid": "appointment-uuid",
  "exchange": "exchange-uuid",
  "user": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "appointment_date": "2025-12-15",
  "time_slots": [...],
  "status": "approved",
  "notes": "Partnership discussion",
  "created_at": "2025-12-03T10:30:00Z",
  "updated_at": "2025-12-03T16:00:00Z"
}
```

**cURL Example:**

```bash
curl -X PATCH http://localhost:8000/api/appointments/{uuid}/update_status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved"
  }'
```

**Error Responses:**

```json
// 400 Bad Request - Missing status
{
  "error": "status field is required."
}

// 400 Bad Request - Invalid status
{
  "error": "Invalid status. Must be one of: pending, approved, rejected"
}

// 403 Forbidden - No permission
{
  "error": "You do not have permission to update this appointment status."
}
```

---

## Data Models

### Appointment Object

```json
{
  "uuid": "UUID",
  "exchange": "UUID",
  "user": "UUID",
  "name": "String (max 200 chars)",
  "email": "Email",
  "appointment_date": "Date (YYYY-MM-DD)",
  "time_slots": [
    {
      "day": "String",
      "start_time": "String",
      "end_time": "String",
      "selected": "Boolean"
    }
  ],
  "status": "pending|approved|rejected",
  "notes": "String (max 500 chars, optional)",
  "created_at": "DateTime",
  "updated_at": "DateTime"
}
```

### Appointment List Object (Lightweight)

```json
{
  "uuid": "UUID",
  "exchange": "UUID",
  "exchange_name": "String",
  "exchange_logo": "URL String",
  "user": "UUID",
  "user_name": "String",
  "name": "String",
  "email": "Email",
  "appointment_date": "Date",
  "time_slots": "Array",
  "status": "String",
  "created_at": "DateTime"
}
```

---

## Status Workflow

```
pending → approved (by exchange owner)
pending → rejected (by exchange owner)
```

**Status Descriptions:**

| Status | Description |
|--------|-------------|
| `pending` | Appointment submitted, awaiting review |
| `approved` | Appointment approved by exchange owner |
| `rejected` | Appointment declined by exchange owner |

---

## Pagination

All list endpoints support pagination with the following parameters:

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 500)

**Paginated Response Structure:**

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/appointments/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Error Handling

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource does not exist |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "field_name": {
    "error": "Error message description"
  }
}
```

or

```json
{
  "error": "Error message description"
}
```

---

## Business Rules

1. **Date Validation:**
   - Appointment date must be in the future
   - Cannot book appointments for past dates

2. **Time Slots:**
   - At least one time slot must be provided
   - Selected slots must include day, start_time, and end_time
   - Time slots stored as flexible JSON structure

3. **Permissions:**
   - Users can only view/edit their own appointments
   - Exchange owners can view appointments for their exchanges
   - Exchange owners can approve/reject appointments
   - Staff/superusers have full access

4. **Status Management:**
   - Initial status is always "pending"
   - Only exchange owners can approve/reject
   - Users cannot directly change status (except cancellation)

5. **Form Data:**
   - Name is required and cannot be empty
   - Email must be valid format
   - Notes are optional (max 500 characters)

---

## Use Cases

### 1. User Books an Appointment

```bash
# Step 1: User selects exchange and fills form
POST /api/appointments/
{
  "exchange": "exchange-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "appointment_date": "2025-12-15",
  "time_slots": [...],
  "notes": "Discussion about partnership"
}

# Step 2: User checks their appointments
GET /api/appointments/my-appointments/
```

### 2. Exchange Owner Reviews Bookings

```bash
# Step 1: Owner views all appointments for their exchanges
GET /api/appointments/exchange-appointments/

# Step 2: Owner approves an appointment
PATCH /api/appointments/{uuid}/update_status/
{
  "status": "approved"
}
```

### 3. User Updates Appointment

```bash
# Update appointment details
PATCH /api/appointments/{uuid}/
{
  "appointment_date": "2025-12-20",
  "notes": "Updated requirements"
}
```

---

## Testing Examples

### Postman Collection Structure

```
Exchange Appointments
├── Create Appointment
├── List Appointments
├── Get Appointment Details
├── Update Appointment
├── Delete Appointment
├── My Appointments
├── Exchange Appointments
└── Update Status
```

### Sample Test Data

```json
{
  "test_exchange_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "test_appointment": {
    "name": "Test User",
    "email": "test@example.com",
    "appointment_date": "2025-12-20",
    "time_slots": [
      {
        "day": "Wednesday",
        "start_time": "10:00 AM",
        "end_time": "12:00 PM",
        "selected": true
      }
    ],
    "notes": "Test appointment"
  }
}
```

---

## Integration Notes

1. **Frontend Integration:**
   - Use date picker for appointment_date field
   - Implement time slot selector matching the UI design
   - Show real-time validation for date/time selection
   - Display appointment status with visual indicators

2. **Email Notifications (Future):**
   - Send confirmation email on booking
   - Notify user when status changes
   - Remind users of upcoming appointments

3. **Calendar Integration (Future):**
   - Display appointments in calendar view
   - Show available/booked time slots
   - Filter by date range

---

## Admin Panel

Appointments can be managed in the Django admin panel at `/admin/exchange/exchangeappointment/`

**Features:**
- View all appointments
- Filter by status, date, exchange
- Search by name, email, exchange name
- Bulk approve/reject/complete appointments
- View appointment details and time slots

---

## Summary

The Appointment Booking API provides a complete solution for users to book appointments with exchanges. Key features include:

✅ Simple booking form submission  
✅ Flexible time slot selection (JSON storage)  
✅ Status management workflow  
✅ Role-based permissions  
✅ Pagination support  
✅ Comprehensive validation  
✅ Admin panel integration  

For questions or support, contact the development team.
