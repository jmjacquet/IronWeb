# -*- coding: utf-8 -*-
import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.local")
	os.environ.setdefault("ENTIDAD_DB", "ironweb_sucec")
	# os.environ.setdefault("ENTIDAD_DB", "ironweb_420")
	os.environ.setdefault("ENTIDAD_ID", "000")
	os.environ.setdefault("ENTIDAD_DIR", "prueba")
    
	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)



