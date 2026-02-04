# Exchange Reviews API Documentation

## Overview

Users can submit, view, update, and delete reviews for exchanges. Each user can submit only one review per exchange.

---

## Endpoints

### 1. Submit a Review

**POST** `/api/exchange-reviews/`

Submit a new review for an exchange.

#### Request Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "exchange": "exchange-uuid-here",
  "rating": 5,
  "review_text": "Great service! Highly recommend."
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| exchange | UUID | Yes | UUID of the exchange being reviewed |
| rating | Integer | Yes | Rating from 1 to 5 stars |
| review_text | String | No | Review description (max 500 characters) |

#### Success Response (201 Created)
```json
{
  "success": true,
  "message": "Review submitted successfully",
  "data": {
    "uuid": "review-uuid",
    "exchange": "exchange-uuid",
    "user": {
      "uuid": "user-uuid",
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "rating": 5,
    "review_text": "Great service! Highly recommend.",
    "created_at": "2025-12-03T10:30:00Z",
    "updated_at": "2025-12-03T10:30:00Z"
  },
  "exchange_stats": {
    "average_rating": 4.8,
    "total_reviews": 25
  }
}
```

#### Error Responses

**400 Bad Request** - Already reviewed:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "error": ["You have already submitted a review for this exchange."]
  }
}
```

**400 Bad Request** - Invalid rating:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "rating": ["Rating must be between 1 and 5 stars."]
  }
}
```

**404 Not Found** - Exchange not found:
```json
{
  "success": false,
  "message": "Exchange not found.",
  "errors": {
    "exchange": ["Exchange does not exist."]
  }
}
```

---

### 2. Get Reviews for an Exchange

**GET** `/api/exchange-reviews/exchange/{exchange_uuid}/`

Get all reviews for a specific exchange with statistics.

#### Request Headers
```
Content-Type: application/json
```

#### Success Response (200 OK)
```json
{
  "count": 25,
  "next": "http://api.com/api/exchange-reviews/exchange/{uuid}/?page=2",
  "previous": null,
  "message": "Reviews for Veterans Tech Solutions retrieved successfully",
  "exchange": {
    "uuid": "exchange-uuid",
    "business_name": "Veterans Tech Solutions",
    "business_logo": "https://cdn.example.com/logo.png"
  },
  "statistics": {
    "average_rating": 4.8,
    "total_reviews": 25,
    "rating_breakdown": {
      "5": 20,
      "4": 3,
      "3": 1,
      "2": 1,
      "1": 0
    }
  },
  "results": [
    {
      "uuid": "review-uuid",
      "user": {
        "uuid": "user-uuid",
        "full_name": "John Doe",
        "email": "joh***@example.com"
      },
      "rating": 5,
      "review_text": "Excellent experience!",
      "created_at": "2025-12-03T10:30:00Z",
      "updated_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

---

### 3. Get My Reviews

**GET** `/api/exchange-reviews/my-reviews/`

Get all reviews submitted by the authenticated user.

#### Request Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Success Response (200 OK)
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "message": "Your reviews retrieved successfully",
  "results": [
    {
      "uuid": "review-uuid",
      "user": {
        "uuid": "user-uuid",
        "full_name": "John Doe",
        "email": "joh***@example.com"
      },
      "rating": 5,
      "review_text": "Great service!",
      "created_at": "2025-12-03T10:30:00Z",
      "updated_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

---

### 4. Get Specific Review

**GET** `/api/exchange-reviews/{review_uuid}/`

Get details of a specific review.

#### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Review retrieved successfully",
  "data": {
    "uuid": "review-uuid",
    "exchange": "exchange-uuid",
    "user": {
      "uuid": "user-uuid",
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "rating": 5,
    "review_text": "Great service!",
    "created_at": "2025-12-03T10:30:00Z",
    "updated_at": "2025-12-03T10:30:00Z"
  }
}
```

---

### 5. Update Own Review

**PATCH** `/api/exchange-reviews/{review_uuid}/`

Update your own review (partial update).

#### Request Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "rating": 4,
  "review_text": "Updated review text"
}
```

#### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Review updated successfully",
  "data": {
    "uuid": "review-uuid",
    "exchange": "exchange-uuid",
    "user": {
      "uuid": "user-uuid",
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "rating": 4,
    "review_text": "Updated review text",
    "created_at": "2025-12-03T10:30:00Z",
    "updated_at": "2025-12-03T11:45:00Z"
  }
}
```

#### Error Response

**403 Forbidden** - Not your review:
```json
{
  "success": false,
  "message": "You can only update your own reviews"
}
```

---

### 6. Delete Own Review

**DELETE** `/api/exchange-reviews/{review_uuid}/`

Delete your own review.

#### Request Headers
```
Authorization: Bearer <access_token>
```

#### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Review deleted successfully"
}
```

#### Error Response

**403 Forbidden** - Not your review:
```json
{
  "success": false,
  "message": "You can only delete your own reviews"
}
```

---

### 7. List All Reviews

**GET** `/api/exchange-reviews/`

List all reviews with pagination.

#### Success Response (200 OK)
```json
{
  "count": 100,
  "next": "http://api.com/api/exchange-reviews/?page=2",
  "previous": null,
  "message": "Reviews retrieved successfully",
  "results": [
    {
      "uuid": "review-uuid",
      "user": {
        "uuid": "user-uuid",
        "full_name": "John Doe",
        "email": "joh***@example.com"
      },
      "rating": 5,
      "review_text": "Excellent!",
      "created_at": "2025-12-03T10:30:00Z",
      "updated_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

---

## Business Rules

### One Review Per User Per Exchange
- Each user can only submit **one review** per exchange
- Attempting to submit a second review returns a validation error
- Users can update or delete their existing review

### Rating System
- Ratings must be between **1 and 5 stars** (integer)
- 5 = Excellent
- 4 = Very Good
- 3 = Good
- 2 = Fair
- 1 = Poor

### Review Text
- Optional field
- Maximum **500 characters**
- Can be left blank for star-only ratings

### Permissions
- **Submit Review**: Requires authentication
- **View Reviews**: Public (no authentication required)
- **Update Review**: Only the review author
- **Delete Review**: Only the review author

---

## Statistics Calculation

When viewing exchange reviews, the API provides:

1. **Average Rating**: Mean of all ratings (rounded to 1 decimal)
2. **Total Reviews**: Count of all reviews
3. **Rating Breakdown**: Count of reviews for each star level (1-5)

Example:
```json
"statistics": {
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

---

## Privacy Features

When listing reviews publicly, user information is partially hidden:
- Email is masked: `joh***@example.com` (first 3 characters + domain)
- Full name is shown if available, otherwise "Anonymous"
- User UUID is provided for reference

---

## cURL Examples

### Submit a Review
```bash
curl -X POST http://127.0.0.1:8000/api/exchange-reviews/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "exchange-uuid-here",
    "rating": 5,
    "review_text": "Great service! Highly recommend."
  }'
```

### Get Exchange Reviews
```bash
curl -X GET http://127.0.0.1:8000/api/exchange-reviews/exchange/{exchange_uuid}/ \
  -H "Content-Type: application/json"
```

### Update Review
```bash
curl -X PATCH http://127.0.0.1:8000/api/exchange-reviews/{review_uuid}/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "review_text": "Updated review"
  }'
```

### Delete Review
```bash
curl -X DELETE http://127.0.0.1:8000/api/exchange-reviews/{review_uuid}/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Integration with Exchange Model

Reviews are related to exchanges through a ForeignKey relationship:
- Each review is linked to one exchange
- Each exchange can have multiple reviews
- When listing exchanges, you can include review statistics

---

## Admin Panel

Administrators can manage reviews through Django admin:
- View all reviews
- Filter by rating, date, exchange, user
- Search by exchange name, user email, or review text
- Delete inappropriate reviews if needed

---

**Created:** December 3, 2025  
**Version:** 1.0
