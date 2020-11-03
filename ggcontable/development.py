# -*- coding: utf-8 -*-
from .settings import *
from decouple import config

DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG

DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'gg_ironweb',           # Or path to database file if using sqlite3.
            'USER':  DB_USER,    
            'PASSWORD':  DB_PASS,            # Not used with sqlite3.
            'HOST':  'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',      
        },
    }

# MIDDLEWARE_CLASSES += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',#Barra DEBUG
# )

STATIC_ROOT = '/home/grupogua/apps/ironweb_prueba_static'

# INSTALLED_APPS += (
#     'debug_toolbar',    
# )


