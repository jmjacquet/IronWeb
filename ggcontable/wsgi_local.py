"""
WSGI config for IronWeb project - LOCAL

This exposes the WSGI callable as a module-level variable named ``application``.
For local development with debug toolbar and other dev tools.
"""
import os
import sys

# Add project directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
sys.path.append(PROJECT_DIR)

# Set Django settings module for local development
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.docker_local")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()