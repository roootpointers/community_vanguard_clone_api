# Updated Exchange API Examples

This document provides updated API examples matching the new Exchange model structure.

---

## Create Exchange Application (POST /api/exchange/)

### Example Request (Complete)

```json
{
  "business_name": "Veterans Tech Solutions",
  "business_ein": "12-3456789",
  "email": "john@vettech.com",
  "phone": "555-123-4567",
  "website": "https://vettech.com",
  "address": "123 Main St, Austin, TX 78701",
  "seller_type": "veteran_owned",
  "category": "a7ec5950-caf2-4d49-a3b9-7725cc3b8a8a",
  "sub_category": "8d414331-3c1e-4860-bcb9-07a457c00692",
  "mission_statement": "To provide innovative technology solutions for veterans",
  "offers_benefits": "10% discount for all veterans, free consultation for first-time customers, priority support",
  "business_hours": {
    "monday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
    "tuesday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
    "wednesday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
    "thursday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
    "friday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
    "saturday": {"is_open": false},
    "sunday": {"is_open": false}
  },
  "business_logo": "https://cdn.example.com/logos/vettech-logo.png",
  "business_background_image": "https://cdn.example.com/backgrounds/vettech-bg.jpg",
  "verification_urls": [
    "https://cdn.example.com/documents/tax-document.pdf",
    "https://cdn.example.com/documents/business-license.jpg"
  ],
  "preview_image_urls": [
    "https://cdn.example.com/images/office-1.jpg",
    "https://cdn.example.com/images/team-2.jpg",
    "https://cdn.example.com/images/workspace-3.jpg"
  ],
  "id_me_verified": false,
  "manual_verification_doc": "https://cdn.example.com/documents/dd214.pdf",
  "facebook": "https://facebook.com/vettech",
  "facebook_enabled": true,
  "twitter": "https://twitter.com/vettech",
  "twitter_enabled": true,
  "instagram": "https://instagram.com/vettech",
  "instagram_enabled": true,
  "linkedin": "https://linkedin.com/company/vettech",
  "linkedin_enabled": false
}
```

### Example Request (Minimal)

```json
{
  "business_name": "Veterans Tech Solutions",
  "email": "john@vettech.com",
  "seller_type": "veteran_owned"
}
```

### Success Response (201 Created)

```json
{
  "success": true,
  "message": "Exchange application submitted successfully",
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "user": {
      "uuid": "user-uuid-here",
      "full_name": "John Smith",
      "email": "john@vettech.com"
    },
    "business_name": "Veterans Tech Solutions",
    "business_ein": "12-3456789",
    "seller_type": "veteran_owned",
    "category": {
      "uuid": "a7ec5950-caf2-4d49-a3b9-7725cc3b8a8a",
      "name": "Technology"
    },
    "sub_category": {
      "uuid": "8d414331-3c1e-4860-bcb9-07a457c00692",
      "name": "Software Development",
      "category_name": "Technology"
    },
    "id_me_verified": false,
    "manual_verification_doc": "https://cdn.example.com/documents/dd214.pdf",
    "business_logo": "https://cdn.example.com/logos/vettech-logo.png",
    "business_background_image": "https://cdn.example.com/backgrounds/vettech-bg.jpg",
    "mission_statement": "To provide innovative technology solutions for veterans",
    "address": "123 Main St, Austin, TX 78701",
    "phone": "555-123-4567",
    "email": "john@vettech.com",
    "website": "https://vettech.com",
    "offers_benefits": "10% discount for all veterans, free consultation for first-time customers",
    "business_hours": {
      "monday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
      "tuesday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
      "wednesday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
      "thursday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
      "friday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
      "saturday": {"is_open": false},
      "sunday": {"is_open": false}
    },
    "facebook": "https://facebook.com/vettech",
    "facebook_enabled": true,
    "twitter": "https://twitter.com/vettech",
    "twitter_enabled": true,
    "instagram": "https://instagram.com/vettech",
    "instagram_enabled": true,
    "linkedin": "https://linkedin.com/company/vettech",
    "linkedin_enabled": false,
    "status": "under_review",
    "verifications": [
      {
        "uuid": "verif-uuid-1",
        "verification_file": "https://cdn.example.com/documents/tax-document.pdf",
        "file_type": "document",
        "created_at": "2025-12-01T10:30:00Z",
        "updated_at": "2025-12-01T10:30:00Z"
      },
      {
        "uuid": "verif-uuid-2",
        "verification_file": "https://cdn.example.com/documents/business-license.jpg",
        "file_type": "photo",
        "created_at": "2025-12-01T10:30:00Z",
        "updated_at": "2025-12-01T10:30:00Z"
      }
    ],
    "preview_images": [
      {
        "uuid": "preview-uuid-1",
        "image_url": "https://cdn.example.com/images/office-1.jpg",
        "order": 0,
        "created_at": "2025-12-01T10:30:00Z",
        "updated_at": "2025-12-01T10:30:00Z"
      },
      {
        "uuid": "preview-uuid-2",
        "image_url": "https://cdn.example.com/images/team-2.jpg",
        "order": 1,
        "created_at": "2025-12-01T10:30:00Z",
        "updated_at": "2025-12-01T10:30:00Z"
      },
      {
        "uuid": "preview-uuid-3",
        "image_url": "https://cdn.example.com/images/workspace-3.jpg",
        "order": 2,
        "created_at": "2025-12-01T10:30:00Z",
        "updated_at": "2025-12-01T10:30:00Z"
      }
    ],
    "created_at": "2025-12-01T10:30:00Z",
    "updated_at": "2025-12-01T10:30:00Z"
  }
}
```

---

## Query Parameters

### Filter by Seller Type
```
GET /api/exchange/?seller_type=veteran_owned
```

Available seller types:
- `veteran_owned` - Veteran Owned Business
- `spouse_owned` - Military Spouse Owned
- `service_organization` - Service Organization
- `affiliate` - Affiliate

### Filter by Category
```
GET /api/exchange/?category=a7ec5950-caf2-4d49-a3b9-7725cc3b8a8a
```

### Filter by Status
```
GET /api/exchange/?status=under_review
```

Available statuses:
- `pending` - Pending Review
- `under_review` - Under Review
- `approved` - Approved
- `rejected` - Rejected

### Search
```
GET /api/exchange/?search=veterans
```

Searches in: business_name, email, mission_statement, offers_benefits

### Multiple Filters
```
GET /api/exchange/?seller_type=veteran_owned&status=approved&search=tech
```

---

## Update Exchange (PATCH /api/exchange/{uuid}/)

### Example: Add More Preview Images

```json
{
  "preview_image_urls": [
    "https://cdn.example.com/images/product-1.jpg",
    "https://cdn.example.com/images/product-2.jpg"
  ]
}
```

### Example: Update Business Hours

```json
{
  "business_hours": {
    "monday": {"is_open": true, "open_time": "08:00", "close_time": "18:00"},
    "tuesday": {"is_open": true, "open_time": "08:00", "close_time": "18:00"},
    "wednesday": {"is_open": true, "open_time": "08:00", "close_time": "18:00"},
    "thursday": {"is_open": true, "open_time": "08:00", "close_time": "18:00"},
    "friday": {"is_open": true, "open_time": "08:00", "close_time": "18:00"},
    "saturday": {"is_open": true, "open_time": "10:00", "close_time": "16:00"},
    "sunday": {"is_open": false}
  }
}
```

### Example: Update Contact Info and Social Media

```json
{
  "phone": "555-999-8888",
  "website": "https://newwebsite.com",
  "facebook": "https://facebook.com/newpage",
  "facebook_enabled": true,
  "instagram": "https://instagram.com/newpage",
  "instagram_enabled": true
}
```

---

## Seller Type Examples

### Veteran Owned Business

```json
{
  "business_name": "Patriot Coffee Company",
  "business_ein": "98-7654321",
  "email": "sarah@patriotcoffee.com",
  "phone": "555-234-5678",
  "website": "https://patriotcoffee.com",
  "address": "789 Coffee Lane, Seattle, WA 98101",
  "seller_type": "veteran_owned",
  "category": "specialty-food-uuid",
  "sub_category": "coffee-tea-uuid",
  "mission_statement": "Premium ethically-sourced coffee supporting veteran communities",
  "offers_benefits": "15% veteran discount, free delivery over $50, loyalty rewards program",
  "business_logo": "https://cdn.example.com/logos/patriot-coffee.png",
  "id_me_verified": true
}
```

### Military Spouse Owned

```json
{
  "business_name": "Military Family Bakery",
  "email": "info@milfambakery.com",
  "phone": "555-345-6789",
  "seller_type": "spouse_owned",
  "mission_statement": "Homemade baked goods from military families, for military families",
  "offers_benefits": "10% military discount, custom orders for military events"
}
```

### Service Organization

```json
{
  "business_name": "Veterans Support Network",
  "email": "contact@veteransupport.org",
  "phone": "555-456-7890",
  "website": "https://veteransupport.org",
  "seller_type": "service_organization",
  "mission_statement": "Providing comprehensive support services for veterans and their families",
  "offers_benefits": "Free counseling, job placement assistance, housing support"
}
```

### Affiliate

```json
{
  "business_name": "Veteran Fitness Alliance",
  "email": "lisa@vetfitness.com",
  "phone": "555-567-8901",
  "website": "https://vetfitness.com",
  "seller_type": "affiliate",
  "category": "health-wellness-uuid",
  "sub_category": "fitness-uuid",
  "mission_statement": "Health and wellness programs specifically designed for veterans",
  "offers_benefits": "Group classes, personal training, nutrition counseling"
}
```

---

## Field Mappings (Old → New)

| Old Field Name | New Field Name | Notes |
|---------------|----------------|-------|
| `org_name` | `business_name` | Required |
| `contact_person` | *(removed)* | No longer used |
| `exchange_type` | `seller_type` | Different choice values |
| `website_link` | `website` | |
| *(new)* | `business_ein` | Business EIN Number |
| *(new)* | `id_me_verified` | Boolean for ID.me verification |
| *(new)* | `manual_verification_doc` | URL for manual verification |
| *(new)* | `offers_benefits` | Text field for offers description |
| *(new)* | `business_hours` | JSON field for weekly schedule |
| *(new)* | `preview_image_urls` | Array for multiple preview images |
| *(new)* | `facebook_enabled` | Boolean toggle |
| *(new)* | `twitter_enabled` | Boolean toggle |
| *(new)* | `instagram_enabled` | Boolean toggle |
| *(new)* | `linkedin_enabled` | Boolean toggle |

---

## Validation Rules

- **business_name**: Required, max 255 characters
- **business_ein**: Optional, max 20 characters
- **seller_type**: Required, must be one of: veteran_owned, spouse_owned, service_organization, affiliate
- **email**: Required, valid email format, converted to lowercase
- **phone**: Optional, must have at least 10 digits
- **website**: Optional, valid URL format
- **mission_statement**: Optional, max 500 characters
- **offers_benefits**: Optional, max 500 characters
- **business_hours**: Optional, must be valid JSON object with day keys
- **verification_urls**: Optional, max 10 URLs, each must be valid URL
- **preview_image_urls**: Optional, max 10 URLs, each must be valid URL
- **category**: Optional, must be valid UUID of existing Category
- **sub_category**: Optional, must be valid UUID of existing SubCategory belonging to the selected category

---

**Last Updated:** December 1, 2025
