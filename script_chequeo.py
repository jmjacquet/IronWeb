# -*- coding: utf-8 -*-
#!/usr/bin/python

# import the MySQLdb and sys modules
import MySQLdb
import sys
host = "opal3.opalstack.com"
user = "gg_ironweb"
passwd = "Sarasa9090!"
UPDATE_DELETE =  True
# BASES_EXCEPTUADAS = ('gg_gestion','gg_configuracion','gg_multeo')
# LISTA_BASES = "SELECT SCHEMA_NAME FROM `SCHEMATA` WHERE (SCHEMA_NAME LIKE 'gg_%') AND (SCHEMA_NAME NOT IN "+str(BASES_EXCEPTUADAS)+");"

lista_dbs = []
connection = MySQLdb.connect (host = host, user = user, passwd = passwd, db = "information_schema")
# cursor = connection.cursor ()
# cursor.execute(LISTA_BASES)
# row = cursor.fetchall()
# # close the cursor object
# cursor.close ()
# # close the connection
# connection.close ()
# lista_dbs = list(row)
lista_dbs = ['ironweb_prueba', 'ironweb_brolcazsrl', 'ironweb_cirugiamf', 'ironweb_cornercorto',
			 'ironweb_digra', 'ironweb_estudioguarrera', 'ironweb_labartoladeco',
			 'ironweb_laboralsaludsf', 'ironweb_sucec']

#SCRIPT_EJECUCION = "INSERT INTO `configuracion_vars` VALUES(1, 'pago_online', 'Variable de PAGO ONLine a Cajero24', NULL, 'N', NULL);"
#SCRIPT_EJECUCION =INSERT INTO `configuracion_vars` VALUES(2, 'NoComercio', 'Variable de Entidad para Cajero24 ', NULL, NULL, NULL);"
#SCRIPT_EJECUCION =INSERT INTO `configuracion_vars` VALUES(3, 'modif_bases_imp', 'Modificación de Bases Imponibles de Períodos pagados', NULL, 'N', NULL);"
#SCRIPT_EJECUCION ="INSERT INTO `configuracion_vars` VALUES(4, 'dri_retenciones', 'Modificación del campo label de Retenciones en Liquidación y Boleta DReI', NULL, NULL, NULL);"
#SCRIPT_EJECUCION = "INSERT INTO `configuracion_vars` VALUES(5, 'dri_cartel_inicio', 'Cartel que aparece al Liquidar DReI', NULL, NULL, NULL);"
#SCRIPT_EJECUCION = "DELETE FROM `django_session`;"
#SCRIPT_EJECUCION = "ALTER TABLE tributo ADD COLUMN CORRER_VENC_FDESDE DATE NULL;"
SCRIPT_EJECUCION = "ALTER TABLE `gral_empresa` DROP COLUMN  `ruta_empresa_media` "
# SCRIPT_EJECUCION = "SELECT count(*) FROM `cpb_comprobante`;"

print "##############################################"
print SCRIPT_EJECUCION

total_bases = len(lista_dbs)
bases_ok = 0

for r in lista_dbs:
	nombre_base = r 
	db = MySQLdb.connect (host = host, user = user, passwd = passwd, db =nombre_base)
	cursor = db.cursor ()
	try:
		cursor.execute(SCRIPT_EJECUCION)
		if UPDATE_DELETE:			
			db.commit()
			print nombre_base+' --> OK'
		else:
			row = cursor.fetchone()
			for f in row:
				print nombre_base+' --> '+str(f)
		bases_ok+=1
	except Exception as e:
		print nombre_base+' --> '+str(e)
	# close the cursor object
	cursor.close ()
	# close the connection
	db.close ()
print "##############################################"
print "SCRIPT EJECUTADO CON EXITO EN %s de %s BASES" % (bases_ok,total_bases)



# exit the program
sys.exit()