# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.conf import settings
import os
from views import *
from django.views.generic import RedirectView,TemplateView
from django.contrib import admin

# Uncomment the next two lines to enable the admin:


urlpatterns = patterns('general.views',
	
    # url(r'^estudios/$', EstudiosView.as_view(),name="padrones_estudio"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', PrincipalView.as_view(),name="principal"),
    url(r'^buscarDatosAPICUIT/$', 'buscarDatosAPICUIT', name='buscarDatosAPICUIT'),
    url(r'^buscarDatosEmpresa/$', 'buscarDatosEmpresa', name='buscarDatosEmpresa'),
    url(r'^recargar_clientes/$', recargar_clientes, name='recargar_clientes'),
    url(r'^recargar_vendedores/$', recargar_vendedores, name='recargar_vendedores'),
    url(r'^recargar_proveedores/$', recargar_proveedores, name='recargar_proveedores'),
    url(r'^recargar_productos/(?P<tipo>\d+)/$', recargar_productos, name='recargar_productos'),

	url(r'^entidad_baja_reactivar/(?P<id>\d+)/$', entidad_baja_reactivar, name='entidad_baja_reactivar'),

    url(r'^empresa/$', EmpresaView.as_view(), name="empresa_listado"),
    url(r'^empresa/empresa_editar/(?P<id>\d+)/$', EmpresaEditView.as_view(), name="empresa_editar"),
	
	url(r'^tareas/$', TareasView.as_view(), name="tareas_listado"),
    url(r'^tareas/tareas_nueva/$', TareasCreateView.as_view(), name="tareas_nueva"),
    url(r'^tareas/tareas_editar/(?P<id>\d+)/$', TareasEditView.as_view(), name="tareas_editar"),
    url(r'^tareas/tareas_eliminar/(?P<id>\d+)/$', TareasDeleteView, name="tareas_eliminar"),
    # url(r'^lista_precios/$', ListaPreciosView.as_view(),name="lista_precios"),


    url(r'^chequear_email/(?P<id>\d+)/$', chequear_email, name="chequear_email"),
    )