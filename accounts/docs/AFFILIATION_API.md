# Affiliation API Documentation

## Overview
The Affiliation API provides complete CRUD (Create, Read, Update, Delete) operations for managing organizational/military affiliations. Users can view available affiliations, while administrators can manage them. Affiliations are used during profile setup for users to indicate their organizational affiliation.

---

## Endpoints

### 1. List All Affiliations

**Endpoint:** `GET /api/accounts/affiliations/`

**Description:** Retrieves a paginated list of all affiliations available for selection.

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
    "message": "Affiliations retrieved successfully",
    "data": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "name": "U.S. Army"
        },
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174001",
            "name": "U.S. Navy"
        },
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174002",
            "name": "U.S. Air Force"
        }
    ]
}
```

---

### 2. Create New Affiliation

**Endpoint:** `POST /api/accounts/affiliations/`

**Description:** Create a new affiliation. Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "U.S. Space Force"
}
```

**Success Response (201 Created):**
```json
{
    "success": true,
    "message": "Affiliation created successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174003",
        "name": "U.S. Space Force",
        "created_at": "2025-12-10T10:30:00Z",
        "updated_at": "2025-12-10T10:30:00Z"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Failed to create affiliation",
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

### 3. Retrieve Single Affiliation

**Endpoint:** `GET /api/accounts/affiliations/{uuid}/`

**Description:** Retrieve details of a specific affiliation by UUID.

**Authentication:** Not required (AllowAny)

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Affiliation retrieved successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "U.S. Army",
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

### 4. Update Affiliation (Full Update)

**Endpoint:** `PUT /api/accounts/affiliations/{uuid}/`

**Description:** Update all fields of an affiliation. Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "United States Army"
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Affiliation updated successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "United States Army",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-12-10T10:30:00Z"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Failed to update affiliation",
    "errors": {
        "name": ["Affiliation with this name already exists."]
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

### 5. Update Affiliation (Partial Update)

**Endpoint:** `PATCH /api/accounts/affiliations/{uuid}/`

**Description:** Partially update an affiliation (update only specific fields). Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "U.S. Marine Corps"
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Affiliation updated successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174001",
        "name": "U.S. Marine Corps",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-12-10T10:35:00Z"
    }
}
```

---

### 6. Delete Affiliation

**Endpoint:** `DELETE /api/accounts/affiliations/{uuid}/`

**Description:** Delete an affiliation. Only accessible by administrators. **Warning:** This will affect all user profiles that reference this affiliation.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Affiliation \"U.S. Space Force\" deleted successfully",
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
| GET | `/api/accounts/affiliations/` | List all affiliations | No |
| POST | `/api/accounts/affiliations/` | Create new affiliation | Yes (Admin) |
| GET | `/api/accounts/affiliations/{uuid}/` | Retrieve single affiliation | No |
| PUT | `/api/accounts/affiliations/{uuid}/` | Full update affiliation | Yes (Admin) |
| PATCH | `/api/accounts/affiliations/{uuid}/` | Partial update affiliation | Yes (Admin) |
| DELETE | `/api/accounts/affiliations/{uuid}/` | Delete affiliation | Yes (Admin) |

---

## Using Affiliations in Profile Setup

When creating or updating a user profile, you can select an affiliation by providing the affiliation UUID:

**Example Profile Update Request:**
```json
POST /api/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "full_name": "John Doe",
    "branch": "Army",
    "rank": "Captain",
    "affiliation": "123e4567-e89b-12d3-a456-426614174000",
    "location": "Fort Liberty, NC",
    "education": "Bachelor's",
    "degree": "Computer Science"
}
```

**Response with Affiliation:**
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
        "affiliation": {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "name": "U.S. Army"
        },
        "location": "Fort Liberty, NC",
        "education": "Bachelor's",
        "degree": "Computer Science"
    }
}
```

---

## Testing with cURL

### List All Affiliations
```bash
curl -X GET http://localhost:8000/api/accounts/affiliations/
```

### Create New Affiliation (Admin)
```bash
curl -X POST http://localhost:8000/api/accounts/affiliations/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "U.S. Coast Guard"
  }'
```

### Retrieve Single Affiliation
```bash
curl -X GET http://localhost:8000/api/accounts/affiliations/123e4567-e89b-12d3-a456-426614174000/
```

### Update Affiliation (Admin)
```bash
curl -X PUT http://localhost:8000/api/accounts/affiliations/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "United States Army"
  }'
```

### Partially Update Affiliation (Admin)
```bash
curl -X PATCH http://localhost:8000/api/accounts/affiliations/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "U.S. Army Reserve"
  }'
```

### Delete Affiliation (Admin)
```bash
curl -X DELETE http://localhost:8000/api/accounts/affiliations/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>"
```

---

## Admin Management

Administrators can manage affiliations through both the Django admin panel and the API:

### Django Admin Panel
1. **Navigate to:** `Admin Panel > Accounts > Affiliations`
2. **Actions Available:**
   - Add new affiliations
   - Edit existing affiliations
   - Delete affiliations
   - View affiliation metadata (created_at, updated_at)

### API Management (Recommended)
Using the Affiliation API endpoints provides more flexibility:
- **Create:** `POST /api/accounts/affiliations/`
- **Update:** `PUT/PATCH /api/accounts/affiliations/{uuid}/`
- **Delete:** `DELETE /api/accounts/affiliations/{uuid}/`

**Affiliation Model Fields:**
- `uuid` (auto-generated): Unique identifier for the affiliation
- `name` (required, unique): Name of the affiliation (e.g., "U.S. Army", "U.S. Navy")
- `created_at` (auto): Timestamp when the affiliation was created
- `updated_at` (auto): Timestamp when the affiliation was last updated

---

## Common Use Cases

### 1. Get Available Affiliations for Selection UI
```
GET /api/accounts/affiliations/
```
Use this endpoint to populate a dropdown or radio button list in your profile setup UI.

### 2. Admin Creates New Affiliation
```
POST /api/accounts/affiliations/
Authorization: Bearer <admin_token>
{
    "name": "Department of Defense Civilian"
}
```

### 3. Create Profile with Affiliation
```
POST /api/profile/
{
    "full_name": "Jane Smith",
    "affiliation": "uuid1"
}
```

### 4. Update User Affiliation
```
PATCH /api/profile/{profile_uuid}/
{
    "affiliation": "uuid2"
}
```

### 5. View User Profile with Affiliation
```
GET /api/profile/{profile_uuid}/
```
Returns the full profile including expanded affiliation object.

### 6. Admin Updates Affiliation Name
```
PATCH /api/accounts/affiliations/{uuid}/
Authorization: Bearer <admin_token>
{
    "name": "U.S. Armed Forces"
}
```

### 7. Admin Deletes Obsolete Affiliation
```
DELETE /api/accounts/affiliations/{uuid}/
Authorization: Bearer <admin_token>
```

---

## Error Handling

### Common Error Codes
- **400 Bad Request:** Invalid data in request body (e.g., missing name, duplicate name)
- **401 Unauthorized:** Missing or invalid authentication token
- **403 Forbidden:** User is not an administrator (for create/update/delete operations)
- **404 Not Found:** Affiliation with specified UUID does not exist

### Validation Rules
- **name:** Required, must be unique, max length 255 characters
- **uuid:** Auto-generated, cannot be modified

---

## Best Practices

1. **For Users:** Always fetch the latest affiliations list before displaying profile setup forms
2. **For Admins:** 
   - Use clear, official names for affiliations (e.g., "U.S. Army" not "Army")
   - Before deleting an affiliation, consider the impact on existing user profiles
   - Use PATCH for partial updates to avoid overwriting unintended fields
3. **For Developers:**
   - Cache the affiliations list on the client side to reduce API calls
   - Implement proper error handling for all CRUD operations
   - Always use UUID for affiliation references, never use the name field
   - Validate affiliation selection on the client side before submission

---

## Integration Examples

### React Example - Fetching Affiliations
```javascript
const fetchAffiliations = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/accounts/affiliations/');
    const result = await response.json();
    if (result.success) {
      setAffiliations(result.data);
    }
  } catch (error) {
    console.error('Error fetching affiliations:', error);
  }
};
```

### React Example - Creating Affiliation (Admin)
```javascript
const createAffiliation = async (name) => {
  try {
    const response = await fetch('http://localhost:8000/api/accounts/affiliations/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken}`
      },
      body: JSON.stringify({ name })
    });
    const result = await response.json();
    if (result.success) {
      console.log('Affiliation created:', result.data);
    }
  } catch (error) {
    console.error('Error creating affiliation:', error);
  }
};
```

---

## Notes

- Affiliations are typically used to represent military branches, government agencies, or organizational units
- Each user profile can have one affiliation (ForeignKey relationship)
- Changes to affiliation names will be reflected in all user profiles that reference that affiliation
- Deleting an affiliation may set the affiliation field to null for affected user profiles (depending on the model's `on_delete` behavior)
