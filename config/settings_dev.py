# config/settings_dev.py
"""
Development settings - TEMPORARY cache without Redis
Use this file while setting up Redis
"""

from .settings import *

# Override cache to use in-memory (no Redis needed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

DEBUG = True

# Disable debug toolbar for now
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [mw for mw in MIDDLEWARE if 'debug_toolbar' not in mw]

print("🔧 Using LOCAL MEMORY cache (no Redis needed for development)")