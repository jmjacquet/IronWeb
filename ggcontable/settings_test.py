# -*- coding: utf-8 -*-
"""
Minimal settings for running the test suite.
Uses SQLite in-memory so no MySQL connection is needed.
"""
from __future__ import unicode_literals
import os

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
SITE_ROOT = PROJECT_ROOT

SECRET_KEY = 'test-secret-key-not-used-in-production'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

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
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'ggcontable.urls'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
STATICFILES_ROOT = os.path.join(SITE_ROOT, 'staticfiles')

TEMPLATE_DIRS = (os.path.join(SITE_ROOT, 'templates'),)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

USE_TZ = True
TIME_ZONE = 'America/Argentina/Buenos_Aires'
LANGUAGE_CODE = 'es-AR'
USE_I18N = True
SITE_ID = 1

AUTH_PROFILE_MODULE = 'usuarios.UserProfile'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'usuarios.authentication.UsuarioBackend',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_COOKIE_NAME = 'ironweb_test_session'
SESSION_COOKIE_DOMAIN = None

# Tenant env vars required by some imports
ENTIDAD_ID = os.environ.get('ENTIDAD_ID', '1')
ENTIDAD_DB = os.environ.get('ENTIDAD_DB', 'ironweb_prueba')
ENTIDAD_DIR = os.environ.get('ENTIDAD_DIR', 'prueba')

EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 587
SERVER_EMAIL = ''
DEFAULT_FROM_EMAIL = ''

LOGGING = {'version': 1, 'disable_existing_loggers': True}
