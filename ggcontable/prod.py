# -*- coding: utf-8 -*-
"""
Django settings for IronWeb project - PRODUCTION (Docker)
"""
from .settings import *
from decouple import config
import os

DEBUG = config('DEBUG', default='False') == 'True'

DB_USER = config('DB_USER')
DB_PASS = config('DB_PASS')
DB_HOST = config('DB_HOST', default='mariadb_ironweb')
DB_PORT = config('DB_PORT', default='3306')

# Single default DB - TenantMiddleware switches connection per request based on Host header
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ironweb_prueba',  # Overwritten by middleware per request
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 300,
    },
}

STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(SITE_ROOT, 'static'))
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(SITE_ROOT, 'media'))

# CRITICAL: Add TenantMiddleware as FIRST middleware
# This must be before any other middleware that might access the database
MIDDLEWARE_CLASSES = (
    'ggcontable.middleware.TenantMiddleware',  # MUST be first!
) + MIDDLEWARE_CLASSES

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "staticfiles"),
)

# Email configuration
EMAIL_USE_TLS = True
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_PORT = 587
SERVER_EMAIL = config('SERVER_EMAIL', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')

# Session configuration
SESSION_COOKIE_NAME = config('SESSION_COOKIE_NAME', default='ironweb_session')
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

USE_I18N = True
USE_THOUSAND_SEPARATOR = False
USE_L10N = False  # Disable localization
DATE_FORMAT = "d/m/Y"
DATETIME_FORMAT = "d/m/Y H:i"
SHORT_DATE_FORMAT = "d/m/Y"
USE_TZ = True
DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"
TIME_INPUT_FORMATS = ("%H:%M",)
DATE_INPUT_FORMATS = ("%d/%m/%Y",)