# Admin Intel Management API Documentation

This document describes the admin-only endpoints for managing Intel posts (approve/reject functionality).

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

### 1. List All Intel Posts (Admin)

Get a paginated list of all intel posts with admin-specific details including rejection reasons.

**Endpoint:** `GET /api/admin-intel/`

**Query Parameters:**
- `status` (optional): Filter by status (`under_review`, `approved`, `rejected`)
- `urgency` (optional): Filter by urgency (`low`, `medium`, `high`)
- `search` (optional): Search in description, location, or user email
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 200)

**Example Request:**
```bash
GET /api/admin-intel/?status=under_review&page=1&page_size=20
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Intel posts retrieved successfully",
    "count": 45,
    "next": "http://api.example.com/api/admin-intel/?page=2",
    "previous": null,
    "results": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "user_email": "user@example.com",
            "user_full_name": "John Doe",
            "description": "Suspicious activity observed",
            "category_name": "Security",
            "location": "Downtown Area",
            "urgency": "high",
            "status": "under_review",
            "status_display": "Under Review",
            "rejection_reason": null,
            "likes_count": 5,
            "comments_count": 3,
            "created_at": "2025-12-11T10:30:00Z",
            "updated_at": "2025-12-11T10:30:00Z"
        }
    ]
}
```

---

### 2. Get Intel Post Details (Admin)

Get detailed information about a specific intel post, including all media files and rejection reason.

**Endpoint:** `GET /api/admin-intel/{uuid}/`

**URL Parameters:**
- `uuid`: Intel post UUID

**Example Request:**
```bash
GET /api/admin-intel/123e4567-e89b-12d3-a456-426614174000/
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Intel post retrieved successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "user": {
            "uuid": "user-uuid",
            "email": "user@example.com",
            "full_name": "John Doe"
        },
        "description": "Detailed description of the intel",
        "category": {
            "uuid": "cat-uuid",
            "name": "Security",
            "icon": "🔒"
        },
        "location": "Downtown Area",
        "urgency": "high",
        "status": "under_review",
        "status_display": "Under Review",
        "rejection_reason": null,
        "likes_count": 5,
        "comments_count": 3,
        "media_files": [
            {
                "uuid": "media-uuid",
                "file_url": "https://example.com/media/file1.jpg",
                "file_type": "photo",
                "created_at": "2025-12-11T10:30:00Z"
            }
        ],
        "is_liked_by_user": false,
        "created_at": "2025-12-11T10:30:00Z",
        "updated_at": "2025-12-11T10:30:00Z"
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "message": "Intel post not found"
}
```

---

### 3. Approve Intel Post

Approve an intel post, changing its status to 'approved' and clearing any rejection reason.

**Endpoint:** `POST /api/admin-intel/{uuid}/approve/`

**URL Parameters:**
- `uuid`: Intel post UUID

**Request Body:** Empty object `{}` (optional)

**Example Request:**
```bash
POST /api/admin-intel/123e4567-e89b-12d3-a456-426614174000/approve/
Content-Type: application/json

{}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Intel post approved successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "status": "approved",
        "status_display": "Approved"
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "message": "Intel post not found"
}
```

---

### 4. Reject Intel Post

Reject an intel post with a reason, changing its status to 'rejected'.

**Endpoint:** `POST /api/admin-intel/{uuid}/reject/`

**URL Parameters:**
- `uuid`: Intel post UUID

**Request Body:**
```json
{
    "rejection_reason": "Reason for rejecting the intel post"
}
```

**Required Fields:**
- `rejection_reason` (string, max 1000 characters): The reason for rejection. Cannot be empty or only whitespace.

**Example Request:**
```bash
POST /api/admin-intel/123e4567-e89b-12d3-a456-426614174000/reject/
Content-Type: application/json

{
    "rejection_reason": "The intel does not contain sufficient evidence to support the claim."
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Intel post rejected successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "status": "rejected",
        "status_display": "Rejected",
        "rejection_reason": "The intel does not contain sufficient evidence to support the claim."
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "rejection_reason": [
        "Rejection reason cannot be empty"
    ]
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "message": "Intel post not found"
}
```

---

### 5. Get Pending Intel Posts

Get all intel posts that are pending review (status = 'under_review').

**Endpoint:** `GET /api/admin-intel/pending/`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 200)

**Example Request:**
```bash
GET /api/admin-intel/pending/?page=1
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Pending intel posts retrieved successfully",
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "user_email": "user@example.com",
            "user_full_name": "John Doe",
            "description": "Intel waiting for review",
            "category_name": "Security",
            "location": "Downtown Area",
            "urgency": "high",
            "status": "under_review",
            "status_display": "Under Review",
            "rejection_reason": null,
            "likes_count": 0,
            "comments_count": 0,
            "created_at": "2025-12-11T10:30:00Z",
            "updated_at": "2025-12-11T10:30:00Z"
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
    "message": "Failed to approve intel post",
    "error": "Error description"
}
```

---

## Status Workflow

1. **Under Review** (default): Intel is submitted and awaiting admin review
2. **Approved**: Admin approves the intel (rejection_reason is cleared)
3. **Rejected**: Admin rejects the intel (rejection_reason is required and saved)

---

## Notes

- Only admin users (staff or superuser) can access these endpoints
- Rejection reason is mandatory when rejecting an intel post
- Approving an intel will clear any previous rejection reason
- All timestamps are in UTC format
- UUIDs are used for all resource identifiers
