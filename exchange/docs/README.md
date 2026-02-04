# Exchange App Documentation

This directory contains all documentation related to the Exchange app.

## Available Documentation

### [EXCHANGE_API_DOCUMENTATION.md](./EXCHANGE_API_DOCUMENTATION.md)
Complete API documentation for the Exchange endpoints, including:
- Model definitions
- API endpoints (Create, List, Retrieve, Update, Delete)
- Request/response examples
- Validation rules
- Media upload workflow (URL-based)
- Admin interface features
- Testing examples

## Quick Links

### API Endpoints
- **POST** `/api/exchange/` - Create new exchange application
- **GET** `/api/exchange/` - List exchanges with filtering
- **GET** `/api/exchange/{uuid}/` - Get exchange details
- **PATCH/PUT** `/api/exchange/{uuid}/` - Update exchange
- **DELETE** `/api/exchange/{uuid}/` - Delete exchange

### Key Features
- URL-based media storage (all images/files stored as URLs)
- Support for multiple verification file URLs
- Filtering by exchange_type, category, sub_category, status
- Full-text search across organization details
- Comprehensive admin interface with bulk actions

### Exchange Types
- `vob` - Veteran-Owned Business
- `vso` - Veteran Service Organization
- `community_leader` - Community Leader
- `affiliate` - Affiliate

### Status Options
- `pending` - Pending Review (default)
- `approved` - Approved
- `rejected` - Rejected

## Media Upload Architecture

The Exchange app uses URL-based media storage instead of direct file uploads:

1. Upload files to external storage (AWS S3, Cloudinary, etc.)
2. Get public URLs for uploaded files
3. Submit URLs to Exchange API

All media fields accept URL strings:
- `business_logo`
- `business_background_image`
- `verification_urls` (array of URLs)

## Related Documentation

For more information about the overall project structure, see the main README.md in the project root.
