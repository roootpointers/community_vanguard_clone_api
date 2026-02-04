# Intel API Documentation

## Overview
The Intel API provides endpoints for creating, managing, and interacting with intelligence reports ("Drop Ground Truth Intel"). Users can post intel reports with multiple media files, like/unlike posts, comment on posts, and reply to comments.

---

## Table of Contents
1. [Intel Posts](#intel-posts)
2. [Likes System](#likes-system)
3. [Comments & Replies](#comments--replies)
4. [Authentication](#authentication)

---

## Intel Posts

### Create Intel Post
Post a new intelligence report with optional multiple media files.

**Endpoint:** `POST /api/intel/`

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "description": "Parking lot behind shelter needs attention",
  "category": "Infrastructure",
  "location": "Downtown Shelter, Main Street",
  "urgency": "medium",
  "status": "pending",
  "media_urls": [
    "https://cdn.example.com/intel/photo1.jpg",
    "https://cdn.example.com/intel/photo2.jpg"
  ]
}
```

**Fields:**
- `description` (required): Detailed description of the intel
- `category` (required): Category (e.g., Security, Infrastructure, Health)
- `location` (required): Physical location
- `urgency` (required): `low`, `medium`, or `high`
- `status` (optional): `pending`, `verified`, `investigating`, `resolved` (default: `pending`)
- `media_urls` (optional): Array of media file URLs

**Success Response (201):**
```json
{
  "success": true,
  "message": "Intel post created successfully",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "user": {
      "uuid": "user-uuid",
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "description": "Parking lot behind shelter needs attention",
    "category": "Infrastructure",
    "location": "Downtown Shelter, Main Street",
    "urgency": "medium",
    "status": "pending",
    "likes_count": 0,
    "comments_count": 0,
    "media_files": [
      {
        "uuid": "media-uuid-1",
        "file_url": "https://cdn.example.com/intel/photo1.jpg",
        "file_type": "photo",
        "created_at": "2025-10-23T10:30:00Z"
      }
    ],
    "is_liked_by_user": false,
    "created_at": "2025-10-23T10:30:00Z",
    "updated_at": "2025-10-23T10:30:00Z"
  }
}
```

---

### List Intel Posts
Retrieve paginated list of intel posts with filtering and search.

**Endpoint:** `GET /api/intel/`

**Authentication:** Required

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `category`: Filter by category
- `location`: Filter by location
- `urgency`: Filter by urgency (low, medium, high)
- `status`: Filter by status (pending, verified, investigating, resolved)
- `search`: Search in description, category, location
- `ordering`: Sort by `-created_at`, `created_at`, `-likes_count`, `likes_count`, `-comments_count`

**Example:**
```http
GET /api/intel/?category=Infrastructure&urgency=high&page=1&page_size=20&ordering=-created_at
Authorization: Bearer YOUR_JWT_TOKEN
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Intel posts retrieved successfully",
  "count": 150,
  "next": "http://localhost:8000/api/intel/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "user": {
        "uuid": "user-uuid",
        "full_name": "John Doe",
        "email": "user@example.com"
      },
      "description": "Parking lot behind shelter needs attention",
      "category": "Infrastructure",
      "location": "Downtown Shelter, Main Street",
      "urgency": "medium",
      "status": "pending",
      "likes_count": 5,
      "comments_count": 3,
      "media_count": 2,
      "is_liked_by_user": false,
      "created_at": "2025-10-23T10:30:00Z",
      "updated_at": "2025-10-23T10:30:00Z"
    }
  ]
}
```

---

### Get Single Intel Post
Retrieve detailed information about a specific intel post.

**Endpoint:** `GET /api/intel/{uuid}/`

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "Intel post retrieved successfully",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "user": { "uuid": "...", "email": "...", "full_name": "..." },
    "description": "...",
    "category": "Infrastructure",
    "location": "...",
    "urgency": "medium",
    "status": "pending",
    "likes_count": 5,
    "comments_count": 3,
    "media_files": [...],
    "is_liked_by_user": true,
    "created_at": "2025-10-23T10:30:00Z",
    "updated_at": "2025-10-23T10:30:00Z"
  }
}
```

---

### Update Intel Post
Update an intel post (creator only).

**Endpoint:** `PUT/PATCH /api/intel/{uuid}/`

**Authentication:** Required

**Permission:** Only the creator can update

**Request Body:**
```json
{
  "description": "Updated description",
  "urgency": "high",
  "status": "investigating"
}
```

---

### Delete Intel Post
Delete an intel post (creator only).

**Endpoint:** `DELETE /api/intel/{uuid}/`

**Authentication:** Required

**Permission:** Only the creator can delete

---

### Get My Intel Posts
Retrieve all intel posts created by the authenticated user.

**Endpoint:** `GET /api/intel/my-intels/`

**Authentication:** Required

**Query Parameters:** Same as list endpoint

---

## Likes System

### Toggle Like on Intel Post
Like or unlike an intel post.

**Endpoint:** `POST /api/intel-like/toggle/`

**Authentication:** Required

**Request Body:**
```json
{
  "intel_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response - Liked (201):**
```json
{
  "success": true,
  "message": "Intel post liked successfully",
  "data": {
    "is_liked": true,
    "likes_count": 6,
    "like_uuid": "like-uuid"
  }
}
```

**Success Response - Unliked (200):**
```json
{
  "success": true,
  "message": "Intel post unliked successfully",
  "data": {
    "is_liked": false,
    "likes_count": 5
  }
}
```

---

### List Users Who Liked Intel
Get list of users who liked a specific intel post.

**Endpoint:** `GET /api/intel-like/{intel_uuid}/list/`

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "Likes retrieved successfully",
  "count": 5,
  "data": [
    {
      "uuid": "like-uuid",
      "user": {
        "uuid": "user-uuid",
        "full_name": "John Doe",
        "email": "user@example.com"
      },
      "intel": "intel-uuid",
      "created_at": "2025-10-23T10:30:00Z"
    }
  ]
}
```

---

## Comments & Replies

### Post Comment on Intel
Add a comment to an intel post.

**Endpoint:** `POST /api/intel-comment/`

**Authentication:** Required

**Request Body:**
```json
{
  "intel": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Simple setup, but it works.",
  "parent_comment": null
}
```

**Fields:**
- `intel` (required): UUID of the intel post
- `content` (required): Comment text
- `parent_comment` (optional): UUID of parent comment for replies (null for top-level comments)

**Success Response (201):**
```json
{
  "success": true,
  "message": "Comment posted successfully",
  "data": {
    "uuid": "comment-uuid",
    "user": {
      "uuid": "user-uuid",
      "full_name": "Henry",
      "email": "henry@example.com",
      "profile_photo": "https://cdn.example.com/profile.jpg"
    },
    "intel": "intel-uuid",
    "parent_comment": null,
    "content": "Simple setup, but it works.",
    "likes_count": 0,
    "replies_count": 0,
    "is_liked_by_user": false,
    "replies": [],
    "created_at": "2025-10-23T10:35:00Z",
    "updated_at": "2025-10-23T10:35:00Z"
  }
}
```

---

### Post Reply to Comment
Reply to an existing comment.

**Endpoint:** `POST /api/intel-comment/`

**Authentication:** Required

**Request Body:**
```json
{
  "intel": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Looks organized — not bad at all.",
  "parent_comment": "parent-comment-uuid"
}
```

**Note:** Only 1 level of nesting allowed (cannot reply to a reply).

---

### Get Comments for Intel Post
Retrieve all top-level comments for an intel post.

**Endpoint:** `GET /api/intel-comment/intel/{intel_uuid}/`

**Authentication:** Required

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page (default: 20)

**Success Response (200):**
```json
{
  "success": true,
  "message": "Comments retrieved successfully",
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "uuid": "comment-uuid",
      "user": {
        "uuid": "user-uuid",
        "full_name": "Henry",
        "email": "henry@example.com",
        "profile_photo": "https://cdn.example.com/profile.jpg"
      },
      "intel": "intel-uuid",
      "parent_comment": null,
      "content": "Simple setup, but it works.",
      "likes_count": 2,
      "replies_count": 1,
      "is_liked_by_user": false,
      "replies": [
        {
          "uuid": "reply-uuid",
          "user": {...},
          "content": "Looks organized — not bad at all.",
          "likes_count": 2,
          "replies_count": 0,
          "is_liked_by_user": true,
          "created_at": "2025-10-23T10:45:00Z",
          "updated_at": "2025-10-23T10:45:00Z"
        }
      ],
      "created_at": "2025-10-23T10:35:00Z",
      "updated_at": "2025-10-23T10:35:00Z"
    }
  ]
}
```

---

### Get Replies for Comment
Retrieve all replies for a specific comment.

**Endpoint:** `GET /api/intel-comment/{comment_uuid}/replies/`

**Authentication:** Required

---

### Update Comment
Update a comment (creator only).

**Endpoint:** `PUT/PATCH /api/intel-comment/{comment_uuid}/`

**Authentication:** Required

**Permission:** Only the creator can update

---

### Delete Comment
Delete a comment (creator only).

**Endpoint:** `DELETE /api/intel-comment/{comment_uuid}/`

**Authentication:** Required

**Permission:** Only the creator can delete

---

### Toggle Like on Comment
Like or unlike a comment.

**Endpoint:** `POST /api/comment-like/toggle/`

**Authentication:** Required

**Request Body:**
```json
{
  "comment_uuid": "comment-uuid"
}
```

**Success Response - Liked (201):**
```json
{
  "success": true,
  "message": "Comment liked successfully",
  "data": {
    "is_liked": true,
    "likes_count": 3,
    "like_uuid": "like-uuid"
  }
}
```

**Success Response - Unliked (200):**
```json
{
  "success": true,
  "message": "Comment unliked successfully",
  "data": {
    "is_liked": false,
    "likes_count": 2
  }
}
```

---

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "An error occurred",
  "error": "Error details..."
}
```

---

## Complete Endpoint Summary

### Intel Posts
- `POST /api/intel/` - Create intel post
- `GET /api/intel/` - List intel posts (with filters)
- `GET /api/intel/{uuid}/` - Get single intel post
- `PUT/PATCH /api/intel/{uuid}/` - Update intel post (creator only)
- `DELETE /api/intel/{uuid}/` - Delete intel post (creator only)
- `GET /api/intel/my-intels/` - Get user's intel posts

### Likes
- `POST /api/intel-like/toggle/` - Toggle like on intel post
- `GET /api/intel-like/{intel_uuid}/list/` - List users who liked intel

### Comments
- `POST /api/intel-comment/` - Post comment or reply
- `GET /api/intel-comment/intel/{intel_uuid}/` - Get comments for intel
- `GET /api/intel-comment/{comment_uuid}/replies/` - Get replies for comment
- `PUT/PATCH /api/intel-comment/{comment_uuid}/` - Update comment (creator only)
- `DELETE /api/intel-comment/{comment_uuid}/` - Delete comment (creator only)
- `POST /api/comment-like/toggle/` - Toggle like on comment

---

## Testing with cURL

```bash
# Create Intel Post
curl -X POST \
  "http://localhost:8000/api/intel/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Parking lot behind shelter needs attention",
    "category": "Infrastructure",
    "location": "Downtown Shelter",
    "urgency": "medium",
    "media_urls": ["https://cdn.example.com/photo1.jpg"]
  }'

# List Intel Posts
curl -X GET \
  "http://localhost:8000/api/intel/?category=Infrastructure&page=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Toggle Like
curl -X POST \
  "http://localhost:8000/api/intel-like/toggle/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"intel_uuid": "550e8400-e29b-41d4-a716-446655440000"}'

# Post Comment
curl -X POST \
  "http://localhost:8000/api/intel-comment/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "intel": "550e8400-e29b-41d4-a716-446655440000",
    "content": "Great intel!",
    "parent_comment": null
  }'
```
