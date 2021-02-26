#/usr/bin/env python
# coding: utf-8

"""
	Filtering logs
"""
import re
#[23/Feb/2021 09:16:39] ERROR [django.request:256] Internal Server Error:

import pprint


def encabezado(text):
    #return re.match(r'\[\d{1,2}/\w{1,3}/\d{1,4} \d{1,2}:\d{1,2}:\d{1,2}\]',text)
    return re.match(r'\[\d{1,2}/Feb/\d{1,4} \d{1,2}:\d{1,2}:\d{1,2}\]',text)

def log_parser():
	try:
		dicc = {}
		ruta = ''
		with open('errores.log') as in_file:
			for line in in_file:
				
				if encabezado(line):
					fecha,ruta = line.split("ERROR [django.request:256] Internal Server Error:")
					dicc[ruta] = []
				else:
					dicc[ruta].append(line)
			
			pprint.pprint([dicc[x][-3:] for x in dicc])
	except Exception as e:
		print e


if __name__ == '__main__':
	log_parser()


