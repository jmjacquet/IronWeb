# -*- coding: utf-8 -*-
import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.local")
	# os.environ.setdefault("ENTIDAD_DB", "ironweb_prueba")
	os.environ.setdefault("ENTIDAD_DB", "ironweb_cornercorto")
	os.environ.setdefault("ENTIDAD_ID", "1")
	os.environ.setdefault("ENTIDAD_DIR", "prueba")
    
	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)



