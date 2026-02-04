# Report System API Documentation

## Overview
The Report System allows users to report other users for violations of community guidelines.

## Endpoints

### 1. Create a Report
**POST** `/api/network/reports/create/`

Create a new report for a user.

**Required Authentication:** Yes (User must be authenticated)

**Request Body:**
```json
{
    "reported_user_uuid": "e5cfc307-4e95-4a8d-9886-98c52cac66b9",
    "reason": "harassment",
    "description": "The user is harassing me in the forum"
}
```

**Parameters:**
- `reported_user_uuid` (UUID, required): UUID of the user being reported
- `reason` (string, required): One of the following:
  - `harassment` - Harassment
  - `hate_speech` - Hate Speech
  - `spam` - Spam
  - `inappropriate_content` - Inappropriate Content
  - `impersonation` - Impersonation
  - `scam` - Scam
  - `other` - Other
- `description` (string, optional): Detailed description of the violation

**Response:**
```json
{
    "success": true,
    "message": "Report submitted successfully",
    "data": {
        "uuid": "dd47e1d2-2647-47b3-abd9-109dfb2e3b43",
        "reported_user": {
            "uuid": "e5cfc307-4e95-4a8d-9886-98c52cac66b9",
            "username": "ferozkhandeveloper",
            "email": "ferozkhan.developer@gmail.com",
            "full_name": "Feroz Khan",
            "first_name": "",
            "last_name": "",
            "profile_photo": "https://op-vanguard-apis.rootpointers.net/media/..."
        },
        "reported_by": {
            "uuid": "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6",
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "profile_photo": "https://..."
        },
        "reason": "harassment",
        "reason_display": "Harassment",
        "description": "The user is harassing me in the forum",
        "status": "pending",
        "status_display": "Pending",
        "created_at": "2025-12-17T10:30:00.123456Z",
        "updated_at": "2025-12-17T10:30:00.123456Z"
    }
}
```

**Errors:**
- `400 Bad Request` - Validation error or duplicate report
- `401 Unauthorized` - User not authenticated
- `500 Internal Server Error` - Server error

---

### 2. Get My Reports
**GET** `/api/network/reports/my-reports/`

Get list of reports made by the current user.

**Required Authentication:** Yes

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): Filter by status (pending, reviewed, resolved, dismissed)

**Response:**
```json
{
    "success": true,
    "message": "Your reports retrieved successfully",
    "count": 5,
    "next": "http://api.example.com/api/network/reports/my-reports/?page=2",
    "previous": null,
    "results": [
        {
            "uuid": "dd47e1d2-2647-47b3-abd9-109dfb2e3b43",
            "reported_user": {...},
            "reported_by": {...},
            "reason": "harassment",
            "reason_display": "Harassment",
            "description": "...",
            "status": "pending",
            "status_display": "Pending",
            "created_at": "2025-12-17T10:30:00.123456Z",
            "updated_at": "2025-12-17T10:30:00.123456Z"
        }
    ]
}
```

---

### 3. List All Reports
**GET** `/api/network/reports/admin-list/`

Get list of all reports in the system.

**Required Authentication:** Yes

**Query Parameters:**
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page
- `status` (string, optional): Filter by status
- `reason` (string, optional): Filter by reason

**Response:**
```json
{
    "success": true,
    "message": "Reports retrieved successfully",
    "count": 25,
    "next": "http://api.example.com/api/network/reports/admin-list/?page=2",
    "previous": null,
    "results": [...]
}
```

---

### 4. Get Reports About a User
**GET** `/api/network/reports/{user_uuid}/user/`

Get all reports about a specific user.

**Required Authentication:** Yes

**URL Parameters:**
- `user_uuid` (UUID, required): UUID of the reported user

**Query Parameters:**
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page
- `status` (string, optional): Filter by status

**Response:**
```json
{
    "success": true,
    "message": "Reports about username retrieved successfully",
    "count": 3,
    "next": null,
    "previous": null,
    "results": [...]
}
```

---

## Error Responses

### Validation Error
```json
{
    "success": false,
    "message": "Validation error",
    "errors": {
        "reported_user_uuid": ["User not found"],
        "reason": ["This field is required."]
    }
}
```

### Duplicate Report
```json
{
    "success": false,
    "message": "Validation error",
    "errors": {
        "non_field_errors": ["You have already reported this user"]
    }
}
```

---

## Report Status

Reports can have the following statuses (managed via Django Admin):
- **Pending** - Initial status when report is created
- **Reviewed** - Report has been reviewed
- **Resolved** - Report has been resolved
- **Dismissed** - Report has been dismissed

Status changes are managed through the Django Admin interface.

---

## Report Reasons

1. **Harassment** - User is harassing other users
2. **Hate Speech** - User is using hate speech
3. **Spam** - User is spamming content
4. **Inappropriate Content** - User is posting inappropriate content
5. **Impersonation** - User is impersonating someone
6. **Scam** - User is scamming others
7. **Other** - Other violations

---

## Rate Limiting

- Users can report each user only once (duplicate reports are automatically rejected)

---

## Database Model

### Report Fields

| Field | Type | Description |
|-------|------|-------------|
| uuid | UUID | Primary key |
| reported_user | ForeignKey | User being reported |
| reported_by | ForeignKey | User making the report |
| reason | CharField | Reason for report |
| description | TextField | Detailed description (optional) |
| status | CharField | Current status |
| created_at | DateTime | Report creation time |
| updated_at | DateTime | Last update time |

### Constraints

- `reported_user` and `reported_by` must be different users
- `reported_user` and `reported_by` must be unique together (one report per user pair)

---

## Admin Management

Report status can be changed through the Django Admin interface at `/admin/network/report/`. Admins can:
- View all reports with filtering by status and reason
- Search reports by user email/username
- Update report status directly in the admin panel
