# Donation Management System API Documentation

## Overview
The Donation Management System provides comprehensive APIs for managing donations, setting targets, and tracking progress. This system supports multiple currencies, payment methods, and provides analytics capabilities.

## Base URL
```
/api/donation/
```

## Models

### Donation
Represents a donation made by a donor.

**Fields:**
- `id`: Unique identifier (auto-generated)
- `donor_name`: Name of the donor (string, max 255 chars)
- `donor_email`: Email address of the donor (email)
- `amount`: Donation amount (decimal, min 0.01)
- `currency`: Currency code (USD, EUR, GBP, CAD, AUD, JPY)
- `method`: Payment method (Card, Bank Transfer, Paypal, Cash, Crypto, Other)
- `month`: Month of donation (1-12, optional)
- `year`: Year of donation (optional)
- `notes`: Additional notes (text, optional)
- `created_at`: Timestamp when created (auto)
- `updated_at`: Timestamp when updated (auto)
- `formatted_amount`: Read-only formatted amount with currency symbol

### DonationTarget
Represents a fundraising target for a specific period.

**Fields:**
- `id`: Unique identifier (auto-generated)
- `month`: Target month (1-12)
- `year`: Target year
- `target_amount`: Target amount (decimal, min 0.01)
- `currency`: Currency code (default USD)
- `description`: Description of the target (text, optional)
- `created_at`: Timestamp when created (auto)
- `updated_at`: Timestamp when updated (auto)
- `month_name`: Read-only month name
- `collected_amount`: Read-only calculated collected amount
- `progress_percentage`: Read-only progress percentage

## API Endpoints

### Donations

#### 1. List All Donations
**GET** `/api/donation/donations/`

Returns a paginated list of all donations.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10)
- `search`: Search in donor name, email, or notes
- `currency`: Filter by currency (USD, EUR, GBP, etc.)
- `method`: Filter by payment method
- `month`: Filter by month
- `year`: Filter by year
- `ordering`: Sort by field (e.g., `-created_at`, `amount`, `donor_name`)

**Example Response:**
```json
{
  "count": 100,
  "next": "http://api/donation/donations/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "donor_name": "John Doe",
      "amount": "5000.00",
      "currency": "USD",
      "method": "Card",
      "formatted_amount": "$5,000.00",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### 2. Create Donation
**POST** `/api/donation/donations/`

Create a new donation record.

**Request Body:**
```json
{
  "donor_name": "John Doe",
  "donor_email": "john@example.com",
  "amount": "5000.00",
  "currency": "USD",
  "method": "Card",
  "month": 1,
  "year": 2024,
  "notes": "Monthly contribution"
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "donor_name": "John Doe",
  "donor_email": "john@example.com",
  "amount": "5000.00",
  "currency": "USD",
  "method": "Card",
  "month": 1,
  "year": 2024,
  "notes": "Monthly contribution",
  "formatted_amount": "$5,000.00",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 3. Retrieve Donation
**GET** `/api/donation/donations/{id}/`

Get details of a specific donation.

#### 4. Update Donation
**PUT** `/api/donation/donations/{id}/`
**PATCH** `/api/donation/donations/{id}/`

Update a donation record.

#### 5. Delete Donation
**DELETE** `/api/donation/donations/{id}/`

Delete a donation record.

**Response:** 204 No Content

#### 6. Donations By Month
**GET** `/api/donation/donations/by_month/`

Get donations grouped by month for a specific year.

**Query Parameters:**
- `year`: Year (required)

**Example Response:**
```json
{
  "1": {
    "month": 1,
    "count": 15,
    "total_amount": "25000.00",
    "donations": [...]
  },
  "2": {
    "month": 2,
    "count": 20,
    "total_amount": "30000.00",
    "donations": [...]
  }
}
```

#### 7. Donations By Donor
**GET** `/api/donation/donations/by_donor/`

Get all donations from a specific donor.

**Query Parameters:**
- `email`: Donor email (required)

**Example Response:**
```json
{
  "email": "john@example.com",
  "total_donations": 5,
  "total_amount": "15000.00",
  "donations": [...]
}
```

#### 8. Bulk Delete Donations
**DELETE** `/api/donation/donations/bulk_delete/`

Delete multiple donations at once.

**Request Body:**
```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "message": "Successfully deleted 5 donations",
  "deleted_count": 5
}
```

### Donation Targets

#### 1. List All Targets
**GET** `/api/donation/targets/`

Returns a paginated list of all donation targets.

**Query Parameters:**
- `page`: Page number
- `month`: Filter by month
- `year`: Filter by year
- `currency`: Filter by currency
- `ordering`: Sort by field

**Example Response:**
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "month": 3,
      "year": 2024,
      "month_name": "March",
      "target_amount": "400.00",
      "currency": "USD",
      "description": "Every contribution strengthens the mission",
      "collected_amount": 0.0,
      "progress_percentage": 0.0,
      "created_at": "2024-03-01T00:00:00Z",
      "updated_at": "2024-03-01T00:00:00Z"
    }
  ]
}
```

#### 2. Create Target
**POST** `/api/donation/targets/`

Create a new donation target.

**Request Body:**
```json
{
  "month": 3,
  "year": 2024,
  "target_amount": "400.00",
  "currency": "USD",
  "description": "Every contribution strengthens the mission"
}
```

#### 3. Retrieve Target
**GET** `/api/donation/targets/{id}/`

Get details of a specific target.

#### 4. Update Target
**PUT** `/api/donation/targets/{id}/`
**PATCH** `/api/donation/targets/{id}/`

Update a target record.

#### 5. Delete Target
**DELETE** `/api/donation/targets/{id}/`

Delete a target record.

#### 6. Target By Period
**GET** `/api/donation/targets/by_period/`

Get target for a specific month and year.

**Query Parameters:**
- `month`: Month (1-12, required)
- `year`: Year (required)

**Example Response:**
```json
{
  "id": 1,
  "month": 3,
  "year": 2024,
  "month_name": "March",
  "target_amount": "400.00",
  "currency": "USD",
  "description": "Every contribution strengthens the mission",
  "collected_amount": 150.00,
  "progress_percentage": 37.5,
  "created_at": "2024-03-01T00:00:00Z",
  "updated_at": "2024-03-01T00:00:00Z"
}
```

#### 7. Current Year Targets
**GET** `/api/donation/targets/current_year/`

Get all targets for the current year.

#### 8. Progress Tracker
**GET** `/api/donation/targets/progress_tracker/`

Get progress tracker data for multiple months.

**Query Parameters:**
- `months`: Comma-separated month numbers (e.g., "1,2,3")
- `year`: Year (required)

**Example Response:**
```json
{
  "year": 2024,
  "months": [1, 2, 3],
  "targets": [...],
  "overall": {
    "total_target": 1200.00,
    "total_collected": 450.00,
    "progress_percentage": 37.5
  }
}
```

### Statistics

#### Get Donation Statistics
**GET** `/api/donation/stats/`

Get comprehensive donation statistics and analytics.

**Query Parameters:**
- `currency`: Filter by currency (optional)
- `start_date`: Start date (ISO format, optional)
- `end_date`: End date (ISO format, optional)

**Example Response:**
```json
{
  "overview": {
    "total_donations": 100,
    "total_amount": 125000.00,
    "average_donation": 1250.00,
    "recent_donations_7_days": 15
  },
  "by_currency": {
    "USD": {
      "count": 80,
      "total": 100000.00
    },
    "EUR": {
      "count": 15,
      "total": 20000.00
    },
    "GBP": {
      "count": 5,
      "total": 5000.00
    }
  },
  "by_method": {
    "Card": {
      "count": 60,
      "total": 75000.00
    },
    "Bank Transfer": {
      "count": 30,
      "total": 45000.00
    },
    "Paypal": {
      "count": 10,
      "total": 5000.00
    }
  },
  "top_donors": [
    {
      "donor_name": "John Doe",
      "donor_email": "john@example.com",
      "total_donated": 15000.00,
      "donation_count": 5
    }
  ]
}
```

## Permissions

All endpoints use `IsAuthenticatedOrReadOnly` permission:
- **Authenticated users**: Full CRUD access
- **Unauthenticated users**: Read-only access

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error message"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Examples

### Adding a Donation with Month/Year
```bash
curl -X POST http://localhost:8000/api/donation/donations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "donor_name": "Jane Smith",
    "donor_email": "jane@example.com",
    "amount": "2500.00",
    "currency": "USD",
    "method": "Bank Transfer",
    "month": 3,
    "year": 2024
  }'
```

### Setting a Monthly Target
```bash
curl -X POST http://localhost:8000/api/donation/targets/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "month": 3,
    "year": 2024,
    "target_amount": "400.00",
    "currency": "USD",
    "description": "Every contribution strengthens the mission"
  }'
```

### Searching Donations
```bash
curl "http://localhost:8000/api/donation/donations/?search=john&currency=USD&ordering=-amount"
```

### Getting Progress Tracker Data
```bash
curl "http://localhost:8000/api/donation/targets/progress_tracker/?months=1,2,3&year=2024"
```

## Notes

1. **Currency Support**: The system supports USD, EUR, GBP, CAD, AUD, and JPY.
2. **Payment Methods**: Card, Bank Transfer, Paypal, Cash, Crypto, and Other.
3. **Pagination**: Default page size is 10, configurable via `page_size` parameter.
4. **Filtering**: Most list endpoints support filtering by common fields.
5. **Search**: Donations can be searched by donor name, email, or notes.
6. **Progress Calculation**: Target progress is calculated automatically based on matching donations.
7. **Unique Targets**: Each month/year combination can only have one target.
