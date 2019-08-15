# -*- coding: utf-8 -*-
import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.development")
	os.environ.setdefault("ENTIDAD_DB", "ironweb_410")
	os.environ.setdefault("ENTIDAD_ID", "000")
	os.environ.setdefault("ENTIDAD_DIR", "copyfast")
    
	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)



