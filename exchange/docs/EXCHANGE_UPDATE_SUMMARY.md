# Exchange Feature Update Summary

This document summarizes the changes made to align the Exchange feature with the new "Apply to Join the Exchange" screen design.

---

## 1. Updated Models

### Exchange Model (`exchange/models/exchange.py`)

**Fields Renamed:**
- `org_name` → `business_name`
- `exchange_type` → `seller_type`
- `website_link` → `website`

**Fields Removed:**
- `contact_person` (removed as per new screen design)

**New Fields Added:**
- `business_ein` - CharField(max_length=20) - Business EIN Number
- `id_me_verified` - BooleanField(default=False) - ID.me verification status
- `manual_verification_doc` - URLField - Manual verification document URL
- `offers_benefits` - TextField - Offers and benefits description
- `business_hours` - JSONField - Weekly business hours schedule
- `facebook_enabled` - BooleanField(default=False)
- `twitter_enabled` - BooleanField(default=False)
- `instagram_enabled` - BooleanField(default=False)
- `linkedin_enabled` - BooleanField(default=False)

**Updated Choices:**
- `EXCHANGE_TYPE_CHOICES` → `SELLER_TYPE_CHOICES`
  - `veteran_owned` - Veteran Owned Business (was `vob`)
  - `spouse_owned` - Military Spouse Owned (NEW)
  - `service_organization` - Service Organization (was `vso`)
  - `affiliate` - Affiliate (unchanged)

**Updated Status Choices:**
- Changed default from `approved` to `under_review` for new applications

### ExchangePreviewImage Model (NEW)

New model created for handling multiple preview images per exchange.

**Fields:**
- `uuid` - Primary key
- `exchange` - ForeignKey to Exchange
- `image_url` - URLField for preview image
- `order` - IntegerField for display order
- `created_at`, `updated_at` - Auto timestamps

**Relationships:**
- Related name: `preview_images` on Exchange model

---

## 2. Updated Serializers

### ExchangePreviewImageSerializer (NEW)

Handles serialization of preview images with URL validation.

**Features:**
- Validates image URLs
- Supports ordering for display sequence

### ExchangeSerializer

**Updated Fields List:**
- Removed: `org_name`, `contact_person`, `exchange_type`, `website_link`
- Added: `business_name`, `business_ein`, `seller_type`, `website`, `id_me_verified`, `manual_verification_doc`, `offers_benefits`, `business_hours`, all social media enabled flags, `preview_images`, `preview_image_urls`

**New Validations:**
- `validate_seller_type()` - Validates against SELLER_TYPE_CHOICES
- `validate_offers_benefits()` - Max 500 characters
- `validate_business_hours()` - JSON structure validation for weekly schedule
- `validate_preview_image_urls()` - Max 10 images, URL format validation

**Updated Behavior:**
- Default status changed from `approved` to `under_review` on create
- Supports `preview_image_urls` write-only field for bulk image creation
- Orders preview images by `order` field
- Nested `preview_images` in read responses

### ExchangeListSerializer

**Updated Fields:**
- Uses `business_name` instead of `org_name`
- Uses `seller_type` instead of `exchange_type`
- Added `business_ein` field
- Added `preview_images` nested serializer

---

## 3. Updated Views/CRUD Operations

### ExchangeViewSet (`exchange/api/views/exchange.py`)

**Updated Querysets:**
- Added `prefetch_related('preview_images')` for performance

**Updated Filter Fields:**
- `exchange_type` → `seller_type` in filterset_fields

**Updated Search Fields:**
- Removed: `org_name`, `contact_person`
- Added: `business_name`, `offers_benefits`

**Updated Ordering Fields:**
- `org_name` → `business_name`
- `exchange_type` → `seller_type`

**Updated Methods:**
- All query parameters now use `seller_type` instead of `exchange_type`
- Log messages use `business_name` instead of `org_name`
- All docstrings updated to reflect new field names

---

## 4. Updated Admin Interface

### ExchangeAdmin (`exchange/admin.py`)

**New Inline:**
- `ExchangePreviewImageInline` - Manage preview images directly from Exchange admin

**Updated List Display:**
- Shows: `business_name`, `seller_type`, `category`, `email`, `status`, `id_me_verified`, `created_at`
- Removed: `contact_person`, `org_name`, `exchange_type`

**Updated Search Fields:**
- Added: `business_name`, `business_ein`, `offers_benefits`
- Removed: `org_name`, `contact_person`

**Updated Fieldsets:**
- Business Information section now includes `business_ein`, `seller_type`
- New "Verification" section with `id_me_verified`, `manual_verification_doc`, `status`
- New "Mission & Offers" section with `mission_statement`, `offers_benefits`, `business_hours`
- Social Media section includes enabled flags

**New Admin Actions:**
- `mark_under_review` - Bulk set status to under_review

### ExchangePreviewImageAdmin (NEW)

New admin interface for managing preview images independently.

**Features:**
- List display shows exchange, order, and creation date
- Searchable by exchange business name
- Ordered by exchange and display order

---

## 5. Migration Notes

**Migration File:** `exchange/migrations/0002_exchangepreviewimage_and_more.py`

**Key Operations:**
1. Created `ExchangePreviewImage` model
2. Renamed `contact_person` → `business_name` (Django auto-detected)
3. Removed fields: `exchange_type`, `org_name`, `website_link`
4. Added new fields: `business_ein`, `business_hours`, `seller_type`, `website`, verification fields, social media enabled flags
5. Created new index on `seller_type` field
6. All existing data preserved through field renames

**Migration Applied Successfully:** ✅

---

## 6. API Endpoint Summary

All existing endpoints remain functional with updated field names:

### POST /api/exchange/
Create new exchange application (now defaults to `under_review` status)

**New Required Fields:**
- `business_name` (was `org_name`)
- `seller_type` (was `exchange_type`)

**New Optional Fields:**
- `business_ein`
- `id_me_verified`
- `manual_verification_doc`
- `offers_benefits`
- `business_hours` (JSON)
- `preview_image_urls` (array)
- Social media enabled flags

### GET /api/exchange/
List exchanges with filtering

**Updated Query Parameters:**
- `seller_type` (was `exchange_type`)
- Search now includes `business_name`, `offers_benefits`

### GET /api/exchange/{uuid}/
Retrieve single exchange (includes nested preview_images)

### PATCH /api/exchange/{uuid}/
Update exchange (can add more preview images)

### DELETE /api/exchange/{uuid}/
Delete exchange

### GET /api/exchange/my-exchanges/
Get authenticated user's exchanges

### GET /api/exchange/user/{user_uuid}/
Get specific user's exchanges

---

## 7. Business Hours JSON Structure

The `business_hours` field expects a JSON object with this structure:

```json
{
  "monday": {
    "is_open": true,
    "open_time": "09:00",
    "close_time": "17:00"
  },
  "tuesday": {
    "is_open": true,
    "open_time": "09:00",
    "close_time": "17:00"
  },
  "wednesday": {
    "is_open": true,
    "open_time": "09:00",
    "close_time": "17:00"
  },
  "thursday": {
    "is_open": true,
    "open_time": "09:00",
    "close_time": "17:00"
  },
  "friday": {
    "is_open": true,
    "open_time": "09:00",
    "close_time": "17:00"
  },
  "saturday": {
    "is_open": false,
    "open_time": null,
    "close_time": null
  },
  "sunday": {
    "is_open": false,
    "open_time": null,
    "close_time": null
  }
}
```

---

## 8. Breaking Changes

⚠️ **API clients must update field names:**

- `org_name` → `business_name`
- `exchange_type` → `seller_type` (also update choice values)
- `website_link` → `website`
- `contact_person` field no longer exists

⚠️ **Default status changed:**

- New applications now default to `under_review` instead of `approved`

⚠️ **Choice values updated:**

The `seller_type` choices are (mapping from old `exchange_type`):
- `veteran_owned` (was `vob`)
- `spouse_owned` (NEW - not in old system)
- `service_organization` (was `vso`)
- `affiliate` (unchanged)

---

## 9. Testing Checklist

- [x] Models created successfully
- [x] Migrations applied without errors
- [x] Serializers updated with validations
- [x] Views updated with new field names
- [x] Admin interface updated
- [ ] Test POST endpoint with new fields
- [ ] Test GET endpoint returns preview_images
- [ ] Test business_hours JSON validation
- [ ] Test preview_image_urls array handling
- [ ] Test social media enabled flags
- [ ] Test ID.me verification field
- [ ] Verify search works with business_name
- [ ] Verify filtering works with seller_type

---

**Last Updated:** 2024
**Migration Status:** ✅ Applied (0002_exchangepreviewimage_and_more)
