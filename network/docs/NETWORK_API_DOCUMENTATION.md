# Network API Documentation

## Overview

The Network API provides a complete followers & following system for the Vanguard platform, allowing veterans to connect and build their network within the community. Users can follow/unfollow others, view their followers and following lists, check mutual connections, and get network statistics.

**Base URL**: `/api/network/`

---

## Authentication

All Network API endpoints require authentication via JWT token:

```
Authorization: Bearer <your_access_token>
```

---

## Endpoints

### 1. Follow a User

Follow another user in the platform.

**Endpoint**: `POST /api/network/follow/`

**Request Body**:
```json
{
    "user_uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response** (201 Created):
```json
{
    "success": true,
    "message": "Successfully followed user",
    "data": {
        "uuid": "987fcdeb-51a2-43f7-8e9c-123456789012",
        "follower": {
            "uuid": "current-user-uuid",
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "profile_photo": "https://example.com/photo.jpg"
        },
        "following": {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "username": "jane_smith",
            "email": "jane@example.com",
            "full_name": "Jane Smith",
            "first_name": "Jane",
            "last_name": "Smith",
            "profile_photo": "https://example.com/photo2.jpg"
        },
        "notify_on_post": true,
        "created_at": "2025-11-06T12:00:00Z"
    }
}
```

**Error Responses**:
- `400 Bad Request`: User not found, trying to follow yourself, or already following
- `404 Not Found`: User does not exist

---

### 2. Unfollow a User

Unfollow a user you are currently following.

**Endpoint**: `POST /api/network/unfollow/`

**Request Body**:
```json
{
    "user_uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Successfully unfollowed user"
}
```

**Error Responses**:
- `400 Bad Request`: Not following this user
- `404 Not Found`: User does not exist

---

### 3. Toggle Follow

Toggle follow status for a user (follow if not following, unfollow if following).

**Endpoint**: `POST /api/network/toggle-follow/`

**Request Body**:
```json
{
    "user_uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Now following user",
    "data": {
        "is_following": true,
        "follow": {
            "uuid": "987fcdeb-51a2-43f7-8e9c-123456789012",
            "follower": {...},
            "following": {...},
            "notify_on_post": true,
            "created_at": "2025-11-06T12:00:00Z"
        }
    }
}
```

Or if unfollowed:
```json
{
    "success": true,
    "message": "Unfollowed user",
    "data": {
        "is_following": false
    }
}
```

---

### 4. My Followers

Get the list of users following the authenticated user.

**Endpoint**: `GET /api/network/followers/`

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Followers retrieved successfully",
    "count": 50,
    "next": "http://example.com/api/network/followers/?page=2",
    "previous": null,
    "results": [
        {
            "uuid": "follow-uuid",
            "user": {
                "uuid": "user-uuid",
                "username": "follower1",
                "email": "follower1@example.com",
                "full_name": "Follower One",
                "first_name": "Follower",
                "last_name": "One",
                "profile_photo": "https://example.com/photo.jpg"
            },
            "is_following_back": true,
            "created_at": "2025-11-05T10:30:00Z"
        }
    ]
}
```

---

### 5. My Following

Get the list of users the authenticated user is following.

**Endpoint**: `GET /api/network/following/`

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Following list retrieved successfully",
    "count": 35,
    "next": null,
    "previous": null,
    "results": [
        {
            "uuid": "follow-uuid",
            "user": {
                "uuid": "user-uuid",
                "username": "following1",
                "email": "following1@example.com",
                "full_name": "Following One",
                "first_name": "Following",
                "last_name": "One",
                "profile_photo": "https://example.com/photo.jpg"
            },
            "is_follower": false,
            "notify_on_post": true,
            "created_at": "2025-11-04T15:20:00Z"
        }
    ]
}
```

---

### 6. User's Followers

Get the list of followers for a specific user.

**Endpoint**: `GET /api/network/{user_uuid}/followers/`

**Path Parameters**:
- `user_uuid`: UUID of the user

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
    "success": true,
    "message": "User followers retrieved successfully",
    "count": 120,
    "next": "http://example.com/api/network/{user_uuid}/followers/?page=2",
    "previous": null,
    "results": [
        {
            "uuid": "follow-uuid",
            "user": {
                "uuid": "follower-uuid",
                "username": "follower_username",
                "email": "follower@example.com",
                "full_name": "Follower Name",
                "first_name": "Follower",
                "last_name": "Name",
                "profile_photo": "https://example.com/photo.jpg"
            },
            "is_following_back": true,
            "created_at": "2025-11-03T08:15:00Z"
        }
    ]
}
```

---

### 7. User's Following

Get the list of users that a specific user is following.

**Endpoint**: `GET /api/network/{user_uuid}/following/`

**Path Parameters**:
- `user_uuid`: UUID of the user

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
    "success": true,
    "message": "User following list retrieved successfully",
    "count": 85,
    "next": null,
    "previous": null,
    "results": [
        {
            "uuid": "follow-uuid",
            "user": {
                "uuid": "following-uuid",
                "username": "following_username",
                "email": "following@example.com",
                "full_name": "Following Name",
                "first_name": "Following",
                "last_name": "Name",
                "profile_photo": "https://example.com/photo.jpg"
            },
            "is_follower": false,
            "notify_on_post": true,
            "created_at": "2025-11-02T14:45:00Z"
        }
    ]
}
```

---

### 8. Mutual Followers

Get users who follow both you and another specific user.

**Endpoint**: `GET /api/network/mutual-followers/{user_uuid}/`

**Path Parameters**:
- `user_uuid`: UUID of the other user

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Mutual followers retrieved successfully",
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "uuid": "user-uuid",
            "username": "mutual_user",
            "email": "mutual@example.com",
            "full_name": "Mutual User",
            "first_name": "Mutual",
            "last_name": "User",
            "profile_photo": "https://example.com/photo.jpg"
        }
    ]
}
```

---

### 9. My Network Stats

Get network statistics for the authenticated user.

**Endpoint**: `GET /api/network/stats/`

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Network statistics retrieved successfully",
    "data": {
        "followers_count": 120,
        "following_count": 85,
        "mutual_followers_count": 0
    }
}
```

---

### 10. User Network Stats

Get network statistics for a specific user.

**Endpoint**: `GET /api/network/{user_uuid}/stats/`

**Path Parameters**:
- `user_uuid`: UUID of the user

**Response** (200 OK):
```json
{
    "success": true,
    "message": "User network statistics retrieved successfully",
    "data": {
        "followers_count": 250,
        "following_count": 180,
        "mutual_followers_count": 45,
        "is_following": true,
        "is_follower": false
    }
}
```

**Fields**:
- `followers_count`: Number of users following this user
- `following_count`: Number of users this user is following
- `mutual_followers_count`: Number of users who follow both you and this user
- `is_following`: Whether you are following this user
- `is_follower`: Whether this user is following you

---

## Data Models

### Follow

Represents a follower/following relationship between two users.

**Fields**:
- `uuid` (UUID): Unique identifier for the follow relationship
- `follower` (User): User who is following
- `following` (User): User being followed
- `notify_on_post` (boolean): Whether to notify follower when following user posts (default: true)
- `created_at` (datetime): When the follow relationship was created

**Constraints**:
- A user cannot follow themselves
- A follower/following pair must be unique (no duplicate follows)

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created (successful follow) |
| 400 | Bad Request (validation error, already following, etc.) |
| 401 | Unauthorized (missing or invalid token) |
| 404 | Not Found (user does not exist) |
| 500 | Internal Server Error |

---

## Common Error Response Format

```json
{
    "success": false,
    "message": "Error message describing what went wrong"
}
```

---

## Use Cases

### Following a User
1. User clicks "Follow" button on another user's profile
2. Frontend sends POST request to `/api/network/follow/` with `user_uuid`
3. Backend creates Follow relationship
4. Returns follow details including both users' information

### Viewing Network
1. User navigates to their followers/following page
2. Frontend requests `/api/network/followers/` or `/api/network/following/`
3. Backend returns paginated list with 20 users per page
4. Each result includes whether there's a mutual follow relationship

### Profile Statistics
1. User views another user's profile
2. Frontend requests `/api/network/{user_uuid}/stats/`
3. Backend returns follower/following counts and relationship status
4. Display statistics and "Follow" button based on `is_following` status

---

## Notes

- All endpoints return standardized response format with `success`, `message`, and `data`/`results` fields
- Pagination is supported on list endpoints with configurable page size (max 100)
- The `is_following_back` and `is_follower` fields help identify mutual follows
- Network stats include mutual follower counts for discovering shared connections
- All follow actions are instant - no approval required (direct follow system)

---

## Integration Example

```javascript
// Follow a user
async function followUser(userUuid) {
    const response = await fetch('/api/network/follow/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_uuid: userUuid })
    });
    return await response.json();
}

// Get my followers
async function getMyFollowers(page = 1) {
    const response = await fetch(`/api/network/followers/?page=${page}`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });
    return await response.json();
}

// Get user stats
async function getUserStats(userUuid) {
    const response = await fetch(`/api/network/${userUuid}/stats/`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });
    return await response.json();
}
```
