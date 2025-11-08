"""
Base settings shared across all environments.
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-=f!l2ggh322@zn=%^=p5*$-j(lsb@bksemt+na*bjaggohtv9g')

# Application definition
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'constance',
    'constance.backends.database',

    # Local apps
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be near the top
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Swagger Settings
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

# Django Constance - Dynamic Settings
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    # OpenAI Configuration
    'OPENAI_API_KEY': (
        os.environ.get('OPENAI_API_KEY', ''),
        'OpenAI API Key for ChatGPT integration',
        str
    ),
    'OPENAI_MODEL': (
        'gpt-3.5-turbo',
        'OpenAI model to use (gpt-3.5-turbo, gpt-4, etc.)',
        str
    ),
    'OPENAI_MAX_TOKENS': (
        500,
        'Maximum tokens for AI message generation',
        int
    ),
    'OPENAI_TEMPERATURE': (
        0.8,
        'Temperature for AI responses (0.0-1.0)',
        float
    ),

    # Tap Payment Configuration
    'TAP_API_KEY': (
        os.environ.get('TAP_API_KEY', ''),
        'Tap Payment Gateway API Key',
        str
    ),
    'TAP_SECRET_KEY': (
        os.environ.get('TAP_SECRET_KEY', ''),
        'Tap Payment Gateway Secret Key',
        str
    ),
    'TAP_BASE_URL': (
        'https://api.tap.company/v2',
        'Tap Payment API Base URL',
        str
    ),

    # Site Configuration
    'SITE_URL': (
        os.environ.get('SITE_URL', 'http://localhost:8000'),
        'Site URL for payment redirects and webhooks',
        str
    ),
    'SITE_NAME': (
        'Motivational Messages',
        'Site name displayed in emails and notifications',
        str
    ),
    'SUPPORT_EMAIL': (
        'support@motivationalapp.com',
        'Support email address',
        str
    ),

    # Feature Flags
    'ENABLE_AI_MESSAGES': (
        True,
        'Enable AI message generation feature',
        bool
    ),
    'ENABLE_PAYMENT_GATEWAY': (
        True,
        'Enable payment gateway integration',
        bool
    ),
    'ENABLE_EMAIL_NOTIFICATIONS': (
        False,
        'Enable email notifications to users',
        bool
    ),
    'MAINTENANCE_MODE': (
        False,
        'Enable maintenance mode',
        bool
    ),

    # Message Limits
    'DEFAULT_MESSAGE_LIMIT': (
        1,
        'Default daily message limit for basic users',
        int
    ),
    'MAX_MESSAGE_LENGTH': (
        1000,
        'Maximum length for AI-generated messages',
        int
    ),

    # Subscription Settings
    'TRIAL_PERIOD_DAYS': (
        7,
        'Trial period duration in days',
        int
    ),
    'AUTO_RENEW_DEFAULT': (
        True,
        'Default auto-renew setting for new subscriptions',
        bool
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'OpenAI Settings': (
        'OPENAI_API_KEY',
        'OPENAI_MODEL',
        'OPENAI_MAX_TOKENS',
        'OPENAI_TEMPERATURE',
    ),
    'Payment Gateway': (
        'TAP_API_KEY',
        'TAP_SECRET_KEY',
        'TAP_BASE_URL',
    ),
    'Site Configuration': (
        'SITE_URL',
        'SITE_NAME',
        'SUPPORT_EMAIL',
    ),
    'Feature Flags': (
        'ENABLE_AI_MESSAGES',
        'ENABLE_PAYMENT_GATEWAY',
        'ENABLE_EMAIL_NOTIFICATIONS',
        'MAINTENANCE_MODE',
    ),
    'Business Rules': (
        'DEFAULT_MESSAGE_LIMIT',
        'MAX_MESSAGE_LENGTH',
        'TRIAL_PERIOD_DAYS',
        'AUTO_RENEW_DEFAULT',
    ),
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
