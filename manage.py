#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.settings")
	os.environ.setdefault("DEBUG", "True")
	os.environ.setdefault("ENTIDAD_DB", "ironweb_410")
	#os.environ.setdefault("ENTIDAD_DB", "gg_ironweb")
	os.environ.setdefault("ENTIDAD_ID", "1")
	os.environ.setdefault("ENTIDAD_DIR", "copyfast")
	os.environ.setdefault("DB_USER", "gg")
	os.environ.setdefault("DB_PASS", "battlehome")
	os.environ.setdefault("EMAIL_HOST_USER", "ironweb_mail")
	os.environ.setdefault("EMAIL_HOST_PASSWORD", "battlehome")
    
	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)



