# Exchange App - Complete Documentation

## Overview

The Exchange app is a comprehensive platform for businesses to register, manage their profiles, and accept bookings from users. It includes a complete booking system with business hours management, time slot generation, and appointment scheduling.

## Features

### Exchange Management
- ✅ Business registration and profiles  
- ✅ Category and subcategory organization
- ✅ Verification system (ID.me and manual)
- ✅ Reviews and ratings
- ✅ Quote requests
- ✅ Appointment scheduling (legacy)
- ✅ **NEW: Advanced Booking System**

### Booking System (NEW) 🎉
A production-ready slot-based booking system with:
- **Relational business hours model** (proper database table, not JSON)
- Dynamic time slot generation
- Smart capacity management
- No double-booking (database constraints)
- Complete booking lifecycle
- RESTful API endpoints
- Admin dashboard

> **Note:** Business hours are managed separately via the BusinessHours model (with proper relations), not through the Exchange.business_hours JSON field.

**Quick Links:**
- 📖 [API Documentation](docs/BOOKING_SYSTEM_API.md)
- 📚 [Complete Guide](docs/BOOKING_SYSTEM_README.md)
- 🚀 [Quick Start](docs/BOOKING_QUICK_START.md)
- 📋 [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)
- 🎯 [Create Exchange with Business Hours](docs/CREATE_EXCHANGE_WITH_BUSINESS_HOURS.md) ⭐

## Project Structure

```
exchange/
├── models/
│   ├── exchange.py          # Main exchange model
│   ├── category.py          # Categories and subcategories
│   ├── review.py            # Reviews
│   ├── appointment.py       # Legacy appointments
│   ├── quote.py             # Quote requests
│   ├── business_hours.py    # 🆕 Operating hours
│   └── booking.py           # 🆕 Time slots & bookings
├── api/
│   ├── serializers/
│   │   ├── exchange.py
│   │   ├── category.py
│   │   └── booking.py       # 🆕 Booking serializers
│   ├── views/
│   │   ├── exchange.py
│   │   ├── category.py
│   │   ├── admin.py
│   │   └── booking.py       # 🆕 Booking viewsets
│   ├── urls.py              # API routing
│   └── booking_utils.py     # 🆕 Helper functions
├── docs/
│   ├── BOOKING_SYSTEM_API.md           # 🆕 Complete API docs
│   ├── BOOKING_SYSTEM_README.md        # 🆕 Full guide
│   ├── BOOKING_QUICK_START.md          # 🆕 Quick start
│   └── IMPLEMENTATION_SUMMARY.md       # 🆕 Summary
├── migrations/
└── admin.py                 # Django admin configuration
```

## API Endpoints

### Exchange & Categories
- `/api/exchange/` - Exchange CRUD
- `/api/category/` - Categories
- `/api/subcategory/` - Subcategories
- `/api/exchange-reviews/` - Reviews
- `/api/appointments/` - Legacy appointments
- `/api/quotes/` - Quote requests

### Booking System (NEW)
- `/api/business-hours/` - Business hours management
- `/api/time-slots/` - Time slot management
- `/api/bookings/` - Booking operations

See [BOOKING_SYSTEM_API.md](docs/BOOKING_SYSTEM_API.md) for complete API documentation.

## Getting Started

### 1. Apply Migrations

```bash
python manage.py migrate
```

### 2. Create an Exchange

Via admin panel or API. You can now include business hours directly:

```json
POST /api/exchange/
{
  "business_name": "ABC Services",
  "seller_type": "vendor",
  "email": "contact@abc.com",
  "phone": "+1234567890",
  "operating_hours": [
    {"day_of_week": 0, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 1, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 2, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 3, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 4, "open_time": "09:00", "close_time": "17:00"},
    {"day_of_week": 5, "is_closed": true},
    {"day_of_week": 6, "is_closed": true}
  ]
}
```

See [CREATE_EXCHANGE_WITH_BUSINESS_HOURS.md](docs/CREATE_EXCHANGE_WITH_BUSINESS_HOURS.md) for complete documentation.

### 3. Set Up Booking System (Optional)

See [BOOKING_QUICK_START.md](docs/BOOKING_QUICK_START.md) for detailed setup.

**Quick version:**

```python
from exchange.api.booking_utils import create_recurring_business_hours, generate_time_slots_for_exchange
from exchange.models import Exchange
from datetime import date

# Get exchange
exchange = Exchange.objects.get(business_name="ABC Services")

# Create business hours (Mon-Fri 9-5)
hours = create_recurring_business_hours(exchange, template='weekday_9to5')

# Generate time slots for next month
result = generate_time_slots_for_exchange(
    exchange=exchange,
    start_date=date(2024, 1, 20),
    end_date=date(2024, 2, 20),
    slot_duration_minutes=30,
    max_capacity=1
)

print(f"Created {result['created']} time slots!")
```

## Models Overview

### Exchange
Main business profile with contact info, media, verification status, etc.

### Category & SubCategory
Organizational hierarchy for exchanges.

### ExchangeReview
User reviews and ratings for exchanges.

### ExchangeQuote
Quote requests from users to exchanges.

### ExchangeAppointment
Legacy appointment system (consider migrating to new booking system).

### BusinessHours (NEW)
Operating hours configuration per day of week.

### TimeSlot (NEW)
Available booking slots with capacity management.

### Booking (NEW)
User bookings with complete lifecycle tracking.

## Admin Interface

Access at: `/admin/exchange/`

### Available Sections:
- **Exchanges** - Manage all registered businesses
- **Categories** - Organize exchange types
- **Reviews** - Moderate user reviews
- **Appointments** - View legacy appointments
- **Quotes** - Manage quote requests
- **Business Hours** 🆕 - Set operating hours
- **Time Slots** 🆕 - Manage available slots
- **Bookings** 🆕 - Handle user bookings

### Bulk Actions:
- Approve/reject exchanges
- Confirm/complete bookings
- Mark no-shows
- Update availability

## Usage Examples

### Frontend Integration

#### Display Available Slots
```javascript
const slots = await fetch(
  `/api/time-slots/available_slots/?exchange=${id}&date_from=2024-01-20&date_to=2024-01-27`
);
const data = await slots.json();

// data.slots organized by date
Object.entries(data.slots).forEach(([date, slots]) => {
  console.log(`${date}: ${slots.length} slots available`);
});
```

#### Create a Booking
```javascript
const booking = await fetch('/api/bookings/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    time_slot: slotId,
    customer_name: "John Doe",
    customer_email: "john@example.com",
    customer_phone: "+1234567890",
    notes: "First visit"
  })
});
```

## Testing

### Run Tests
```bash
python manage.py test exchange
```

### Manual Testing Checklist

Exchange Management:
- [ ] Create exchange via API
- [ ] Update exchange details
- [ ] Upload business logo
- [ ] Add preview images
- [ ] Submit for verification

Booking System:
- [ ] Create business hours
- [ ] Generate time slots
- [ ] View available slots
- [ ] Create booking
- [ ] Cancel booking
- [ ] Verify capacity updates

## Best Practices

### For Exchange Owners
1. Keep business hours up to date
2. Generate slots regularly (weekly/monthly)
3. Respond to bookings promptly
4. Use admin notes for internal tracking
5. Monitor booking statistics

### For Developers
1. Use utility functions from `booking_utils.py`
2. Leverage database indexes for queries
3. Handle race conditions (concurrent bookings)
4. Implement proper error handling
5. Use transactions for critical operations

### For Frontend Integration
1. Show loading states during booking
2. Display clear error messages
3. Refresh slot availability after booking
4. Implement optimistic UI updates
5. Handle booking conflicts gracefully

## Performance Considerations

- Use date range filters to limit queries
- Implement pagination for large result sets
- Cache available slots for popular exchanges
- Use select_related/prefetch_related
- Monitor slow queries with Django Debug Toolbar

## Security

- All booking endpoints require authentication
- Users can only view/cancel their own bookings
- Exchange owners can view their exchange's bookings
- Admin actions restricted by permissions
- Input validation at multiple layers
- Database constraints prevent data corruption

## Migration Path

### From Legacy Appointments to New Booking System

If you're using `ExchangeAppointment`, consider migrating:

1. **Advantages of new system:**
   - Proper capacity management
   - No double booking
   - Better availability tracking
   - More flexible time management
   - Richer API

2. **Migration steps:**
   - Set up business hours
   - Generate time slots
   - Migrate existing appointments to bookings
   - Update frontend to use new endpoints
   - Gradually phase out old system

## Troubleshooting

### Common Issues

**"No business hours configured"**
→ Create business hours first before generating slots

**"Slot is fully booked"**
→ Increase max_capacity or generate more slots

**"Cannot book past slot"**
→ Check date/time, generate future slots

**Capacity not updating**
→ Use model methods, not direct queryset updates

See [BOOKING_SYSTEM_README.md](docs/BOOKING_SYSTEM_README.md) for detailed troubleshooting.

## Future Enhancements

Planned features:
- [ ] Email notifications for bookings
- [ ] SMS reminders
- [ ] Calendar export (iCal)
- [ ] Waiting list functionality
- [ ] Holiday management
- [ ] Recurring bookings
- [ ] Payment integration
- [ ] Analytics dashboard
- [ ] Mobile app support

## Contributing

When adding features:
1. Update models with proper validation
2. Create/update serializers
3. Add API endpoints
4. Write tests
5. Update documentation
6. Update admin interface

## Support

- **Booking System**: See [docs/](docs/) folder
- **General Exchange**: Check model docstrings
- **API**: Review [BOOKING_SYSTEM_API.md](docs/BOOKING_SYSTEM_API.md)
- **Quick Start**: See [BOOKING_QUICK_START.md](docs/BOOKING_QUICK_START.md)

## License

Same as parent project.

---

**Status**: ✅ Production Ready

The booking system is fully implemented, tested, and documented. All core features are operational and ready for use.
