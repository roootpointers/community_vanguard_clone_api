# Admin Exchange Management API Documentation

This document describes the admin-only endpoints for viewing and managing Exchange applications.

## Authentication

All admin endpoints require:
- Valid authentication token
- User must be admin (staff or superuser)

**Headers:**
```
Authorization: Bearer <your_token>
```

---

## Endpoints

### 1. List All Exchange Applications (Admin)

Get a paginated list of all exchange applications with filtering and search capabilities.

**Endpoint:** `GET /api/admin-exchange/`

**Query Parameters:**
- `status` (optional): Filter by status (`under_review`, `approved`, `rejected`)
- `seller_type` (optional): Filter by seller type (`customer`, `vendor`, `community_support_provider`)
- `category` (optional): Filter by category UUID
- `sub_category` (optional): Filter by sub-category UUID
- `search` (optional): Search in business_name, email, mission_statement, or user email
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 200)

**Example Request:**
```bash
GET /api/admin-exchange/?status=under_review&page=1&page_size=20
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Exchange retrieved successfully",
    "count": 45,
    "next": "http://api.example.com/api/admin-exchange/?page=2",
    "previous": null,
    "results": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "user": {
                "uuid": "user-uuid",
                "email": "user@example.com",
                "full_name": "John Doe"
            },
            "business_name": "Tech Solutions Inc",
            "business_ein": "12-3456789",
            "seller_type": "vendor",
            "email": "contact@techsolutions.com",
            "phone": "+1234567890",
            "address": "123 Main St, City, State 12345",
            "offers_benefits": "We offer IT consulting and support services",
            "category": {
                "uuid": "cat-uuid",
                "name": "Technology",
                "created_at": "2025-12-01T10:00:00Z",
                "updated_at": "2025-12-01T10:00:00Z"
            },
            "sub_category": {
                "uuid": "subcat-uuid",
                "category": "cat-uuid",
                "category_name": "Technology",
                "name": "IT Services",
                "created_at": "2025-12-01T10:00:00Z",
                "updated_at": "2025-12-01T10:00:00Z"
            },
            "business_logo": "https://example.com/logos/logo.png",
            "business_background_image": "https://example.com/backgrounds/bg.jpg",
            "mission_statement": "Providing innovative technology solutions",
            "status": "under_review",
            "verification": [
                {
                    "uuid": "ver-uuid",
                    "verification_file": "https://example.com/docs/cert.pdf",
                    "file_type": "document",
                    "created_at": "2025-12-11T10:30:00Z",
                    "updated_at": "2025-12-11T10:30:00Z"
                }
            ],
            "preview_images": [
                {
                    "uuid": "img-uuid",
                    "image_url": "https://example.com/previews/img1.jpg",
                    "order": 0,
                    "created_at": "2025-12-11T10:30:00Z",
                    "updated_at": "2025-12-11T10:30:00Z"
                }
            ],
            "latest_reviews": [],
            "exchange_stats": {
                "average_rating": 0,
                "total_reviews": 0,
                "rating_breakdown": {
                    "5": 0,
                    "4": 0,
                    "3": 0,
                    "2": 0,
                    "1": 0
                }
            },
            "created_at": "2025-12-11T10:30:00Z",
            "updated_at": "2025-12-11T10:30:00Z"
        }
    ]
}
```

---

### 2. Get Exchange Application Details (Admin)

Get detailed information about a specific exchange application.

**Endpoint:** `GET /api/admin-exchange/{uuid}/`

**URL Parameters:**
- `uuid`: Exchange application UUID

**Example Request:**
```bash
GET /api/admin-exchange/123e4567-e89b-12d3-a456-426614174000/
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Exchange retrieved successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "user": {
            "uuid": "user-uuid",
            "email": "user@example.com",
            "full_name": "John Doe"
        },
        "business_name": "Tech Solutions Inc",
        "business_ein": "12-3456789",
        "seller_type": "vendor",
        "category": {
            "uuid": "cat-uuid",
            "name": "Technology",
            "created_at": "2025-12-01T10:00:00Z",
            "updated_at": "2025-12-01T10:00:00Z"
        },
        "sub_category": {
            "uuid": "subcat-uuid",
            "category": "cat-uuid",
            "category_name": "Technology",
            "name": "IT Services",
            "created_at": "2025-12-01T10:00:00Z",
            "updated_at": "2025-12-01T10:00:00Z"
        },
        "id_me_verified": false,
        "manual_verification_doc": null,
        "business_logo": "https://example.com/logos/logo.png",
        "business_background_image": "https://example.com/backgrounds/bg.jpg",
        "mission_statement": "Providing innovative technology solutions",
        "address": "123 Main St, City, State 12345",
        "phone": "+1234567890",
        "email": "contact@techsolutions.com",
        "website": "https://techsolutions.com",
        "offers_benefits": "We offer IT consulting and support services",
        "business_hours": {
            "monday": {"open_time": "09:00", "close_time": "17:00", "is_open": true},
            "tuesday": {"open_time": "09:00", "close_time": "17:00", "is_open": true},
            "wednesday": {"open_time": "09:00", "close_time": "17:00", "is_open": true},
            "thursday": {"open_time": "09:00", "close_time": "17:00", "is_open": true},
            "friday": {"open_time": "09:00", "close_time": "17:00", "is_open": true},
            "saturday": {"is_open": false},
            "sunday": {"is_open": false}
        },
        "facebook": "https://facebook.com/techsolutions",
        "facebook_enabled": true,
        "twitter": "https://twitter.com/techsolutions",
        "twitter_enabled": true,
        "instagram": "https://instagram.com/techsolutions",
        "instagram_enabled": false,
        "linkedin": "https://linkedin.com/company/techsolutions",
        "linkedin_enabled": true,
        "status": "under_review",
        "verifications": [
            {
                "uuid": "ver-uuid",
                "verification_file": "https://example.com/docs/cert.pdf",
                "file_type": "document",
                "created_at": "2025-12-11T10:30:00Z",
                "updated_at": "2025-12-11T10:30:00Z"
            }
        ],
        "preview_images": [
            {
                "uuid": "img-uuid",
                "image_url": "https://example.com/previews/img1.jpg",
                "order": 0,
                "created_at": "2025-12-11T10:30:00Z",
                "updated_at": "2025-12-11T10:30:00Z"
            }
        ],
        "latest_reviews": [],
        "exchange_stats": {
            "average_rating": 0,
            "total_reviews": 0,
            "rating_breakdown": {
                "5": 0,
                "4": 0,
                "3": 0,
                "2": 0,
                "1": 0
            }
        },
        "created_at": "2025-12-11T10:30:00Z",
        "updated_at": "2025-12-11T10:30:00Z"
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "message": "Exchange not found"
}
```

---

### 3. Get Pending Exchange Applications

Get all exchange applications that are pending review (status = 'under_review').

**Endpoint:** `GET /api/admin-exchange/pending/`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 200)

**Example Request:**
```bash
GET /api/admin-exchange/pending/?page=1
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Exchange retrieved successfully",
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "user": {
                "uuid": "user-uuid",
                "email": "user@example.com",
                "full_name": "John Doe"
            },
            "business_name": "Tech Solutions Inc",
            "status": "under_review",
            ...
        }
    ]
}
```

---

### 4. Get Approved Exchange Applications

Get all approved exchange applications.

**Endpoint:** `GET /api/admin-exchange/approved/`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 200)

**Example Request:**
```bash
GET /api/admin-exchange/approved/?page=1
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Exchange retrieved successfully",
    "count": 35,
    "next": "http://api.example.com/api/admin-exchange/approved/?page=2",
    "previous": null,
    "results": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "user": {
                "uuid": "user-uuid",
                "email": "user@example.com",
                "full_name": "John Doe"
            },
            "business_name": "Tech Solutions Inc",
            "status": "approved",
            ...
        }
    ]
}
```

---

### 5. Get Rejected Exchange Applications

Get all rejected exchange applications.

**Endpoint:** `GET /api/admin-exchange/rejected/`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 200)

**Example Request:**
```bash
GET /api/admin-exchange/rejected/?page=1
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Exchange retrieved successfully",
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "user": {
                "uuid": "user-uuid",
                "email": "user@example.com",
                "full_name": "John Doe"
            },
            "business_name": "Tech Solutions Inc",
            "status": "rejected",
            ...
        }
    ]
}
```

---

## Common Error Responses

### 401 Unauthorized
User is not authenticated.
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
User is not an admin (not staff or superuser).
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 500 Internal Server Error
Server error occurred.
```json
{
    "success": false,
    "message": "Failed to retrieve exchanges",
    "error": "Error description"
}
```

---

## Filtering Options

### Status Values
- `under_review`: Pending admin review
- `approved`: Approved by admin
- `rejected`: Rejected by admin

### Seller Type Values
- `customer`: Customer
- `vendor`: Vendor
- `community_support_provider`: Community Support Provider

---

## Notes

- Only admin users (staff or superuser) can access these endpoints
- All timestamps are in UTC format
- UUIDs are used for all resource identifiers
- The response includes exchange statistics and latest reviews
- Verification files and preview images are returned as URL arrays
- Business hours are stored and returned as JSON objects
