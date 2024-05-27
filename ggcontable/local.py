# -*- coding: utf-8 -*-
from .settings import *
import os
from decouple import config

DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG

DB_USER = 'gg'
DB_PASS = 'battlehome'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'

# DB_USER = 'gg_ironweb'
# DB_PASS = 'Sarasa9090!'
# DB_PORT = '3307'

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
            'HOST':  DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': DB_PORT,
        },
    }

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',#Barra DEBUG
)

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')


import sys
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
if TESTING: #Covers regular testing and django-coverage
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', #
            'NAME': 'test.db', # Ruta al archivo de la base de datos
            }
        }
        
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


STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
