from django.contrib import admin
from ggcontable.settings import *
from .models import *

class PermisosAdmin(admin.ModelAdmin):
    list_display = ('permiso_name','permiso','grupo','categoria')
    search_fields = ['permiso_name','permiso']


admin.site.register(UsuPermiso,PermisosAdmin)
admin.site.register(UsuGrupo)
admin.site.register(UsuCategPermisos)
