# Exchange API Documentation

## Overview
The Exchange API allows organizations and businesses to apply to join the Operation Vanguard exchange platform. All media fields (logos, images, verification files) accept URL strings instead of file uploads.

## Base URL
```
/api/exchange/
```

## Authentication
Currently set to `AllowAny`. Modify `permission_classes` in the view if authentication is required.

---

## Models

### Exchange Model
Represents an organization/business applying to join the exchange.

**Fields:**
- `uuid` (UUID): Unique identifier (primary key)
- `user` (ForeignKey): Associated user (optional)
- `org_name` (string): Organization name
- `contact_person` (string): Contact person name
- `email` (email): Contact email
- `phone` (string): Contact phone number
- `website_link` (URL): Organization website (optional)
- `address` (string): Organization address
- `exchange_type` (choice): Type of organization
  - `vob`: Veteran-Owned Business
  - `vso`: Veteran Service Organization
  - `community_leader`: Community Leader
  - `affiliate`: Affiliate
- `category` (string): Organization category
- `sub_category` (string): Sub-category (optional)
- `business_logo` (URL string): Logo URL (optional)
- `business_background_image` (URL string): Background image URL (optional)
- `mission_statement` (text): Organization mission
- `facebook`, `twitter`, `instagram`, `linkedin` (URLs): Social media links (optional)
- `status` (choice): Application status
  - `pending`: Pending Review
  - `approved`: Approved
  - `rejected`: Rejected
- `created_at`, `updated_at` (datetime): Timestamps

### ExchangeVerification Model
Stores verification document/image URLs for exchanges. Supports multiple URLs per exchange.

**Fields:**
- `uuid` (UUID): Unique identifier
- `exchange` (ForeignKey): Associated exchange
- `verification_file` (URL string): Verification document/image URL
- `file_type` (string): Type of file ('photo' or 'document')
- `created_at`, `updated_at` (datetime): Timestamps

---

## API Endpoints

### 1. Create Exchange Application
**POST** `/api/exchange/`

Submit a new exchange application with URL strings for all media fields.

#### Request Format
Use `application/json` content-type with URL strings for media fields.

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `org_name` | string | Yes | Organization name |
| `contact_person` | string | Yes | Contact person name |
| `email` | email | No | Contact email |
| `phone` | string | No | Contact phone (min 10 digits) |
| `website_link` | URL | No | Organization website |
| `address` | string | No | Organization address |
| `exchange_type` | choice | Yes | `vob`, `vso`, `community_leader`, or `affiliate` |
| `category` | string | No | Organization category |
| `sub_category` | string | No | Sub-category |
| `business_logo` | URL string | No | Logo image URL |
| `business_background_image` | URL string | No | Background image URL |
| `mission_statement` | text | No | Organization mission |
| `facebook` | URL | No | Facebook URL |
| `twitter` | URL | No | Twitter URL |
| `instagram` | URL | No | Instagram URL |
| `linkedin` | URL | No | LinkedIn URL |
| `verification_urls` | array | No | Array of verification file URLs (max 10) |

#### Example Request (cURL)

```bash
curl --location 'http://127.0.0.1:8000/api/exchange/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "org_name": "Veterans Tech Solutions",
  "contact_person": "John Doe",
  "email": "john@vettech.com",
  "phone": "555-123-4567",
  "website_link": "https://vettech.com",
  "address": "123 Main St, Austin, TX 78701",
  "exchange_type": "vob",
  "category": "Technology",
  "sub_category": "Software Development",
  "mission_statement": "To provide innovative technology solutions for veterans",
  "business_logo": "https://cdn.example.com/logos/vettech-logo.png",
  "business_background_image": "https://cdn.example.com/backgrounds/vettech-bg.jpg",
  "verification_urls": [
    "https://cdn.example.com/documents/tax-document.pdf",
    "https://cdn.example.com/documents/business-license.jpg"
  ],
  "facebook": "https://facebook.com/vettech",
  "instagram": "https://instagram.com/vettech"
}'
```

#### Example Request (JavaScript/Fetch)

```javascript
fetch('http://127.0.0.1:8000/api/exchange/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    org_name: 'Veterans Tech Solutions',
    contact_person: 'John Doe',
    email: 'john@vettech.com',
    phone: '555-123-4567',
    website_link: 'https://vettech.com',
    address: '123 Main St, Austin, TX 78701',
    exchange_type: 'vob',
    category: 'Technology',
    sub_category: 'Software Development',
    mission_statement: 'To provide innovative technology solutions for veterans',
    business_logo: 'https://cdn.example.com/logos/vettech-logo.png',
    business_background_image: 'https://cdn.example.com/backgrounds/vettech-bg.jpg',
    verification_urls: [
      'https://cdn.example.com/documents/tax-document.pdf',
      'https://cdn.example.com/documents/business-license.jpg'
    ],
    facebook: 'https://facebook.com/vettech',
    instagram: 'https://instagram.com/vettech'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Success Response (201 Created)

```json
{
  "success": true,
  "message": "Exchange application submitted successfully",
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "user": null,
    "user_email": null,
    "org_name": "Veterans Tech Solutions",
    "contact_person": "John Doe",
    "email": "john@vettech.com",
    "phone": "555-123-4567",
    "website_link": "https://vettech.com",
    "address": "123 Main St, Austin, TX 78701",
    "exchange_type": "vob",
    "exchange_type_display": "Veteran-Owned Business",
    "category": "Technology",
    "sub_category": "Software Development",
    "business_logo": "https://cdn.example.com/logos/vettech-logo.png",
    "business_background_image": "https://cdn.example.com/backgrounds/vettech-bg.jpg",
    "mission_statement": "To provide innovative technology solutions for veterans",
    "facebook": "https://facebook.com/vettech",
    "twitter": null,
    "instagram": "https://instagram.com/vettech",
    "linkedin": null,
    "status": "pending",
    "status_display": "Pending Review",
    "verifications": [
      {
        "uuid": "abc123...",
        "verification_file": "https://cdn.example.com/documents/tax-document.pdf",
        "file_type": "document",
        "url": "https://cdn.example.com/documents/tax-document.pdf",
        "created_at": "2025-10-21T10:30:00Z"
      },
      {
        "uuid": "def456...",
        "verification_file": "https://cdn.example.com/documents/business-license.jpg",
        "file_type": "photo",
        "url": "https://cdn.example.com/documents/business-license.jpg",
        "created_at": "2025-10-21T10:30:00Z"
      }
    ],
    "created_at": "2025-10-21T10:30:00Z",
    "updated_at": "2025-10-21T10:30:00Z"
  }
}
```

#### Error Response (400 Bad Request)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "email": ["Enter a valid email address."],
    "phone": ["Phone number must be at least 10 digits."],
    "verification_urls": ["Maximum 10 verification URLs allowed."],
    "business_logo": ["Enter a valid URL."]
  }
}
```

---

### 2. List Exchanges
**GET** `/api/exchange/`

Retrieve a list of all exchange applications with optional filtering.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `exchange_type` | string | Filter by exchange type (`vob`, `vso`, `community_leader`, `affiliate`) |
| `category` | string | Filter by category (case-insensitive partial match) |
| `sub_category` | string | Filter by sub-category (case-insensitive partial match) |
| `status` | string | Filter by status (`pending`, `approved`, `rejected`) |
| `search` | string | Search in org_name, contact_person, email, mission_statement |
| `ordering` | string | Order by field (e.g., `-created_at`, `org_name`) |

#### Example Requests

```bash
# Get all exchanges
GET /api/exchange/

# Filter by exchange type
GET /api/exchange/?exchange_type=vob

# Filter by category and sub-category
GET /api/exchange/?category=Technology&sub_category=Software

# Filter by status
GET /api/exchange/?status=approved

# Multiple filters
GET /api/exchange/?exchange_type=vob&category=Technology&status=pending

# Search
GET /api/exchange/?search=veterans

# Order by created date (newest first)
GET /api/exchange/?ordering=-created_at
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Exchanges retrieved successfully",
  "data": {
    "count": 2,
    "results": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "org_name": "Veterans Tech Solutions",
        "contact_person": "John Doe",
        "email": "john@vettech.com",
        "phone": "555-123-4567",
        "exchange_type": "vob",
        "exchange_type_display": "Veteran-Owned Business",
        "category": "Technology",
        "sub_category": "Software Development",
        "business_logo": "https://cdn.example.com/logos/vettech-logo.png",
        "status": "pending",
        "status_display": "Pending Review",
        "verification_count": 2,
        "created_at": "2025-10-21T10:30:00Z"
      },
      {
        "uuid": "789def01-2345-6789-abcd-ef0123456789",
        "org_name": "Military Family Support",
        "contact_person": "Jane Smith",
        "email": "jane@militaryfamily.org",
        "phone": "555-987-6543",
        "exchange_type": "vso",
        "exchange_type_display": "Veteran Service Organization",
        "category": "Support Services",
        "sub_category": "Family Counseling",
        "business_logo": "https://cdn.example.com/logos/mfs-logo.png",
        "status": "approved",
        "status_display": "Approved",
        "verification_count": 3,
        "created_at": "2025-10-20T15:45:00Z"
      }
    ]
  }
}
```

---

### 3. Get Exchange Details
**GET** `/api/exchange/{uuid}/`

Retrieve detailed information about a specific exchange application.

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Exchange retrieved successfully",
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "user": null,
    "user_email": null,
    "org_name": "Veterans Tech Solutions",
    "contact_person": "John Doe",
    "email": "john@vettech.com",
    "phone": "555-123-4567",
    "website_link": "https://vettech.com",
    "address": "123 Main St, Austin, TX 78701",
    "exchange_type": "vob",
    "exchange_type_display": "Veteran-Owned Business",
    "category": "Technology",
    "sub_category": "Software Development",
    "business_logo": "https://cdn.example.com/logos/vettech-logo.png",
    "business_background_image": "https://cdn.example.com/backgrounds/vettech-bg.jpg",
    "mission_statement": "To provide innovative technology solutions for veterans",
    "facebook": "https://facebook.com/vettech",
    "twitter": null,
    "instagram": "https://instagram.com/vettech",
    "linkedin": null,
    "status": "pending",
    "status_display": "Pending Review",
    "verifications": [
      {
        "uuid": "abc123...",
        "verification_file": "https://cdn.example.com/documents/tax-document.pdf",
        "file_type": "document",
        "url": "https://cdn.example.com/documents/tax-document.pdf",
        "created_at": "2025-10-21T10:30:00Z"
      }
    ],
    "created_at": "2025-10-21T10:30:00Z",
    "updated_at": "2025-10-21T10:30:00Z"
  }
}
```

#### Error Response (404 Not Found)

```json
{
  "success": false,
  "message": "Exchange not found"
}
```

---

### 4. Update Exchange
**PUT/PATCH** `/api/exchange/{uuid}/`

Update an existing exchange application. Use PUT for full updates or PATCH for partial updates.

#### Request Example (PATCH)

```bash
curl --location --request PATCH 'http://127.0.0.1:8000/api/exchange/123e4567-e89b-12d3-a456-426614174000/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "phone": "555-999-8888",
  "website_link": "https://newwebsite.com",
  "verification_urls": [
    "https://cdn.example.com/documents/new-verification.pdf"
  ]
}'
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Exchange application updated successfully",
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "org_name": "Veterans Tech Solutions",
    "phone": "555-999-8888",
    "website_link": "https://newwebsite.com",
    ...
  }
}
```

---

### 5. Delete Exchange
**DELETE** `/api/exchange/{uuid}/`

Delete an exchange application.

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Exchange application deleted successfully"
}
```

---

### 6. Get Exchanges Grouped by Category
**GET** `/api/exchange/grouped-by-category/`

Retrieve all exchanges organized by category. Each category contains an array of exchanges and a count.

#### Query Parameters (Optional)

| Parameter | Type | Description |
|-----------|------|-------------|
| `exchange_type` | string | Filter by exchange type (`vob`, `vso`, `community_leader`, `affiliate`) |
| `status` | string | Filter by status (`pending`, `approved`, `rejected`) |
| `search` | string | Search in org_name, contact_person, email, mission_statement |

#### Example Requests

```bash
# Get all exchanges grouped by category
GET /api/exchange/grouped-by-category/

# Get VOB exchanges grouped by category
GET /api/exchange/grouped-by-category/?exchange_type=vob

# Get approved exchanges grouped by category
GET /api/exchange/grouped-by-category/?status=approved

# Search and group by category
GET /api/exchange/grouped-by-category/?search=veteran
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Exchanges grouped by category retrieved successfully",
  "data": {
    "Technology": {
      "count": 3,
      "exchanges": [
        {
          "uuid": "123e4567-e89b-12d3-a456-426614174000",
          "org_name": "Veterans Tech Solutions",
          "contact_person": "John Doe",
          "email": "john@vettech.com",
          "phone": "555-123-4567",
          "exchange_type": "vob",
          "exchange_type_display": "Veteran-Owned Business",
          "category": "Technology",
          "sub_category": "Software Development",
          "business_logo": "https://cdn.example.com/logos/logo.png",
          "status": "pending",
          "status_display": "Pending Review",
          "verification_count": 2,
          "created_at": "2025-10-21T10:30:00Z"
        },
        {
          "uuid": "456def78-e89b-12d3-a456-426614174001",
          "org_name": "Tech Veterans Inc",
          "contact_person": "Jane Smith",
          "email": "jane@techvets.com",
          "phone": "555-234-5678",
          "exchange_type": "vob",
          "exchange_type_display": "Veteran-Owned Business",
          "category": "Technology",
          "sub_category": "IT Services",
          "business_logo": "https://cdn.example.com/logos/techvets.png",
          "status": "approved",
          "status_display": "Approved",
          "verification_count": 1,
          "created_at": "2025-10-20T15:45:00Z"
        }
      ]
    },
    "Auto": {
      "count": 2,
      "exchanges": [
        {
          "uuid": "789abc01-2345-6789-abcd-ef0123456789",
          "org_name": "Veteran Auto Repair",
          "contact_person": "Mike Johnson",
          "email": "mike@vetautorepair.com",
          "phone": "555-345-6789",
          "exchange_type": "vob",
          "exchange_type_display": "Veteran-Owned Business",
          "category": "Auto",
          "sub_category": "Repair Services",
          "business_logo": "https://cdn.example.com/logos/autorepair.png",
          "status": "approved",
          "status_display": "Approved",
          "verification_count": 3,
          "created_at": "2025-10-19T09:15:00Z"
        }
      ]
    },
    "Health and Wellness": {
      "count": 1,
      "exchanges": [
        {
          "uuid": "abc123de-f456-7890-abcd-ef0123456789",
          "org_name": "Veteran Fitness Center",
          "contact_person": "Sarah Williams",
          "email": "sarah@vetfitness.com",
          "phone": "555-456-7890",
          "exchange_type": "affiliate",
          "exchange_type_display": "Affiliate",
          "category": "Health and Wellness",
          "sub_category": "Fitness",
          "business_logo": "https://cdn.example.com/logos/fitness.png",
          "status": "pending",
          "status_display": "Pending Review",
          "verification_count": 1,
          "created_at": "2025-10-18T14:20:00Z"
        }
      ]
    }
  },
  "total_categories": 3,
  "total_exchanges": 6
}
```

#### Use Cases

This endpoint is perfect for:
- Displaying exchanges in a categorized view on the frontend
- Creating category-based navigation
- Showing statistics by category
- Building category-filtered dashboards

---

## Validation Rules

### Required Fields
- `org_name`, `exchange_type`

### Optional Fields
- All other fields are optional (email, phone, address, contact_person, category, mission_statement, etc.)

### Email Validation
- Must be a valid email format if provided
- Automatically converted to lowercase

### Phone Validation
- Must contain at least 10 numeric digits if provided
- Can include formatting characters (e.g., dashes, parentheses)

### URL Validation
- All URL fields (`website_link`, `business_logo`, `business_background_image`, `facebook`, `twitter`, `instagram`, `linkedin`, `verification_urls`) must be valid URLs if provided

### Exchange Type Validation
- Must be one of: `vob`, `vso`, `community_leader`, `affiliate`

### Verification URLs Validation
- Maximum 10 URLs per request
- Each URL must be valid
- File type automatically determined by URL extension:
  - `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp` → 'photo'
  - All other extensions → 'document'

---

## Media Upload Workflow

Since all media fields accept URL strings, the typical workflow is:

1. **Upload files to external storage** (e.g., AWS S3, Cloudinary, or your own storage service)
2. **Get the public URL** for each uploaded file
3. **Submit the URLs** to the Exchange API

### Example Workflow with AWS S3

```javascript
// Step 1: Upload file to S3
const uploadToS3 = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('https://your-upload-endpoint.com/upload', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.url; // Returns the S3 URL
};

// Step 2: Get URLs for all files
const logoUrl = await uploadToS3(logoFile);
const backgroundUrl = await uploadToS3(backgroundFile);
const verificationUrls = await Promise.all(
  verificationFiles.map(file => uploadToS3(file))
);

// Step 3: Submit to Exchange API
const response = await fetch('http://127.0.0.1:8000/api/exchange/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    org_name: 'Veterans Tech Solutions',
    business_logo: logoUrl,
    business_background_image: backgroundUrl,
    verification_urls: verificationUrls,
    // ... other fields
  })
});
```

---

## Admin Interface

The Exchange app includes a comprehensive Django admin interface with:

### Features
- Inline editing of verification file URLs
- Bulk actions: Approve, Reject, Mark as Pending
- Filtering by exchange type, status, category, creation date
- Search by org name, contact person, email, phone, mission statement
- Organized fieldsets for better data management

### Bulk Actions
1. **Approve exchanges**: Set status to 'approved'
2. **Reject exchanges**: Set status to 'rejected'
3. **Mark as pending review**: Set status to 'pending'

---

## File Structure

```
exchange/
├── docs/
│   └── EXCHANGE_API_DOCUMENTATION.md  # This file
├── models/
│   ├── __init__.py
│   └── exchange.py          # Exchange and ExchangeVerification models
├── api/
│   ├── __init__.py
│   ├── urls.py              # API URL routes
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── exchange.py      # Serializers
│   └── views/
│       ├── __init__.py
│       └── exchange.py      # ViewSet with CRUD operations
├── admin.py                 # Admin configuration
├── apps.py                  # App configuration
└── migrations/
    └── 0001_initial.py      # Initial migration
```

---

## Testing Examples

### Create Exchange with cURL

```bash
curl --location 'http://127.0.0.1:8000/api/exchange/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "org_name": "FreshMart Grocery",
  "contact_person": "Mike Johnson",
  "email": "mike@freshmart.com",
  "phone": "555-444-3333",
  "address": "456 Oak Ave, San Antonio, TX 78210",
  "exchange_type": "vob",
  "category": "Specialty Food and Beverage",
  "mission_statement": "To provide fresh, healthy, and affordable groceries",
  "business_logo": "https://cdn.example.com/logos/freshmart.png",
  "verification_urls": [
    "https://cdn.example.com/documents/tax-doc.pdf"
  ]
}'
```

### List Filtered Exchanges

```bash
# Get all VOB exchanges in Technology category
curl 'http://127.0.0.1:8000/api/exchange/?exchange_type=vob&category=Technology'

# Get approved exchanges
curl 'http://127.0.0.1:8000/api/exchange/?status=approved'

# Search for specific organization
curl 'http://127.0.0.1:8000/api/exchange/?search=FreshMart'
```

---

## Notes

1. **URL-Based Storage**: All media fields store URLs, not files
2. **External Storage**: Files should be uploaded to external storage (S3, CDN, etc.) before submitting URLs
3. **Status Management**: New applications default to 'pending' status
4. **User Association**: If user is authenticated, they are automatically associated with the exchange
5. **Multiple URLs**: The `verification_urls` field accepts multiple URLs in a single request
6. **File Type Detection**: File types are automatically determined from URL extensions
7. **Pagination**: List endpoint supports pagination (configure in DRF settings)
8. **Ordering**: Default ordering is by creation date (newest first)
9. **Flexible Validation**: Most fields are optional to allow flexible form submission

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Request completed successfully |
| 201 | Created - Exchange created successfully |
| 400 | Bad Request - Validation error |
| 404 | Not Found - Exchange not found |
| 500 | Internal Server Error - Server error |

---

## Future Enhancements

Potential features for future development:
- Email notifications on status changes
- Advanced search with Elasticsearch
- Public API with rate limiting
- Review/comment system for admins
- Document verification workflow
- Automated approval based on criteria
- Analytics dashboard
- Webhooks for status changes
- Integration with external storage providers
