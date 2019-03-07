from django.conf.urls import *
from django.conf import settings
import os
from views import *
from django.views.generic import RedirectView,TemplateView

urlpatterns = patterns('egresos.views',
	
    url(r'^buscarDatosProd/$', 'buscarDatosProd', name='buscarDatosProd'),

    # url(r'^estudios/$', EstudiosView.as_view(),name="padrones_estudio"),
    url(r'^compras/$',  CPBCompraViewList.as_view(),name="cpb_compra_listado"),
    url(r'^compras/nuevo/$', CPBCompraCreateView.as_view(), name="cpb_compra_nuevo"),    
    url(r'^compras/editar/(?P<id>\d+)/$', CPBCompraEditView.as_view(), name="cpb_compra_editar"),
    url(r'^compras/eliminar/(?P<id>\d+)/$', CPBCompraDeleteView, name="cpb_compra_eliminar"),
    url(r'^compras/clonar/(?P<id>\d+)/$', CPBCompraClonarCreateView.as_view(), name="cpb_compra_clonar"),    

    
    url(r'^remitos/$',  CPBRemitoCViewList.as_view(),name="cpb_remitoc_listado"),
    url(r'^remitos/nuevo/(?P<id>\d+)/$', CPBRemitoCCreateView.as_view(), name="cpb_remitoc_nuevo"),    
    url(r'^remitos/editar/(?P<id>\d+)/$', CPBRemitoCEditView.as_view(), name="cpb_remitoc_editar"),
    url(r'^remitos/eliminar/(?P<id>\d+)/$', CPBRemitoCDeleteView, name="cpb_remitoc_eliminar"),

    url(r'^pagos/$',  CPBPagosViewList.as_view(),name="cpb_pago_listado"),
    url(r'^pagos/nuevo/$', CPBPagoCreateView.as_view(), name="cpb_pago_nuevo"),    
    url(r'^pagos/editar/(?P<id>\d+)/$', CPBPagoEditView.as_view(), name="cpb_pago_editar"),
    url(r'^pagos/eliminar/(?P<id>\d+)/$', CPBPagoDeleteView, name="cpb_pago_eliminar"),

    url(r'^cpb_pago/nuevo_pago/$', CPBPagarCreateView.as_view(), name="cpb_rec_pago_nuevo_pago"),    
    url(r'^pagos/comprobantes/$',  CPBPagosSeleccionarView,name="cpb_pago_comprobantes"), 
  
   
      
    )