# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.conf import settings
import os
from views import *
from django.views.generic import RedirectView,TemplateView

# Uncomment the next two lines to enable the admin:


urlpatterns = [
	url(r'^orden_pedido/$', OPView.as_view(), name="orden_pedido_listado"),
    url(r'^orden_pedido/nueva/$', OPCreateView.as_view(), name="orden_pedido_nuevo"),
    url(r'^orden_pedido/editar/(?P<id>\d+)/$', OPEditView.as_view(), name="orden_pedido_editar"),
    url(r'^orden_pedido/eliminar/(?P<id>[\w-]+)/$', OPDeleteView.as_view(), name="orden_pedido_eliminar"),
    url(r'^orden_pedido/editarEstado/(?P<id>\d+)/$', OPEstadoEditView.as_view(), name="orden_pedido_editar_estado"),
    url(r'^orden_pedido/nuevoPresup/(?P<id>\d+)/$', OPPresupCreateView.as_view(), name="orden_pedido_presup_nuevo"),  
    url(r'^orden_pedido_ver/(?P<id>\d+)/$', OPVerView.as_view(), name="orden_pedido_ver"), 
    
    url(r'^orden_trabajo/$', OTView.as_view(), name="orden_trabajo_listado"),
    url(r'^orden_trabajo/nuevo/(?P<id>\d+)/$', OTCreateView.as_view(), name="orden_trabajo_nuevo"),
    url(r'^orden_trabajo/editar/(?P<id>\d+)/$', OTEditView.as_view(), name="orden_trabajo_editar"),
    url(r'^orden_trabajo/eliminar/(?P<id>[\w-]+)/$', OTDeleteView.as_view(), name="orden_trabajo_eliminar"),
    url(r'^orden_trabajo_ver/(?P<id>\d+)/$', OTVerView.as_view(), name="orden_trabajo_ver"), 
    url(r'^orden_trabajo/editarEstado/(?P<id>\d+)/$', OTEstadoEditView.as_view(), name="orden_trabajo_editar_estado"),

    url(r'^orden_colocacion/$', OCView.as_view(), name="orden_colocacion_listado"),
    url(r'^orden_colocacion/nuevo/(?P<id>\d+)/$', OCCreateView.as_view(), name="orden_colocacion_nuevo"),
    url(r'^orden_colocacion/editar/(?P<id>\d+)/$', OCEditView.as_view(), name="orden_colocacion_editar"),
    url(r'^orden_colocacion/eliminar/(?P<id>[\w-]+)/$', OCDeleteView.as_view(), name="orden_colocacion_eliminar"),
    url(r'^orden_colocacion_ver/(?P<id>\d+)/$', OCVerView.as_view(), name="orden_colocacion_ver"), 
    url(r'^orden_colocacion/editarEstado/(?P<id>\d+)/$', OCEstadoEditView.as_view(), name="orden_colocacion_editar_estado"),

    url(r'^imprimirNotaPedido/(?P<id>\d+)/$',imprimirNotaPedido,name="imprimirNotaPedido"),
    url(r'^imprimirOrdenTrabajo/(?P<id>\d+)/$',imprimirOrdenTrabajo,name="imprimirOrdenTrabajo"),
    url(r'^imprimirOrdenColocacion/(?P<id>\d+)/$',imprimirOrdenColocacion,name="imprimirOrdenColocacion"),


    ]

