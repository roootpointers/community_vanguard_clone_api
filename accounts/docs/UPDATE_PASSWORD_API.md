# Update Password API (Authenticated Users)

## Overview
This endpoint allows authenticated users to update their password by verifying their current password first. This is the recommended endpoint for logged-in users to change their password securely.

## Endpoint Details

### Update Password
Update password for the currently authenticated user.

**Endpoint:** `POST /api/accounts/update-password/`

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "current_password": "string (required)",
  "new_password": "string (required)",
  "confirm_password": "string (required)"
}
```

---

## Request Example

### Update Password
```http
POST /api/accounts/update-password/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "current_password": "Mikeynolds1999",
  "new_password": "Mikeynold1534",
  "confirm_password": "Mikeynold1534"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Password updated successfully.",
  "data": {
    "email": "mike.reynolds@example.com",
    "full_name": "Mike Reynolds"
  }
}
```

---

## Validation Rules

### Current Password
- ✅ Must be provided
- ✅ Must match the user's current password
- ❌ Error if incorrect: "Current password is incorrect."

### New Password
- ✅ Must be provided
- ✅ Must pass Django's password validators:
  - Minimum 8 characters
  - Not too similar to user information
  - Not a commonly used password
  - Not entirely numeric
- ✅ Must be different from current password
- ❌ Error if same as current: "New password must be different from current password."

### Confirm Password
- ✅ Must be provided
- ✅ Must match new_password exactly
- ❌ Error if mismatch: "New password and confirm password do not match."

---

## Response Fields

### Success Response (200 OK)

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` for successful requests |
| `message` | string | "Password updated successfully." |
| `data` | object | User information |
| `data.email` | string | User's email address |
| `data.full_name` | string | User's full name |

---

## Error Responses

### Current Password Incorrect
**Status Code:** `400 BAD REQUEST`

```json
{
  "success": false,
  "message": "Password update failed.",
  "errors": {
    "current_password": [
      "Current password is incorrect."
    ]
  }
}
```

### Passwords Don't Match
**Status Code:** `400 BAD REQUEST`

```json
{
  "success": false,
  "message": "Password update failed.",
  "errors": {
    "confirm_password": [
      "New password and confirm password do not match."
    ]
  }
}
```

### New Password Same as Current
**Status Code:** `400 BAD REQUEST`

```json
{
  "success": false,
  "message": "Password update failed.",
  "errors": {
    "new_password": [
      "New password must be different from current password."
    ]
  }
}
```

### Weak Password
**Status Code:** `400 BAD REQUEST`

```json
{
  "success": false,
  "message": "Password update failed.",
  "errors": {
    "new_password": [
      "This password is too short. It must contain at least 8 characters.",
      "This password is too common."
    ]
  }
}
```

### Authentication Required
**Status Code:** `401 UNAUTHORIZED`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Invalid Token
**Status Code:** `401 UNAUTHORIZED`

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

### Server Error
**Status Code:** `500 INTERNAL SERVER ERROR`

```json
{
  "success": false,
  "message": "An error occurred while updating password.",
  "error": "Error details..."
}
```

---

## Security Features

1. ✅ **Authentication Required:** Only logged-in users can update password
2. ✅ **Current Password Verification:** Must provide correct current password
3. ✅ **Password Validation:** Uses Django's built-in password validators
4. ✅ **No Reuse:** New password must be different from current password
5. ✅ **Password Hashing:** Passwords are securely hashed with `set_password()`
6. ✅ **Logging:** All password update attempts are logged

---

## Use Cases

1. **User Profile Settings:** Allow users to change their password from settings page
2. **Security Update:** Users can update password for security reasons
3. **Post-Breach:** Users can quickly change password if account compromised
4. **Regular Rotation:** Support password rotation policies

---

## Comparison with Change Password Endpoint

| Feature | `/api/accounts/update-password/` (NEW) | `/api/accounts/change-password/` (OLD) |
|---------|----------------------------------------|----------------------------------------|
| **Authentication** | Required ✅ | Not required ❌ |
| **Current Password** | Verified ✅ | Not required ❌ |
| **Use Case** | Logged-in users | Password reset flow |
| **Security** | High 🔒 | Medium ⚠️ |
| **User Identification** | From JWT token | From email field |

**Recommendation:** Use `/api/accounts/update-password/` for authenticated users changing their password in settings.

---

## Example Implementation

### JavaScript/Fetch API
```javascript
async function updatePassword(token, currentPassword, newPassword, confirmPassword) {
  const response = await fetch(
    'http://localhost:8000/api/accounts/update-password/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
      })
    }
  );
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Password updated successfully!');
    // Optionally redirect to login or show success message
  } else {
    console.error('Password update failed:', data.errors);
    // Show validation errors to user
  }
  
  return data;
}

// Usage
const token = 'your-jwt-token';
updatePassword(token, 'OldPassword123', 'NewPassword456', 'NewPassword456');
```

### React Example with Form Validation
```javascript
import { useState } from 'react';

function ChangePasswordForm({ userToken }) {
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setSuccess(false);

    try {
      const response = await fetch(
        'http://localhost:8000/api/accounts/update-password/',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${userToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        }
      );

      const data = await response.json();

      if (data.success) {
        setSuccess(true);
        setFormData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
        // Optionally logout user and redirect to login
        setTimeout(() => {
          // Redirect or logout
        }, 2000);
      } else {
        setErrors(data.errors);
      }
    } catch (error) {
      console.error('Error:', error);
      setErrors({ general: 'An error occurred. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Change Password</h2>
      
      {success && (
        <div className="success-message">
          Password updated successfully!
        </div>
      )}

      <div className="form-group">
        <label>Current Password</label>
        <input
          type="password"
          name="current_password"
          value={formData.current_password}
          onChange={handleChange}
          required
        />
        {errors.current_password && (
          <span className="error">{errors.current_password[0]}</span>
        )}
      </div>

      <div className="form-group">
        <label>New Password</label>
        <input
          type="password"
          name="new_password"
          value={formData.new_password}
          onChange={handleChange}
          required
        />
        {errors.new_password && (
          <span className="error">{errors.new_password[0]}</span>
        )}
      </div>

      <div className="form-group">
        <label>Confirm Password</label>
        <input
          type="password"
          name="confirm_password"
          value={formData.confirm_password}
          onChange={handleChange}
          required
        />
        {errors.confirm_password && (
          <span className="error">{errors.confirm_password[0]}</span>
        )}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Updating...' : 'Save Changes'}
      </button>
    </form>
  );
}
```

---

## Testing with cURL

### Successful Update
```bash
curl -X POST \
  "http://localhost:8000/api/accounts/update-password/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPassword123",
    "new_password": "NewPassword456",
    "confirm_password": "NewPassword456"
  }'
```

### Test Incorrect Current Password
```bash
curl -X POST \
  "http://localhost:8000/api/accounts/update-password/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "WrongPassword",
    "new_password": "NewPassword456",
    "confirm_password": "NewPassword456"
  }'
```

### Test Password Mismatch
```bash
curl -X POST \
  "http://localhost:8000/api/accounts/update-password/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPassword123",
    "new_password": "NewPassword456",
    "confirm_password": "DifferentPassword789"
  }'
```

---

## Testing with Postman

1. **Create New Request**
   - Method: `POST`
   - URL: `http://localhost:8000/api/accounts/update-password/`

2. **Set Authorization**
   - Type: `Bearer Token`
   - Token: Your JWT access token

3. **Set Request Body**
   - Type: `raw`
   - Format: `JSON`
   ```json
   {
     "current_password": "Mikeynolds1999",
     "new_password": "Mikeynold1534",
     "confirm_password": "Mikeynold1534"
   }
   ```

4. **Send Request**
   - Click "Send"
   - Check response for success or validation errors

---

## Best Practices

1. **Clear Form on Success:** Clear all password fields after successful update
2. **Show Validation Errors:** Display field-specific errors to users
3. **Password Strength Indicator:** Show real-time password strength
4. **Confirm Before Submit:** Add a confirmation dialog for important action
5. **Logout After Change:** Consider logging out user after password change
6. **Success Feedback:** Show clear success message to user
7. **Password Requirements:** Display password requirements before user types

---

## Related Endpoints

- `POST /api/accounts/email-login/` - Login with new password
- `POST /api/accounts/change-password/` - Old password change (no auth required)
- `GET /api/profile/` - View user profile
- `PUT /api/profile/` - Update user profile

---

## Notes

- **Session Security:** After password change, consider invalidating all existing tokens/sessions
- **Email Notification:** Consider sending email notification about password change
- **Audit Log:** All password updates are logged for security auditing
- **Token Expiry:** JWT tokens remain valid until expiry even after password change
- **Password Validators:** Customize validators in Django settings if needed
