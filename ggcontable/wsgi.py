import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

sys.path.append(PROJECT_DIR)

# try:
# 	application = get_wsgi_application()
# except Exception as e:
#     logger.error('Admin Command Error: %s', ' '.join(sys.argv), exc_info=sys.exc_info())
#     raise e	



os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("DB_USER", "gg")
os.environ.setdefault("DB_PASS", "battlehome")
os.environ.setdefault("EMAIL_HOST_USER", "ironweb_mail")
os.environ.setdefault("EMAIL_HOST_PASSWORD", "battlehome")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.settings")
# os.environ.setdefault("ENTIDAD_DB", "gg_ironweb")
# os.environ.setdefault("ENTIDAD_DB", "ironweb_411")
# os.environ.setdefault("ENTIDAD_ID", "1")
# os.environ.setdefault("ENTIDAD_DIR", "sucec")

from django.core.wsgi import get_wsgi_application

try:
	_application = None
	def application(environ, start_response):
		global _application
		if _application == None:
			os.environ['ENTIDAD_ID'] = environ['ENTIDAD_ID']
			os.environ['ENTIDAD_DB'] = environ['ENTIDAD_DB']
			os.environ['ENTIDAD_DIR'] = environ['ENTIDAD_DIR']
			_application = get_wsgi_application()
		return _application(environ, start_response)

except Exception as e:
    logger.error('Admin Command Error: %s', ' '.join(sys.argv), exc_info=sys.exc_info())
    raise e	
