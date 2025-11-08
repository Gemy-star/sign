# Settings Migration Guide

This document explains the new settings structure and how to migrate from the old single settings file to the new split settings configuration.

## Overview

The settings have been reorganized into a modular structure:

```
core/
├── settings/
│   ├── __init__.py       # Settings package initialization
│   ├── base.py           # Common settings for all environments
│   ├── local.py          # Local development settings
│   └── production.py     # Production environment settings
```

## Key Changes

### 1. Settings Split
- **base.py**: Contains common settings shared across all environments
- **local.py**: Development-specific settings (DEBUG=True, SQLite, etc.)
- **production.py**: Production settings (DEBUG=False, PostgreSQL, security hardening)

### 2. Django Constance Integration
Dynamic settings are now managed via `django-constance`, allowing runtime configuration changes through the admin panel without code deployment.

#### Constance Configuration Categories:
- **OpenAI Settings**: API keys, model selection, temperature, max tokens
- **Payment Gateway**: Tap Payment API credentials
- **Site Configuration**: Site URL, name, support email
- **Feature Flags**: Enable/disable features without code changes
- **Business Rules**: Message limits, trial periods, auto-renew defaults

## Installation Steps

### 1. Install New Dependencies

```bash
pip install django-constance[database]==3.1.0
```

### 2. Run Migrations

```bash
# Make sure to use the correct settings module
python manage.py migrate

# This will create the constance_config table for dynamic settings
```

### 3. Set Environment Variables

Update your `.env` file or environment:

```bash
# For local development
export DJANGO_SETTINGS_MODULE=core.settings.local

# For production
export DJANGO_SETTINGS_MODULE=core.settings.production
```

### 4. Update Configuration Files

The following files have been automatically updated:
- ✅ `manage.py` - Uses `core.settings.local` by default
- ✅ `core/wsgi.py` - Uses `core.settings.production`
- ✅ `core/asgi.py` - Uses `core.settings.production`

## Environment-Specific Settings

### Local Development (local.py)

**Default Settings:**
- `DEBUG = True`
- Database: SQLite
- CORS: Allows localhost origins
- Email: Console backend (prints to terminal)
- Cache: Dummy cache (no caching)
- Security: Relaxed for development

**Usage:**
```bash
# Automatically used by manage.py
python manage.py runserver

# Or explicitly set
DJANGO_SETTINGS_MODULE=core.settings.local python manage.py runserver
```

### Production (production.py)

**Default Settings:**
- `DEBUG = False`
- Database: PostgreSQL (from environment variables)
- CORS: Strict origin control
- Email: SMTP backend
- Cache: Redis
- Security: Full hardening (SSL redirect, secure cookies, HSTS, etc.)

**Required Environment Variables:**
```bash
# Django
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=core.settings.production

# Database
DB_NAME=motivational_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Tap Payment
TAP_API_KEY=your-tap-api-key
TAP_SECRET_KEY=your-tap-secret-key

# Site
SITE_URL=https://yourdomain.com

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Redis (optional)
REDIS_URL=redis://127.0.0.1:6379/1

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Usage:**
```bash
# For production deployment
DJANGO_SETTINGS_MODULE=core.settings.production gunicorn core.wsgi:application
```

## Django Constance Usage

### Accessing Dynamic Settings in Code

```python
from constance import config

# OpenAI settings
api_key = config.OPENAI_API_KEY
model = config.OPENAI_MODEL
max_tokens = config.OPENAI_MAX_TOKENS

# Payment settings
tap_key = config.TAP_API_KEY
tap_secret = config.TAP_SECRET_KEY

# Site settings
site_url = config.SITE_URL
site_name = config.SITE_NAME

# Feature flags
if config.ENABLE_AI_MESSAGES:
    # AI feature enabled
    pass

if config.MAINTENANCE_MODE:
    # Show maintenance page
    pass
```

### Managing Settings via Admin Panel

1. Login to Django Admin: `http://localhost:8000/admin/`
2. Navigate to: **Constance** → **Config**
3. Update any setting values
4. Changes take effect immediately (no restart required)

### Available Constance Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `OPENAI_API_KEY` | string | '' | OpenAI API Key |
| `OPENAI_MODEL` | string | gpt-3.5-turbo | Model to use |
| `OPENAI_MAX_TOKENS` | int | 500 | Max tokens per message |
| `OPENAI_TEMPERATURE` | float | 0.8 | Response creativity (0.0-1.0) |
| `TAP_API_KEY` | string | '' | Tap Payment API Key |
| `TAP_SECRET_KEY` | string | '' | Tap Payment Secret |
| `TAP_BASE_URL` | string | https://api.tap.company/v2 | Tap API URL |
| `SITE_URL` | string | http://localhost:8000 | Site URL |
| `SITE_NAME` | string | Motivational Messages | Site name |
| `SUPPORT_EMAIL` | string | support@... | Support email |
| `ENABLE_AI_MESSAGES` | bool | True | Enable AI messages |
| `ENABLE_PAYMENT_GATEWAY` | bool | True | Enable payments |
| `ENABLE_EMAIL_NOTIFICATIONS` | bool | False | Enable emails |
| `MAINTENANCE_MODE` | bool | False | Maintenance mode |
| `DEFAULT_MESSAGE_LIMIT` | int | 1 | Daily message limit |
| `MAX_MESSAGE_LENGTH` | int | 1000 | Max message length |
| `TRIAL_PERIOD_DAYS` | int | 7 | Trial period days |
| `AUTO_RENEW_DEFAULT` | bool | True | Auto-renew default |

## Migration Checklist

### Development Environment

- [ ] Install django-constance: `pip install django-constance[database]==3.1.0`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Verify local settings work: `python manage.py runserver`
- [ ] Access admin panel and check Constance config
- [ ] Test API endpoints with new settings

### Production Environment

- [ ] Update `.env` or environment variables with all required values
- [ ] Set `DJANGO_SETTINGS_MODULE=core.settings.production`
- [ ] Install PostgreSQL and create database
- [ ] Install Redis (optional but recommended)
- [ ] Run migrations on production database
- [ ] Configure constance settings via admin panel
- [ ] Test payment gateway integration
- [ ] Test AI message generation
- [ ] Verify SSL/HTTPS redirects work
- [ ] Check security headers
- [ ] Test email sending (if enabled)

## Troubleshooting

### Issue: "No module named 'constance'"
**Solution:**
```bash
pip install django-constance[database]==3.1.0
```

### Issue: "ImproperlyConfigured: Requested setting OPENAI_API_KEY"
**Solution:**
1. Run migrations to create constance tables: `python manage.py migrate`
2. Set values in admin panel or environment variables

### Issue: Settings not loading
**Solution:** Ensure `DJANGO_SETTINGS_MODULE` is set correctly:
```bash
# Check current setting
echo $DJANGO_SETTINGS_MODULE

# Set for local dev
export DJANGO_SETTINGS_MODULE=core.settings.local

# Set for production
export DJANGO_SETTINGS_MODULE=core.settings.production
```

### Issue: Database errors in production
**Solution:** Verify all database environment variables are set:
```bash
DB_NAME=motivational_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Benefits of New Structure

### 1. **Environment Isolation**
- Development and production settings are completely separated
- No risk of accidentally deploying debug mode

### 2. **Dynamic Configuration**
- Change API keys without code deployment
- Toggle features via admin panel
- Adjust business rules in real-time

### 3. **Security**
- Production settings enforce security best practices
- Secrets managed via environment variables
- No sensitive data in code

### 4. **Maintainability**
- Clear separation of concerns
- Easy to add new environments (staging, testing)
- Shared settings in one place (base.py)

### 5. **Team Collaboration**
- Each developer can customize local.py
- Production settings standardized
- No conflicts in settings files

## Rollback Instructions

If you need to rollback to the old settings structure:

1. Restore the original `core/settings.py` file
2. Update `manage.py`, `wsgi.py`, `asgi.py` to use `core.settings`
3. Uninstall constance (optional): `pip uninstall django-constance`
4. Remove constance from INSTALLED_APPS

**Note:** Not recommended after running migrations, as constance tables will exist.

## Next Steps

1. Review and customize settings in [core/settings/base.py](core/settings/base.py)
2. Add environment-specific overrides in local.py or production.py
3. Configure dynamic settings via Django admin
4. Update deployment scripts to use correct DJANGO_SETTINGS_MODULE
5. Test thoroughly in all environments

## Support

For questions or issues:
- Check Django documentation: https://docs.djangoproject.com/en/stable/topics/settings/
- Django Constance docs: https://django-constance.readthedocs.io/
- Project README: [README.md](README.md)
