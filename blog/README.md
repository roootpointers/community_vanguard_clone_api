# Blog Management System

A comprehensive Django REST Framework application for managing blog posts with features like Mission Genesis blog designation, view tracking, and search capabilities.

## ✅ Features

### Core Functionality
- **Blog CRUD Operations**
  - Create, read, update, and delete blog posts
  - Auto-generated URL-friendly slugs
  - Rich content support
  - Featured image URLs

- **Status Management**
  - Published: Visible to public
  - Draft: Work in progress
  - Archived: Hidden from main listings

- **Mission Genesis Blog**
  - Designate one blog as special "Mission Genesis" blog
  - Automatic enforcement (only one can be active)
  - Easy toggle functionality

- **View Tracking**
  - Automatic view count increment
  - Popular blogs endpoint
  - Analytics support

- **Advanced Features**
  - Search across title, content, and author
  - Filter by status, author, Mission Genesis flag
  - Pagination support
  - Bulk operations

## 📊 Database Model

### Blog Model
- `uuid`: Primary key (UUID)
- `title`: Blog title (max 255 chars)
- `slug`: Auto-generated URL-friendly slug (unique)
- `content`: Blog content (TextField)
- `author`: Author name
- `status`: Draft/Published/Archived
- `featured_image`: Featured image URL (optional)
- `is_mission_genesis`: Boolean flag (only one can be true)
- `views_count`: Number of views (auto-increment)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## 🔌 API Endpoints

### Base URL
```
/api/blog/
```

### Blog Endpoints

#### List Blogs
**GET** `/api/blog/blogs/`
- Paginated list of all blogs
- Query params: `page`, `page_size`, `search`, `status`, `author`, `is_mission_genesis`, `ordering`

**Response:**
```json
{
    "success": true,
    "message": "Blogs retrieved successfully",
    "count": 100,
    "next": "...",
    "previous": null,
    "results": [
        {
            "uuid": "8039f5e4-54a0-402c-842b-f20aabd41e34",
            "title": "Getting Started with Operation Vanguard",
            "excerpt": "Operation Vanguard is a comprehensive platform...",
            "author": "Admin",
            "status": "Published",
            "is_mission_genesis": true,
            "views_count": 150,
            "created_at": "2025-12-19T10:00:00Z"
        }
    ]
}
```

#### Create Blog
**POST** `/api/blog/blogs/`

**Request Body:**
```json
{
    "title": "Blog Title",
    "content": "Full blog content here...",
    "author": "Author Name",
    "status": "Published",
    "featured_image": "https://example.com/image.jpg",
    "is_mission_genesis": false
}
```

**Response:**
```json
{
    "success": true,
    "message": "Blog created successfully",
    "data": {
        "uuid": "...",
        "title": "Blog Title",
        "slug": "blog-title",
        "content": "Full blog content...",
        "excerpt": "Full blog content...",
        "author": "Author Name",
        "status": "Published",
        "featured_image": "https://example.com/image.jpg",
        "is_mission_genesis": false,
        "views_count": 0,
        "created_at": "2025-12-19T10:00:00Z",
        "updated_at": "2025-12-19T10:00:00Z"
    }
}
```

#### Get Blog Details
**GET** `/api/blog/blogs/{uuid}/`
- Automatically increments view count
- Returns full blog details

#### Update Blog
**PUT/PATCH** `/api/blog/blogs/{uuid}/`

#### Delete Blog
**DELETE** `/api/blog/blogs/{uuid}/`

#### Get Published Blogs
**GET** `/api/blog/blogs/published/`
- Returns only published blogs

#### Get Mission Genesis Blog
**GET** `/api/blog/blogs/mission_genesis/`
- Returns the designated Mission Genesis blog

#### Toggle Mission Genesis
**POST** `/api/blog/blogs/{uuid}/toggle_mission_genesis/`
- Toggle Mission Genesis status for a blog

#### Get Blogs by Author
**GET** `/api/blog/blogs/by_author/?author=AuthorName`

#### Get Popular Blogs
**GET** `/api/blog/blogs/popular/?limit=10`
- Returns most viewed blogs

#### Bulk Delete
**DELETE** `/api/blog/blogs/bulk_delete/`

**Request Body:**
```json
{
    "uuids": ["uuid1", "uuid2", "uuid3"]
}
```

## 🎨 Admin Interface

Access at: `http://localhost:8000/admin/blog/`

### Features:
- **List Display:**
  - Title
  - Author
  - Color-coded status (Green=Published, Orange=Draft, Gray=Archived)
  - Mission Genesis badge
  - View count
  - Creation date

- **Filters:**
  - Status
  - Mission Genesis flag
  - Author
  - Creation date

- **Search:**
  - Title, content, author

- **Bulk Actions:**
  - Mark as Published
  - Mark as Draft
  - Mark as Archived
  - Set as Mission Genesis blog (only one at a time)

- **Auto-generated Slug:**
  - Slugs are automatically created from titles
  - Unique enforcement with counter suffix

## 📝 Usage Examples

### Create a Blog via API
```bash
curl -X POST http://localhost:8000/api/blog/blogs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Veteran Success Stories: From Service to Civilian Life",
    "content": "Read inspiring stories from veterans who have successfully transitioned...",
    "author": "John Doe",
    "status": "Published",
    "featured_image": "https://example.com/veteran-stories.jpg"
  }'
```

### Search Blogs
```bash
curl "http://localhost:8000/api/blog/blogs/?search=veteran&status=Published"
```

### Get Mission Genesis Blog
```bash
curl http://localhost:8000/api/blog/blogs/mission_genesis/
```

### Get Popular Blogs
```bash
curl "http://localhost:8000/api/blog/blogs/popular/?limit=5"
```

## 🔐 Permissions

All endpoints use `IsAuthenticatedOrReadOnly`:
- **Authenticated users**: Full CRUD access
- **Unauthenticated users**: Read-only access

## 🏗️ File Structure

```
blog/
├── __init__.py
├── admin.py                  # Admin configuration
├── apps.py                   # App config
├── tests.py                  # Tests
├── models/
│   ├── __init__.py
│   └── blog.py              # Blog model
├── api/
│   ├── __init__.py
│   ├── urls.py              # URL routing
│   ├── utils.py             # Response utilities
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── blog_serializer.py
│   └── views/
│       ├── __init__.py
│       └── blog_views.py
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py      # Initial migration
└── docs/
```

## 🎯 Features from Screenshots

### Main Blog Page ✅
- Title column
- Content preview (excerpt)
- Author column
- Mission Genesis badge display
- Search functionality
- "Add Blog" button
- Pagination

### Add Blog Modal ✅
All fields implemented:
- **Title** (required) - Text input
- **Content** (required) - Large textarea
- **Author** - Text input
- **Status** - Dropdown (Published/Draft/Archived)
- **Featured Image** - URL input with Image URL/Upload tabs
- **Mission Genesis checkbox** - "Set as Mission Genesis blog (only one blog can be Mission Genesis at a time)"

## 🚀 Quick Start

### 1. The app is already installed and configured

### 2. Access the API
```
API Base: http://localhost:8000/api/blog/
Admin: http://localhost:8000/admin/blog/
```

### 3. Create your first blog post
Use the admin interface or POST to `/api/blog/blogs/`

## ✨ Special Features

### Mission Genesis Blog
- Only one blog can be designated as "Mission Genesis"
- When setting a new blog as Mission Genesis, the previous one is automatically unset
- Special badge in admin interface
- Dedicated API endpoint to fetch

### Auto Slug Generation
- Slugs are automatically created from titles
- Duplicate slugs get a counter suffix (e.g., `blog-title-2`)
- URL-friendly format

### View Tracking
- View count automatically increments when retrieving a blog
- Popular blogs endpoint based on views
- Great for analytics

### Smart Search
- Search across title, content, and author
- Case-insensitive
- Fast indexed queries

## 🎉 Status: COMPLETE ✅

All features from the screenshots implemented:
- ✅ Blog CRUD operations
- ✅ Mission Genesis designation
- ✅ Status management (Published/Draft/Archived)
- ✅ Featured images
- ✅ Author tracking
- ✅ View counting
- ✅ Search and filtering
- ✅ Pagination
- ✅ Admin interface with badges
- ✅ Standardized API responses
- ✅ UUID primary keys
- ✅ Auto-generated slugs

The blog management system is production-ready!
