# -*- coding: utf-8 -*-
from .settings import *
import os

DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG

DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.environ.get('ENTIDAD_DB'),           # Or path to database file if using sqlite3.
            'USER': 'root',                      # Not used with sqlite3.
            'PASSWORD': 'qwerty',            # Not used with sqlite3.
            'HOST': 'mydb',                   # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',    
        },
    }

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',#Barra DEBUG
)

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')

INSTALLED_APPS += (
    'debug_toolbar',    
)


