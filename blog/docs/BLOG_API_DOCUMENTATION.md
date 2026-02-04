# Blog Management System API Documentation

## Overview
The Blog Management System provides comprehensive APIs for managing blog posts with features like Mission Genesis designation, view tracking, search capabilities, and status management.

## Base URL
```
/api/blog/
```

## Models

### Blog
Represents a blog post.

**Fields:**
- `uuid`: Unique identifier (UUID, auto-generated)
- `title`: Blog title (string, max 255 chars, required)
- `slug`: URL-friendly slug (auto-generated from title, unique)
- `content`: Blog content (text, required)
- `excerpt`: Read-only first 200 characters of content
- `author`: Author name (string, max 255 chars, required)
- `status`: Publication status (Draft, Published, Archived)
- `featured_image`: Featured image URL (optional)
- `is_mission_genesis`: Mission Genesis flag (boolean, only one can be true)
- `views_count`: Number of views (integer, auto-increment)
- `created_at`: Timestamp when created (auto)
- `updated_at`: Timestamp when updated (auto)

## API Endpoints

### Blogs

#### 1. List All Blogs
**GET** `/api/blog/blogs/`

Returns a paginated list of all blogs.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10)
- `search`: Search in title, content, or author
- `status`: Filter by status (Draft, Published, Archived)
- `author`: Filter by author name
- `is_mission_genesis`: Filter by Mission Genesis flag (true/false)
- `ordering`: Sort by field (e.g., `-created_at`, `views_count`, `title`)

**Example Response:**
```json
{
  "success": true,
  "message": "Blogs retrieved successfully",
  "count": 100,
  "next": "http://api/blog/blogs/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "8039f5e4-54a0-402c-842b-f20aabd41e34",
      "title": "Getting Started with Operation Vanguard",
      "excerpt": "Operation Vanguard is a comprehensive platform designed to support military veterans...",
      "author": "Admin",
      "status": "Published",
      "is_mission_genesis": true,
      "views_count": 150,
      "created_at": "2025-12-19T10:00:00Z"
    }
  ]
}
```

#### 2. Create Blog
**POST** `/api/blog/blogs/`

Create a new blog post.

**Request Body:**
```json
{
  "title": "Veteran Success Stories: From Service to Civilian Life",
  "content": "Read inspiring stories from veterans who have successfully transitioned from military service to civilian life. These stories highlight the challenges, triumphs, and lessons learned along the way.",
  "author": "John Doe",
  "status": "Published",
  "featured_image": "https://example.com/images/veteran-stories.jpg",
  "is_mission_genesis": false
}
```

**Response:** 201 Created
```json
{
  "success": true,
  "message": "Blog created successfully",
  "data": {
    "uuid": "8039f5e4-54a0-402c-842b-f20aabd41e34",
    "title": "Veteran Success Stories: From Service to Civilian Life",
    "slug": "veteran-success-stories-from-service-to-civilian-life",
    "content": "Read inspiring stories from veterans who have successfully transitioned...",
    "excerpt": "Read inspiring stories from veterans who have successfully transitioned from military service to civilian life. These stories highlight the challenges, triumphs, and lessons learned along the...",
    "author": "John Doe",
    "status": "Published",
    "featured_image": "https://example.com/images/veteran-stories.jpg",
    "is_mission_genesis": false,
    "views_count": 0,
    "created_at": "2025-12-19T10:00:00Z",
    "updated_at": "2025-12-19T10:00:00Z"
  }
}
```

#### 3. Retrieve Blog
**GET** `/api/blog/blogs/{uuid}/`

Get details of a specific blog. **Note:** This automatically increments the view count.

**Example Response:**
```json
{
  "success": true,
  "message": "Blog retrieved successfully",
  "data": {
    "uuid": "8039f5e4-54a0-402c-842b-f20aabd41e34",
    "title": "Veteran Success Stories: From Service to Civilian Life",
    "slug": "veteran-success-stories-from-service-to-civilian-life",
    "content": "Full blog content here...",
    "excerpt": "Read inspiring stories from veterans...",
    "author": "John Doe",
    "status": "Published",
    "featured_image": "https://example.com/images/veteran-stories.jpg",
    "is_mission_genesis": false,
    "views_count": 151,
    "created_at": "2025-12-19T10:00:00Z",
    "updated_at": "2025-12-19T10:05:00Z"
  }
}
```

#### 4. Update Blog
**PUT** `/api/blog/blogs/{uuid}/`
**PATCH** `/api/blog/blogs/{uuid}/`

Update a blog post. Use PUT for full updates, PATCH for partial updates.

**Request Body (PATCH example):**
```json
{
  "status": "Archived"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Blog updated successfully",
  "data": {
    "uuid": "8039f5e4-54a0-402c-842b-f20aabd41e34",
    "title": "Veteran Success Stories: From Service to Civilian Life",
    "slug": "veteran-success-stories-from-service-to-civilian-life",
    "content": "Full blog content...",
    "excerpt": "Read inspiring stories...",
    "author": "John Doe",
    "status": "Archived",
    "featured_image": "https://example.com/images/veteran-stories.jpg",
    "is_mission_genesis": false,
    "views_count": 151,
    "created_at": "2025-12-19T10:00:00Z",
    "updated_at": "2025-12-19T10:30:00Z"
  }
}
```

#### 5. Delete Blog
**DELETE** `/api/blog/blogs/{uuid}/`

Delete a blog post.

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Blog deleted successfully",
  "data": null
}
```

#### 6. Published Blogs
**GET** `/api/blog/blogs/published/`

Get all blogs with "Published" status. Supports same query parameters as list endpoint.

**Example Response:**
```json
{
  "success": true,
  "message": "Published blogs retrieved successfully",
  "count": 45,
  "next": null,
  "previous": null,
  "results": [...]
}
```

#### 7. Mission Genesis Blog
**GET** `/api/blog/blogs/mission_genesis/`

Get the blog designated as "Mission Genesis" blog.

**Example Response:**
```json
{
  "success": true,
  "message": "Mission Genesis blog retrieved successfully",
  "data": {
    "uuid": "8039f5e4-54a0-402c-842b-f20aabd41e34",
    "title": "Getting Started with Operation Vanguard",
    "slug": "getting-started-with-operation-vanguard",
    "content": "Full content...",
    "excerpt": "Operation Vanguard is...",
    "author": "Admin",
    "status": "Published",
    "featured_image": "https://example.com/hero.jpg",
    "is_mission_genesis": true,
    "views_count": 500,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-12-19T10:00:00Z"
  }
}
```

**Error Response (if not found):**
```json
{
  "success": false,
  "message": "No Mission Genesis blog found"
}
```

#### 8. Toggle Mission Genesis Status
**POST** `/api/blog/blogs/{uuid}/toggle_mission_genesis/`

Toggle the Mission Genesis flag for a specific blog. When enabled, all other blogs will have their Mission Genesis flag disabled.

**Example Response:**
```json
{
  "success": true,
  "message": "Mission Genesis status enabled",
  "data": {
    "uuid": "8039f5e4-54a0-402c-842b-f20aabd41e34",
    "title": "Getting Started with Operation Vanguard",
    "is_mission_genesis": true,
    ...
  }
}
```

#### 9. Blogs By Author
**GET** `/api/blog/blogs/by_author/`

Get all blogs by a specific author.

**Query Parameters:**
- `author`: Author name (required)

**Example Request:**
```
GET /api/blog/blogs/by_author/?author=John Doe
```

**Example Response:**
```json
{
  "success": true,
  "message": "Blogs by John Doe retrieved successfully",
  "count": 12,
  "next": null,
  "previous": null,
  "results": [...]
}
```

#### 10. Popular Blogs
**GET** `/api/blog/blogs/popular/`

Get the most popular blogs based on view count.

**Query Parameters:**
- `limit`: Number of blogs to return (default: 10)

**Example Request:**
```
GET /api/blog/blogs/popular/?limit=5
```

**Example Response:**
```json
{
  "success": true,
  "message": "Popular blogs retrieved successfully",
  "data": [
    {
      "uuid": "...",
      "title": "Most Viewed Blog",
      "excerpt": "...",
      "author": "Admin",
      "status": "Published",
      "is_mission_genesis": false,
      "views_count": 1500,
      "created_at": "2025-01-01T00:00:00Z"
    },
    ...
  ]
}
```

#### 11. Bulk Delete Blogs
**DELETE** `/api/blog/blogs/bulk_delete/`

Delete multiple blogs at once.

**Request Body:**
```json
{
  "uuids": [
    "uuid1",
    "uuid2",
    "uuid3"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully deleted 3 blog(s)",
  "data": {
    "deleted_count": 3
  }
}
```

## Permissions

All endpoints use `IsAuthenticatedOrReadOnly` permission:
- **Authenticated users**: Full CRUD access
- **Unauthenticated users**: Read-only access

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "title": ["This field is required."],
    "content": ["This field is required."]
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "No Mission Genesis blog found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error"
}
```

## Usage Examples

### Create a Blog Post
```bash
curl -X POST http://localhost:8000/api/blog/blogs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Mental Health Resources for Veterans",
    "content": "Mental health is a critical aspect of overall well-being...",
    "author": "Dr. Jane Smith",
    "status": "Published",
    "featured_image": "https://example.com/mental-health.jpg"
  }'
```

### Search for Blogs
```bash
curl "http://localhost:8000/api/blog/blogs/?search=veteran&status=Published&ordering=-views_count"
```

### Get Mission Genesis Blog
```bash
curl http://localhost:8000/api/blog/blogs/mission_genesis/
```

### Update Blog Status
```bash
curl -X PATCH http://localhost:8000/api/blog/blogs/{uuid}/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "status": "Archived"
  }'
```

### Get Popular Blogs
```bash
curl "http://localhost:8000/api/blog/blogs/popular/?limit=10"
```

### Filter Published Blogs
```bash
curl "http://localhost:8000/api/blog/blogs/published/?page=1&page_size=20"
```

### Bulk Delete Blogs
```bash
curl -X DELETE http://localhost:8000/api/blog/blogs/bulk_delete/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "uuids": ["uuid1", "uuid2", "uuid3"]
  }'
```

## Field Validation

### Title
- Required
- Maximum 255 characters
- Cannot be empty or whitespace only
- Auto-generates unique slug

### Content
- Required
- TextField (no character limit)
- Cannot be empty or whitespace only

### Author
- Required
- Maximum 255 characters
- Cannot be empty or whitespace only

### Status
- One of: "Draft", "Published", "Archived"
- Default: "Published"

### Featured Image
- Optional
- Valid URL format
- Maximum 500 characters

### Mission Genesis
- Boolean field
- Only one blog can have this set to true at a time
- System automatically handles enforcement

## Special Features

### Auto Slug Generation
- Slugs are automatically generated from the title
- URL-friendly format (lowercase, hyphens)
- Duplicate slugs get a counter suffix (e.g., `blog-title-2`)
- Unique enforcement across all blogs

### View Tracking
- View count automatically increments when retrieving a blog via GET `/api/blog/blogs/{uuid}/`
- Does not increment for list operations
- Used for popular blogs ranking

### Mission Genesis Enforcement
- Only one blog can be marked as Mission Genesis at a time
- When setting a new blog as Mission Genesis, the system automatically removes the flag from all other blogs
- Special endpoint to retrieve the current Mission Genesis blog
- Toggle endpoint for easy management

### Excerpt Generation
- First 200 characters of content
- Automatically adds "..." if content is longer
- Read-only field included in list responses

## Best Practices

1. **Always use UUID for blog references** in API calls, not slugs or IDs
2. **Set appropriate status** based on blog readiness (Draft → Published → Archived)
3. **Use pagination** for list endpoints to avoid performance issues
4. **Search is case-insensitive** and searches across title, content, and author
5. **Mission Genesis should be used sparingly** - only for the most important introductory blog
6. **Featured images should be optimized** for web display before uploading
7. **Use PATCH for partial updates** instead of PUT when only updating specific fields

## Notes

1. **Slug Uniqueness**: Slugs are automatically made unique by appending a counter if needed
2. **View Count**: Only increments on individual blog retrieval, not on list operations
3. **Ordering**: Default ordering is by creation date (newest first)
4. **Pagination**: Default page size is 10 items per page
5. **Search**: Searches across title, content, and author fields
6. **Mission Genesis**: Only one blog can be designated as Mission Genesis at any time
