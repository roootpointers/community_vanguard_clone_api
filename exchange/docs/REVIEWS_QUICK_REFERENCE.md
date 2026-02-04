# Exchange Reviews - Quick Reference

## API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/exchange-reviews/` | Submit a review | ✅ Yes |
| GET | `/api/exchange-reviews/` | List all reviews | ❌ No |
| GET | `/api/exchange-reviews/{uuid}/` | Get specific review | ❌ No |
| PATCH | `/api/exchange-reviews/{uuid}/` | Update own review | ✅ Yes |
| DELETE | `/api/exchange-reviews/{uuid}/` | Delete own review | ✅ Yes |
| GET | `/api/exchange-reviews/exchange/{uuid}/` | Get exchange reviews + stats | ❌ No |
| GET | `/api/exchange-reviews/my-reviews/` | Get my reviews | ✅ Yes |

---

## Quick Test Examples

### 1. Submit a Review
```json
POST /api/exchange-reviews/
{
  "exchange": "exchange-uuid",
  "rating": 5,
  "review_text": "Great service!"
}
```

### 2. Get Exchange Reviews with Stats
```
GET /api/exchange-reviews/exchange/{exchange-uuid}/
```

Returns:
- All reviews for the exchange
- Average rating
- Total review count
- Rating breakdown (1-5 stars)

### 3. Update Your Review
```json
PATCH /api/exchange-reviews/{review-uuid}/
{
  "rating": 4,
  "review_text": "Updated review"
}
```

---

## Key Features

✅ **One review per user per exchange**  
✅ **1-5 star rating system**  
✅ **Optional review text (500 chars max)**  
✅ **Users can update/delete their own reviews**  
✅ **Public review viewing**  
✅ **Privacy-protected user info in lists**  
✅ **Real-time statistics calculation**  
✅ **Pagination support**

---

## Database Schema

```
ExchangeReview
├── uuid (Primary Key)
├── exchange (ForeignKey to Exchange)
├── user (ForeignKey to User)
├── rating (Integer 1-5)
├── review_text (Text, max 500 chars)
├── created_at
└── updated_at

Constraints:
- Unique together: (exchange, user)
```

---

## Response Format

### Review Statistics
```json
{
  "average_rating": 4.8,
  "total_reviews": 25,
  "rating_breakdown": {
    "5": 20,
    "4": 3,
    "3": 1,
    "2": 1,
    "1": 0
  }
}
```

### User Privacy (in lists)
```json
{
  "uuid": "user-uuid",
  "full_name": "John Doe",
  "email": "joh***@example.com"  // Masked email
}
```

---

## Common Errors

| Error | Reason | Solution |
|-------|--------|----------|
| Already reviewed | User submitted review before | Update existing review instead |
| Invalid rating | Rating not 1-5 | Use integer between 1 and 5 |
| Exchange not found | Invalid exchange UUID | Verify exchange exists |
| Permission denied | Trying to update others' review | Can only update own reviews |
| Text too long | Review > 500 chars | Shorten review text |

---

## Admin Features

Django Admin Panel includes:
- List all reviews
- Filter by rating, date, exchange
- Search by exchange, user, or text
- View full review details
- Delete inappropriate reviews

---

For complete documentation, see [REVIEWS_API_DOCUMENTATION.md](./REVIEWS_API_DOCUMENTATION.md)
