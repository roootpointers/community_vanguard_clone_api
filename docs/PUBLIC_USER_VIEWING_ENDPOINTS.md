# Public User Viewing Endpoints - Quick Reference

## Overview
Three endpoints allow authenticated users to view user profiles and exchanges in the system.

---

## 1. List All Users

**Endpoint:** `GET /api/user/`

**Purpose:** Retrieve a paginated list of all users with filtering and search

**Authentication:** Required

**Features:**
- Pagination (page, page_size with max 100)
- Search across email, full_name, branch, rank, location
- Filter by exact email
- Ordering by created_at, full_name, email

**Example:**
```bash
GET http://localhost:8000/api/user/?search=Army&ordering=-created_at&page_size=30
Authorization: Bearer YOUR_JWT_TOKEN
```

**Returns:**
- Paginated list of users
- Full profile information for each user
- Total count, next/previous page links

---

## 2. View User Profile

**Endpoint:** `GET /api/user/{uuid}/profile/`

**Purpose:** View detailed profile information of any user

**Authentication:** Required

**Example:**
```bash
GET http://localhost:8000/api/user/550e8400-e29b-41d4-a716-446655440000/profile/
Authorization: Bearer YOUR_JWT_TOKEN
```

**Returns:**
- Full user profile (name, email, branch, rank, location, etc.)
- Role information
- Military/civilian skills
- Education and certifications
- Verification status

---

## 3. View User's Exchanges

**Endpoint:** `GET /api/exchange/user/{user_uuid}/`

**Purpose:** View all approved exchanges posted by a specific user

**Authentication:** Required

**Privacy:** Only shows approved exchanges (pending/rejected are hidden)

**Features:**
- Pagination support (page, page_size)
- Filter by exchange_type, category, sub_category
- Search functionality
- Includes user information in response

**Example:**
```bash
GET http://localhost:8000/api/exchange/user/550e8400-e29b-41d4-a716-446655440000/
Authorization: Bearer YOUR_JWT_TOKEN
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10, max: 100)
- `exchange_type` - Filter by type (vob, vso, community_leader, affiliate)
- `category` - Filter by category
- `sub_category` - Filter by sub-category
- `search` - Search in org_name, contact_person, email, mission_statement

---

## Complete API Endpoints Summary

### Account Endpoints
- `GET /api/user/` - **NEW:** List all users (paginated, searchable, filterable)
- `GET /api/user/{uuid}/profile/` - View any user's profile
- `GET /api/profile/` - Your own profile (CRUD operations)
- `POST /api/accounts/email-signup/` - Register new account
- `POST /api/accounts/email-login/` - Login
- `POST /api/accounts/change-password/` - Change password

### Exchange Endpoints
- `POST /api/exchange/` - Create exchange
- `GET /api/exchange/` - List all (grouped by category)
- `GET /api/exchange/{uuid}/` - View specific exchange
- `PUT/PATCH /api/exchange/{uuid}/` - Update (creator only)
- `DELETE /api/exchange/{uuid}/` - Delete (creator only)
- `GET /api/exchange/my-exchanges/` - Your own exchanges (all statuses)
- `GET /api/exchange/user/{user_uuid}/` - View user's approved exchanges

---

## Use Case Examples

### 1. User Directory with Search
```javascript
// Display searchable user directory
async function loadUserDirectory(token, searchTerm = '', page = 1) {
  const response = await fetch(
    `http://localhost:8000/api/user/?search=${searchTerm}&page=${page}&page_size=30`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const data = await response.json();
  
  console.log(`Found ${data.count} users`);
  return data;
}
```

### 2. User Profile Page
```javascript
// Display user profile and their exchanges
async function loadUserPage(userUuid, token) {
  // Get profile
  const profileRes = await fetch(
    `http://localhost:8000/api/user/${userUuid}/profile/`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const profile = await profileRes.json();
  
  // Get exchanges
  const exchangesRes = await fetch(
    `http://localhost:8000/api/exchange/user/${userUuid}/`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const exchanges = await exchangesRes.json();
  
  return { profile, exchanges };
}
```

### 3. User Discovery
```javascript
// Find users by branch and view their contributions
async function findVeteransByBranch(branch, token) {
  // Search for users by branch
  const usersRes = await fetch(
    `http://localhost:8000/api/user/?search=${branch}&ordering=-created_at`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const users = await usersRes.json();
  
  // For each user, get their exchanges
  const usersWithExchanges = await Promise.all(
    users.results.slice(0, 10).map(async (user) => {
      const exchangesRes = await fetch(
        `http://localhost:8000/api/exchange/user/${user.uuid}/?exchange_type=vso`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      const exchanges = await exchangesRes.json();
      return { ...user, exchangeCount: exchanges.count };
    })
  );
  
  return usersWithExchanges;
}
```

### 4. Community Statistics
```javascript
// Track user contributions
async function getUserContributions(userUuid, token) {
  const response = await fetch(
    `http://localhost:8000/api/exchange/user/${userUuid}/`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  const data = await response.json();
  return {
    userName: data.user.full_name,
    totalExchanges: data.count,
    totalPages: data.total_pages
  };
}
```

---

## Security & Privacy

### List Users Endpoint
- ✅ Authentication required
- ✅ Paginated for performance (default 20, max 100)
- ✅ Search and filter capabilities
- ✅ Optimized database queries with select_related
- ✅ Public profile data only (no passwords/tokens)

### User Profile Endpoint
- ✅ Authentication required
- ✅ All profile data is public within authenticated community
- ✅ No sensitive data exposed (passwords, tokens, etc.)
- ✅ Read-only access

### User Exchanges Endpoint
- ✅ Authentication required
- ✅ Only shows **approved** exchanges
- ✅ Pending/rejected exchanges are hidden for privacy
- ✅ Includes user context in response
- ✅ Full pagination and filtering support

---

## Documentation Files

- `accounts/docs/LIST_USERS_API.md` - **NEW:** Detailed list users endpoint documentation
- `accounts/docs/USER_PROFILE_API.md` - Detailed profile endpoint documentation
- `exchange/docs/USER_EXCHANGES_API.md` - Detailed exchanges endpoint documentation
- `exchange/docs/EXCHANGE_API_DOCUMENTATION.md` - General exchange API documentation

---

## Testing

### Test List All Users
```bash
curl -X GET \
  "http://localhost:8000/api/user/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# With search
curl -X GET \
  "http://localhost:8000/api/user/?search=Army&page_size=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Profile Viewing
```bash
curl -X GET \
  "http://localhost:8000/api/user/550e8400-e29b-41d4-a716-446655440000/profile/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Exchange Viewing
```bash
curl -X GET \
  "http://localhost:8000/api/exchange/user/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test with Filters
```bash
curl -X GET \
  "http://localhost:8000/api/exchange/user/550e8400-e29b-41d4-a716-446655440000/?exchange_type=vso&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Response Examples

### List Users Response
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
      "branch": "Army",
      "rank": "Sergeant",
      "location": "San Francisco, CA",
      "is_verified": true
    }
  ]
}
```

### Profile Response
```json
{
  "success": true,
  "message": "User profile retrieved successfully",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "branch": "Army",
    "rank": "Sergeant",
    "location": "San Francisco, CA",
    "is_verified": true
  }
}
```

### Exchanges Response
```json
{
  "success": true,
  "message": "Exchanges by John Doe retrieved successfully",
  "count": 25,
  "next": "http://localhost:8000/api/exchange/user/550e.../page=2",
  "previous": null,
  "total_pages": 3,
  "current_page": 1,
  "page_size": 10,
  "user": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "email": "john.doe@example.com"
  },
  "results": [...]
}
```
