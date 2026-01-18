# -*- coding: utf-8 -*-
"""
Django settings for IronWeb project - DEVELOPMENT (Docker/Dockploy)
"""
from .settings import *
from decouple import config
import os

DEBUG = config('DEBUG', default="True") == "True"

DB_USER = config('DB_USER', default="")
DB_PASS = config('DB_PASS', default="")
DB_HOST = config('DB_HOST', default="mariadb_shared")
DB_PORT = config('DB_PORT', default='3306')

MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(SITE_ROOT, 'media'))
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(SITE_ROOT, 'static'))
INTERNAL_IPS = ('127.0.0.1', 'localhost', '0.0.0.0')

# Database name is set dynamically by TenantMiddleware via ENTIDAD_DB env var
# Default fallback for initial connection
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get('ENTIDAD_DB', 'ironweb_prueba'),  # Default fallback
        "USER": DB_USER,
        "PASSWORD": DB_PASS,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
}

# CRITICAL: Add TenantMiddleware as FIRST middleware
# This must be before any other middleware that might access the database
MIDDLEWARE_CLASSES = (
    'ggcontable.middleware.TenantMiddleware',  # MUST be first!
) + MIDDLEWARE_CLASSES

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "staticfiles"),
)

# Debug toolbar configuration for development
if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

    # Add debug toolbar middleware after TenantMiddleware
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    # Always show toolbar in DEBUG mode
    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar,
        'INTERCEPT_REDIRECTS': False,
    }

    INTERNAL_IPS = ['127.0.0.1', 'localhost', '0.0.0.0']

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# Email configuration
EMAIL_USE_TLS = True
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_PORT = 587
SERVER_EMAIL = config('SERVER_EMAIL', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')

# Session configuration
SESSION_COOKIE_NAME = config('SESSION_COOKIE_NAME', default='ironweb_session_dev')
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"