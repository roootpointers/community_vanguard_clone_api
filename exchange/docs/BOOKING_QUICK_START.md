# Booking System - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Run Migrations

```bash
python manage.py makemigrations exchange
python manage.py migrate
```

### Step 2: Create Business Hours

Business hours are managed as a **separate relational model**, not in the Exchange JSON field.

**Via API (Bulk Create):**
```bash
POST /api/business-hours/bulk_create/

{
  "exchange": "your-exchange-uuid",
  "hours": [
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

**Via Django Admin:**
1. Go to Exchange > Business Hours
2. Add business hours for each day
3. Mark weekends as closed if needed

**Via Django Shell:**
```python
from exchange.models import Exchange, BusinessHours
from datetime import time

exchange = Exchange.objects.first()  # or get your exchange

# Create Monday-Friday 9-5
for day in range(5):  # 0-4 (Mon-Fri)
    BusinessHours.objects.create(
        exchange=exchange,
        day_of_week=day,
        open_time=time(9, 0),
        close_time=time(17, 0),
        is_closed=False
    )

# Mark weekend as closed
for day in [5, 6]:  # Saturday, Sunday
    BusinessHours.objects.create(
        exchange=exchange,
        day_of_week=day,
        is_closed=True
    )
```

### Step 3: Generate Time Slots

Use the API or shell:

**Via API (Recommended):**
```bash
POST /api/time-slots/generate_slots/

{
  "exchange_uuid": "your-exchange-uuid",
  "start_date": "2024-01-20",
  "end_date": "2024-02-20",
  "slot_duration_minutes": 30,
  "max_capacity": 1
}
```

**Via Shell:**
```python
from exchange.api.booking_utils import generate_time_slots_for_exchange
from datetime import date

result = generate_time_slots_for_exchange(
    exchange=exchange,
    start_date=date(2024, 1, 20),
    end_date=date(2024, 2, 20),
    slot_duration_minutes=30,
    max_capacity=1
)

print(f"✅ Created {result['created']} slots!")
```

### Step 4: Test a Booking

```python
from exchange.models import Booking
from accounts.models import User

user = User.objects.first()
slot = TimeSlot.objects.filter(is_available=True).first()

booking = Booking.objects.create(
    user=user,
    exchange=exchange,
    time_slot=slot,
    customer_name="John Doe",
    customer_email="john@example.com",
    customer_phone="+1234567890",
    notes="Test booking"
)

print(f"✅ Booking created: {booking.uuid}")
print(f"Slot capacity: {slot.current_bookings}/{slot.max_capacity}")
```

---

## 📋 Common Tasks

### View Available Slots
```python
from exchange.api.booking_utils import get_available_slots_for_date_range
from datetime import date

slots = get_available_slots_for_date_range(
    exchange=exchange,
    start_date=date(2024, 1, 20),
    end_date=date(2024, 1, 27)
)

for slot in slots:
    print(f"{slot.date} {slot.start_time} - {slot.end_time}")
```

### Cancel a Booking
```python
booking.cancel(reason="Schedule conflict")
print(f"✅ Booking cancelled. Slot capacity: {slot.current_bookings}/{slot.max_capacity}")
```

### Get User's Upcoming Bookings
```python
from exchange.api.booking_utils import get_user_upcoming_bookings

upcoming = get_user_upcoming_bookings(user, days_ahead=30)
for booking in upcoming:
    print(f"{booking.time_slot.date} at {booking.time_slot.start_time}")
```

### Get Booking Statistics
```python
from exchange.api.booking_utils import get_booking_statistics

stats = get_booking_statistics(exchange)
print(stats)
# {'total': 10, 'pending': 3, 'confirmed': 5, 'completed': 1, 'cancelled': 1, 'no_show': 0}
```

---

## 🔧 Using Templates for Business Hours

```python
from exchange.api.booking_utils import create_recurring_business_hours

# Create weekday 9-5 hours
hours = create_recurring_business_hours(exchange, template='weekday_9to5')
print(f"✅ Created {len(hours)} business hours!")

# Available templates:
# - 'weekday_9to5': Mon-Fri 9 AM - 5 PM
# - 'weekday_9to6': Mon-Fri 9 AM - 6 PM
# - 'seven_days': All days 9 AM - 5 PM
```

---

## 🌐 API Examples

### 1. Get Available Slots (Frontend)

```javascript
const response = await fetch(
  `/api/time-slots/available_slots/?exchange=${exchangeId}&date_from=2024-01-20&date_to=2024-01-27`
);
const data = await response.json();

// Display slots grouped by date
Object.entries(data.slots).forEach(([date, slots]) => {
  console.log(`${date}:`);
  slots.forEach(slot => {
    console.log(`  ${slot.start_time} - ${slot.end_time}`);
  });
});
```

### 2. Create a Booking

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

const result = await booking.json();
console.log('Booking created:', result.uuid);
```

### 3. View My Bookings

```javascript
const response = await fetch('/api/bookings/upcoming/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const bookings = await response.json();

bookings.forEach(booking => {
  console.log(
    `${booking.time_slot_details.date} at ${booking.time_slot_details.start_time} - ${booking.exchange_name}`
  );
});
```

### 4. Cancel a Booking

```javascript
await fetch(`/api/bookings/${bookingId}/cancel/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    cancellation_reason: "Can't make it"
  })
});
```

---

## 📊 Admin Dashboard

Access at: `/admin/exchange/`

**Quick Actions:**
- **Business Hours** → Set operating hours
- **Time Slots** → View/manage all slots
- **Bookings** → View/manage all bookings

**Bulk Operations:**
- Confirm multiple bookings
- Mark bookings as completed
- Mark no-shows

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Business hours created for your exchange
- [ ] Time slots generated successfully
- [ ] Can create a booking via API
- [ ] Slot capacity decrements after booking
- [ ] Can cancel a booking
- [ ] Slot capacity increments after cancellation
- [ ] Cannot book past slots
- [ ] Cannot double-book same slot
- [ ] Upcoming bookings endpoint works
- [ ] Admin panel shows all bookings

---

## 🆘 Troubleshooting

### "No business hours configured"
→ Create business hours first (see Step 2)

### "This time slot is no longer available"
→ Slot is fully booked or marked unavailable

### "Cannot book a time slot in the past"
→ Generate future slots or check date format

### Capacity not updating
→ Ensure using `booking.cancel()` method, not direct status update

---

## 📚 More Information

- **Full API Documentation**: `BOOKING_SYSTEM_API.md`
- **Complete README**: `BOOKING_SYSTEM_README.md`
- **Model Reference**: Check model docstrings in `models/`

---

## 🎯 Next Steps

1. **Customize** business hours for your needs
2. **Generate** slots for the next month
3. **Test** the booking flow end-to-end
4. **Integrate** with your frontend
5. **Set up** automated slot generation (cron job)
6. **Configure** email notifications (optional)

---

## 💡 Pro Tips

- Generate slots 1-4 weeks at a time
- Use different `slot_duration_minutes` for different services
- Set `max_capacity > 1` for group bookings
- Regularly run `cancel_expired_pending_bookings()` utility
- Monitor booking statistics for insights
- Use Django admin for quick management

---

**Happy Booking! 🎉**
