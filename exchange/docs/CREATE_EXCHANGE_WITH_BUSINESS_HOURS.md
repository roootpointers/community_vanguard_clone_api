# Create Exchange with Business Hours

## Overview

When creating an exchange, you can now specify business hours at the same time. This eliminates the need for a separate API call to create business hours after exchange creation.

---

## API Endpoint

**Endpoint:** `POST /exchange/api/exchanges/`

**Authentication:** Required

---

## Request Format

### Basic Exchange Creation (Without Business Hours)

```json
{
  "business_name": "ABC Services",
  "business_ein": "12-3456789",
  "seller_type": "veteran-owned",
  "email": "contact@abcservices.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State 12345",
  "mission_statement": "Providing quality services to our community",
  "business_hours": {
    "monday": {"open_time": "09:00", "close_time": "17:00"},
    "tuesday": {"open_time": "09:00", "close_time": "17:00"},
    "wednesday": {"open_time": "09:00", "close_time": "17:00"},
    "thursday": {"open_time": "09:00", "close_time": "17:00"},
    "friday": {"open_time": "09:00", "close_time": "17:00"},
    "saturday": {"is_closed": true},
    "sunday": {"is_closed": true}
  }
}
```

### Exchange Creation WITH Business Hours (Relational Model)

```json
{
  "business_name": "ABC Services",
  "business_ein": "12-3456789",
  "seller_type": "veteran-owned",
  "email": "contact@abcservices.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State 12345",
  "mission_statement": "Providing quality services to our community",
  "business_hours": {
    "monday": {"open_time": "09:00", "close_time": "17:00"},
    "tuesday": {"open_time": "09:00", "close_time": "17:00"},
    "wednesday": {"open_time": "09:00", "close_time": "17:00"},
    "thursday": {"open_time": "09:00", "close_time": "17:00"},
    "friday": {"open_time": "09:00", "close_time": "17:00"},
    "saturday": {"is_closed": true},
    "sunday": {"is_closed": true}
  },
  "operating_hours": [
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
      "is_closed": true
    },
    {
      "day_of_week": 6,
      "is_closed": true
    }
  ]
}
```

---

## Field Descriptions

### operating_hours (Array of Objects)

An array of business hours objects, one for each day you want to configure.

**Required Fields:**
- `day_of_week` (integer, 0-6): Day of the week (0 = Monday, 6 = Sunday)

**Conditional Fields:**
- `is_closed` (boolean): Set to `true` if the exchange is closed on this day
- `open_time` (string, HH:MM or HH:MM:SS): Opening time (required if not closed)
- `close_time` (string, HH:MM or HH:MM:SS): Closing time (required if not closed)

---

## Day of Week Reference

| Day of Week | Integer Value |
|-------------|---------------|
| Monday      | 0             |
| Tuesday     | 1             |
| Wednesday   | 2             |
| Thursday    | 3             |
| Friday      | 4             |
| Saturday    | 5             |
| Sunday      | 6             |

---

## Examples

### Example 1: 9-5 Weekdays, Closed Weekends

```json
{
  "business_name": "Tech Support Center",
  "email": "support@techcenter.com",
  "phone": "+1234567890",
  "operating_hours": [
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

### Example 2: 24/7 Operation

```json
{
  "business_name": "24/7 Emergency Services",
  "email": "emergency@services.com",
  "phone": "+1234567890",
  "operating_hours": [
    {"day_of_week": 0, "open_time": "00:00", "close_time": "23:59"},
    {"day_of_week": 1, "open_time": "00:00", "close_time": "23:59"},
    {"day_of_week": 2, "open_time": "00:00", "close_time": "23:59"},
    {"day_of_week": 3, "open_time": "00:00", "close_time": "23:59"},
    {"day_of_week": 4, "open_time": "00:00", "close_time": "23:59"},
    {"day_of_week": 5, "open_time": "00:00", "close_time": "23:59"},
    {"day_of_week": 6, "open_time": "00:00", "close_time": "23:59"}
  ]
}
```

### Example 3: Different Hours Each Day

```json
{
  "business_name": "Retail Store",
  "email": "info@retailstore.com",
  "phone": "+1234567890",
  "operating_hours": [
    {"day_of_week": 0, "open_time": "10:00", "close_time": "18:00"},
    {"day_of_week": 1, "open_time": "10:00", "close_time": "18:00"},
    {"day_of_week": 2, "open_time": "10:00", "close_time": "18:00"},
    {"day_of_week": 3, "open_time": "10:00", "close_time": "18:00"},
    {"day_of_week": 4, "open_time": "10:00", "close_time": "20:00"},
    {"day_of_week": 5, "open_time": "10:00", "close_time": "20:00"},
    {"day_of_week": 6, "open_time": "12:00", "close_time": "17:00"}
  ]
}
```

### Example 4: Partial Week Schedule

You don't need to specify all 7 days. Only specify the days you want to configure:

```json
{
  "business_name": "Weekend Market",
  "email": "market@weekend.com",
  "phone": "+1234567890",
  "operating_hours": [
    {"day_of_week": 5, "open_time": "08:00", "close_time": "16:00"},
    {"day_of_week": 6, "open_time": "08:00", "close_time": "16:00"}
  ]
}
```

---

## Response

### Success Response (201 Created)

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "business_name": "ABC Services",
  "business_ein": "12-3456789",
  "seller_type": "veteran-owned",
  "email": "contact@abcservices.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State 12345",
  "mission_statement": "Providing quality services to our community",
  "business_hours": {
    "monday": {"open_time": "09:00", "close_time": "17:00"},
    "tuesday": {"open_time": "09:00", "close_time": "17:00"},
    "wednesday": {"open_time": "09:00", "close_time": "17:00"},
    "thursday": {"open_time": "09:00", "close_time": "17:00"},
    "friday": {"open_time": "09:00", "close_time": "17:00"},
    "saturday": {"is_closed": true},
    "sunday": {"is_closed": true}
  },
  "status": "under_review",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Note:** The `operating_hours` field is write-only and won't appear in the response. To view the created business hours, use the business hours API:

```
GET /exchange/api/business-hours/?exchange=550e8400-e29b-41d4-a716-446655440000
```

---

## Validation Rules

1. **day_of_week**: Must be an integer between 0-6
2. **open_time & close_time**: 
   - Required when `is_closed` is false or not specified
   - Must be in HH:MM or HH:MM:SS format
   - close_time must be after open_time
3. **is_closed**: When true, open_time and close_time are optional
4. **Duplicates**: Cannot specify the same day_of_week twice

---

## Error Responses

### Invalid day_of_week

```json
{
  "operating_hours": [
    "Invalid day_of_week: 7. Must be 0-6 (Monday-Sunday)."
  ]
}
```

### Missing Time When Not Closed

```json
{
  "operating_hours": [
    "Day 0: open_time and close_time are required when not closed."
  ]
}
```

### Invalid Time Format

```json
{
  "operating_hours": [
    "Invalid time format. Use HH:MM or HH:MM:SS."
  ]
}
```

---

## Benefits

1. **Single API Call**: Create exchange and business hours together
2. **Atomic Operation**: If exchange creation fails, business hours won't be created
3. **Cleaner Code**: No need for separate business hours creation logic
4. **Better UX**: Users can set up everything in one step

---

## Backward Compatibility

This feature is **optional**. You can still:
- Create an exchange without business hours
- Add business hours later using the dedicated business hours API
- Use both the JSON `business_hours` field (for display) and the relational `operating_hours` (for bookings)

---

## Workflow

### Option 1: All-in-One (Recommended)

```
1. Create exchange with operating_hours
   ↓
2. Exchange is created with business hours automatically
   ↓
3. Generate time slots
   ↓
4. Accept bookings
```

### Option 2: Step-by-Step

```
1. Create exchange without operating_hours
   ↓
2. Create business hours using /api/business-hours/bulk_create/
   ↓
3. Generate time slots
   ↓
4. Accept bookings
```

---

## Python Client Example

```python
import requests

url = "http://localhost:8000/exchange/api/exchanges/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN_HERE",
    "Content-Type": "application/json"
}

data = {
    "business_name": "My Business",
    "email": "contact@mybusiness.com",
    "phone": "+1234567890",
    "address": "123 Main St",
    "operating_hours": [
        {"day_of_week": 0, "open_time": "09:00", "close_time": "17:00"},
        {"day_of_week": 1, "open_time": "09:00", "close_time": "17:00"},
        {"day_of_week": 2, "open_time": "09:00", "close_time": "17:00"},
        {"day_of_week": 3, "open_time": "09:00", "close_time": "17:00"},
        {"day_of_week": 4, "open_time": "09:00", "close_time": "17:00"},
        {"day_of_week": 5, "is_closed": True},
        {"day_of_week": 6, "is_closed": True}
    ]
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    exchange = response.json()
    print(f"Exchange created: {exchange['uuid']}")
    print("Business hours were automatically created!")
else:
    print(f"Error: {response.json()}")
```

---

## JavaScript/TypeScript Example

```javascript
const createExchange = async () => {
  const response = await fetch('http://localhost:8000/exchange/api/exchanges/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_TOKEN_HERE',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      business_name: 'My Business',
      email: 'contact@mybusiness.com',
      phone: '+1234567890',
      address: '123 Main St',
      operating_hours: [
        { day_of_week: 0, open_time: '09:00', close_time: '17:00' },
        { day_of_week: 1, open_time: '09:00', close_time: '17:00' },
        { day_of_week: 2, open_time: '09:00', close_time: '17:00' },
        { day_of_week: 3, open_time: '09:00', close_time: '17:00' },
        { day_of_week: 4, open_time: '09:00', close_time: '17:00' },
        { day_of_week: 5, is_closed: true },
        { day_of_week: 6, is_closed: true }
      ]
    })
  });

  if (response.ok) {
    const exchange = await response.json();
    console.log('Exchange created:', exchange.uuid);
    console.log('Business hours were automatically created!');
  } else {
    const error = await response.json();
    console.error('Error:', error);
  }
};
```

---

## Notes

1. **Two Fields for Business Hours:**
   - `business_hours` (JSONField): Legacy field for display purposes, stored in Exchange model
   - `operating_hours` (Relational): New field for creating BusinessHours records (used for booking system)

2. **Write-Only Field:**
   - `operating_hours` is write-only and won't appear in responses
   - To view business hours, use: `GET /exchange/api/business-hours/?exchange={uuid}`

3. **Optional Feature:**
   - You can still create exchanges without specifying `operating_hours`
   - Business hours can be added later using the dedicated API endpoints

4. **No Update Support (Yet):**
   - Currently, `operating_hours` only works during creation
   - To update business hours, use the dedicated business hours update endpoints
   - Future versions may support updating via the exchange endpoint

---

## See Also

- [Booking System API Documentation](BOOKING_SYSTEM_API.md)
- [Business Hours Management](BOOKING_SYSTEM_API.md#1-business-hours-management)
- [Booking Quick Start Guide](BOOKING_QUICK_START.md)
