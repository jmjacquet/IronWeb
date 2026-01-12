"""
WSGI config for IronWeb project - PRODUCTION

This exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

sys.path.append(PROJECT_DIR)

# Use docker_prod settings for production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ggcontable.prod')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()