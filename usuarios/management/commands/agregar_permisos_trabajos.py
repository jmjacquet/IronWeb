# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from usuarios.models import usu_usuario, UsuPermiso


class Command(BaseCommand):
    help = 'Agrega permisos de trabajos al usuario demo'

    def handle(self, *args, **options):
        # Buscar el usuario demo
        try:
            usuario = usu_usuario.objects.get(usuario='demo')
            self.stdout.write(self.style.SUCCESS('Usuario demo encontrado: %s' % usuario.nombre))
        except usu_usuario.DoesNotExist:
            self.stdout.write(self.style.ERROR('Usuario demo no encontrado'))
            return

        # Permisos necesarios para ver el menú de trabajos
        permisos_necesarios = ['trab_pedidos', 'trab_trabajos', 'trab_colocacion']
        
        permisos_agregados = []
        permisos_no_encontrados = []
        
        for permiso_name in permisos_necesarios:
            try:
                # Buscar el permiso por permiso_name
                permiso = UsuPermiso.objects.get(permiso_name=permiso_name)
                
                # Verificar si el usuario ya tiene el permiso
                if permiso in usuario.permisos.all():
                    self.stdout.write(self.style.WARNING('El usuario ya tiene el permiso: %s' % permiso_name))
                else:
                    # Agregar el permiso al usuario
                    usuario.permisos.add(permiso)
                    permisos_agregados.append(permiso_name)
                    self.stdout.write(self.style.SUCCESS('Permiso agregado: %s' % permiso_name))
            except UsuPermiso.DoesNotExist:
                permisos_no_encontrados.append(permiso_name)
                self.stdout.write(self.style.ERROR('Permiso no encontrado en la base de datos: %s' % permiso_name))

        if permisos_agregados:
            self.stdout.write(self.style.SUCCESS('\nPermisos agregados exitosamente: %s' % ', '.join(permisos_agregados)))
        
        if permisos_no_encontrados:
            self.stdout.write(self.style.WARNING('\nPermisos no encontrados en la base de datos: %s' % ', '.join(permisos_no_encontrados)))
            self.stdout.write(self.style.WARNING('Necesitas crear estos permisos en la tabla usu_permiso primero.'))
