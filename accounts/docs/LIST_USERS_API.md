# List All Users API

## Overview
This endpoint allows authenticated users to view a paginated list of all users in the system with filtering and search capabilities.

## Endpoint Details

### List All Users
Retrieve a paginated list of all users with their profile information.

**Endpoint:** `GET /api/user/`

**Authentication:** Required (JWT Token)

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `search` (optional): Search in email, full_name, branch, rank, location
- `email` (optional): Filter by exact email address
- `ordering` (optional): Sort by created_at, full_name, email (prefix with `-` for descending)

---

## Request Examples

### 1. List All Users (Basic)
```http
GET /api/user/
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "count": 150,
  "next": "http://localhost:8000/api/user/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "role": {
        "uuid": "role-uuid-here",
        "role_name": "Veteran",
        "created_at": "2024-10-15T08:00:00Z",
        "updated_at": "2024-10-15T08:00:00Z"
      },
      "birth_date": "1990-05-15",
      "gender": "Male",
      "profile_photo": "https://cdn.example.com/profiles/johndoe.jpg",
      "branch": "Army",
      "rank": "Sergeant",
      "mos_afsc": "11B",
      "location": "San Francisco, CA",
      "interest": "Technology, Veterans Affairs",
      "preferred_contribution_path": "Volunteer",
      "affiliation": "Veterans Organization",
      "is_verified": true,
      "education": "Bachelor of Science in Computer Science",
      "degree": "BS",
      "military_civilian_skills": {
        "military": ["Leadership", "Logistics"],
        "civilian": ["Project Management", "Software Development"]
      },
      "certifications": "PMP, CISSP",
      "ets": "2022-12-31",
      "family_status": "Married",
      "created_at": "2024-10-15T08:00:00Z",
      "updated_at": "2024-10-20T12:30:00Z"
    },
    {
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "email": "jane.smith@example.com",
      "full_name": "Jane Smith",
      "role": {
        "uuid": "role-uuid-here-2",
        "role_name": "Supporter",
        "created_at": "2024-10-16T09:00:00Z",
        "updated_at": "2024-10-16T09:00:00Z"
      },
      "branch": "Navy",
      "rank": "Lieutenant",
      "location": "Seattle, WA",
      "is_verified": true,
      "created_at": "2024-10-16T09:00:00Z",
      "updated_at": "2024-10-21T10:15:00Z"
    }
  ]
}
```

### 2. Search Users
```http
GET /api/user/?search=john
Authorization: Bearer <your_jwt_token>
```

Search will look for "john" in:
- Email
- Full name
- Branch
- Rank
- Location

### 3. Filter by Email
```http
GET /api/user/?email=john.doe@example.com
Authorization: Bearer <your_jwt_token>
```

### 4. Pagination with Custom Page Size
```http
GET /api/user/?page=2&page_size=50
Authorization: Bearer <your_jwt_token>
```

### 5. Ordering/Sorting
```http
# Sort by full name (ascending)
GET /api/user/?ordering=full_name
Authorization: Bearer <your_jwt_token>

# Sort by creation date (descending - newest first)
GET /api/user/?ordering=-created_at
Authorization: Bearer <your_jwt_token>

# Sort by email (ascending)
GET /api/user/?ordering=email
Authorization: Bearer <your_jwt_token>
```

### 6. Combined Filters
```http
GET /api/user/?search=Army&ordering=-created_at&page_size=30
Authorization: Bearer <your_jwt_token>
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `message` | string | Descriptive message about the operation |
| `count` | integer | Total number of users matching the query |
| `next` | string/null | URL for the next page |
| `previous` | string/null | URL for the previous page |
| `results` | array | Array of user objects |

### User Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | string | User's unique identifier |
| `email` | string | User's email address |
| `full_name` | string | User's full name |
| `role` | object/null | User's role information |
| `birth_date` | string/null | Date of birth (YYYY-MM-DD) |
| `gender` | string/null | User's gender |
| `profile_photo` | string/null | URL to profile photo |
| `branch` | string/null | Military branch |
| `rank` | string/null | Military rank |
| `mos_afsc` | string/null | Military Occupational Specialty |
| `location` | string/null | Current location |
| `interest` | string/null | Areas of interest |
| `preferred_contribution_path` | string/null | Preferred contribution method |
| `affiliation` | string/null | Organization affiliation |
| `is_verified` | boolean | Whether profile is verified |
| `education` | string/null | Educational background |
| `degree` | string/null | Academic degree |
| `military_civilian_skills` | object/null | Skills JSON object |
| `certifications` | string/null | Professional certifications |
| `ets` | string/null | End of Term of Service date |
| `family_status` | string/null | Family status |
| `created_at` | string | Account creation timestamp |
| `updated_at` | string | Last update timestamp |

---

## Error Responses

### Authentication Required
**Status Code:** `401 UNAUTHORIZED`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Invalid Token
**Status Code:** `401 UNAUTHORIZED`

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

### Invalid Page Number
**Status Code:** `404 NOT FOUND`

```json
{
  "detail": "Invalid page."
}
```

### Server Error
**Status Code:** `500 INTERNAL SERVER ERROR`

```json
{
  "success": false,
  "message": "Failed to retrieve users",
  "error": "Error details..."
}
```

---

## Use Cases

1. **User Directory:** Display a searchable directory of all users
2. **Member Discovery:** Find users with specific skills or backgrounds
3. **Admin Panel:** Manage and view all system users
4. **Networking:** Browse community members for connections
5. **Statistics:** Generate user reports and analytics
6. **Search Functionality:** Find users by name, location, branch, etc.

---

## Example Implementation

### JavaScript/Fetch API
```javascript
async function getAllUsers(token, page = 1, pageSize = 20) {
  const response = await fetch(
    `http://localhost:8000/api/user/?page=${page}&page_size=${pageSize}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  const data = await response.json();
  
  if (data.success) {
    console.log(`Total users: ${data.count}`);
    console.log(`Current page: ${page}`);
    console.log(`Users on this page: ${data.results.length}`);
    
    data.results.forEach(user => {
      console.log(`- ${user.full_name} (${user.email})`);
    });
  }
  
  return data;
}

// Usage
const token = 'your-jwt-token';
getAllUsers(token, 1, 20);
```

### Search Users
```javascript
async function searchUsers(token, searchTerm) {
  const response = await fetch(
    `http://localhost:8000/api/user/?search=${encodeURIComponent(searchTerm)}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  const data = await response.json();
  return data.results;
}

// Find all users with "Army" in their profile
searchUsers(token, 'Army');
```

### Filter by Branch
```javascript
async function getUsersByBranch(token, branch) {
  const response = await fetch(
    `http://localhost:8000/api/user/?search=${branch}&ordering=-created_at`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  const data = await response.json();
  return data.results.filter(user => 
    user.branch && user.branch.toLowerCase().includes(branch.toLowerCase())
  );
}

// Get all Army veterans
getUsersByBranch(token, 'Army');
```

---

## Testing with cURL

### Basic List
```bash
curl -X GET \
  "http://localhost:8000/api/user/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### With Search
```bash
curl -X GET \
  "http://localhost:8000/api/user/?search=john" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### With Pagination
```bash
curl -X GET \
  "http://localhost:8000/api/user/?page=2&page_size=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### With Ordering
```bash
curl -X GET \
  "http://localhost:8000/api/user/?ordering=-created_at" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Combined Query
```bash
curl -X GET \
  "http://localhost:8000/api/user/?search=Army&ordering=full_name&page_size=30" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Testing with Postman

1. **Create New Request**
   - Method: `GET`
   - URL: `http://localhost:8000/api/user/`

2. **Set Authorization**
   - Type: `Bearer Token`
   - Token: Your JWT access token

3. **Add Query Parameters** (Optional)
   - `page`: 1
   - `page_size`: 20
   - `search`: john
   - `ordering`: -created_at

4. **Send Request**
   - Click "Send"
   - View paginated user list in response

---

## Performance Considerations

- **Default Page Size:** 20 users per page
- **Maximum Page Size:** 100 users per page
- **Optimized Queries:** Uses `select_related('profile')` for efficient database queries
- **Index Recommendations:** Consider indexing `email`, `full_name`, `created_at` for better performance

---

## Privacy & Security

- ✅ **Authentication Required:** Only authenticated users can view the list
- ✅ **Public Data Only:** No sensitive information like passwords exposed
- ✅ **Rate Limiting:** Consider implementing rate limiting for production
- ✅ **Profile Relations:** Efficiently loads user profiles to avoid N+1 queries

---

## Related Endpoints

- `GET /api/user/{uuid}/profile/` - View specific user's profile
- `GET /api/exchange/user/{user_uuid}/` - View user's exchanges
- `GET /api/profile/` - Your own profile
- `POST /api/accounts/email-signup/` - Register new user

---

## Notes

- **Missing Profiles:** Users without completed profiles will have `null` values for profile fields
- **Ordering:** Use `-` prefix for descending order (e.g., `-created_at` for newest first)
- **Search:** Case-insensitive search across multiple fields
- **Pagination:** Automatically applied with sensible defaults
- **Performance:** Optimized with `select_related` to reduce database queries
