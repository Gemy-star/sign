# Settings Configuration Summary

## Quick Overview

The Django settings have been reorganized into a **modular, environment-aware structure** with **dynamic configuration support** via django-constance.

## File Structure

```
core/
├── settings/
│   ├── __init__.py        # Auto-loads correct settings
│   ├── base.py            # Common settings (shared)
│   ├── local.py           # Development settings
│   └── production.py      # Production settings
```

## Quick Start

### 1. Install Dependencies
```bash
pip install django-constance[database]==3.1.0
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Configure Environment (Optional)
```bash
# For development (default)
export DJANGO_SETTINGS_MODULE=core.settings.local

# For production
export DJANGO_SETTINGS_MODULE=core.settings.production
```

### 4. Configure Dynamic Settings
- Login to admin: http://localhost:8000/admin/
- Navigate to: **Constance** → **Config**
- Set your API keys and configuration values

## Key Features

### ✅ Environment Separation
- **Local**: SQLite, DEBUG=True, relaxed security
- **Production**: PostgreSQL, DEBUG=False, full security hardening

### ✅ Dynamic Configuration (django-constance)
Change settings **without restarting** via admin panel:
- OpenAI API keys and model settings
- Payment gateway credentials
- Feature flags (enable/disable features)
- Business rules (message limits, trial periods)

### ✅ Security Hardening
Production settings include:
- SSL redirect
- Secure cookies
- HSTS headers
- CSRF protection
- XSS filters

## Settings Organization

### Base Settings (base.py)
Common configuration shared across all environments:
- Django apps and middleware
- REST Framework configuration
- JWT authentication
- Swagger/API documentation
- Constance configuration
- Logging setup

### Local Settings (local.py)
Development-specific overrides:
- DEBUG = True
- SQLite database
- Console email backend
- Dummy cache
- Relaxed CORS and security

### Production Settings (production.py)
Production-ready configuration:
- DEBUG = False
- PostgreSQL database
- SMTP email backend
- Redis cache
- Strict security settings
- Error logging and monitoring

## Environment Variables

### Required for Production
```bash
SECRET_KEY=<secret>
ALLOWED_HOSTS=yourdomain.com
OPENAI_API_KEY=sk-...
TAP_API_KEY=<key>
TAP_SECRET_KEY=<secret>
SITE_URL=https://yourdomain.com
DB_NAME=motivational_db
DB_USER=postgres
DB_PASSWORD=<password>
```

### Optional
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=email@example.com
REDIS_URL=redis://localhost:6379/1
```

## Django Constance Settings

Manage these via Admin Panel → Constance → Config:

| Category | Settings |
|----------|----------|
| **OpenAI** | API Key, Model, Max Tokens, Temperature |
| **Payment** | Tap API Key, Secret Key, Base URL |
| **Site** | URL, Name, Support Email |
| **Features** | AI Messages, Payment Gateway, Emails, Maintenance Mode |
| **Business** | Message Limits, Trial Period, Auto-Renew |

## Updated Files

### Core Django Files
- ✅ [manage.py](manage.py) - Uses `core.settings.local`
- ✅ [core/wsgi.py](core/wsgi.py) - Uses `core.settings.production`
- ✅ [core/asgi.py](core/asgi.py) - Uses `core.settings.production`

### Configuration Files
- ✅ [core/settings/](core/settings/) - New modular settings
- ✅ [requirements.txt](requirements.txt) - Added django-constance
- ✅ [.env.example](.env.example) - Updated with all variables

### Services
- ✅ [api/services.py](api/services.py) - Uses constance config

### Documentation
- ✅ [SETTINGS_MIGRATION.md](SETTINGS_MIGRATION.md) - Detailed migration guide
- ✅ [SETTINGS_SUMMARY.md](SETTINGS_SUMMARY.md) - This file

## Usage Examples

### Accessing Settings in Code

```python
# Static settings (from settings files)
from django.conf import settings
debug_mode = settings.DEBUG

# Dynamic settings (from constance)
from constance import config
api_key = config.OPENAI_API_KEY
model = config.OPENAI_MODEL

# Feature flags
if config.ENABLE_AI_MESSAGES:
    # Generate AI message
    pass

if config.MAINTENANCE_MODE:
    # Show maintenance page
    pass
```

### Running Different Environments

```bash
# Development (default)
python manage.py runserver

# Production
DJANGO_SETTINGS_MODULE=core.settings.production gunicorn core.wsgi

# Custom settings
DJANGO_SETTINGS_MODULE=core.settings.staging python manage.py migrate
```

## Benefits

1. **🔒 Security**: Production settings enforce best practices
2. **🚀 Flexibility**: Change configs without code deployment
3. **🛠️ Maintainability**: Clear separation of environments
4. **👥 Team-Friendly**: Each dev can customize local settings
5. **📊 Observable**: Dynamic settings tracked in database
6. **🔄 Reversible**: Can rollback if needed

## Migration Checklist

- [x] Settings split into base, local, production
- [x] Django-constance integrated
- [x] Services updated to use constance
- [x] manage.py, wsgi.py, asgi.py updated
- [x] requirements.txt updated
- [x] .env.example updated
- [x] Documentation created

## Next Steps

1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Create superuser: `python manage.py createsuperuser`
3. ✅ Configure constance via admin panel
4. ✅ Test local development
5. ✅ Prepare production environment variables
6. ✅ Test production deployment

## Documentation

- **Detailed Guide**: [SETTINGS_MIGRATION.md](SETTINGS_MIGRATION.md)
- **API Docs**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

## Support

For issues or questions:
- Review migration guide
- Check environment variables
- Verify constance configuration in admin
- See troubleshooting section in SETTINGS_MIGRATION.md
