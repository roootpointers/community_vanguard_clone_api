# View User Profile API

## Overview
This endpoint allows authenticated users to view the profile of any user in the system by their UUID.

## Endpoint Details

### View User Profile
Retrieve detailed profile information for a specific user.

**Endpoint:** `GET /api/user/{uuid}/profile/`

**Authentication:** Required (JWT Token)

**Path Parameters:**
- `uuid` (required): The unique identifier of the user whose profile you want to view

---

## Request Example

### View User Profile
```http
GET /api/user/550e8400-e29b-41d4-a716-446655440000/profile/
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User profile retrieved successfully",
  "data": {
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
    "interest": "Technology, Veterans Affairs, Community Service",
    "preferred_contribution_path": "Volunteer",
    "affiliation": "Veterans Organization",
    "is_verified": true,
    "education": "Bachelor of Science in Computer Science",
    "degree": "BS",
    "military_civilian_skills": {
      "military": ["Leadership", "Logistics", "Operations"],
      "civilian": ["Project Management", "Software Development", "Team Building"]
    },
    "certifications": "PMP, CISSP, AWS Certified",
    "ets": "2022-12-31",
    "family_status": "Married with 2 children",
    "created_at": "2024-10-15T08:00:00Z",
    "updated_at": "2024-10-20T12:30:00Z"
  }
}
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `message` | string | Descriptive message about the operation |
| `data` | object | User profile data |
| `data.uuid` | string | User's unique identifier |
| `data.email` | string | User's email address |
| `data.full_name` | string | User's full name |
| `data.role` | object/null | User's role information |
| `data.birth_date` | string/null | Date of birth (YYYY-MM-DD) |
| `data.gender` | string/null | User's gender |
| `data.profile_photo` | string/null | URL to profile photo |
| `data.branch` | string/null | Military branch |
| `data.rank` | string/null | Military rank |
| `data.mos_afsc` | string/null | Military Occupational Specialty / Air Force Specialty Code |
| `data.location` | string/null | Current location |
| `data.interest` | string/null | Areas of interest |
| `data.preferred_contribution_path` | string/null | Preferred way to contribute |
| `data.affiliation` | string/null | Organization affiliation |
| `data.is_verified` | boolean | Whether the profile is verified |
| `data.education` | string/null | Educational background |
| `data.degree` | string/null | Academic degree |
| `data.military_civilian_skills` | object/null | JSON object with military and civilian skills |
| `data.certifications` | string/null | Professional certifications |
| `data.ets` | string/null | End of Term of Service date |
| `data.family_status` | string/null | Family status information |
| `data.created_at` | string | Profile creation timestamp |
| `data.updated_at` | string | Last update timestamp |

---

## Error Responses

### User Not Found
**Status Code:** `404 NOT FOUND`

```json
{
  "success": false,
  "message": "User not found"
}
```

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

### Invalid UUID Format
**Status Code:** `404 NOT FOUND`

```json
{
  "detail": "Not found."
}
```

### Server Error
**Status Code:** `500 INTERNAL SERVER ERROR`

```json
{
  "success": false,
  "message": "Failed to retrieve user profile",
  "error": "Error details..."
}
```

---

## Privacy & Security Notes

1. **Authentication Required:** Only authenticated users can view profiles
2. **Public Information:** All profile data is considered public within the authenticated community
3. **No Sensitive Data:** Passwords and other sensitive information are never exposed
4. **Read-Only:** This endpoint only retrieves data; it does not modify profiles

---

## Use Cases

1. **User Discovery:** Browse other users' profiles in the community
2. **Networking:** Find users with similar backgrounds or interests
3. **Verification:** Check user credentials and affiliations
4. **Community Building:** Connect with other veterans and supporters
5. **Profile Pages:** Display public user information on profile pages

---

## Related Endpoints

- `GET /api/exchange/user/{user_uuid}/` - View user's exchanges
- `GET /api/profile/` - Manage your own profile (CRUD operations)
- `GET /api/user/` - List all users (if implemented)

---

## Example: Full User Profile Workflow

```javascript
// Fetch user profile
async function getUserProfile(userUuid, token) {
  const response = await fetch(
    `http://localhost:8000/api/user/${userUuid}/profile/`,
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
    console.log(`Profile for ${data.data.full_name}`);
    console.log(`Branch: ${data.data.branch}`);
    console.log(`Rank: ${data.data.rank}`);
    console.log(`Location: ${data.data.location}`);
    console.log(`Verified: ${data.data.is_verified}`);
  }
  
  return data;
}

// Usage
const userUuid = '550e8400-e29b-41d4-a716-446655440000';
const token = 'your-jwt-token';
getUserProfile(userUuid, token);
```

---

## Testing with cURL

```bash
# View user profile
curl -X GET \
  "http://localhost:8000/api/user/550e8400-e29b-41d4-a716-446655440000/profile/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Testing with Postman

1. **Create New Request**
   - Method: `GET`
   - URL: `http://localhost:8000/api/user/{uuid}/profile/`
   - Replace `{uuid}` with actual user UUID

2. **Set Authorization**
   - Type: `Bearer Token`
   - Token: Your JWT access token

3. **Send Request**
   - Click "Send"
   - View user profile in response

---

## Notes

- **Missing Profile Data:** If a user hasn't completed their profile, some fields may be `null`
- **Role Information:** The `role` field will be `null` if the user hasn't been assigned a role
- **Timestamps:** All timestamps are in ISO 8601 format (UTC)
- **Skills Format:** The `military_civilian_skills` field is a JSON object with arrays of skills
- **Profile Completion:** Not all fields are required; users may have partially completed profiles
