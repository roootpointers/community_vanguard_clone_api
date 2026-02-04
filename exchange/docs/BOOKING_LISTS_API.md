# Booking Lists API Documentation

## Overview
This document describes the API endpoints for listing bookings in two categories:
1. **Sent Requests** - Bookings the user has made (requests sent to other exchanges)
2. **Received Requests** - Bookings others have made on the user's exchanges (requests received)

---

## Base URL
```
/api/bookings/
```

---

## 1. Get Sent Booking Requests

### Endpoint
```
GET /api/bookings/sent_requests/
```

### Description
Retrieves all booking requests that the authenticated user has sent (bookings made by the user on exchanges).

### Authentication
**Required** - Bearer Token

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by booking status (`pending`, `confirmed`, `cancelled`, `completed`, `no_show`) |

### Request Example
```http
GET /api/bookings/sent_requests/
Authorization: Bearer <your_token>

# With status filter
GET /api/bookings/sent_requests/?status=pending
Authorization: Bearer <your_token>
```

### Response Format
```json
{
  "success": true,
  "message": "Sent booking requests retrieved successfully",
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "uuid": "123e4567-e89b-12d3-a456-426614174000",
      "user": 1,
      "exchange": "abc123-def456",
      "time_slot": "slot-uuid-123",
      "time_slot_details": {
        "uuid": "slot-uuid-123",
        "date": "2025-12-30",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "available_capacity": 0
      },
      "exchange_name": "Strategic Consulting Hub",
      "user_name": "John Doe",
      "status": "approved",
      "customer_name": "Mike",
      "customer_email": "mike123@gmail.com",
      "customer_phone": "+1234567890",
      "notes": "Need consultation on business strategy",
      "cancelled_at": null,
      "cancellation_reason": null,
      "admin_notes": null,
      "created_at": "2025-11-12T08:30:00Z",
      "updated_at": "2025-11-12T09:00:00Z"
    },
    {
      "uuid": "223e4567-e89b-12d3-a456-426614174001",
      "user": 1,
      "exchange": "xyz789-abc123",
      "time_slot": "slot-uuid-456",
      "time_slot_details": {
        "uuid": "slot-uuid-456",
        "date": "2025-12-31",
        "start_time": "14:00:00",
        "end_time": "15:00:00",
        "available_capacity": 1
      },
      "exchange_name": "Tech Support Center",
      "user_name": "John Doe",
      "status": "pending",
      "customer_name": "Mike",
      "customer_email": "mike123@gmail.com",
      "customer_phone": "+1234567890",
      "notes": "Technical assistance needed",
      "cancelled_at": null,
      "cancellation_reason": null,
      "admin_notes": null,
      "created_at": "2025-11-13T10:15:00Z",
      "updated_at": "2025-11-13T10:15:00Z"
    }
  ]
}
```

### Status Codes
| Code | Description |
|------|-------------|
| 200 | Success - Returns list of sent booking requests |
| 401 | Unauthorized - Invalid or missing token |

---

## 2. Get Received Booking Requests

### Endpoint
```
GET /api/bookings/received_requests/
```

### Description
Retrieves all booking requests that have been made on the authenticated user's exchanges (bookings received from other users).

### Authentication
**Required** - Bearer Token

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| exchange | UUID | No | Filter by specific exchange UUID |
| status | string | No | Filter by booking status (`pending`, `confirmed`, `cancelled`, `completed`, `no_show`) |

### Request Example
```http
GET /api/bookings/received_requests/
Authorization: Bearer <your_token>

# With exchange filter
GET /api/bookings/received_requests/?exchange=abc123-def456
Authorization: Bearer <your_token>

# With status filter
GET /api/bookings/received_requests/?status=pending
Authorization: Bearer <your_token>

# With both filters
GET /api/bookings/received_requests/?exchange=abc123-def456&status=confirmed
Authorization: Bearer <your_token>
```

### Response Format
```json
{
  "success": true,
  "message": "Received booking requests retrieved successfully",
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "uuid": "323e4567-e89b-12d3-a456-426614174002",
      "user": 5,
      "exchange": "abc123-def456",
      "time_slot": "slot-uuid-789",
      "time_slot_details": {
        "uuid": "slot-uuid-789",
        "date": "2025-12-30",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "available_capacity": 0
      },
      "exchange_name": "Strategic Consulting Hub",
      "user_name": "Jane Smith",
      "status": "pending",
      "customer_name": "Jane Smith",
      "customer_email": "jane@example.com",
      "customer_phone": "+9876543210",
      "notes": "First time consultation",
      "cancelled_at": null,
      "cancellation_reason": null,
      "admin_notes": null,
      "created_at": "2025-11-14T11:00:00Z",
      "updated_at": "2025-11-14T11:00:00Z"
    },
    {
      "uuid": "423e4567-e89b-12d3-a456-426614174003",
      "user": 7,
      "exchange": "abc123-def456",
      "time_slot": "slot-uuid-101",
      "time_slot_details": {
        "uuid": "slot-uuid-101",
        "date": "2025-12-31",
        "start_time": "15:00:00",
        "end_time": "16:00:00",
        "available_capacity": 1
      },
      "exchange_name": "Strategic Consulting Hub",
      "user_name": "Bob Johnson",
      "status": "confirmed",
      "customer_name": "Bob Johnson",
      "customer_email": "bob@example.com",
      "customer_phone": "+5555555555",
      "notes": "Follow-up meeting",
      "cancelled_at": null,
      "cancellation_reason": null,
      "admin_notes": "VIP client",
      "created_at": "2025-11-15T09:30:00Z",
      "updated_at": "2025-11-15T10:00:00Z"
    }
  ]
}
```

### Response (No Exchanges)
If the user doesn't own any exchanges:
```json
{
  "success": true,
  "message": "You do not own any exchanges yet.",
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

### Status Codes
| Code | Description |
|------|-------------|
| 200 | Success - Returns list of received booking requests |
| 401 | Unauthorized - Invalid or missing token |

---

## Booking Status Values

| Status | Description |
|--------|-------------|
| `pending` | Booking is awaiting confirmation |
| `confirmed` | Booking has been confirmed |
| `cancelled` | Booking has been cancelled |
| `completed` | Booking has been completed |
| `no_show` | Customer did not show up |

---

## Usage Examples

### Example 1: Get All Sent Requests
```javascript
// Using JavaScript fetch
const response = await fetch('/api/bookings/sent_requests/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  }
});
${data.message}: ${data.count} requests`);
console.log(data.results
const data = await response.json();
console.log(`You have ${data.count} sent booking requests`);
```

### Example 2: Get Pending Received Requests
```javascript
// Using JavaScript fetch
const response = await fetch('/api/bookings/received_requests/?status=pending', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  }
});

const data = ${data.message}: ${data.count} pending requests`);
console.log(data.results
console.log(`You have ${data.count} pending requests on your exchanges`);
```

### Example 3: Get Requests for Specific Exchange
```python
# Using Python requests
import requests

headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}

response = requests.get(
    '/api/bookings/received_requests/',
    params={'exchange': 'abc123-def456'},
    headers=headers
)

data = response.json()
print(f"Exchange has {data['count']} booking requests")
```

---

## Notes

1. **Sent Requests** shows bookings where the current user is the `user` field (the person who made the booking)
2. **Received Requests** shows bookings where the current user owns the `exchange` (the business receiving the booking)
3. Both endpoints support filtering by `status` to show only specific booking states
4. Received requests can be filtered by `exchange` UUID to see bookings for a specific business
5. Results are ordered by creation date (most recent first)
6. All endpoints require authentication

---

## Related Endpoints

- `POST /api/bookings/` - Create a new booking
- `GET /api/bookings/{uuid}/` - Get booking details
- `POST /api/bookings/{uuid}/cancel/` - Cancel a booking
- `PATCH /api/bookings/{uuid}/update_status/` - Update booking status (admin)
- `GET /api/bookings/upcoming/` - Get upcoming bookings
- `GET /api/bookings/history/` - Get past bookings
