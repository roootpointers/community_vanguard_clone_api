# Preferred Contribution Path API Documentation

## Overview
The Preferred Contribution Path API provides complete CRUD (Create, Read, Update, Delete) operations for managing contribution path options. Users can view available paths, while administrators can manage them. Contribution paths are used during profile setup for users to indicate their preferred method of contribution to the community.

---

## Endpoints

### 1. List All Preferred Contribution Paths

**Endpoint:** `GET /api/accounts/preferred-contribution-paths/`

**Description:** Retrieves a paginated list of all preferred contribution paths available for selection.

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
    "message": "Preferred contribution paths retrieved successfully",
    "data": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Mentorship"
        },
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174001",
            "name": "Resource Sharing"
        },
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174002",
            "name": "Skill Development"
        }
    ]
}
```

---

### 2. Create New Preferred Contribution Path

**Endpoint:** `POST /api/accounts/preferred-contribution-paths/`

**Description:** Create a new preferred contribution path. Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "Community Building"
}
```

**Success Response (201 Created):**
```json
{
    "success": true,
    "message": "Preferred contribution path created successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174003",
        "name": "Community Building",
        "created_at": "2025-12-10T10:30:00Z",
        "updated_at": "2025-12-10T10:30:00Z"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Failed to create preferred contribution path",
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

### 3. Retrieve Single Preferred Contribution Path

**Endpoint:** `GET /api/accounts/preferred-contribution-paths/{uuid}/`

**Description:** Retrieve details of a specific preferred contribution path by UUID.

**Authentication:** Not required (AllowAny)

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Preferred contribution path retrieved successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Mentorship",
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

### 4. Update Preferred Contribution Path (Full Update)

**Endpoint:** `PUT /api/accounts/preferred-contribution-paths/{uuid}/`

**Description:** Update all fields of a preferred contribution path. Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "Mentorship and Coaching"
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Preferred contribution path updated successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Mentorship and Coaching",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-12-10T10:30:00Z"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Failed to update preferred contribution path",
    "errors": {
        "name": ["Preferred contribution path with this name already exists."]
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

### 5. Update Preferred Contribution Path (Partial Update)

**Endpoint:** `PATCH /api/accounts/preferred-contribution-paths/{uuid}/`

**Description:** Partially update a preferred contribution path (update only specific fields). Only accessible by administrators.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "name": "Knowledge Sharing"
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Preferred contribution path updated successfully",
    "data": {
        "uuid": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Knowledge Sharing",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-12-10T10:35:00Z"
    }
}
```

---

### 6. Delete Preferred Contribution Path

**Endpoint:** `DELETE /api/accounts/preferred-contribution-paths/{uuid}/`

**Description:** Delete a preferred contribution path. Only accessible by administrators. **Warning:** This will affect all user profiles that reference this path.

**Authentication:** Required (Admin only)

**Request Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Preferred contribution path \"Community Building\" deleted successfully",
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
| GET | `/api/accounts/preferred-contribution-paths/` | List all paths | No |
| POST | `/api/accounts/preferred-contribution-paths/` | Create new path | Yes (Admin) |
| GET | `/api/accounts/preferred-contribution-paths/{uuid}/` | Retrieve single path | No |
| PUT | `/api/accounts/preferred-contribution-paths/{uuid}/` | Full update path | Yes (Admin) |
| PATCH | `/api/accounts/preferred-contribution-paths/{uuid}/` | Partial update path | Yes (Admin) |
| DELETE | `/api/accounts/preferred-contribution-paths/{uuid}/` | Delete path | Yes (Admin) |

---

## Using Preferred Contribution Paths in Profile Setup

When creating or updating a user profile, you can select a preferred contribution path by providing the path UUID:

**Example Profile Update Request:**
```json
POST /api/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "full_name": "John Doe",
    "branch": "Army",
    "rank": "Captain",
    "preferred_contribution_path": "123e4567-e89b-12d3-a456-426614174000",
    "location": "Fort Liberty, NC",
    "education": "Bachelor's",
    "degree": "Computer Science"
}
```

**Response with Preferred Contribution Path:**
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
        "preferred_contribution_path": {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Mentorship"
        },
        "location": "Fort Liberty, NC",
        "education": "Bachelor's",
        "degree": "Computer Science"
    }
}
```

---

## Testing with cURL

### List All Preferred Contribution Paths
```bash
curl -X GET http://localhost:8000/api/accounts/preferred-contribution-paths/
```

### Create New Preferred Contribution Path (Admin)
```bash
curl -X POST http://localhost:8000/api/accounts/preferred-contribution-paths/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Training and Education"
  }'
```

### Retrieve Single Preferred Contribution Path
```bash
curl -X GET http://localhost:8000/api/accounts/preferred-contribution-paths/123e4567-e89b-12d3-a456-426614174000/
```

### Update Preferred Contribution Path (Admin)
```bash
curl -X PUT http://localhost:8000/api/accounts/preferred-contribution-paths/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mentorship and Guidance"
  }'
```

### Partially Update Preferred Contribution Path (Admin)
```bash
curl -X PATCH http://localhost:8000/api/accounts/preferred-contribution-paths/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Resource Development"
  }'
```

### Delete Preferred Contribution Path (Admin)
```bash
curl -X DELETE http://localhost:8000/api/accounts/preferred-contribution-paths/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer <admin_access_token>"
```

---

## Admin Management

Administrators can manage preferred contribution paths through both the Django admin panel and the API:

### Django Admin Panel
1. **Navigate to:** `Admin Panel > Accounts > Preferred Contribution Paths`
2. **Actions Available:**
   - Add new paths
   - Edit existing paths
   - Delete paths
   - View path metadata (created_at, updated_at)

### API Management (Recommended)
Using the Preferred Contribution Path API endpoints provides more flexibility:
- **Create:** `POST /api/accounts/preferred-contribution-paths/`
- **Update:** `PUT/PATCH /api/accounts/preferred-contribution-paths/{uuid}/`
- **Delete:** `DELETE /api/accounts/preferred-contribution-paths/{uuid}/`

**PreferredContributionPath Model Fields:**
- `uuid` (auto-generated): Unique identifier for the path
- `name` (required, unique): Name of the contribution path (e.g., "Mentorship", "Resource Sharing")
- `created_at` (auto): Timestamp when the path was created
- `updated_at` (auto): Timestamp when the path was last updated

---

## Common Use Cases

### 1. Get Available Paths for Selection UI
```
GET /api/accounts/preferred-contribution-paths/
```
Use this endpoint to populate a dropdown or radio button list in your profile setup UI.

### 2. Admin Creates New Contribution Path
```
POST /api/accounts/preferred-contribution-paths/
Authorization: Bearer <admin_token>
{
    "name": "Event Organization"
}
```

### 3. Create Profile with Preferred Contribution Path
```
POST /api/profile/
{
    "full_name": "Jane Smith",
    "preferred_contribution_path": "uuid1"
}
```

### 4. Update User's Preferred Contribution Path
```
PATCH /api/profile/{profile_uuid}/
{
    "preferred_contribution_path": "uuid2"
}
```

### 5. View User Profile with Contribution Path
```
GET /api/profile/{profile_uuid}/
```
Returns the full profile including expanded contribution path object.

### 6. Admin Updates Path Name
```
PATCH /api/accounts/preferred-contribution-paths/{uuid}/
Authorization: Bearer <admin_token>
{
    "name": "Mentorship and Leadership"
}
```

### 7. Admin Deletes Obsolete Path
```
DELETE /api/accounts/preferred-contribution-paths/{uuid}/
Authorization: Bearer <admin_token>
```

---

## Example Contribution Paths

Here are some common contribution path examples that might be used:

- **Mentorship** - Guiding and advising others
- **Resource Sharing** - Sharing knowledge, tools, and materials
- **Skill Development** - Teaching specific skills or techniques
- **Community Building** - Organizing events and fostering connections
- **Content Creation** - Creating educational content or documentation
- **Technical Support** - Providing technical assistance
- **Project Leadership** - Leading initiatives and projects
- **Research and Innovation** - Exploring new ideas and technologies
- **Training and Education** - Conducting workshops and training sessions
- **Networking** - Connecting people and facilitating partnerships

---

## Error Handling

### Common Error Codes
- **400 Bad Request:** Invalid data in request body (e.g., missing name, duplicate name)
- **401 Unauthorized:** Missing or invalid authentication token
- **403 Forbidden:** User is not an administrator (for create/update/delete operations)
- **404 Not Found:** Contribution path with specified UUID does not exist

### Validation Rules
- **name:** Required, must be unique, max length 255 characters
- **uuid:** Auto-generated, cannot be modified

---

## Best Practices

1. **For Users:** Always fetch the latest contribution paths list before displaying profile setup forms
2. **For Admins:** 
   - Use clear, descriptive names for contribution paths
   - Before deleting a path, consider the impact on existing user profiles
   - Use PATCH for partial updates to avoid overwriting unintended fields
   - Keep the list of paths concise and meaningful
3. **For Developers:**
   - Cache the contribution paths list on the client side to reduce API calls
   - Implement proper error handling for all CRUD operations
   - Always use UUID for path references, never use the name field
   - Validate path selection on the client side before submission

---

## Integration Examples

### React Example - Fetching Contribution Paths
```javascript
const fetchContributionPaths = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/accounts/preferred-contribution-paths/');
    const result = await response.json();
    if (result.success) {
      setContributionPaths(result.data);
    }
  } catch (error) {
    console.error('Error fetching contribution paths:', error);
  }
};
```

### React Example - Creating Contribution Path (Admin)
```javascript
const createContributionPath = async (name) => {
  try {
    const response = await fetch('http://localhost:8000/api/accounts/preferred-contribution-paths/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken}`
      },
      body: JSON.stringify({ name })
    });
    const result = await response.json();
    if (result.success) {
      console.log('Contribution path created:', result.data);
    } else {
      console.error('Failed to create:', result.errors);
    }
  } catch (error) {
    console.error('Error creating contribution path:', error);
  }
};
```

### React Example - Profile Form with Contribution Path Selection
```javascript
const ProfileForm = () => {
  const [paths, setPaths] = useState([]);
  const [selectedPath, setSelectedPath] = useState('');

  useEffect(() => {
    fetchContributionPaths();
  }, []);

  const handleSubmit = async (formData) => {
    const profileData = {
      ...formData,
      preferred_contribution_path: selectedPath
    };
    // Submit profile data
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Other form fields */}
      <select 
        value={selectedPath} 
        onChange={(e) => setSelectedPath(e.target.value)}
      >
        <option value="">Select contribution path</option>
        {paths.map(path => (
          <option key={path.uuid} value={path.uuid}>
            {path.name}
          </option>
        ))}
      </select>
    </form>
  );
};
```

---

## Notes

- Contribution paths represent the user's preferred way of contributing to the community
- Each user profile can have one preferred contribution path (ForeignKey relationship)
- Changes to path names will be reflected in all user profiles that reference that path
- Deleting a path may set the preferred_contribution_path field to null for affected user profiles (depending on the model's `on_delete` behavior)
- Contribution paths help administrators understand user engagement preferences and organize community activities
