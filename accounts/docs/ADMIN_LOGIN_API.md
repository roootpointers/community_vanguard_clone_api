# Admin Login API Documentation

## Endpoint

```
POST /api/accounts/admin-login/
```

## Description

This endpoint allows administrators (users with `is_staff=True` or `is_superuser=True`) to login and receive JWT access and refresh tokens. Regular users without admin privileges will be denied access.

---

## Request

### Headers
```
Content-Type: application/json
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| email | string | Yes | Admin user's email address |
| password | string | Yes | Admin user's password |

### Example Request

```json
{
  "email": "baberibrar@gmail.com",
  "password": "12345678"
}
```

### cURL Example

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "baberibrar@gmail.com",
    "password": "12345678"
  }'
```

---

## Response

### Success Response (200 OK)

When admin login is successful:

```json
{
  "success": true,
  "message": "Admin logged in successfully",
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "email": "baberibrar@gmail.com",
    "full_name": "Admin User",
    "account_type": "email",
    "is_profile": true,
    "is_role": true,
    "is_active": true,
    "is_staff": true,
    "is_superuser": true,
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-12-03T14:20:00Z"
  }
}
```

### Error Responses

#### 400 Bad Request - Invalid Credentials

```json
{
  "success": false,
  "message": "Invalid credentials.",
  "errors": {
    "error": ["Incorrect password."]
  }
}
```

#### 403 Forbidden - No Admin Privileges

When user exists but doesn't have admin privileges:

```json
{
  "success": false,
  "message": "Access denied. Admin privileges required.",
  "errors": {
    "error": ["Access denied. Admin privileges required."]
  }
}
```

#### 404 Not Found - User Does Not Exist

```json
{
  "success": false,
  "message": "User not found.",
  "errors": {
    "email": ["User does not exist."]
  }
}
```

#### 400 Bad Request - Account Deactivated

```json
{
  "success": false,
  "message": "Invalid credentials.",
  "errors": {
    "error": ["User account is deactivated."]
  }
}
```

#### 400 Bad Request - Validation Errors

```json
{
  "success": false,
  "message": "Invalid credentials.",
  "errors": {
    "email": ["This field is required."],
    "password": ["This field is required."]
  }
}
```

---

## Authentication Flow

1. **Submit Credentials**: User submits email and password
2. **Validate Email**: Check if user exists with provided email
3. **Validate Password**: Verify password is correct
4. **Check Active Status**: Ensure account is active
5. **Verify Admin Privileges**: Check if user has `is_staff=True` or `is_superuser=True`
6. **Generate Tokens**: Create JWT access and refresh tokens
7. **Return Response**: Send user data with tokens

---

## Security Features

- ✅ Password verification using Django's secure password hashing
- ✅ Email case-insensitive lookup
- ✅ Active account verification
- ✅ Admin privilege verification (is_staff or is_superuser)
- ✅ JWT token-based authentication
- ✅ Detailed error logging
- ✅ Separate endpoint from regular user login

---

## Differences from Regular Login

| Feature | Regular Login | Admin Login |
|---------|--------------|-------------|
| Endpoint | `/api/accounts/email-login/` | `/api/accounts/admin-login/` |
| Access | All users | Only staff/superusers |
| Response | User data + tokens | User data + tokens + admin flags |
| Error (non-admin) | N/A | 403 Forbidden |

---

## Admin Privilege Requirements

A user must have **at least one** of the following:

- `is_staff = True` (Can access Django admin)
- `is_superuser = True` (Has all permissions)

### How to Make a User an Admin

**Via Django Admin:**
1. Login to Django admin: `/admin/`
2. Go to Users
3. Edit the user
4. Check "Staff status" or "Superuser status"
5. Save

**Via Django Shell:**
```python
from accounts.models import User

user = User.objects.get(email='baberibrar@gmail.com')
user.is_staff = True  # For staff access
# OR
user.is_superuser = True  # For superuser access
user.save()
```

**Via Management Command (create superuser):**
```bash
python manage.py createsuperuser
```

---

## Token Usage

### Using Access Token in Subsequent Requests

Include the access token in the Authorization header:

```bash
curl -X GET http://127.0.0.1:8000/api/some-endpoint/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Refreshing Tokens

Use the refresh token to get a new access token when it expires:

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

## Testing

### Test with Valid Admin

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "baberibrar@gmail.com",
    "password": "12345678"
  }'
```

### Test with Regular User (Should Fail)

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "regularuser@example.com",
    "password": "password123"
  }'
```

Expected: `403 Forbidden - Access denied. Admin privileges required.`

### Test with Invalid Password

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "baberibrar@gmail.com",
    "password": "wrongpassword"
  }'
```

Expected: `400 Bad Request - Incorrect password.`

---

## Common Issues

### Issue: "Access denied. Admin privileges required."

**Cause:** User exists but doesn't have admin privileges.

**Solution:** 
```python
user = User.objects.get(email='youremail@example.com')
user.is_staff = True
user.save()
```

### Issue: "User not found."

**Cause:** No user exists with that email.

**Solution:** Create the user or verify the email is correct.

### Issue: "User account is deactivated."

**Cause:** User has `is_active=False`.

**Solution:**
```python
user = User.objects.get(email='youremail@example.com')
user.is_active = True
user.save()
```

---

## Related Endpoints

- **Regular User Login**: `POST /api/accounts/email-login/`
- **Social Login**: `POST /api/accounts/social-login/`
- **Token Refresh**: `POST /api/token/refresh/`
- **Change Password**: `POST /api/accounts/update-password/`

---

**Created:** December 3, 2025  
**Version:** 1.0
