# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os,sys
from decouple import config

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..') #every dot represent the location of the folder so when you try to delete one dot, the path will be change

SITE_ROOT = PROJECT_ROOT


ADMINS = (
    ('JuanMa', 'ironweb@ironwebgestion.com.ar'),
    ('JuanManuel', 'jmjacquet@gmail.com'),
)

MANAGERS = ADMINS

#Traigo los datos de configuracion del Apache
ENTIDAD_ID = os.environ.get('ENTIDAD_ID')
ENTIDAD_DB = os.environ.get('ENTIDAD_DB')
ENTIDAD_DIR = os.environ.get('ENTIDAD_DIR')

DB_USER = config('DB_USER')
DB_PASS = config('DB_PASS')
DB_HOST = config('DB_HOST')


ALLOWED_HOSTS = '*'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
LANGUAGE_CODE = 'es-AR'
SITE_ID = 1
USE_I18N = True
USE_THOUSAND_SEPARATOR = True
USE_L10N = True
USE_TZ = True
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
TIME_INPUT_FORMATS = ('%H:%M',)
DATE_INPUT_FORMATS = ('%d/%m/%Y',)


MEDIA_URL = '/media/'
STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')


ADMIN_MEDIA_PREFIX = os.path.join(SITE_ROOT, '/static/admin/')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',    
)
TEMPLATE_CONTEXT_PROCESSORS =   (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

SECRET_KEY = config('SECRET_KEY')

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    
)

ROOT_URLCONF = 'ggcontable.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ggcontable.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',    
    'django.contrib.humanize',
    'bootstrap3',
    'crispy_forms',    
    'django_extensions',    
    'localflavor',
    'modal',    
    'general',
    'usuarios',    
    'entidades',    
    'productos',
    'comprobantes',    
    'ingresos',
    'egresos',
    'trabajos',
    'reportes',
    'felectronica',
    'djangosecure',
)


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

EMAIL_USE_TLS = True
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_PORT = 587

SERVER_EMAIL = config('SERVER_EMAIL', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(SITE_ROOT, "errores.log"),
            'formatter': 'verbose'
        },
         'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
             # But the emails are plain text by default - HTML is nicer
            'include_html': True,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        # 'xhtml2pdf': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        # },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console', ],
        # },

        'general': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'comprobantes': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}
ROOT_URL = '/'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL='/'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
AUTH_PROFILE_MODULE = 'usuarios.UserProfile'
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend','usuarios.authentication.UsuarioBackend',)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = config('SESSION_COOKIE_NAME', default='')


#Dir de Cetificados de Facturacion Electronica
CERTIFICADOS_PATH = os.path.join(MEDIA_ROOT,'certificados',)
#Traigo si la empresa figura en Modo homologacion(Prueba)


from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'error',} 

#
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         # 'LOCATION': 'unix:/home/grupogua/apps/server_apache/memcached.sock',
#         # 'LOCATION': 'cache:11211',
#         'LOCATION': 'unix:/tmp/memcached.sock',
#         'KEY_PREFIX': ENTIDAD_DB+'_'
#
#     }
# }

