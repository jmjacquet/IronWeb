from django.conf.urls import *
from django.conf import settings
import os
from .views import *
from django.views.generic import RedirectView,TemplateView

# Uncomment the next two lines to enable the admin:


urlpatterns = [
	
  url(r'^password/$', password,name="password"),
  url(r'^cambiar_password/$', cambiar_password, name='cambiar_password'),
  url(r'^usuarios_conectados/$', get_usuarios_conectados, name='usuarios_conectados'),
  
  url(r'^$', UsuarioList.as_view(),name="usuarios"),
  url(r'^usuarios/nuevo/$', UsuarioCreateView, name="usuarios_nuevo"),
  url(r'^usuarios/editar/(?P<id>\d+)/$', UsuarioEditView, name="usuarios_editar"),
  # url(r'^usuarios/eliminar/(?P<id>[\w-]+)/$', UsuarioDeleteView.as_view(), name="usuarios_eliminar"),

  url(r'^usuarios/baja_reactivar/(?P<id>\d+)/$', usuarios_baja_reactivar, name='usuarios_baja_reactivar'),
    
]
