"""
Production settings.

This file contains settings specific to production environment.
Security-focused and optimized for performance.
"""

import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Must be set in environment variables
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'sign-sa.net,72.61.90.66').split(',')

# Database - MySQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'signdb'),
        'USER': os.environ.get('DB_USER', 'sign'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'gemy2803150'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Alternative: Use DATABASE_URL for easy configuration
# Uncomment if using dj-database-url
# import dj_database_url
# DATABASES['default'] = dj_database_url.config(conn_max_age=600)

# CORS Settings - Strict in production
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://sign-sa.net,http://72.61.90.66').split(',')
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# CSRF Settings
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://sign-sa.net,http://72.61.90.66'
).split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else ['https://sign-sa.net', 'http://72.61.90.66']

# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow framing from same origin for Swagger UI

# Email Backend - SendGrid for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # This is literally the string 'apikey' for SendGrid
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_FROM_ADDRESS', 'noreply@sign-sa.net')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'admin@sign-sa.net')

# Optional: Set friendly from name
# from constance import config
# DEFAULT_FROM_EMAIL = f'{config.EMAIL_FROM_NAME} <{config.EMAIL_FROM_ADDRESS}>'

# Cache - Redis for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session - Redis for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Static files - Production configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Use WhiteNoise instead of ManifestStaticFilesStorage for better compatibility
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files - Production configuration
# Consider using cloud storage (S3, Google Cloud Storage, etc.)
MEDIA_ROOT = BASE_DIR / 'media'

# Swagger Settings - Allow CDN resources
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'PERSIST_AUTH': True,
}

# Optional: AWS S3 Configuration
# Uncomment and configure if using django-storages with S3
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_DEFAULT_ACL = 'public-read'
# AWS_QUERYSTRING_AUTH = False

# Logging - Production configuration
# Create logs directory if it doesn't exist
import os
LOGS_DIR = os.environ.get('LOGS_DIR', str(BASE_DIR / 'logs'))
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Admin notification emails
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@sign-sa.net')),
]
MANAGERS = ADMINS

# Production-specific REST Framework settings
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    # Remove BrowsableAPIRenderer in production
]

# Rate limiting (optional - requires django-ratelimit)
# RATELIMIT_ENABLE = True
# RATELIMIT_USE_CACHE = 'default'

# Sentry Integration (optional - for error tracking)
# Uncomment and configure if using Sentry
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
#
# sentry_sdk.init(
#     dsn=os.environ.get('SENTRY_DSN'),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=1.0,
#     send_default_pii=True,
#     environment='production',
# )

# OpenAI Configuration - Get from Django Constance (configured via admin)
# Falls back to environment variable if Constance is not yet set up
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Tap Payment Configuration - Get from environment or Constance
TAP_API_KEY = os.environ.get('TAP_API_KEY', '')
TAP_SECRET_KEY = os.environ.get('TAP_SECRET_KEY', '')

# Site URL - Get from environment or Constance
SITE_URL = os.environ.get('SITE_URL', 'https://sign-sa.net')

# Note: These settings can be managed via Django Constance at /admin/constance/config/
# The actual values will be loaded from the database at runtime

# Print production mode indicator
print("Running in PRODUCTION mode")
print(f"Allowed Hosts: {ALLOWED_HOSTS}")
print(f"Database: MySQL at {DATABASES['default']['HOST']}")
print(f"Cache: Redis at {CACHES['default']['LOCATION']}")

# Redis health check (optional)
try:
    from django_redis import get_redis_connection
    redis_conn = get_redis_connection("default")
    redis_conn.ping()
    print("✓ Redis connection successful")
except Exception as e:
    print(f"⚠ Warning: Redis connection failed: {e}")
    print("  Falling back to database cache")
    # Fallback to database cache if Redis is not available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }
