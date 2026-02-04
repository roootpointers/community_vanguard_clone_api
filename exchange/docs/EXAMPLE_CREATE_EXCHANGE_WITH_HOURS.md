# Complete Example: Create Exchange with Business Hours

## Simple cURL Example

Create an exchange with business hours in a single request:

```bash
curl -X POST http://localhost:8000/exchange/api/exchanges/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "ABC Services",
    "seller_type": "veteran-owned",
    "email": "contact@abcservices.com",
    "phone": "+1234567890",
    "address": "123 Main St, City, State 12345",
    "mission_statement": "Providing quality services to our community",
    "business_hours": {
      "monday": {"open_time": "09:00", "close_time": "17:00"},
      "tuesday": {"open_time": "09:00", "close_time": "17:00"},
      "wednesday": {"open_time": "09:00", "close_time": "17:00"},
      "thursday": {"open_time": "09:00", "close_time": "17:00"},
      "friday": {"open_time": "09:00", "close_time": "17:00"},
      "saturday": {"is_closed": true},
      "sunday": {"is_closed": true}
    },
    "operating_hours": [
      {"day_of_week": 0, "open_time": "09:00", "close_time": "17:00"},
      {"day_of_week": 1, "open_time": "09:00", "close_time": "17:00"},
      {"day_of_week": 2, "open_time": "09:00", "close_time": "17:00"},
      {"day_of_week": 3, "open_time": "09:00", "close_time": "17:00"},
      {"day_of_week": 4, "open_time": "09:00", "close_time": "17:00"},
      {"day_of_week": 5, "is_closed": true},
      {"day_of_week": 6, "is_closed": true}
    ]
  }'
```

## Python Requests Example

```python
import requests

# Configuration
API_URL = "http://localhost:8000/exchange/api/exchanges/"
TOKEN = "YOUR_TOKEN_HERE"

# Request headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Exchange data with business hours
exchange_data = {
    "business_name": "Tech Repair Shop",
    "seller_type": "veteran-owned",
    "email": "info@techrepair.com",
    "phone": "+15551234567",
    "address": "456 Tech Ave, San Francisco, CA 94102",
    "mission_statement": "Expert electronics repair with fast turnaround",
    "website": "https://techrepair.com",
    
    # JSON business hours (for display)
    "business_hours": {
        "monday": {"open_time": "10:00", "close_time": "18:00"},
        "tuesday": {"open_time": "10:00", "close_time": "18:00"},
        "wednesday": {"open_time": "10:00", "close_time": "18:00"},
        "thursday": {"open_time": "10:00", "close_time": "18:00"},
        "friday": {"open_time": "10:00", "close_time": "18:00"},
        "saturday": {"open_time": "10:00", "close_time": "15:00"},
        "sunday": {"is_closed": True}
    },
    
    # Relational business hours (for booking system)
    "operating_hours": [
        {"day_of_week": 0, "open_time": "10:00", "close_time": "18:00"},
        {"day_of_week": 1, "open_time": "10:00", "close_time": "18:00"},
        {"day_of_week": 2, "open_time": "10:00", "close_time": "18:00"},
        {"day_of_week": 3, "open_time": "10:00", "close_time": "18:00"},
        {"day_of_week": 4, "open_time": "10:00", "close_time": "18:00"},
        {"day_of_week": 5, "open_time": "10:00", "close_time": "15:00"},
        {"day_of_week": 6, "is_closed": True}
    ]
}

# Create the exchange
response = requests.post(API_URL, json=exchange_data, headers=headers)

if response.status_code == 201:
    exchange = response.json()
    exchange_uuid = exchange['uuid']
    
    print(f"✅ Exchange created successfully!")
    print(f"   UUID: {exchange_uuid}")
    print(f"   Name: {exchange['business_name']}")
    print(f"   Status: {exchange['status']}")
    
    # Verify business hours were created
    hours_url = f"http://localhost:8000/exchange/api/business-hours/?exchange={exchange_uuid}"
    hours_response = requests.get(hours_url, headers=headers)
    
    if hours_response.status_code == 200:
        hours = hours_response.json()
        print(f"\n✅ Business hours created: {len(hours)} days configured")
        
        for hour in hours:
            if hour['is_closed']:
                print(f"   {hour['day_name']}: Closed")
            else:
                print(f"   {hour['day_name']}: {hour['open_time']} - {hour['close_time']}")
    
else:
    print(f"❌ Error creating exchange: {response.status_code}")
    print(response.json())
```

## JavaScript/Fetch Example

```javascript
// Configuration
const API_URL = 'http://localhost:8000/exchange/api/exchanges/';
const TOKEN = 'YOUR_TOKEN_HERE';

// Exchange data
const exchangeData = {
  business_name: 'Fitness Training Center',
  seller_type: 'vendor',
  email: 'hello@fitnesscenter.com',
  phone: '+15559876543',
  address: '789 Health St, Austin, TX 78701',
  mission_statement: 'Personal training and group fitness classes',
  
  // JSON business hours (for display)
  business_hours: {
    monday: { open_time: '06:00', close_time: '21:00' },
    tuesday: { open_time: '06:00', close_time: '21:00' },
    wednesday: { open_time: '06:00', close_time: '21:00' },
    thursday: { open_time: '06:00', close_time: '21:00' },
    friday: { open_time: '06:00', close_time: '21:00' },
    saturday: { open_time: '08:00', close_time: '18:00' },
    sunday: { open_time: '08:00', close_time: '18:00' }
  },
  
  // Relational business hours (for booking system)
  operating_hours: [
    { day_of_week: 0, open_time: '06:00', close_time: '21:00' },
    { day_of_week: 1, open_time: '06:00', close_time: '21:00' },
    { day_of_week: 2, open_time: '06:00', close_time: '21:00' },
    { day_of_week: 3, open_time: '06:00', close_time: '21:00' },
    { day_of_week: 4, open_time: '06:00', close_time: '21:00' },
    { day_of_week: 5, open_time: '08:00', close_time: '18:00' },
    { day_of_week: 6, open_time: '08:00', close_time: '18:00' }
  ]
};

// Create exchange
async function createExchangeWithHours() {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(exchangeData)
    });

    if (response.ok) {
      const exchange = await response.json();
      console.log('✅ Exchange created successfully!');
      console.log('   UUID:', exchange.uuid);
      console.log('   Name:', exchange.business_name);
      console.log('   Status:', exchange.status);

      // Verify business hours
      const hoursResponse = await fetch(
        `http://localhost:8000/exchange/api/business-hours/?exchange=${exchange.uuid}`,
        { headers: { 'Authorization': `Bearer ${TOKEN}` } }
      );

      if (hoursResponse.ok) {
        const hours = await hoursResponse.json();
        console.log(`\n✅ Business hours created: ${hours.length} days configured`);
        
        hours.forEach(hour => {
          if (hour.is_closed) {
            console.log(`   ${hour.day_name}: Closed`);
          } else {
            console.log(`   ${hour.day_name}: ${hour.open_time} - ${hour.close_time}`);
          }
        });
      }
    } else {
      const error = await response.json();
      console.error('❌ Error:', error);
    }
  } catch (error) {
    console.error('❌ Network error:', error);
  }
}

// Run it
createExchangeWithHours();
```

## React Component Example

```jsx
import React, { useState } from 'react';

const CreateExchangeForm = () => {
  const [formData, setFormData] = useState({
    business_name: '',
    email: '',
    phone: '',
    address: '',
  });

  const [businessHours, setBusinessHours] = useState([
    { day_of_week: 0, day_name: 'Monday', open_time: '09:00', close_time: '17:00', is_closed: false },
    { day_of_week: 1, day_name: 'Tuesday', open_time: '09:00', close_time: '17:00', is_closed: false },
    { day_of_week: 2, day_name: 'Wednesday', open_time: '09:00', close_time: '17:00', is_closed: false },
    { day_of_week: 3, day_name: 'Thursday', open_time: '09:00', close_time: '17:00', is_closed: false },
    { day_of_week: 4, day_name: 'Friday', open_time: '09:00', close_time: '17:00', is_closed: false },
    { day_of_week: 5, day_name: 'Saturday', open_time: '', close_time: '', is_closed: true },
    { day_of_week: 6, day_name: 'Sunday', open_time: '', close_time: '', is_closed: true },
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Prepare operating hours (exclude day_name, handle closed days)
    const operating_hours = businessHours.map(({ day_of_week, open_time, close_time, is_closed }) => {
      if (is_closed) {
        return { day_of_week, is_closed: true };
      }
      return { day_of_week, open_time, close_time, is_closed: false };
    });

    // Prepare business_hours JSON for display
    const business_hours_json = {};
    businessHours.forEach(hour => {
      const dayKey = hour.day_name.toLowerCase();
      if (hour.is_closed) {
        business_hours_json[dayKey] = { is_closed: true };
      } else {
        business_hours_json[dayKey] = {
          open_time: hour.open_time,
          close_time: hour.close_time
        };
      }
    });

    const payload = {
      ...formData,
      seller_type: 'vendor',
      business_hours: business_hours_json,
      operating_hours
    };

    try {
      const response = await fetch('http://localhost:8000/exchange/api/exchanges/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const exchange = await response.json();
        alert(`Exchange created successfully! UUID: ${exchange.uuid}`);
      } else {
        const error = await response.json();
        console.error('Error:', error);
        alert('Failed to create exchange');
      }
    } catch (error) {
      console.error('Network error:', error);
      alert('Network error');
    }
  };

  const updateBusinessHour = (index, field, value) => {
    const updated = [...businessHours];
    updated[index][field] = value;
    setBusinessHours(updated);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Create Exchange</h2>
      
      <input
        type="text"
        placeholder="Business Name"
        value={formData.business_name}
        onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
        required
      />
      
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />
      
      <input
        type="tel"
        placeholder="Phone"
        value={formData.phone}
        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
        required
      />
      
      <input
        type="text"
        placeholder="Address"
        value={formData.address}
        onChange={(e) => setFormData({ ...formData, address: e.target.value })}
      />

      <h3>Business Hours</h3>
      {businessHours.map((hour, index) => (
        <div key={hour.day_of_week} style={{ marginBottom: '10px' }}>
          <label>
            <strong>{hour.day_name}</strong>
            <input
              type="checkbox"
              checked={hour.is_closed}
              onChange={(e) => updateBusinessHour(index, 'is_closed', e.target.checked)}
            />
            Closed
          </label>
          
          {!hour.is_closed && (
            <>
              <input
                type="time"
                value={hour.open_time}
                onChange={(e) => updateBusinessHour(index, 'open_time', e.target.value)}
              />
              <span> to </span>
              <input
                type="time"
                value={hour.close_time}
                onChange={(e) => updateBusinessHour(index, 'close_time', e.target.value)}
              />
            </>
          )}
        </div>
      ))}

      <button type="submit">Create Exchange</button>
    </form>
  );
};

export default CreateExchangeForm;
```

## Expected Response

When you successfully create an exchange with business hours, you'll receive:

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "business_name": "ABC Services",
  "seller_type": "veteran-owned",
  "email": "contact@abcservices.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State 12345",
  "mission_statement": "Providing quality services to our community",
  "business_hours": {
    "monday": {"open_time": "09:00", "close_time": "17:00"},
    "tuesday": {"open_time": "09:00", "close_time": "17:00"},
    "wednesday": {"open_time": "09:00", "close_time": "17:00"},
    "thursday": {"open_time": "09:00", "close_time": "17:00"},
    "friday": {"open_time": "09:00", "close_time": "17:00"},
    "saturday": {"is_closed": true},
    "sunday": {"is_closed": true}
  },
  "status": "under_review",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Verification

To verify business hours were created, query the business hours endpoint:

```bash
curl -X GET "http://localhost:8000/exchange/api/business-hours/?exchange=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
[
  {
    "uuid": "...",
    "day_of_week": 0,
    "day_name": "Monday",
    "open_time": "09:00:00",
    "close_time": "17:00:00",
    "is_closed": false
  },
  {
    "uuid": "...",
    "day_of_week": 1,
    "day_name": "Tuesday",
    "open_time": "09:00:00",
    "close_time": "17:00:00",
    "is_closed": false
  },
  ...
]
```

## Next Steps

After creating an exchange with business hours:

1. **Generate Time Slots**
   ```bash
   curl -X POST http://localhost:8000/exchange/api/time-slots/generate_slots/ \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "exchange_uuid": "550e8400-e29b-41d4-a716-446655440000",
       "start_date": "2024-01-20",
       "end_date": "2024-02-20",
       "slot_duration_minutes": 30,
       "max_capacity": 1
     }'
   ```

2. **Start Accepting Bookings**
   - Slots are now available for booking
   - Users can view available slots
   - Users can create bookings

See [BOOKING_QUICK_START.md](BOOKING_QUICK_START.md) for more details.

## Tips

1. **Keep Both Fields in Sync**: The `business_hours` JSON and `operating_hours` array should have the same data
2. **Use Helper Functions**: Consider creating a helper to convert between formats
3. **Validation**: The API validates both fields independently
4. **Optional Field**: `operating_hours` is optional - you can still create exchanges without it
5. **Day of Week**: Remember 0=Monday, 6=Sunday

## Common Patterns

### Convert JSON to Array Format

```javascript
function businessHoursJsonToArray(jsonHours) {
  const dayMap = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
    'friday': 4, 'saturday': 5, 'sunday': 6
  };
  
  return Object.entries(jsonHours).map(([day, hours]) => ({
    day_of_week: dayMap[day],
    ...hours
  }));
}

const json = {
  monday: { open_time: '09:00', close_time: '17:00' },
  tuesday: { open_time: '09:00', close_time: '17:00' },
  // ... etc
};

const array = businessHoursJsonToArray(json);
// Use this as operating_hours in your request
```

### Convert Array to JSON Format

```javascript
function businessHoursArrayToJson(arrayHours) {
  const dayNames = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
  
  const json = {};
  arrayHours.forEach(hour => {
    const dayName = dayNames[hour.day_of_week];
    if (hour.is_closed) {
      json[dayName] = { is_closed: true };
    } else {
      json[dayName] = {
        open_time: hour.open_time,
        close_time: hour.close_time
      };
    }
  });
  
  return json;
}
```

---

**Ready to create your first exchange with business hours? Pick your preferred language and try the example above!**
