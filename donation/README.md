# Donation Management System

A comprehensive Django REST Framework application for managing donations, setting fundraising targets, and tracking progress.

## Features

### Core Functionality
✅ **Donation Management**
- Create, read, update, and delete donations
- Track donor information (name, email)
- Support multiple currencies (USD, EUR, GBP, CAD, AUD, JPY)
- Multiple payment methods (Card, Bank Transfer, PayPal, Cash, Crypto)
- Month/Year tracking for donations
- Search and filter capabilities
- Bulk delete operations

✅ **Target Setting**
- Set monthly fundraising targets
- Track progress automatically
- Visual progress indicators
- Multi-month progress tracking
- Unique targets per month/year

✅ **Analytics & Reporting**
- Comprehensive donation statistics
- Breakdown by currency and payment method
- Top donors tracking
- Recent donations monitoring
- Monthly and yearly summaries

✅ **Admin Interface**
- Rich admin dashboard with Jazzmin integration
- Color-coded amount displays
- Progress bars for targets
- Filtering and search capabilities
- Bulk actions support

## Installation

The app is already installed and configured in the project. The following steps were completed:

1. ✅ Created app structure with models, serializers, and views
2. ✅ Registered in `INSTALLED_APPS` in `core/settings.py`
3. ✅ Added URL routes to `core/urls.py`
4. ✅ Configured Jazzmin admin icons
5. ✅ Created and ran migrations
6. ✅ Database tables created successfully

## Database Models

### Donation
Stores individual donation records with the following fields:
- `donor_name`: Name of the donor
- `donor_email`: Email address
- `amount`: Donation amount (decimal)
- `currency`: Currency code (USD, EUR, GBP, etc.)
- `method`: Payment method
- `month`: Month of donation (1-12)
- `year`: Year of donation
- `notes`: Additional notes
- `created_at`, `updated_at`: Timestamps

### DonationTarget
Stores fundraising targets for specific periods:
- `month`: Target month (1-12)
- `year`: Target year
- `target_amount`: Goal amount (decimal)
- `currency`: Currency code
- `description`: Target description
- `created_at`, `updated_at`: Timestamps

**Note:** Each month/year combination can only have one target (unique constraint).

## API Endpoints

### Base URL
```
/api/donation/
```

### Donations
- `GET /api/donation/donations/` - List all donations (paginated)
- `POST /api/donation/donations/` - Create a new donation
- `GET /api/donation/donations/{id}/` - Get donation details
- `PUT /api/donation/donations/{id}/` - Update donation
- `PATCH /api/donation/donations/{id}/` - Partial update
- `DELETE /api/donation/donations/{id}/` - Delete donation
- `GET /api/donation/donations/by_month/?year=2024` - Group by month
- `GET /api/donation/donations/by_donor/?email=john@example.com` - By donor
- `DELETE /api/donation/donations/bulk_delete/` - Bulk delete

### Targets
- `GET /api/donation/targets/` - List all targets
- `POST /api/donation/targets/` - Create a new target
- `GET /api/donation/targets/{id}/` - Get target details
- `PUT /api/donation/targets/{id}/` - Update target
- `PATCH /api/donation/targets/{id}/` - Partial update
- `DELETE /api/donation/targets/{id}/` - Delete target
- `GET /api/donation/targets/by_period/?month=3&year=2024` - Get specific period
- `GET /api/donation/targets/current_year/` - Current year targets
- `GET /api/donation/targets/progress_tracker/?months=1,2,3&year=2024` - Progress tracker

### Statistics
- `GET /api/donation/stats/` - Comprehensive statistics
- `GET /api/donation/stats/?currency=USD` - Filter by currency
- `GET /api/donation/stats/?start_date=2024-01-01&end_date=2024-12-31` - Date range

## API Examples

### Create a Donation
```bash
curl -X POST http://localhost:8000/api/donation/donations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "donor_name": "John Doe",
    "donor_email": "john@example.com",
    "amount": "5000.00",
    "currency": "USD",
    "method": "Card",
    "month": 1,
    "year": 2024
  }'
```

### Set a Monthly Target
```bash
curl -X POST http://localhost:8000/api/donation/targets/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "month": 3,
    "year": 2024,
    "target_amount": "400.00",
    "currency": "USD",
    "description": "Every contribution strengthens the mission"
  }'
```

### Search Donations
```bash
curl "http://localhost:8000/api/donation/donations/?search=john&currency=USD&ordering=-amount"
```

### Get Progress Tracker
```bash
curl "http://localhost:8000/api/donation/targets/progress_tracker/?months=1,2,3&year=2024"
```

## Query Parameters

### Donations List
- `page`: Page number
- `page_size`: Items per page (default: 10)
- `search`: Search in name, email, notes
- `currency`: Filter by currency
- `method`: Filter by payment method
- `month`: Filter by month
- `year`: Filter by year
- `ordering`: Sort field (e.g., `-created_at`, `amount`, `donor_name`)

### Targets List
- `page`: Page number
- `month`: Filter by month
- `year`: Filter by year
- `currency`: Filter by currency
- `ordering`: Sort field

## Admin Interface

Access the admin interface at:
```
http://localhost:8000/admin/donation/
```

### Features:
- **Donations Admin**
  - Color-coded amounts (green for $1000+, blue for $100+)
  - Search by donor name, email, notes
  - Filter by currency, method, month, year
  - Date hierarchy navigation
  - Bulk actions

- **Targets Admin**
  - Visual progress bars
  - Real-time collected amount display
  - Monthly period display
  - Progress percentage calculation
  - Filter by year and currency

## Permissions

All endpoints use `IsAuthenticatedOrReadOnly` permission:
- **Authenticated users**: Full CRUD access
- **Unauthenticated users**: Read-only access

## Features Matching Screenshots

### Main Donations Page
✅ Donations table with:
- Donor name
- Amount with currency
- Payment method
- Created date
- Edit/Delete actions
- Pagination (10 per page)
- Search functionality

### Add Donation Modal
✅ Form fields:
- Donor Name
- Donor Email (required)
- Amount (required)
- Currency (dropdown: USD, EUR, GBP, etc.)
- Method (dropdown: Card, Bank Transfer, PayPal, etc.)
- Month (dropdown: 1-12)
- Year (dropdown)
- Cancel/Add buttons

### Set Donation Target Modal
✅ Form fields:
- Month (dropdown: 1-12, required)
- Year (dropdown, required)
- Target Amount (required)
- Cancel/Save Target buttons

### Progress Tracker
✅ Features:
- Duration display (e.g., "3 Months")
- Month tabs (January, February, March)
- Description field
- Collected vs Goal display
- Circular progress indicator
- Real-time progress calculation

## Testing

To test the API endpoints:

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Create a superuser (if not already created):**
   ```bash
   python manage.py createsuperuser
   ```

3. **Access the API:**
   - API Root: http://localhost:8000/api/donation/
   - Admin Panel: http://localhost:8000/admin/

4. **Test endpoints with curl or Postman** (see examples above)

## File Structure

```
donation/
├── __init__.py
├── admin.py              # Admin interface configuration
├── apps.py               # App configuration
├── tests.py              # Unit tests
├── models/
│   ├── __init__.py
│   ├── donation.py       # Donation model
│   └── donation_target.py # DonationTarget model
├── api/
│   ├── __init__.py
│   ├── urls.py           # API URL routing
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── donation_serializer.py
│   │   └── donation_target_serializer.py
│   └── views/
│       ├── __init__.py
│       ├── donation_views.py
│       ├── donation_target_views.py
│       └── donation_stats_views.py
├── docs/
│   └── DONATION_API_DOCUMENTATION.md
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

## Next Steps

### Recommended Enhancements:
1. Add email notifications for new donations
2. Implement recurring donation schedules
3. Add donation receipts generation (PDF)
4. Integrate with payment gateways (Stripe, PayPal)
5. Add donation campaigns
6. Implement donor profiles
7. Add export functionality (CSV, Excel)
8. Create donation widgets for website embedding
9. Add multi-currency conversion
10. Implement donation matching features

### Integration Ideas:
- Connect with existing user system for authenticated donors
- Link with notification system for donation alerts
- Integrate with reporting dashboard
- Add donation history to user profiles

## Support

For detailed API documentation, see:
- [DONATION_API_DOCUMENTATION.md](docs/DONATION_API_DOCUMENTATION.md)

For issues or questions, contact the development team.

## License

Part of the Operation Vanguard Backend system.
