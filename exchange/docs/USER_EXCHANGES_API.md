# View User Exchanges API

## Overview
This endpoint allows authenticated users to view exchanges posted by any specific user in the system.

## Endpoint Details

### View User's Exchanges
View all approved exchanges posted by a specific user.

**Endpoint:** `GET /api/exchange/user/{user_uuid}/`

**Authentication:** Required (JWT Token)

**Privacy Protection:** Only shows **approved** exchanges publicly

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)
- `exchange_type` (optional): Filter by exchange type (vob, vso, community_leader, affiliate)
- `category` (optional): Filter by category
- `sub_category` (optional): Filter by sub-category
- `search` (optional): Search in org_name, contact_person, email, mission_statement

---

## Request Examples

### 1. View User's Exchanges (Basic)
```http
GET /api/exchange/user/550e8400-e29b-41d4-a716-446655440000/
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Exchanges by John Doe retrieved successfully",
  "count": 25,
  "next": "http://localhost:8000/api/exchange/user/550e8400-e29b-41d4-a716-446655440000/?page=2",
  "previous": null,
  "total_pages": 3,
  "current_page": 1,
  "page_size": 10,
  "user": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "email": "john.doe@example.com"
  },
  "results": [
    {
      "uuid": "123e4567-e89b-12d3-a456-426614174000",
      "org_name": "Tech Veterans Foundation",
      "contact_person": "Jane Smith",
      "email": "contact@techvets.org",
      "phone": "+1-555-123-4567",
      "website_link": "https://techvets.org",
      "address": "123 Main St, San Francisco, CA 94102",
      "exchange_type": "vso",
      "category": "Technology",
      "sub_category": "Software Development",
      "business_logo": "https://cdn.example.com/logos/techvets.png",
      "business_background_image": "https://cdn.example.com/backgrounds/techvets.jpg",
      "mission_statement": "Empowering veterans through technology education",
      "facebook": "https://facebook.com/techvets",
      "twitter": "https://twitter.com/techvets",
      "linkedin": "https://linkedin.com/company/techvets",
      "instagram": "https://instagram.com/techvets",
      "youtube": "https://youtube.com/techvets",
      "status": "approved",
      "user": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-10-20T10:30:00Z",
      "updated_at": "2024-10-20T10:30:00Z"
    }
  ]
}
```

### 2. View User's Exchanges with Filters
```http
GET /api/exchange/user/550e8400-e29b-41d4-a716-446655440000/?exchange_type=vso&category=Technology&page=1&page_size=20
Authorization: Bearer <your_jwt_token>
```

### 3. Search in User's Exchanges
```http
GET /api/exchange/user/550e8400-e29b-41d4-a716-446655440000/?search=veteran
Authorization: Bearer <your_jwt_token>
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `message` | string | Descriptive message about the operation |
| `count` | integer | Total number of exchanges by this user |
| `next` | string/null | URL for the next page |
| `previous` | string/null | URL for the previous page |
| `total_pages` | integer | Total number of pages |
| `current_page` | integer | Current page number |
| `page_size` | integer | Number of items per page |
| `user` | object | Information about the user whose exchanges are displayed |
| `user.uuid` | string | User's unique identifier |
| `user.full_name` | string | User's full name |
| `user.email` | string | User's email address |
| `results` | array | Array of exchange objects |

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

### Server Error
**Status Code:** `500 INTERNAL SERVER ERROR`

```json
{
  "success": false,
  "message": "Failed to retrieve user exchanges",
  "error": "Error details..."
}
```

---

## Privacy & Security Notes

1. **Approved Only:** Only exchanges with `status='approved'` are shown publicly
2. **Authentication Required:** User must be logged in to view others' exchanges
3. **Public Information:** All displayed information is considered public
4. **Pagination:** Large result sets are automatically paginated for performance

---

## Use Cases

1. **Profile Pages:** Display a user's contributions on their profile
2. **Discovery:** Browse exchanges by trusted community members
3. **Verification:** Check what exchanges a specific user has posted
4. **Statistics:** Track user activity and contributions

---

## Related Endpoints

- `GET /api/exchange/my-exchanges/` - View your own exchanges (all statuses)
- `GET /api/user/{uuid}/profile/` - View user's profile information
- `GET /api/exchange/` - List all exchanges grouped by category
- `GET /api/exchange/{uuid}/` - View specific exchange details

---

## Example: Full Workflow

```javascript
// Step 1: Get user's profile
const profileResponse = await fetch(
  'http://localhost:8000/api/user/550e8400-e29b-41d4-a716-446655440000/profile/',
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

// Step 2: Get user's exchanges
const exchangesResponse = await fetch(
  'http://localhost:8000/api/exchange/user/550e8400-e29b-41d4-a716-446655440000/',
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

const data = await exchangesResponse.json();
console.log(`${data.user.full_name} has ${data.count} approved exchanges`);
```

---

## Testing with cURL

```bash
# View user's exchanges
curl -X GET \
  "http://localhost:8000/api/exchange/user/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# With filters and pagination
curl -X GET \
  "http://localhost:8000/api/exchange/user/550e8400-e29b-41d4-a716-446655440000/?exchange_type=vso&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
