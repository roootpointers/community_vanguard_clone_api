# Intel Category API Documentation

## Overview
This API provides full CRUD operations for managing Intel Categories. Categories are used to organize intel posts by type (e.g., Security, Infrastructure, Training, etc.).

**Base URL**: `/api/intel-category/`

---

## Authentication & Permissions

| Action | Permission Required |
|--------|-------------------|
| List Categories | Authenticated User |
| Retrieve Category | Authenticated User |
| Create Category | Admin (`is_staff=True` or `is_superuser=True`) |
| Update Category | Admin (`is_staff=True` or `is_superuser=True`) |
| Delete Category | Admin (`is_staff=True` or `is_superuser=True`) |

---

## Endpoints

### 1. List Categories (Paginated)

Get a paginated list of all intel categories.

**Endpoint**: `GET /api/intel-category/`

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)
- `search` (optional): Search by category name
- `ordering` (optional): Order by field (options: `name`, `created_at`, `updated_at`, `-name`, `-created_at`, `-updated_at`)

**Examples**:
```
GET /api/intel-category/
GET /api/intel-category/?page=2&page_size=20
GET /api/intel-category/?search=security
GET /api/intel-category/?ordering=-created_at
```

**Headers**:
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Intel categories retrieved successfully.",
  "count": 15,
  "next": "http://api.example.com/api/intel-category/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Security",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Infrastructure",
      "created_at": "2024-01-16T11:30:00Z",
      "updated_at": "2024-01-16T11:30:00Z"
    }
  ]
}
```

**Error Response** (500):
```json
{
  "success": false,
  "message": "Failed to retrieve intel categories.",
  "errors": "Error details"
}
```

---

### 2. Retrieve Category

Get details of a specific intel category by UUID.

**Endpoint**: `GET /api/intel-category/{uuid}/`

**Headers**:
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Intel category retrieved successfully.",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Security",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:

- **404 Not Found**:
```json
{
  "success": false,
  "message": "Intel category not found.",
  "errors": {
    "uuid": ["Category with this UUID does not exist."]
  }
}
```

---

### 3. Create Category

Create a new intel category (Admin only).

**Endpoint**: `POST /api/intel-category/`

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
  "name": "Cybersecurity"
}
```

**Success Response** (201 Created):
```json
{
  "success": true,
  "message": "Intel category created successfully.",
  "data": {
    "uuid": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Cybersecurity",
    "created_at": "2024-01-20T14:30:00Z",
    "updated_at": "2024-01-20T14:30:00Z"
  }
}
```

**Error Responses**:

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "message": "Failed to create intel category.",
  "errors": {
    "name": ["Category with this name already exists."]
  }
}
```

- **400 Bad Request** - Missing required field:
```json
{
  "success": false,
  "message": "Failed to create intel category.",
  "errors": {
    "name": ["This field is required."]
  }
}
```

- **403 Forbidden** - Non-admin user:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 4. Update Category (Full Update)

Update all fields of an intel category (Admin only).

**Endpoint**: `PUT /api/intel-category/{uuid}/`

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
  "name": "Advanced Cybersecurity"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Intel category updated successfully.",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Advanced Cybersecurity",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T15:45:00Z"
  }
}
```

**Error Responses**:

- **400 Bad Request** - Duplicate name:
```json
{
  "success": false,
  "message": "Failed to update intel category.",
  "errors": {
    "name": ["Category with this name already exists."]
  }
}
```

- **404 Not Found**:
```json
{
  "success": false,
  "message": "Intel category not found.",
  "errors": {
    "uuid": ["Category with this UUID does not exist."]
  }
}
```

---

### 5. Partial Update Category

Update specific fields of an intel category (Admin only).

**Endpoint**: `PATCH /api/intel-category/{uuid}/`

**Headers**:
```json
{
  "Authorization": "Bearer <admin_access_token>",
  "Content-Type": "application/json"
}
```

**Request Body** (any field can be updated):
```json
{
  "name": "Updated Category Name"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Intel category updated successfully.",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Updated Category Name",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T16:00:00Z"
  }
}
```

---

### 6. Delete Category

Delete an intel category (Admin only).

**Endpoint**: `DELETE /api/intel-category/{uuid}/`

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
  "message": "Intel category deleted successfully.",
  "data": {
    "name": "Security"
  }
}
```

**Error Responses**:

- **400 Bad Request** - Category in use:
```json
{
  "success": false,
  "message": "Cannot delete category. It is being used by 15 intel post(s).",
  "errors": {
    "category": ["This category is associated with 15 intel post(s)."]
  }
}
```

- **404 Not Found**:
```json
{
  "success": false,
  "message": "Intel category not found.",
  "errors": {
    "uuid": ["Category with this UUID does not exist."]
  }
}
```

---

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uuid` | UUID | Read-only | Unique identifier for the category |
| `name` | String | Yes | Category name (max 100 characters, must be unique) |
| `created_at` | DateTime | Read-only | Timestamp when category was created |
| `updated_at` | DateTime | Read-only | Timestamp when category was last updated |

---

## Validation Rules

1. **Name Uniqueness**: Category names must be unique (case-insensitive)
2. **Name Required**: Name field is mandatory for create operations
3. **Name Length**: Maximum 100 characters
4. **Delete Protection**: Categories cannot be deleted if they are associated with any intel posts

---

## Usage Examples

### Example 1: Create and List Categories

```bash
# Create a new category
curl -X POST http://api.example.com/api/intel-category/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Cybersecurity"}'

# List all categories with search
curl -X GET "http://api.example.com/api/intel-category/?search=security&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 2: Update and Delete

```bash
# Update a category
curl -X PATCH http://api.example.com/api/intel-category/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Advanced Security"}'

# Delete a category
curl -X DELETE http://api.example.com/api/intel-category/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Notes

- All endpoints require authentication via JWT Bearer token
- Admin-only endpoints require `is_staff=True` or `is_superuser=True`
- Categories are ordered alphabetically by name by default
- Search is case-insensitive and searches within the name field
- Category names are validated for uniqueness in a case-insensitive manner
- All actions are logged for audit purposes
- Delete operations are protected - categories in use cannot be deleted
