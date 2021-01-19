# -*- coding: utf-8 -*-
from .settings import *
import os
from decouple import config

DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG

DB_USER = 'gg'
DB_PASS = 'qwerty'

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "staticfiles"),   
    # os.path.join(SITE_ROOT, "dist"),  
)

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.environ.get('ENTIDAD_DB'),           # Or path to database file if using sqlite3.
            'USER':  DB_USER,    
            'PASSWORD':  DB_PASS,             # Not used with sqlite3.
            'HOST':  '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',      
        },
    }

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',#Barra DEBUG
)

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')

INSTALLED_APPS += (
   'debug_toolbar',   
    # 'compressor' ,
)

# STATICFILES_FINDERS += (
#     'compressor.finders.CompressorFinder',
#     )


# COMPRESS_ENABLED = True
# COMPRESS_CSS_HASHING_METHOD = 'content'

# HTML_MINIFY = True
# COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter','compressor.filters.cssmin.CSSMinFilter']
# COMPRESS_JS_FILTERS = ["compressor.filters.jsmin.JSMinFilter"]


CACHE_TTL = 60

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": ENTIDAD_DB
    }
}