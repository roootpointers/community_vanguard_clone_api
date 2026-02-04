# Postman Collection Migration Guide

## Quick Update Instructions

Since the Exchange API has been updated with new field names, here are the key changes to make in your Postman requests:

### 1. Update Request Body Field Names

**Old → New:**
```json
// OLD (remove these)
"org_name": "Veterans Tech Solutions"
"contact_person": "John Doe"
"exchange_type": "vob"
"website_link": "https://vettech.com"

// NEW (use these instead)
"business_name": "Veterans Tech Solutions"
"seller_type": "veteran_owned"  // Note: choice values changed too!
"website": "https://vettech.com"
```

### 2. Update Seller Type Values

**Old exchange_type choices:**
- `vob` → `veteran_owned`
- `vso` → `service_organization`
- `community_leader` → *(not directly mapped, use `affiliate` or `service_organization`)*
- `affiliate` → `affiliate` *(unchanged)*

**New seller_type choices:**
- `veteran_owned` - Veteran Owned Business
- `spouse_owned` - Military Spouse Owned (NEW)
- `service_organization` - Service Organization
- `affiliate` - Affiliate

### 3. Add New Optional Fields

```json
{
  "business_ein": "12-3456789",
  "id_me_verified": false,
  "manual_verification_doc": "https://cdn.example.com/documents/dd214.pdf",
  "offers_benefits": "10% veteran discount, free shipping",
  "business_hours": {
    "monday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
    "tuesday": {"is_open": true, "open_time": "09:00", "close_time": "17:00"},
    // ... other days
  },
  "preview_image_urls": [
    "https://cdn.example.com/images/preview1.jpg",
    "https://cdn.example.com/images/preview2.jpg"
  ],
  "facebook_enabled": true,
  "twitter_enabled": true,
  "instagram_enabled": true,
  "linkedin_enabled": false
}
```

### 4. Update Query Parameters

**In your GET requests:**

```
OLD: ?exchange_type=vob
NEW: ?seller_type=veteran_owned

OLD: search in org_name, contact_person
NEW: search in business_name, offers_benefits
```

### 5. Complete Request Example

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
  "offers_benefits": "10% discount for all veterans, free consultation",
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
    "https://cdn.example.com/images/team-2.jpg"
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

### 6. Expected Response Changes

**Status field:**
- New applications now default to `under_review` instead of `approved` or `pending`

**New response fields:**
```json
{
  "data": {
    // New fields in response:
    "business_ein": "12-3456789",
    "id_me_verified": false,
    "offers_benefits": "10% discount...",
    "business_hours": {...},
    "preview_images": [
      {
        "uuid": "preview-uuid",
        "image_url": "https://...",
        "order": 0,
        "created_at": "2025-12-01T10:30:00Z"
      }
    ],
    "facebook_enabled": true,
    "twitter_enabled": true,
    "instagram_enabled": true,
    "linkedin_enabled": false
  }
}
```

### 7. Category and Sub-Category

**Note:** These now expect UUIDs, not string names:

```json
// CORRECT:
"category": "a7ec5950-caf2-4d49-a3b9-7725cc3b8a8a"
"sub_category": "8d414331-3c1e-4860-bcb9-07a457c00692"

// INCORRECT (old way):
"category": "Technology"
"sub_category": "Software Development"
```

Use the GET /api/categories/ endpoint to retrieve category UUIDs.

---

## Testing Checklist

- [ ] Update all "Create Exchange" requests with new field names
- [ ] Change `exchange_type` to `seller_type` with new values
- [ ] Update all filter query parameters
- [ ] Test business_hours JSON structure
- [ ] Test preview_image_urls array
- [ ] Test social media enabled flags
- [ ] Verify category/sub_category use UUIDs
- [ ] Check response includes new fields

---

## Need Help?

- See [UPDATED_API_EXAMPLES.md](./UPDATED_API_EXAMPLES.md) for complete request/response examples
- See [EXCHANGE_UPDATE_SUMMARY.md](./EXCHANGE_UPDATE_SUMMARY.md) for detailed migration notes
- Old Postman collection backed up as `Exchange_API_Postman_Collection_OLD.json`

---

**Created:** December 1, 2025
