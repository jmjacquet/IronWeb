# -*- coding: utf-8 -*-
from .settings import *
from decouple import config

DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "staticfiles"),   
    # os.path.join(SITE_ROOT, "dist"),  
)

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



# INSTALLED_APPS += (
#     'debug_toolbar',    
# )