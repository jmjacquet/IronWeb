#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar y agregar permisos de trabajos al usuario demo
Ejecutar con: python manage.py shell < verificar_permisos_demo.py
O mejor: python manage.py shell
Luego copiar y pegar el contenido de este script
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggcontable.local")
django.setup()

from usuarios.models import usu_usuario, UsuPermiso

# Buscar el usuario demo
try:
    usuario = usu_usuario.objects.get(usuario='demo')
    print('✓ Usuario demo encontrado: %s (ID: %s)' % (usuario.nombre, usuario.id_usuario))
except usu_usuario.DoesNotExist:
    print('✗ ERROR: Usuario demo no encontrado')
    exit(1)

# Verificar permisos actuales del usuario
print('\nPermisos actuales del usuario demo:')
permisos_actuales = usuario.permisos.all().values_list('permiso_name', flat=True)
if permisos_actuales:
    for permiso in permisos_actuales:
        print('  - %s' % permiso)
else:
    print('  (ningún permiso asignado)')

# Permisos necesarios para ver el menú de trabajos
permisos_necesarios = ['trab_pedidos', 'trab_trabajos', 'trab_colocacion']

print('\nVerificando permisos necesarios:')
permisos_agregados = []
permisos_no_encontrados = []
permisos_ya_tiene = []

for permiso_name in permisos_necesarios:
    try:
        permiso = UsuPermiso.objects.get(permiso_name=permiso_name)
        if permiso in usuario.permisos.all():
            print('  ✓ %s - Ya tiene este permiso' % permiso_name)
            permisos_ya_tiene.append(permiso_name)
        else:
            usuario.permisos.add(permiso)
            print('  ✓ %s - AGREGADO' % permiso_name)
            permisos_agregados.append(permiso_name)
    except UsuPermiso.DoesNotExist:
        print('  ✗ %s - NO EXISTE en la base de datos' % permiso_name)
        permisos_no_encontrados.append(permiso_name)

# Resumen
print('\n' + '='*60)
if permisos_agregados:
    print('✓ Permisos agregados: %s' % ', '.join(permisos_agregados))
if permisos_ya_tiene:
    print('ℹ Permisos que ya tenía: %s' % ', '.join(permisos_ya_tiene))
if permisos_no_encontrados:
    print('✗ Permisos no encontrados en la BD: %s' % ', '.join(permisos_no_encontrados))
    print('\nPara crear estos permisos, necesitas:')
    print('1. Ir al admin de Django o usar la interfaz de usuarios')
    print('2. Crear los permisos con permiso_name: %s' % ', '.join(permisos_no_encontrados))
    print('3. O ejecutar este script nuevamente después de crearlos')

print('\n' + '='*60)
print('Ahora el usuario demo debería poder ver el menú de trabajos')
print('(si todos los permisos fueron agregados o ya existían)')
