import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

sys.path.append(PROJECT_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = "ggcontable.development"
os.environ['ENTIDAD_ID'] = '1'
os.environ['ENTIDAD_DB'] = 'gg_ironweb'
os.environ['ENTIDAD_DIR'] = 'sucec'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
