# -*- coding: utf-8 -*-
"""
Django settings for IronWeb project - LOCAL (Docker)
"""
from .settings import *
from decouple import config
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DB_USER = config('DB_USER', default='root')
DB_PASS = config('DB_PASS', default='rootpassword')
DB_HOST = config('DB_HOST', default='mariadb_ironweb_local')
DB_PORT = config('DB_PORT', default='3306')

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "staticfiles"),
)

# Database name is set dynamically by TenantMiddleware via ENTIDAD_DB env var
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('ENTIDAD_DB', 'ironweb_prueba'),  # Default fallback
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
}

# CRITICAL: Add TenantMiddleware as FIRST middleware
MIDDLEWARE_CLASSES = (
    'ggcontable.middleware.TenantMiddleware',  # MUST be first!
) + MIDDLEWARE_CLASSES

# Add debug toolbar for local development
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

INSTALLED_APPS += (
    'debug_toolbar',
)

# Debug toolbar configuration
def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    'INTERCEPT_REDIRECTS': False,
}

INTERNAL_IPS = ['127.0.0.1', 'localhost', '0.0.0.0']

# Session configuration (base settings.py assumes production HTTPS + shared cookie domain)
SESSION_COOKIE_NAME = config('SESSION_COOKIE_NAME', default='ironweb_session_local')
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = None

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Make local logs noisier: show warnings, errors and full exception traces in console.
DEBUG_PROPAGATE_EXCEPTIONS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}