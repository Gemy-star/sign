# Motivational Messages API

A comprehensive Django REST Framework API for a subscription-based personal development and motivational messaging platform. The system integrates with OpenAI's ChatGPT for AI-generated motivational content and Tap Payment Gateway for secure subscription management.

## Features

### Core Functionality
- **Subscription Management**: Multiple package tiers with different features and pricing
- **Personal Development Scopes**: 8 life domains for focused personal growth
  - Mental and Emotional Growth
  - Physical Health and Wellness
  - Career and Professional Development
  - Financial Growth
  - Relationships and Social Life
  - Spiritual and Inner Fulfillment
  - Creativity and Learning
  - Lifestyle and Environment
- **Custom Goals**: Premium users can set and track personal development goals
- **AI-Generated Messages**: Personalized motivational content powered by OpenAI ChatGPT
- **Payment Integration**: Secure payments via Tap Payment Gateway
- **Admin Dashboard**: Comprehensive Django admin interface for management

### API Features
- RESTful API with DRF
- JWT Authentication
- Swagger/OpenAPI Documentation
- Pagination and Filtering
- CORS Support
- Comprehensive permission system

## Tech Stack

- **Backend**: Django 5.2.8
- **API**: Django REST Framework 3.15.2
- **Authentication**: JWT (Simple JWT)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **AI Integration**: OpenAI API
- **Payment Gateway**: Tap Payment API
- **Database**: SQLite (default), PostgreSQL (production-ready)

## Installation

### Prerequisites
- Python 3.10 or higher
- pip
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sign
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example .env file
   cp .env.example .env

   # Edit .env with your configuration
   # - Add your SECRET_KEY
   # - Add your OPENAI_API_KEY
   # - Add your TAP_API_KEY and TAP_SECRET_KEY
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data (optional)**
   ```bash
   # You can create initial scopes and packages through the admin panel
   # or create a data fixture
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

Once the server is running, you can access the API documentation at:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## API Endpoints

### Authentication
```
POST   /api/auth/token/          - Obtain JWT token
POST   /api/auth/token/refresh/  - Refresh JWT token
POST   /api/auth/token/verify/   - Verify JWT token
```

### Scopes
```
GET    /api/scopes/              - List all scopes
GET    /api/scopes/{id}/         - Get scope details
GET    /api/scopes/categories/   - Get all scope categories
```

### Packages
```
GET    /api/packages/            - List all packages
GET    /api/packages/{id}/       - Get package details
GET    /api/packages/featured/   - Get featured packages
```

### Subscriptions
```
GET    /api/subscriptions/           - List user subscriptions
POST   /api/subscriptions/           - Create new subscription (initiates payment)
GET    /api/subscriptions/{id}/      - Get subscription details
PATCH  /api/subscriptions/{id}/      - Update subscription
POST   /api/subscriptions/{id}/cancel/        - Cancel subscription
PATCH  /api/subscriptions/{id}/update_scopes/ - Update selected scopes
GET    /api/subscriptions/active/    - Get active subscription
```

### User Goals
```
GET    /api/goals/                   - List user goals
POST   /api/goals/                   - Create new goal
GET    /api/goals/{id}/              - Get goal details
PATCH  /api/goals/{id}/              - Update goal
DELETE /api/goals/{id}/              - Delete goal
POST   /api/goals/{id}/complete/     - Mark goal as completed
PATCH  /api/goals/{id}/update_progress/ - Update goal progress
GET    /api/goals/active/            - Get active goals
```

### AI Messages
```
GET    /api/messages/                - List user messages
POST   /api/messages/                - Generate new AI message
GET    /api/messages/{id}/           - Get message details
POST   /api/messages/{id}/mark_read/ - Mark message as read
POST   /api/messages/{id}/toggle_favorite/ - Toggle favorite
POST   /api/messages/{id}/rate/      - Rate message (1-5)
GET    /api/messages/daily/          - Get daily message
GET    /api/messages/favorites/      - Get favorited messages
```

### Payments
```
POST   /api/payments/webhook/        - Tap Payment webhook
GET    /api/payments/verify/{charge_id}/ - Verify payment status
```

### Dashboard
```
GET    /api/dashboard/stats/         - Get user dashboard statistics
```

## Authentication

The API uses JWT (JSON Web Token) authentication. To access protected endpoints:

1. **Obtain a token**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
   ```

2. **Use the token in requests**:
   ```bash
   curl -X GET http://localhost:8000/api/subscriptions/ \
     -H "Authorization: Bearer <your_access_token>"
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | No |
| `OPENAI_API_KEY` | OpenAI API key for ChatGPT | Yes |
| `OPENAI_MODEL` | OpenAI model (default: gpt-3.5-turbo) | No |
| `TAP_API_KEY` | Tap Payment API key | Yes |
| `TAP_SECRET_KEY` | Tap Payment secret key | Yes |
| `SITE_URL` | Your site URL for payment redirects | Yes |

## Models Overview

### Scope
Represents different life domains for personal development (mental, physical, career, etc.)

### Package
Subscription packages with pricing, duration, and feature limits

### Subscription
User subscriptions linked to packages with payment tracking

### UserGoal
Custom goals set by users (available in premium packages)

### AIMessage
AI-generated motivational messages based on scopes and goals

### PaymentTransaction
Payment transaction records for audit and reconciliation

## Usage Examples

### Creating a Subscription

```python
# 1. First, get available packages
GET /api/packages/

# 2. Create subscription with payment
POST /api/subscriptions/
{
  "package_id": 1,
  "selected_scope_ids": [1, 2, 3],
  "customer_email": "user@example.com",
  "redirect_url": "https://yourapp.com/success"
}

# 3. User completes payment on Tap Payment page
# 4. Webhook activates subscription automatically
```

### Generating AI Messages

```python
# Generate a daily motivational message
POST /api/messages/
{
  "message_type": "daily"
}

# Generate scope-specific message
POST /api/messages/
{
  "scope_id": 1,
  "message_type": "scope_based"
}

# Generate goal-specific message
POST /api/messages/
{
  "goal_id": 1,
  "message_type": "goal_specific",
  "custom_prompt": "I'm struggling with staying motivated this week"
}
```

## Admin Panel

Access the Django admin panel at `/admin/` to:
- Manage scopes, packages, subscriptions
- View user goals and AI messages
- Track payment transactions
- Bulk operations on subscriptions
- View detailed analytics

## Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Production Checklist

1. Set `DEBUG=False` in settings
2. Configure `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up static files with WhiteNoise or CDN
5. Use environment variables for all secrets
6. Set up HTTPS
7. Configure CORS properly
8. Set up proper logging
9. Use Gunicorn or uWSGI
10. Set up monitoring and error tracking

### Example Production Setup

```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

## API Rate Limiting

Messages are limited per subscription package:
- Basic: 1 message per day
- Premium: 5 messages per day
- Enterprise: Unlimited (or custom limit)

## Security Features

- JWT-based authentication
- CORS protection
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection
- Secure password hashing
- Payment data encryption (handled by Tap Payment)

## Support

For issues, questions, or feature requests, please contact:
- Email: support@motivationalapp.com
- GitHub Issues: [repository-url]/issues

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Changelog

### Version 1.0.0 (Initial Release)
- Subscription management system
- AI-powered motivational messages
- Tap Payment integration
- User goals and progress tracking
- Comprehensive API documentation
- Django admin dashboard
