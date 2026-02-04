# Interest API Documentation

## Overview
The Interest API provides complete CRUD (Create, Read, Update, Delete) operations for managing interests. Users can view available interests, while administrators can manage them. Interests are used during profile setup for users to indicate their areas of expertise or interest.

---

## Endpoints

### 1. List All Interests

**Endpoint:** `GET /api/accounts/interests/`

**Description:** Retrieves a paginated list of all interests available for selection.

**Authentication:** Not required (AllowAny)

**Request Headers:**
```
Content-Type: application/json
```

**Request Parameters:** 
- Query parameters for pagination (handled automatically by CommonPagination)

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Interests retrieved successfully",
    "data": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Aviation"
        },
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174001",
            "name": "Medical Training"
        },
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174002",
            "name": "Technology"
        }
    ]
}
```

---

### 2. Create New Interest

**Endpoint:** `POST /api/accounts/interests/`

**Description:** Create a new interest. Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "Cybersecurity"
}
```

**Success Response (201 Created):**
```json
{
    "success": true,
    "message": "Interest created successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174003",
        "name": "Cybersecurity",
        "created_at": "2025-12-10T10:30:00Z",
        "updated_at": "2025-12-10T10:30:00Z"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Failed to create interest",
    "errors": {
        "name": ["This field is required."]
    }
}
```

**Error Response (403 Forbidden):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### 3. Retrieve Single Interest

**Endpoint:** `GET /api/accounts/interests/{uuid}/`

**Description:** Retrieve details of a specific interest by UUID.

**Authentication:** Not required (AllowAny)

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Interest retrieved successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Aviation",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "detail": "Not found."
}
```

---

### 4. Update Interest (Full Update)

**Endpoint:** `PUT /api/accounts/interests/{uuid}/`

**Description:** Update all fields of an interest. Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "Aviation and Aerospace"
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Interest updated successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Aviation and Aerospace",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-12-10T10:30:00Z"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Failed to update interest",
    "errors": {
        "name": ["Interest with this name already exists."]
    }
}
```

**Error Response (403 Forbidden):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### 5. Update Interest (Partial Update)

**Endpoint:** `PATCH /api/accounts/interests/{uuid}/`

**Description:** Partially update an interest (update only specific fields). Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "Medical and Healthcare"
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Interest updated successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Medical and Healthcare",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-12-10T10:35:00Z"
    }
}
```

---

### 6. Delete Interest

**Endpoint:** `DELETE /api/accounts/interests/{uuid}/`

**Description:** Delete an interest. Only accessible by administrators. **Warning:** This will remove the interest from all user profiles that reference it.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Interest \"Cybersecurity\" deleted successfully",
    "data": null
}
```

**Error Response (404 Not Found):**
```json
{
    "detail": "Not found."
}
```

**Error Response (403 Forbidden):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

## API Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/accounts/interests/` | List all interests | No |
| POST | `/api/accounts/interests/` | Create new interest | Yes (Admin) |
| GET | `/api/accounts/interests/{uuid}/` | Retrieve single interest | No |
| PUT | `/api/accounts/interests/{uuid}/` | Full update interest | Yes (Admin) |
| PATCH | `/api/accounts/interests/{uuid}/` | Partial update interest | Yes (Admin) |
| DELETE | `/api/accounts/interests/{uuid}/` | Delete interest | Yes (Admin) |

---

## Using Interests in Profile Setup

When creating or updating a user profile, you can select multiple interests by providing an array of interest UUIDs:

**Example Profile Update Request:**
```json
POST /api/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "full_name": "John Doe",
    "branch": "Army",
    "rank": "Captain",
    "location": "Fort Liberty, NC",
    "interests": [
        "123e4567-e89b-12d3-a456-426614174000",
        "123e4567-e89b-12d3-a456-426614174002"
    ],
    "education": "Bachelor's",
    "degree": "Computer Science"
}
```

**Response with Interests:**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "data": {
        "uuid": "user-profile-uuid",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "branch": "Army",
        "rank": "Captain",
        "location": "Fort Liberty, NC",
        "interests": [
            {
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Aviation"
            },
            {
                "uuid": "123e4567-e89b-12d3-a456-426614174002",
                "name": "Technology"
            }
        ],
        "education": "Bachelor's",
        "degree": "Computer Science"
    }
}
```

---

## Testing with cURL

### List All Interests
```bash
curl -X GET http://localhost:8000/api/accounts/interests/
```

### Create New Interest (Admin)
```bash
curl -X POST http://localhost:8000/api/accounts/interests/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cybersecurity"
  }'
```

### Retrieve Single Interest
```bash
curl -X GET http://localhost:8000/api/accounts/interests/123e4567-e89b-12d3-a456-426614174000/
```

### Update Interest (Admin)
```bash
curl -X PUT http://localhost:8000/api/accounts/interests/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aviation and Aerospace"
  }'
```

### Partially Update Interest (Admin)
```bash
curl -X PATCH http://localhost:8000/api/accounts/interests/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Medical and Healthcare"
  }'
```

### Delete Interest (Admin)
```bash
curl -X DELETE http://localhost:8000/api/accounts/interests/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>"
```

---

## Admin Management

Administrators can manage interests through both the Django admin panel and the API:

### Django Admin Panel
1. **Navigate to:** `Admin Panel > Accounts > Interests`
2. **Actions Available:**
   - Add new interests
   - Edit existing interests
   - Delete interests
   - View interest metadata (created_at, updated_at)

### API Management (Recommended)
Using the Interest API endpoints provides more flexibility:
- **Create:** `POST /api/accounts/interests/`
- **Update:** `PUT/PATCH /api/accounts/interests/{uuid}/`
- **Delete:** `DELETE /api/accounts/interests/{uuid}/`

**Interest Model Fields:**
- `uuid` (auto-generated): Unique identifier for the interest
- `name` (required, unique): Name of the interest (e.g., "Aviation", "Medical Training")
- `created_at` (auto): Timestamp when the interest was created
- `updated_at` (auto): Timestamp when the interest was last updated

---

## Migration Notes

When migrating from the old text-based interest field to the new many-to-many relationship:

1. Run migrations: `python manage.py migrate accounts`
2. The old `interest` TextField will be removed
3. A new `interests` ManyToManyField will be created
4. **Note:** Existing interest data will be lost during migration. You should:
   - Export existing interests before migration
   - Create Interest objects through the admin panel
   - Have users re-select their interests

---

## Implementation Notes

### Model Changes
- **Old:** `interest = models.TextField(null=True, blank=True)`
- **New:** `interests = models.ManyToManyField('Interest', related_name='user_profiles', blank=True)`

### Serializer Changes
- Profile serializers now accept an array of UUIDs for write operations
- Profile serializers return full interest objects (with name and description) for read operations
- Interests are filtered to show only active interests

### API Request Examples

**Selecting No Interests:**
```json
{
    "interests": []
}
```

**Selecting Multiple Interests:**
```json
{
    "interests": [
        "uuid1",
        "uuid2",
        "uuid3"
    ]
}
```

**Omitting Interests (keeps existing):**
```json
{
    "full_name": "John Doe",
    "branch": "Army"
}
```

---

## Common Use Cases

### 1. Get Available Interests for Selection UI
```
GET /api/accounts/interests/
```
Use this endpoint to populate a multi-select dropdown or checkbox list in your profile setup UI.

### 2. Admin Creates New Interest
```
POST /api/accounts/interests/
Authorization: Bearer <admin_token>
{
    "name": "Artificial Intelligence"
}
```

### 3. Create Profile with Interests
```
POST /api/profile/
{
    "full_name": "Jane Smith",
    "interests": ["uuid1", "uuid2"]
}
```

### 4. Update User Interests
```
PATCH /api/profile/{profile_uuid}/
{
    "interests": ["uuid3", "uuid4", "uuid5"]
}
```

### 5. View User Profile with Interests
```
GET /api/profile/{profile_uuid}/
```
Returns the full profile including expanded interest objects.

### 6. Admin Updates Interest Name
```
PATCH /api/accounts/interests/{uuid}/
Authorization: Bearer <admin_token>
{
    "name": "AI and Machine Learning"
}
```

### 7. Admin Deletes Obsolete Interest
```
DELETE /api/accounts/interests/{uuid}/
Authorization: Bearer <admin_token>
```

---

## Error Handling

### Common Error Codes
- **400 Bad Request:** Invalid data in request body (e.g., missing name, duplicate name)
- **401 Unauthorized:** Missing or invalid authentication token
- **403 Forbidden:** User is not an administrator (for create/update/delete operations)
- **404 Not Found:** Interest with specified UUID does not exist

### Validation Rules
- **name:** Required, must be unique, max length 100 characters
- **uuid:** Auto-generated, cannot be modified

---

## Best Practices

1. **For Users:** Always fetch the latest interests list before displaying profile setup forms
2. **For Admins:** 
   - Use descriptive names for interests
   - Before deleting an interest, consider the impact on existing user profiles
   - Use PATCH for partial updates to avoid overwriting unintended fields
3. **For Developers:**
   - Cache the interests list on the client side to reduce API calls
   - Implement proper error handling for all CRUD operations
   - Always use UUID for interest references, never use the name field

---

## Testing

Use these curl commands to test the Interest API:

**List Interests:**
```bash
curl -X GET http://localhost:8000/api/accounts/interests/
```

**Update Profile with Interests:**
```bash
curl -X POST http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "interests": ["uuid1", "uuid2"]
  }'
```
