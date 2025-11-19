# config/settings.py
"""
Django settings for Lead Finder System.
Optimized for production scalability with caching, database optimization,
and performance enhancements.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# ============================================
# APPLICATION DEFINITION
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Local apps
    'leads.apps.LeadsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# ============================================
# DATABASE CONFIGURATION (OPTIMIZED)
# ============================================

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': BASE_DIR / os.getenv('DATABASE_NAME', 'db.sqlite3'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'timeout': 20,
        } if os.getenv('DATABASE_ENGINE', 'sqlite3') == 'django.db.backends.sqlite3' else {}
    }
}


# ============================================
# CACHE CONFIGURATION (REDIS OR LOCAL MEMORY)
# ============================================

REDIS_AVAILABLE = os.getenv('REDIS_URL') or os.getenv('REDIS_AVAILABLE', 'False') == 'True'

if REDIS_AVAILABLE:
    REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1')
    
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            },
            'KEY_PREFIX': 'leadfinder',
            'TIMEOUT': 3600,
        }
    }
    
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    
    print("✅ Using REDIS cache backend")
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-leadfinder',
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    }
    
    print("⚠️  Using LOCAL MEMORY cache (Redis not available)")


# ============================================
# PASSWORD VALIDATION
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================
# INTERNATIONALIZATION
# ============================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True


# ============================================
# STATIC FILES (OPTIMIZED FOR PRODUCTION)
# ============================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================
# LEAD FINDER SPECIFIC SETTINGS
# ============================================

# LinkedIn API Configuration
LINKEDIN_API_URL = os.getenv(
    'LINKEDIN_API_URL',
    'https://linkedin.programando.io/fetch_lead2'
)
LINKEDIN_API_USER_AGENT = os.getenv(
    'LINKEDIN_API_USER_AGENT',
    'PostmanRuntime/7.49.1'
)
LINKEDIN_API_TIMEOUT = int(os.getenv('LINKEDIN_API_TIMEOUT', '10'))

# API Retry & Circuit Breaker Configuration
API_RETRY_ATTEMPTS = int(os.getenv('API_RETRY_ATTEMPTS', '3'))
API_RETRY_BACKOFF = float(os.getenv('API_RETRY_BACKOFF', '2.0'))
API_CIRCUIT_BREAKER_THRESHOLD = int(os.getenv('API_CIRCUIT_BREAKER_THRESHOLD', '5'))
API_CIRCUIT_BREAKER_TIMEOUT = int(os.getenv('API_CIRCUIT_BREAKER_TIMEOUT', '60'))

# Cache TTL (Time To Live) settings
CACHE_TTL_LEADS_SEARCH = int(os.getenv('CACHE_TTL_LEADS_SEARCH', '3600'))
CACHE_TTL_LISTS = int(os.getenv('CACHE_TTL_LISTS', '1800'))
CACHE_TTL_API_RESPONSE = int(os.getenv('CACHE_TTL_API_RESPONSE', '7200'))

# Pagination
LEADS_PER_PAGE = int(os.getenv('LEADS_PER_PAGE', '10'))
MAX_PAGES_DISPLAY = int(os.getenv('MAX_PAGES_DISPLAY', '10'))

# Performance
if DEBUG:
    LOGGING_LEVEL_DB = 'DEBUG'
else:
    LOGGING_LEVEL_DB = 'INFO'


# ============================================
# LOGGING CONFIGURATION
# ============================================

LOGS_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {funcName}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'file_app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'lead_finder.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_api': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'api_calls.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'leads': {
            'handlers': ['console', 'file_app', 'file_errors'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'leads.api': {
            'handlers': ['file_api', 'file_errors'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'file_errors'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL_DB,
            'propagate': False,
        },
    },
}


# ============================================
# SECURITY SETTINGS (PRODUCTION)
# ============================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'