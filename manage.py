#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.settings")
	os.environ.setdefault("ENTIDAD_DB", "ironweb_412")
	os.environ.setdefault("ENTIDAD_ID", "412")
	os.environ.setdefault("ENTIDAD_DIR", "prueba")
    
	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)



