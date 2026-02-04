# Admin Login Quick Test Guide

## Make Your User an Admin

Run this in Django shell to grant admin privileges to your user:

```bash
# Open Django shell
python manage.py shell

# Then run:
from accounts.models import User

user = User.objects.get(email='baberibrar@gmail.com')
user.is_staff = True
user.is_superuser = True
user.save()

print(f"User {user.email} is now an admin!")
print(f"is_staff: {user.is_staff}")
print(f"is_superuser: {user.is_superuser}")
```

## Test the Endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "baberibrar@gmail.com",
    "password": "12345678"
  }'
```

## Expected Response

```json
{
  "success": true,
  "message": "Admin logged in successfully",
  "data": {
    "uuid": "...",
    "email": "baberibrar@gmail.com",
    "is_staff": true,
    "is_superuser": true,
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

## Alternative: Create a New Superuser

```bash
python manage.py createsuperuser
# Follow the prompts to create a new admin user
```
