# Network App

## Overview

The **Network** app provides a complete followers and following system for the Vanguard platform, enabling veterans to connect and build their community network. This app allows users to follow/unfollow other users, view their network connections, check mutual followers, and get network statistics.

## Features

### ✅ Direct Follow System
- **Instant Following**: Users can directly follow any other user without approval
- **No Requests**: Simplified system with no pending requests or private accounts
- **Two-Way Relationships**: Support for mutual follows (users following each other)

### 📊 Network Statistics
- Follower count for any user
- Following count for any user
- Mutual followers between two users
- Relationship status (is following / is follower)

### 🔔 Notification Preferences
- Users can toggle notifications for posts from users they follow
- `notify_on_post` field on each follow relationship

### 🔍 Network Discovery
- View your followers list
- View your following list
- View any user's followers/following (public)
- Find mutual connections between users

## Architecture

### File Structure
```
network/
├── __init__.py
├── admin.py                    # Django admin configuration
├── apps.py                     # App configuration
├── tests.py                    # Unit tests
├── utils.py                    # Utility functions
├── models/
│   ├── __init__.py
│   └── follow.py              # Follow model
├── api/
│   ├── __init__.py
│   ├── serializers.py         # DRF serializers
│   ├── urls.py                # API URL routing
│   └── views.py               # API ViewSet
├── docs/
│   ├── NETWORK_API_DOCUMENTATION.md
│   └── README.md (this file)
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    └── 0002_alter_followrequest_unique_together_and_more.py
```

### Models

#### Follow
Represents a follower/following relationship between two users.

**Fields**:
- `uuid` (PrimaryKey): Unique identifier
- `follower` (ForeignKey): User who is following
- `following` (ForeignKey): User being followed
- `notify_on_post` (Boolean): Notification preference
- `created_at` (DateTime): Timestamp of follow

**Key Methods**:
- `is_following(follower, following)`: Check if one user follows another
- `get_followers_count(user)`: Get follower count for a user
- `get_following_count(user)`: Get following count for a user
- `get_mutual_followers(user1, user2)`: Get users who follow both

**Constraints**:
- Users cannot follow themselves (validated in `clean()`)
- Unique constraint on (follower, following) pair
- Database indexes on follower and following for performance

## API Endpoints

All endpoints are prefixed with `/api/network/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/follow/` | Follow a user |
| POST | `/unfollow/` | Unfollow a user |
| POST | `/toggle-follow/` | Toggle follow status |
| GET | `/followers/` | Get my followers |
| GET | `/following/` | Get who I'm following |
| GET | `/{user_uuid}/followers/` | Get user's followers |
| GET | `/{user_uuid}/following/` | Get user's following |
| GET | `/mutual-followers/{user_uuid}/` | Get mutual followers |
| GET | `/stats/` | Get my network stats |
| GET | `/{user_uuid}/stats/` | Get user's network stats |

See [NETWORK_API_DOCUMENTATION.md](./NETWORK_API_DOCUMENTATION.md) for detailed API documentation.

## Usage Examples

### Follow a User
```python
from network.models import Follow
from accounts.models import User

follower = User.objects.get(username='john_doe')
following = User.objects.get(username='jane_smith')

# Create follow relationship
follow = Follow.objects.create(
    follower=follower,
    following=following,
    notify_on_post=True
)
```

### Check if Following
```python
is_following = Follow.is_following(john, jane)
```

### Get Follower Counts
```python
followers_count = Follow.get_followers_count(jane)
following_count = Follow.get_following_count(jane)
```

### Get Mutual Followers
```python
mutual = Follow.get_mutual_followers(john, jane)
```

## Integration with Other Apps

### With Accounts App
- Uses `AUTH_USER_MODEL` for user relationships
- Integrates with user profiles for display information
- Profile photos included in serialized responses

### With Notification App
- `notify_on_post` field can be used to trigger notifications
- Future integration: Notify users when someone follows them
- Future integration: Notify on new posts from followed users

### With Intel/Exchange Apps
- Network connections can be used to show content from followed users
- Potential for "feed" features showing posts from followed veterans

## Admin Interface

The Django admin provides full management of follow relationships:

**Features**:
- Search followers/following by username or email
- Filter by notification preferences and date
- View follower/following information inline
- Optimized queries with `select_related`

**Access**: `/admin/network/follow/`

## Database

### Table: `network_follow`

| Column | Type | Constraints |
|--------|------|-------------|
| uuid | UUID | PRIMARY KEY |
| follower_id | UUID | FOREIGN KEY, NOT NULL |
| following_id | UUID | FOREIGN KEY, NOT NULL |
| notify_on_post | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | NOT NULL |

**Indexes**:
- Primary key on `uuid`
- Unique constraint on `(follower_id, following_id)`
- Index on `(follower_id, created_at DESC)`
- Index on `(following_id, created_at DESC)`

## Performance Considerations

### Database Optimization
- Indexes on follower and following columns for fast lookups
- `select_related` in admin to prevent N+1 queries
- Pagination (20 per page) for large follower/following lists

### Query Optimization
- Static methods use efficient `filter()` queries
- Count queries use database-level `count()`
- Mutual followers use set intersection for efficiency

### Scalability
- UUID primary keys allow for distributed systems
- Stateless API design supports horizontal scaling
- Potential for caching follower counts

## Testing

Run tests with:
```bash
python manage.py test network
```

Test coverage includes:
- Model validation (cannot follow self)
- Unique constraint enforcement
- Follow/unfollow operations
- Network statistics calculations
- API endpoint responses

## Future Enhancements

### Potential Features
- ❌ ~~Private accounts with follow requests~~ (Removed - direct follow only)
- 📱 Push notifications on new followers
- 🔔 Notifications for posts from followed users
- 📊 Network analytics and insights
- 🎯 Suggested users to follow
- 🔄 Activity feed from followed users
- 👥 Follower recommendations based on mutual connections

### Scalability Improvements
- Redis caching for follower counts
- Denormalized follower/following counts on User model
- Batch operations for bulk follows
- GraphQL support for flexible queries

## Dependencies

- Django 5.1+
- Django REST Framework 3.x
- PostgreSQL (for UUID support and performance)
- JWT Authentication (rest_framework_simplejwt)

## Configuration

Add to `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'network',
]
```

Add to `urls.py`:
```python
urlpatterns = [
    ...
    path('', include('network.api.urls')),
]
```

## Migration History

1. **0001_initial.py**: Created Follow and FollowRequest models
2. **0002_alter_followrequest_unique_together_and_more.py**: Removed FollowRequest model, updated Follow model structure to use models/ directory pattern

## Contributing

When contributing to the network app:
1. Follow the existing code structure (models/ directory pattern)
2. Add tests for new features
3. Update API documentation
4. Maintain consistent response format
5. Optimize database queries with indexes

## Support

For questions or issues:
- Check the API documentation
- Review test cases for usage examples
- Contact the Vanguard development team

---

**Version**: 1.0.0  
**Last Updated**: November 6, 2025  
**Maintained by**: Vanguard Development Team
