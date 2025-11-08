"""
Local development settings.

This file contains settings specific to local development environment.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Database
# SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS Settings for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost",
    "http://127.0.0.1",
]

CORS_ALLOW_ALL_ORIGINS = False  # Set to True only for development if needed
CORS_ALLOW_CREDENTIALS = True

# Email Backend - Console for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache - Local memory cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Session - Database backend for local development
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# Security Settings (relaxed for local development)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = False  # Disable binary profiler to avoid file issues
SILKY_PYTHON_PROFILER_RESULT_PATH = BASE_DIR / 'profiles'
SILKY_META = True
SILKY_INTERCEPT_PERCENT = 100  # Profile 100% of requests in development
SILKY_MAX_REQUEST_BODY_SIZE = -1  # No limit on request body size
SILKY_MAX_RESPONSE_BODY_SIZE = -1  # No limit on response body size
SILKY_MAX_RECORDED_REQUESTS = 10000  # Keep last 10000 requests

# Django Extensions (optional - uncomment if installed)
# INSTALLED_APPS += ['django_extensions']

# Local OpenAI settings (can override from environment)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

# Local Tap Payment settings
TAP_API_KEY = os.environ.get('TAP_API_KEY', '')
TAP_SECRET_KEY = os.environ.get('TAP_SECRET_KEY', '')

# Site URL for local development
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# Logging - More verbose for development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['api']['level'] = 'DEBUG'

# Create logs directory if it doesn't exist
import os
logs_dir = BASE_DIR / 'logs'
os.makedirs(logs_dir, exist_ok=True)

# Development-specific REST Framework settings
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',  # Keep browsable API in dev
]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {'MAX_ENTRIES': 1000}
    }
}

# Print settings on startup (helpful for debugging)
print(f"Running in LOCAL DEVELOPMENT mode")
print(f"DEBUG: {DEBUG}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"Database: SQLite at {DATABASES['default']['NAME']}")
