import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

sys.path.append(PROJECT_DIR)

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.settings")
os.environ['DJANGO_SETTINGS_MODULE'] = "ggcontable.production"
os.environ['ENTIDAD_ID'] = '1'
os.environ['ENTIDAD_DB'] = 'ironweb_demo'
os.environ['ENTIDAD_DIR'] = 'copyfast'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()