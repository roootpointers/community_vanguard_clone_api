# Category and SubCategory API Documentation

## Overview
The Category and SubCategory APIs provide endpoints for managing hierarchical categorization of exchanges. Categories represent top-level classifications, while SubCategories provide more detailed classifications within each category.

**Key Changes:**
- Exchange `category` and `sub_category` fields now accept **UUIDs** instead of plain text
- Existing text data has been automatically migrated to the new structure
- Full CRUD operations available for both models
- Admin-only access for create/update/delete operations
- Public read access for all users

---

## Table of Contents
1. [Category API](#category-api)
2. [SubCategory API](#subcategory-api)
3. [Exchange API Updates](#exchange-api-updates)
4. [Migration Notes](#migration-notes)

---

## Category API

### List All Categories
Retrieve paginated list of all categories with their subcategory counts.

**Endpoint:** `GET /api/category/`

**Authentication:** Required (JWT Token)

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `is_active`: Filter by active status (true/false)
- `search`: Search in name and description
- `ordering`: Sort by `name`, `created_at`, `-name`, `-created_at`

**Example:**
```http
GET /api/category/?is_active=true&page=1&ordering=name
Authorization: Bearer YOUR_JWT_TOKEN
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Categories retrieved successfully",
  "count": 10,
  "next": "http://localhost:8000/api/category/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Education",
      "description": "Educational services and programs",
      "is_active": true,
      "subcategories_count": 5
    },
    {
      "uuid": "660e8400-e29b-41d4-a716-446655440111",
      "name": "Healthcare",
      "description": "Medical and health services",
      "is_active": true,
      "subcategories_count": 8
    }
  ]
}
```

---

### Get Active Categories
Retrieve all active categories without pagination.

**Endpoint:** `GET /api/category/active/`

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "Active categories retrieved successfully",
  "count": 10,
  "data": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Education",
      "description": "Educational services and programs",
      "is_active": true,
      "subcategories_count": 5
    }
  ]
}
```

---

### Get Single Category
Retrieve detailed information about a specific category including all its subcategories.

**Endpoint:** `GET /api/category/{uuid}/`

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "Category retrieved successfully",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Education",
    "description": "Educational services and programs",
    "is_active": true,
    "subcategories_count": 5,
    "subcategories": [
      {
        "uuid": "770e8400-e29b-41d4-a716-446655440222",
        "category": "550e8400-e29b-41d4-a716-446655440000",
        "category_name": "Education",
        "name": "Vocational Training",
        "is_active": true
      },
      {
        "uuid": "880e8400-e29b-41d4-a716-446655440333",
        "category": "550e8400-e29b-41d4-a716-446655440000",
        "category_name": "Education",
        "name": "GI Bill Assistance",
        "is_active": true
      }
    ],
    "created_at": "2025-10-23T10:30:00Z",
    "updated_at": "2025-10-23T10:30:00Z"
  }
}
```

---

### Create Category
Create a new category (Admin only).

**Endpoint:** `POST /api/category/`

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "name": "Employment",
  "description": "Job placement and career services",
  "is_active": true
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Category created successfully",
  "data": {
    "uuid": "990e8400-e29b-41d4-a716-446655440444",
    "name": "Employment",
    "description": "Job placement and career services",
    "is_active": true,
    "subcategories_count": 0,
    "subcategories": [],
    "created_at": "2025-10-30T14:20:00Z",
    "updated_at": "2025-10-30T14:20:00Z"
  }
}
```

**Validation:**
- `name` is required and must be unique (case-insensitive)
- Cannot create duplicate category names

---

### Update Category
Update an existing category (Admin only).

**Endpoint:** `PUT/PATCH /api/category/{uuid}/`

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "description": "Updated description for employment services",
  "is_active": false
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Category updated successfully",
  "data": {
    "uuid": "990e8400-e29b-41d4-a716-446655440444",
    "name": "Employment",
    "description": "Updated description for employment services",
    "is_active": false,
    "subcategories_count": 0,
    "subcategories": [],
    "created_at": "2025-10-30T14:20:00Z",
    "updated_at": "2025-10-30T14:25:00Z"
  }
}
```

---

### Delete Category
Delete a category (Admin only).

**Endpoint:** `DELETE /api/category/{uuid}/`

**Authentication:** Required (Admin)

**Note:** Deleting a category will also delete all its subcategories due to CASCADE relationship.

**Success Response (200):**
```json
{
  "success": true,
  "message": "Category deleted successfully"
}
```

---

## SubCategory API

### List All SubCategories
Retrieve paginated list of all subcategories.

**Endpoint:** `GET /api/subcategory/`

**Authentication:** Required

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page
- `category`: Filter by category UUID
- `is_active`: Filter by active status
- `search`: Search in name and description
- `ordering`: Sort fields

**Example:**
```http
GET /api/subcategory/?category=550e8400-e29b-41d4-a716-446655440000&is_active=true
Authorization: Bearer YOUR_JWT_TOKEN
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "SubCategories retrieved successfully",
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "uuid": "770e8400-e29b-41d4-a716-446655440222",
      "category": "550e8400-e29b-41d4-a716-446655440000",
      "category_name": "Education",
      "name": "Vocational Training",
      "is_active": true
    }
  ]
}
```

---

### Get SubCategories by Category
Retrieve all subcategories for a specific category.

**Endpoint:** `GET /api/subcategory/category/{category_uuid}/`

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "SubCategories for Education retrieved successfully",
  "count": 5,
  "category": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Education"
  },
  "data": [
    {
      "uuid": "770e8400-e29b-41d4-a716-446655440222",
      "category": "550e8400-e29b-41d4-a716-446655440000",
      "category_name": "Education",
      "name": "Vocational Training",
      "is_active": true
    },
    {
      "uuid": "880e8400-e29b-41d4-a716-446655440333",
      "category": "550e8400-e29b-41d4-a716-446655440000",
      "category_name": "Education",
      "name": "GI Bill Assistance",
      "is_active": true
    }
  ]
}
```

---

### Get Active SubCategories
Retrieve all active subcategories (with active categories only).

**Endpoint:** `GET /api/subcategory/active/`

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "Active subcategories retrieved successfully",
  "count": 25,
  "data": [
    {
      "uuid": "770e8400-e29b-41d4-a716-446655440222",
      "category": "550e8400-e29b-41d4-a716-446655440000",
      "category_name": "Education",
      "name": "Vocational Training",
      "is_active": true
    }
  ]
}
```

---

### Get Single SubCategory
Retrieve detailed information about a specific subcategory.

**Endpoint:** `GET /api/subcategory/{uuid}/`

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "SubCategory retrieved successfully",
  "data": {
    "uuid": "770e8400-e29b-41d4-a716-446655440222",
    "category": "550e8400-e29b-41d4-a716-446655440000",
    "category_name": "Education",
    "name": "Vocational Training",
    "description": "Job skills and vocational training programs",
    "is_active": true,
    "created_at": "2025-10-23T10:35:00Z",
    "updated_at": "2025-10-23T10:35:00Z"
  }
}
```

---

### Create SubCategory
Create a new subcategory (Admin only).

**Endpoint:** `POST /api/subcategory/`

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "category": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Career Counseling",
  "description": "One-on-one career guidance",
  "is_active": true
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "SubCategory created successfully",
  "data": {
    "uuid": "aa0e8400-e29b-41d4-a716-446655440555",
    "category": "550e8400-e29b-41d4-a716-446655440000",
    "category_name": "Education",
    "name": "Career Counseling",
    "description": "One-on-one career guidance",
    "is_active": true,
    "created_at": "2025-10-30T14:30:00Z",
    "updated_at": "2025-10-30T14:30:00Z"
  }
}
```

**Validation:**
- `category` UUID is required
- `name` is required
- Combination of `category` + `name` must be unique
- Category must be active

---

### Update SubCategory
Update an existing subcategory (Admin only).

**Endpoint:** `PUT/PATCH /api/subcategory/{uuid}/`

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "description": "Updated career counseling description",
  "is_active": false
}
```

---

### Delete SubCategory
Delete a subcategory (Admin only).

**Endpoint:** `DELETE /api/subcategory/{uuid}/`

**Authentication:** Required (Admin)

---

## Exchange API Updates

### Create Exchange with Categories
Now accepts UUIDs for category and sub_category fields.

**Endpoint:** `POST /api/exchange/`

**Request Body (Updated):**
```json
{
  "org_name": "Veterans Education Center",
  "contact_person": "John Doe",
  "email": "contact@veducation.org",
  "phone": "+1234567890",
  "exchange_type": "vso",
  "category": "550e8400-e29b-41d4-a716-446655440000",
  "sub_category": "770e8400-e29b-41d4-a716-446655440222",
  "mission_statement": "Providing educational support to veterans",
  "business_logo": "https://cdn.example.com/logo.jpg",
  "verification_urls": [
    "https://cdn.example.com/verification1.pdf",
    "https://cdn.example.com/verification2.jpg"
  ]
}
```

**Response includes category names:**
```json
{
  "success": true,
  "message": "Exchange application submitted successfully",
  "data": {
    "uuid": "bb0e8400-e29b-41d4-a716-446655440666",
    "org_name": "Veterans Education Center",
    "category": "550e8400-e29b-41d4-a716-446655440000",
    "category_name": "Education",
    "sub_category": "770e8400-e29b-41d4-a716-446655440222",
    "sub_category_name": "Vocational Training",
    ...
  }
}
```

**Validation:**
- `category` must be a valid UUID of an active Category
- `sub_category` must be a valid UUID of an active SubCategory
- `sub_category` must belong to the selected `category`

---

### List Exchanges
Response now includes category and subcategory names.

**Endpoint:** `GET /api/exchange/`

**Response:**
```json
{
  "success": true,
  "message": "Exchanges retrieved successfully",
  "data": {
    "Education": {
      "count": 5,
      "exchanges": [
        {
          "uuid": "...",
          "org_name": "...",
          "category": "550e8400-e29b-41d4-a716-446655440000",
          "category_name": "Education",
          "sub_category": "770e8400-e29b-41d4-a716-446655440222",
          "sub_category_name": "Vocational Training",
          ...
        }
      ],
      "page": 1,
      "total_pages": 1
    }
  }
}
```

---

## Migration Notes

### Automatic Data Migration
All existing exchange data has been automatically migrated:

1. **Categories Created:** Unique category values from exchanges were extracted and created as Category records
2. **SubCategories Created:** Unique subcategory values were extracted and linked to their parent categories
3. **Exchange Records Updated:** All exchange records now reference the new Category and SubCategory models via UUIDs
4. **Old Fields Removed:** Old text-based `category` and `sub_category` fields have been removed

### Breaking Changes
⚠️ **IMPORTANT:** If you have existing API clients:

**Before:**
```json
{
  "category": "Education",
  "sub_category": "Vocational Training"
}
```

**After:**
```json
{
  "category": "550e8400-e29b-41d4-a716-446655440000",
  "sub_category": "770e8400-e29b-41d4-a716-446655440222"
}
```

**Migration Steps for Clients:**
1. Call `GET /api/category/active/` to retrieve all active categories with UUIDs
2. Call `GET /api/subcategory/active/` to retrieve all active subcategories with UUIDs
3. Update your forms/UIs to use UUID dropdowns instead of text inputs
4. Store category/subcategory UUIDs for future exchange creation

---

## Error Responses

### 400 Bad Request - Invalid UUID
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "category": ["Invalid UUID format"]
  }
}
```

### 400 Bad Request - Category/SubCategory Mismatch
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "error": "Sub-category 'Vocational Training' does not belong to category 'Healthcare'."
  }
}
```

### 400 Bad Request - Inactive Category
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "category": ["Selected category is not active."]
  }
}
```

### 400 Bad Request - Duplicate Category
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "error": "Category 'Education' already exists."
  }
}
```

### 403 Forbidden - Admin Only
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Complete Endpoint Summary

### Category Endpoints
- `GET /api/category/` - List all categories (paginated)
- `GET /api/category/active/` - Get all active categories
- `GET /api/category/{uuid}/` - Get single category with subcategories
- `POST /api/category/` - Create category (admin)
- `PUT/PATCH /api/category/{uuid}/` - Update category (admin)
- `DELETE /api/category/{uuid}/` - Delete category (admin)

### SubCategory Endpoints
- `GET /api/subcategory/` - List all subcategories (paginated)
- `GET /api/subcategory/active/` - Get all active subcategories
- `GET /api/subcategory/category/{category_uuid}/` - Get subcategories by category
- `GET /api/subcategory/{uuid}/` - Get single subcategory
- `POST /api/subcategory/` - Create subcategory (admin)
- `PUT/PATCH /api/subcategory/{uuid}/` - Update subcategory (admin)
- `DELETE /api/subcategory/{uuid}/` - Delete subcategory (admin)

### Exchange Endpoints (Updated)
- All exchange endpoints now use category/sub_category UUIDs
- Responses include `category_name` and `sub_category_name` fields

---

## Testing with cURL

```bash
# Get all active categories
curl -X GET \
  "http://localhost:8000/api/category/active/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get subcategories for a category
curl -X GET \
  "http://localhost:8000/api/subcategory/category/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create category (admin only)
curl -X POST \
  "http://localhost:8000/api/category/" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Housing",
    "description": "Housing assistance and services",
    "is_active": true
  }'

# Create subcategory (admin only)
curl -X POST \
  "http://localhost:8000/api/subcategory/" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Emergency Shelter",
    "description": "Temporary housing solutions",
    "is_active": true
  }'

# Create exchange with category UUIDs
curl -X POST \
  "http://localhost:8000/api/exchange/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "org_name": "Veterans Housing Alliance",
    "contact_person": "Jane Smith",
    "email": "contact@vhousing.org",
    "exchange_type": "vso",
    "category": "550e8400-e29b-41d4-a716-446655440000",
    "sub_category": "770e8400-e29b-41d4-a716-446655440222",
    "mission_statement": "Providing housing to homeless veterans"
  }'
```

---

## Admin Panel
Categories and SubCategories are fully manageable in the Django admin panel with:
- Inline subcategory editing within categories
- Bulk activation/deactivation actions
- Search and filtering capabilities
- Subcategory count display
