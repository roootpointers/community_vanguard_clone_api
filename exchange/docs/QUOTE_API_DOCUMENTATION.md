# Exchange Quote Request API Documentation

## Overview

The Quote Request API allows users to request quotes from exchanges for products or services. Users fill out a form with their requirements, specify a budget range (minimum and maximum), and optionally upload files. Exchange owners can view quote requests and update the status.

---

## Base URL

```
/api/quotes/
```

---

## Authentication

All endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Submit Quote Request

**Endpoint:** `POST /api/quotes/`

**Description:** Submit a new quote request to an exchange.

**Authentication:** Required

**Request Body:**

```json
{
  "exchange": "exchange-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "description": "I need custom veteran-themed merchandise for an upcoming event. Looking for t-shirts, hats, and promotional materials with our organization's logo.",
  "mini_range": 300.00,
  "maxi_range": 2000.00,
  "uploaded_files": [
    "https://example.com/logo.png",
    "https://example.com/requirements.pdf"
  ]
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exchange` | UUID | Yes | UUID of the exchange to request quote from |
| `name` | String | Yes | Full name of the person requesting |
| `email` | Email | Yes | Email address for contact |
| `description` | String | Yes | Description of what you need (max 500 chars) |
| `mini_range` | Decimal | No | Minimum budget (optional) |
| `maxi_range` | Decimal | No | Maximum budget (optional) |
| `uploaded_files` | Array | No | Array of file URLs (optional) |

**Response (201 Created):**

```json
{
  "success": true,
  "message": "Quote Request Submitted Successfully",
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "exchange": "exchange-uuid",
    "user": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "description": "I need custom veteran-themed merchandise...",
    "mini_range": "300.00",
    "maxi_range": "2000.00",
    "uploaded_files": [
      "https://example.com/logo.png",
      "https://example.com/requirements.pdf"
    ],
    "status": "pending",
    "created_at": "2025-12-03T10:30:00Z",
    "updated_at": "2025-12-03T10:30:00Z"
  }
}
```

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/quotes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "exchange-uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "description": "I need custom merchandise for an event",
    "mini_range": 300.00,
    "maxi_range": 500.00,
    "uploaded_files": []
  }'
```

**Validation Rules:**

- Name cannot be empty
- Email must be valid format
- Description is required and max 500 characters
- mini_range and maxi_range are optional decimal fields
- Uploaded files must be an array (can be empty)

**Error Responses:**

```json
// 400 Bad Request - Missing description
{
  "description": {
    "error": "Description is required. Please describe what you need."
  }
}

// 404 Not Found - Exchange not found
{
  "exchange": "Invalid pk \"invalid-uuid\" - object does not exist."
}
```

---

### 2. List All Quote Requests

**Endpoint:** `GET /api/quotes/`

**Description:** Retrieve all quote requests (filtered by user role).

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | String | Filter by status: pending, approved, rejected |
| `exchange` | UUID | Filter by exchange UUID |
| `page` | Integer | Page number for pagination |

**Permissions:**
- Regular users see only their own quote requests
- Exchange owners see quotes for their exchanges
- Staff/superusers see all quotes

**Response (200 OK):**

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/quotes/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "quote-uuid",
      "exchange": "exchange-uuid",
      "exchange_name": "Veteran's Custom Shop",
      "exchange_logo": "https://example.com/logo.png",
      "user": "user-uuid",
      "user_name": "John Doe",
      "name": "John Doe",
      "email": "john@example.com",
      "description": "I need custom merchandise...",
      "mini_range": "300.00",
      "maxi_range": "500.00",
      "status": "pending",
      "created_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

**cURL Example:**

```bash
# List all quotes
curl -X GET http://localhost:8000/api/quotes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/quotes/?status=pending" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by exchange
curl -X GET "http://localhost:8000/api/quotes/?exchange=exchange-uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3. Get Specific Quote Request

**Endpoint:** `GET /api/quotes/{uuid}/`

**Description:** Retrieve details of a specific quote request.

**Authentication:** Required

**Response (200 OK):**

```json
{
  "uuid": "quote-uuid",
  "exchange": "exchange-uuid",
  "user": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "description": "I need custom veteran-themed merchandise...",
  "mini_range": "300.00",
  "maxi_range": "500.00",
  "uploaded_files": [
    "https://example.com/logo.png"
  ],
  "status": "approved",
  "created_at": "2025-12-03T10:30:00Z",
  "updated_at": "2025-12-03T15:45:00Z"
}
```

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/quotes/{uuid}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 4. Update Quote Request

**Endpoint:** `PATCH /api/quotes/{uuid}/`

**Description:** Update quote request details (only the requester can update).

**Authentication:** Required

**Permissions:** Only the quote requester can update

**Request Body (Partial Update):**

```json
{
  "description": "Updated requirements - now also need banners",
  "mini_range": 1000.00,
  "maxi_range": 2000.00
}
```

**Response (200 OK):**

```json
{
  "uuid": "quote-uuid",
  "exchange": "exchange-uuid",
  "user": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "description": "Updated requirements - now also need banners",
  "mini_range": "1000.00",
  "maxi_range": "2000.00",
  "uploaded_files": [...],
  "status": "pending",
  "created_at": "2025-12-03T10:30:00Z",
  "updated_at": "2025-12-03T16:00:00Z"
}
```

**cURL Example:**

```bash
curl -X PATCH http://localhost:8000/api/quotes/{uuid}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated requirements"
  }'
```

---

### 5. Delete Quote Request

**Endpoint:** `DELETE /api/quotes/{uuid}/`

**Description:** Delete/cancel a quote request.

**Authentication:** Required

**Permissions:** Only the quote requester can delete

**Response (204 No Content):**

No response body.

**cURL Example:**

```bash
curl -X DELETE http://localhost:8000/api/quotes/{uuid}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 6. Update Quote Status

**Endpoint:** `PATCH /api/quotes/{uuid}/update_status/`

**Description:** Update the status of a quote request (Exchange owners only).

**Authentication:** Required

**Permissions:**
- Exchange owners can update status for their exchanges
- Staff/superusers can update any quote status

**Request Body:**

```json
{
  "status": "approved"
}
```

**Valid Status Values:**
- `pending` - Initial status
- `approved` - Quote request approved
- `rejected` - Quote request declined

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Quote Status Updated Successfully",
  "data": {
    "uuid": "quote-uuid",
    "exchange": "exchange-uuid",
    "user": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "description": "I need custom merchandise...",
    "mini_range": "300.00",
    "maxi_range": "500.00",
    "uploaded_files": [...],
    "status": "approved",
    "created_at": "2025-12-03T10:30:00Z",
    "updated_at": "2025-12-03T16:30:00Z"
  }
}
```

**cURL Example:**

```bash
curl -X PATCH http://localhost:8000/api/quotes/{uuid}/update_status/ \
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
  "status": {
    "error": "Invalid status. Must be one of: pending, approved, rejected"
  }
}

// 403 Forbidden - No permission
{
  "error": "You do not have permission to update this quote status."
}
```

---

## Data Models

### Quote Request Object

```json
{
  "uuid": "UUID",
  "exchange": "UUID",
  "user": "UUID",
  "name": "String (max 200 chars)",
  "email": "Email",
  "description": "String (max 500 chars)",
  "mini_range": "Decimal (optional)",
  "maxi_range": "Decimal (optional)",
  "uploaded_files": ["URL String"],
  "status": "pending|approved|rejected",
  "created_at": "DateTime",
  "updated_at": "DateTime"
}
```

### Quote List Object (Lightweight)

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
  "description": "String",
  "mini_range": "Decimal",
  "maxi_range": "Decimal",
  "status": "String",
  "created_at": "DateTime"
}
```

---

## Status Workflow

```
pending → approved
        ↘ rejected
```

**Status Descriptions:**

| Status | Description |
|--------|-------------|
| `pending` | Quote request submitted, awaiting review |
| `approved` | Quote request approved by exchange owner |
| `rejected` | Quote request declined by exchange owner |

---

## Pagination

All list endpoints support pagination with the following parameters:

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 500)

**Paginated Response Structure:**

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/quotes/?page=2",
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

1. **Form Validation:**
   - Name and email are required
   - Description is required (max 500 characters)
   - mini_range and maxi_range are optional decimal fields

2. **Budget Range:**
   - Both mini_range and maxi_range are optional
   - If provided, should be positive decimal values

3. **File Uploads:**
   - Optional field
   - Stored as array of file URLs
   - Can be empty array

4. **Permissions:**
   - Users can only view/edit their own quote requests
   - Exchange owners can view quotes for their exchanges
   - Exchange owners can update quote status
   - Staff/superusers have full access

5. **Custom Response Format:**
   - Create and response actions return custom success format
   - Includes success boolean, message, and data object

---

## Use Cases

### 1. Customer Requests a Quote

```bash
# Step 1: Customer submits quote request
POST /api/quotes/
{
  "exchange": "exchange-uuid",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "description": "Need custom t-shirts for veteran event",
  "mini_range": 300.00,
  "maxi_range": 500.00,
  "uploaded_files": ["https://example.com/design.png"]
}

# Step 2: Customer checks their quote requests
GET /api/quotes/
```

### 2. Exchange Owner Reviews and Responds

```bash
# Step 1: Owner views all quote requests
GET /api/quotes/

# Step 2: Owner approves the quote
PATCH /api/quotes/{uuid}/update_status/
{
  "status": "approved"
}
```

### 3. Update Quote Request

```bash
# Customer updates their requirements
PATCH /api/quotes/{uuid}/
{
  "description": "Updated: Need 150 t-shirts instead of 100",
  "mini_range": 500.00,
  "maxi_range": 1000.00
}
```

---

## Testing Examples

### Postman Collection Structure

```
Exchange Quotes
├── Submit Quote Request
├── List All Quotes
├── Get Quote Details
├── Update Quote Request
├── Delete Quote Request
└── Update Quote Status
```

### Sample Test Data

```json
{
  "test_exchange_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "test_quote": {
    "name": "Test User",
    "email": "test@example.com",
    "description": "Need custom merchandise for upcoming event",
    "mini_range": 300.00,
    "maxi_range": 500.00,
    "uploaded_files": []
  }
}
```

---

## Integration Notes

1. **Frontend Integration:**
   - Implement text area for description (500 char limit with counter)
   - Create number inputs for mini_range and maxi_range
   - File upload component for optional attachments
   - Display status with visual indicators

2. **File Upload:**
   - Files should be uploaded to storage first
   - Store URLs in the uploaded_files array
   - Support multiple file types (PDF, images, documents)

3. **Budget Range:**
   - Display as two number inputs (minimum and maximum)
   - Both fields are optional
   - Validate that maxi_range is greater than mini_range if both provided

---

## Admin Panel

Quote requests can be managed in the Django admin panel at `/admin/exchange/exchangequote/`

**Features:**
- View all quote requests
- Filter by status, date, exchange
- Search by name, email, description, exchange name
- Bulk update status (approved, rejected)
- View full quote details including budget range and files

---

## Summary

The Quote Request API provides a complete solution for customers to request quotes from exchanges. Key features include:

✅ Simple form submission (name, email, description)  
✅ Optional budget range (mini_range, maxi_range)  
✅ Optional file uploads  
✅ Status management workflow  
✅ Custom success response format  
✅ Role-based permissions  
✅ Pagination support  
✅ Comprehensive validation  
✅ Admin panel integration  

For questions or support, contact the development team.
