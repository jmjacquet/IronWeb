# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os,sys
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..') #every dot represent the location of the folder so when you try to delete one dot, the path will be change

SITE_ROOT = PROJECT_ROOT

#Traigo los datos de configuracion del Apache
ENTIDAD_ID = os.environ.get('ENTIDAD_ID')
ENTIDAD_DB = os.environ.get('ENTIDAD_DB')
ENTIDAD_DIR = os.environ.get('ENTIDAD_DIR')

DB_USER = "gg"
DB_PASS = "battlehome"
DB_HOST = "web594.webfaction.com"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ENTIDAD_DB,           # Or path to database file if using sqlite3.
        'USER':  DB_USER,    
        'PASSWORD':  DB_PASS,            # Not used with sqlite3.
        'HOST':  DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',      
    },
}

    

ALLOWED_HOSTS = ['*']
TIME_ZONE = 'America/Argentina/Buenos_Aires'
LANGUAGE_CODE = 'es-AR'
SITE_ID = 1
USE_I18N = True
USE_THOUSAND_SEPARATOR = True
USE_L10N = True
USE_TZ = False
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
TIME_INPUT_FORMATS = ('%H:%M',)
DATE_INPUT_FORMATS = ('%d/%m/%Y',)
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
# STATIC_ROOT = '/home/grupogua/webapps/ironweb/ggcontable/staticfiles'
STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                    os.path.join(SITE_ROOT, 'templates'),
                ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',                
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_DIRS = [
    os.path.join(SITE_ROOT, "staticfiles"),   
]

STATICFILES_FINDERS = [
'django.contrib.staticfiles.finders.FileSystemFinder',
'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


ADMIN_MEDIA_PREFIX = os.path.join(SITE_ROOT, '/static/admin/')



SECRET_KEY = '7i@#mz$&m(!02ij#^-z)wd1+g4yay9*s%5vw7ix$@#m)k=unrx'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'ggcontable.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ggcontable.wsgi.application'


INSTALLED_APPS = [
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
    'fm',
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
    ]


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# EMAIL_PORT = 465
EMAIL_HOST = str("smtp.webfaction.com")
EMAIL_HOST_USER = str("grupogua_errores")
EMAIL_HOST_PASSWORD = str("Sarasa1616")
EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'grupogua_errores')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)



SERVER_EMAIL = 'errores_web@grupoguadalupe.com.ar'
DEFAULT_FROM_EMAIL = 'errores_web@grupoguadalupe.com.ar'

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
        
        'general': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
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
SESSION_COOKIE_NAME = "grupogua"
SECRET_KEY='grupoguadalupe'


#Dir de Cetificados de Facturacion Electronica
CERTIFICADOS_PATH = os.path.join(MEDIA_ROOT,'certificados',)
#Traigo si la empresa figura en Modo homologacion(Prueba)


from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'error',} 

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]