# Ban/Unban User API Documentation

## Overview
This API allows administrators to ban and unban users. Banned users cannot log in through any login method (email, social, or admin login).

**Authentication Required**: Yes (Admin only - requires `is_staff=True` or `is_superuser=True`)

---

## Endpoints

### 1. Ban User
Ban a user account, preventing them from logging in.

**Endpoint**: `POST /api/accounts/ban/`

**Headers**:
```json
{
  "Authorization": "Bearer <admin_access_token>",
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "user_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "User user@example.com has been banned successfully.",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "account_type": "email",
    "is_active": true,
    "is_banned": true,
    "is_staff": false,
    "is_superuser": false,
    "is_profile": true,
    "is_role": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z"
  }
}
```

**Error Responses**:

- **400 Bad Request** - Missing user_uuid:
```json
{
  "success": false,
  "message": "user_uuid is required.",
  "errors": {
    "user_uuid": ["This field is required."]
  }
}
```

- **400 Bad Request** - User already banned:
```json
{
  "success": false,
  "message": "User is already banned.",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "is_banned": true
  }
}
```

- **403 Forbidden** - Attempting to ban superuser:
```json
{
  "success": false,
  "message": "Cannot ban superuser accounts.",
  "errors": {
    "user": ["Superusers cannot be banned."]
  }
}
```

- **404 Not Found** - User not found:
```json
{
  "success": false,
  "message": "Not found."
}
```

---

### 2. Unban User
Unban a user account, allowing them to log in again.

**Endpoint**: `POST /api/accounts/unban/`

**Headers**:
```json
{
  "Authorization": "Bearer <admin_access_token>",
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "user_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "User user@example.com has been unbanned successfully.",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "account_type": "email",
    "is_active": true,
    "is_banned": false,
    "is_staff": false,
    "is_superuser": false,
    "is_profile": true,
    "is_role": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:50:00Z"
  }
}
```

**Error Responses**:

- **400 Bad Request** - Missing user_uuid:
```json
{
  "success": false,
  "message": "user_uuid is required.",
  "errors": {
    "user_uuid": ["This field is required."]
  }
}
```

- **400 Bad Request** - User not banned:
```json
{
  "success": false,
  "message": "User is not banned.",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "is_banned": false
  }
}
```

---

### 3. List Banned Users
Get a paginated list of all banned users.

**Endpoint**: `GET /api/accounts/banned-users/`

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 10, max: 100)

**Example**: `/api/accounts/banned-users/?page=1&page_size=20`

**Headers**:
```json
{
  "Authorization": "Bearer <admin_access_token>"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Banned users retrieved successfully.",
  "count": 25,
  "next": "http://api.example.com/api/accounts/banned-users/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "email": "banned1@example.com",
      "full_name": "Banned User 1",
      "account_type": "email",
      "is_active": true,
      "is_banned": true,
      "is_staff": false,
      "is_superuser": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z"
    },
    {
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "email": "banned2@example.com",
      "full_name": "Banned User 2",
      "account_type": "google",
      "is_active": true,
      "is_banned": true,
      "is_staff": false,
      "is_superuser": false,
      "created_at": "2024-01-16T11:30:00Z",
      "updated_at": "2024-01-18T09:20:00Z"
    }
  ]
}
```

---

## Login Prevention

When a banned user attempts to log in, they will receive:

**Response** (403 Forbidden):
```json
{
  "success": false,
  "message": "Your account has been banned. Please contact support.",
  "errors": {
    "account": ["This account is banned."]
  }
}
```

This applies to all login endpoints:
- `/api/accounts/email-login/`
- `/api/accounts/social-login/`
- `/api/accounts/admin-login/`

---

## Admin Interface

Administrators can also ban/unban users through the Django Admin interface:

1. Navigate to the Users section in Django Admin
2. Select one or more users
3. Choose "Ban selected users" or "Unban selected users" from the Actions dropdown
4. Click "Go"

**Notes**:
- The `is_banned` field is displayed in the user list view
- You can filter users by banned status using the filter sidebar
- The ban status is visible in the user detail page under the "Permissions" section

---

## Notes

- **Superusers cannot be banned** through the API (returns 403 Forbidden)
- Banned users are immediately prevented from logging in
- The ban status is logged for audit purposes
- Admin users with appropriate permissions can view all banned users
- Ban/unban actions are logged with the admin user who performed the action
