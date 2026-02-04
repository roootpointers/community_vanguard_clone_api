# Password Management Endpoints - Quick Reference

## Overview
Two separate password endpoints are available for different use cases.

---

## 1. Update Password (For Logged-In Users) ⭐ RECOMMENDED

**Endpoint:** `POST /api/accounts/update-password/`

**Authentication:** Required (JWT Token)

**Purpose:** Allow authenticated users to change their password securely

**Request Body:**
```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword456",
  "confirm_password": "NewPassword456"
}
```

**Features:**
- ✅ Requires authentication
- ✅ Verifies current password
- ✅ Django password validation
- ✅ Prevents password reuse
- ✅ Secure and recommended

**Use For:**
- User settings/profile password change
- Security-conscious password updates
- Logged-in user password rotation

---

## 2. Change Password (Legacy/Reset Flow)

**Endpoint:** `POST /api/accounts/change-password/`

**Authentication:** Not required

**Purpose:** Password reset flow (requires email verification)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "NewPassword123",
  "confirm_password": "NewPassword123"
}
```

**Features:**
- ❌ No authentication required
- ❌ No current password verification
- ⚠️ Less secure
- ℹ️ Assumes email verification done separately

**Use For:**
- Password reset flows
- Forgot password scenarios
- Initial password setup

---

## Comparison Table

| Feature | Update Password (NEW) | Change Password (OLD) |
|---------|----------------------|----------------------|
| **Endpoint** | `/api/accounts/update-password/` | `/api/accounts/change-password/` |
| **Method** | POST | POST |
| **Authentication** | Required ✅ | Not required ❌ |
| **Current Password** | Verified ✅ | Not required ❌ |
| **User From** | JWT Token | Email field |
| **Security Level** | High 🔒 | Medium ⚠️ |
| **Use Case** | Settings page | Password reset |
| **Validation** | Django validators | Basic matching |
| **Prevent Reuse** | Yes ✅ | No ❌ |

---

## When to Use Which?

### Use `update-password` when:
- ✅ User is logged in
- ✅ Changing password in settings/profile
- ✅ User knows their current password
- ✅ High security required

### Use `change-password` when:
- ⚠️ Password reset flow
- ⚠️ Forgot password scenario
- ⚠️ Email verification already done
- ⚠️ User doesn't know current password

---

## Example Usage

### Update Password (Authenticated)
```javascript
// User Settings Page
const response = await fetch(
  'http://localhost:8000/api/accounts/update-password/',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      current_password: 'CurrentPass123',
      new_password: 'NewSecurePass456',
      confirm_password: 'NewSecurePass456'
    })
  }
);
```

### Change Password (Reset Flow)
```javascript
// Forgot Password Flow (after email verification)
const response = await fetch(
  'http://localhost:8000/api/accounts/change-password/',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: 'user@example.com',
      password: 'NewPassword123',
      confirm_password: 'NewPassword123'
    })
  }
);
```

---

## Security Recommendations

1. **Always prefer `update-password`** for authenticated users
2. **Add email verification** before allowing `change-password`
3. **Implement rate limiting** on both endpoints
4. **Send email notifications** when password changes
5. **Invalidate sessions** after password change (optional)
6. **Log all attempts** for security auditing

---

## Documentation

- **Update Password:** `accounts/docs/UPDATE_PASSWORD_API.md`
- **Change Password:** Use existing endpoint documentation

---

## Testing

```bash
# Test Update Password (with auth)
curl -X POST \
  "http://localhost:8000/api/accounts/update-password/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPassword123",
    "new_password": "NewPassword456",
    "confirm_password": "NewPassword456"
  }'

# Test Change Password (no auth)
curl -X POST \
  "http://localhost:8000/api/accounts/change-password/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "NewPassword123",
    "confirm_password": "NewPassword123"
  }'
```
