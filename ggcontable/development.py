# -*- coding: utf-8 -*-
from .settings import *


DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': "ironweb_prueba",           # Or path to database file if using sqlite3.
            'USER':  DB_USER,    
            'PASSWORD':  DB_PASS,            # Not used with sqlite3.
            'HOST':  "localhost",                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',      
        },
    }

# MIDDLEWARE_CLASSES += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',#Barra DEBUG
# )



# INSTALLED_APPS += (
#     'debug_toolbar',    
# )


