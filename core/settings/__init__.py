"""
Settings package for the Django project.

The settings are split into:
- base.py: Common settings shared across all environments
- local.py: Local development settings
- production.py: Production environment settings

Usage:
    Set DJANGO_SETTINGS_MODULE environment variable:
    - Development: DJANGO_SETTINGS_MODULE=core.settings.local
    - Production: DJANGO_SETTINGS_MODULE=core.settings.production
"""

import os

# Default to local settings if not specified
SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE', 'core.settings.local')

if SETTINGS_MODULE.endswith('.local'):
    from .local import *
elif SETTINGS_MODULE.endswith('.production'):
    from .production import *
else:
    from .base import *
