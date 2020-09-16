# -*- coding: utf-8 -*-
from .settings import *
import os

DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.environ.get('ENTIDAD_DB'),           # Or path to database file if using sqlite3.
            'USER':  'gg',    
            'PASSWORD':  'battlehome',            # Not used with sqlite3.
            'HOST':  '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',      
        },
    }

# MIDDLEWARE_CLASSES += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',#Barra DEBUG
# )



# INSTALLED_APPS += (
#     'debug_toolbar',    
# )


