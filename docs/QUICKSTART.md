# Quick Start Guide

Get your Motivational Messages API up and running in 5 minutes!

## Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

## Installation Steps

### 1. Set Up Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy .env.example to .env
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
```

Edit `.env` and add your API keys:
```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key-here
TAP_API_KEY=your-tap-api-key-here
TAP_SECRET_KEY=your-tap-secret-key-here
```

### 4. Set Up Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User
```bash
python manage.py createsuperuser
```
Follow prompts to create your admin account.

### 6. Seed Initial Data
```bash
python manage.py seed_data
```
This creates:
- 16 predefined scopes (life domains)
- 5 subscription packages (Starter, Growth, Elite + annual plans)

### 7. Run Development Server
```bash
python manage.py runserver
```

## Access the Application

### API Documentation
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

### Admin Panel
- **URL**: http://localhost:8000/admin/
- **Login**: Use the superuser credentials you created

## Quick API Test

### 1. Get Access Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"your_username\", \"password\": \"your_password\"}"
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. List Available Packages
```bash
curl -X GET http://localhost:8000/api/packages/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 3. List Scopes
```bash
curl -X GET http://localhost:8000/api/scopes/
```

## Common Tasks

### View All Data in Admin
1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. You can view and manage:
   - Scopes
   - Packages
   - Subscriptions
   - Goals
   - AI Messages
   - Transactions

### Create a Test Subscription (Admin Panel)
1. Login to admin panel
2. Go to "Subscriptions" → "Add Subscription"
3. Select user, package, and scopes
4. Set status to "active"
5. Set start_date to today
6. Set end_date to 30 days from now
7. Save

### Generate AI Message (requires active subscription)
```bash
curl -X POST http://localhost:8000/api/messages/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d "{\"message_type\": \"daily\"}"
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not configured"
**Solution**: Add your OpenAI API key to `.env` file

### Issue: "No active subscription found"
**Solution**: Create an active subscription through admin panel or API

### Issue: Migration errors
**Solution**:
```bash
python manage.py makemigrations --empty api
python manage.py migrate
```

### Issue: Import errors
**Solution**: Make sure all dependencies are installed
```bash
pip install -r requirements.txt
```

## Next Steps

1. **Explore the API**: Use Swagger UI to test all endpoints
2. **Set Up Payment**: Configure Tap Payment credentials
3. **Customize Scopes**: Add or modify scopes in admin panel
4. **Create Packages**: Design your own subscription tiers
5. **Test AI Messages**: Generate motivational messages with different scopes

## Useful Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed initial data
python manage.py seed_data

# Open Django shell
python manage.py shell

# Run tests
python manage.py test
```

## Production Deployment

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up proper static file serving
5. Use Gunicorn or similar WSGI server
6. Configure HTTPS

See [README.md](README.md) for detailed production setup.

## Support

- **Documentation**: See [README.md](README.md)
- **API Docs**: http://localhost:8000/swagger/
- **Issues**: Create an issue in the repository

Happy coding!
