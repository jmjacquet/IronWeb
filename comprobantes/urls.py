from django.conf.urls import *
from django.conf import settings
import os
from views import *
from django.views.generic import RedirectView,TemplateView

urlpatterns = patterns('comprobantes.views',
	
    url(r'^buscarDatosEntidad/$', 'buscarDatosEntidad', name='buscarDatosEntidad'),
    url(r'^buscarDatosProd/$', 'buscarDatosProd', name='buscarDatosProd'),
    url(r'^buscarDatosCPB/$', 'buscarDatosCPB', name='buscarDatosCPB'),
    url(r'^verifCobranza/$', verifCobranza,name="verifCobranza"),
    url(r'^verifUnificacion/$', verifUnificacion,name="verifUnificacion"),
    url(r'^setearLetraCPB/$', 'setearLetraCPB', name='setearLetraCPB'),        
    url(r'^ultimp_nro_cpb_ajax/$', 'ultimp_nro_cpb_ajax', name='ultimp_nro_cpb_ajax'),        
    url(r'^setearCta_FP/$', 'setearCta_FP', name='setearCta_FP'),        

    url(r'^bancos/$', BancosView.as_view(),name="bancos_listado"),
    url(r'^bancos/bancos_nuevo/$', BancosCreateView.as_view(), name="bancos_nuevo"),
    url(r'^bancos/bancos_editar/(?P<id>\d+)/$', BancosEditView.as_view(), name="bancos_editar"),
    url(r'^bancos/bancos_eliminar/(?P<id>[\w-]+)/$', BancosDeleteView.as_view(), name="bancos_eliminar"),

    url(r'^percimp/$', PercImpView.as_view(),name="percimp_listado"),
    url(r'^percimp/percimp_nuevp/$', PercImpCreateView.as_view(), name="percimp_nuevo"),
    url(r'^percimp/percimp_editar/(?P<id>\d+)/$', PercImpEditView.as_view(), name="percimp_editar"),
    url(r'^percimp/percimp_eliminar/(?P<id>[\w-]+)/$', PercImpDeleteView.as_view(), name="percimp_eliminar"),

    url(r'^retenc/$', RetencView.as_view(),name="retenc_listado"),
    url(r'^retenc/retenc_nuevp/$', RetencCreateView.as_view(), name="retenc_nuevo"),
    url(r'^retenc/retenc_editar/(?P<id>\d+)/$', RetencEditView.as_view(), name="retenc_editar"),
    url(r'^retenc/retenc_eliminar/(?P<id>[\w-]+)/$', RetencDeleteView.as_view(), name="retenc_eliminar"),

    url(r'^formapago/$', FPView.as_view(),name="formapago_listado"),
    url(r'^formapago/formapago_nuevo/$', FPCreateView.as_view(), name="formapago_nuevo"),
    url(r'^formapago/formapago_editar/(?P<id>\d+)/$', FPEditView.as_view(), name="formapago_editar"),
    url(r'^formapago/formapago_eliminar/(?P<id>[\w-]+)/$', FPDeleteView.as_view(), name="formapago_eliminar"),

    url(r'^imprimirFactura/(?P<id>\d+)/$',imprimirFactura,name="imprimirFactura"),
    url(r'^imprimirRemito/(?P<id>\d+)/$',imprimirRemito,name="imprimirRemito"),
    url(r'^imprimirPresupuesto/(?P<id>\d+)/$',imprimirPresupuesto,name="imprimirPresupuesto"),
    url(r'^imprimirCobranza/(?P<id>\d+)/$',imprimirCobranza,name="imprimirCobranza"),
    url(r'^imprimirCobranzaCtaCte/(?P<id>\d+)/$',imprimirCobranzaCtaCte,name="imprimirCobranzaCtaCte"),
    url(r'^imprimirPago/(?P<id>\d+)/$',imprimirPago,name="imprimirPago"),

    url(r'^mandarEmail/(?P<id>\d+)/$',mandarEmail,name="mandarEmail"),

    url(r'^movimientos/$', MovInternosViewList.as_view(),name="movimientos_listado"),
    url(r'^movimientos/movimientos_nuevo/$', MovInternosCreateView.as_view(), name="movimientos_nuevo"),
    url(r'^movimientos/movimientos_editar/(?P<id>\d+)/$', MovInternosEditView.as_view(), name="movimientos_editar"),
    url(r'^movimientos/movimientos_eliminar/(?P<id>[\w-]+)/$', MovInternosDeleteView, name="movimientos_eliminar"),    

    url(r'^comprobante_ver/(?P<id>\d+)/$', ComprobantesVerView.as_view(), name="comprobante_ver"),       
    url(r'^recibo_ver/(?P<id>\d+)/$', RecibosVerView.as_view(), name="recibo_ver"),       
    url(r'^orden_pago_ver/(?P<id>\d+)/$', OrdenPagoVerView.as_view(), name="orden_pago_ver"),       
    url(r'^ncredndeb_ver/(?P<id>\d+)/$', NCNDVerView.as_view(), name="ncredndeb_ver"),       
    url(r'^remito_ver/(?P<id>\d+)/$', RemitoVerView.as_view(), name="remito_ver"),       
    url(r'^presup_ver/(?P<id>\d+)/$', PresupVerView.as_view(), name="presup_ver"),       
    # url(r'^movim_ver/(?P<id>\d+)/$', MovimVerView.as_view(), name="movim_ver"),       
    
    url(r'^cpb_anular_reactivar/(?P<id>\d+)/(?P<estado>\d+)/$', cpb_anular_reactivar, name='cpb_anular_reactivar'),
    url(r'^cpbs_anular/$',  cpbs_anular,name="cpbs_anular"),
    url(r'^cpb_editar_seguimiento/(?P<id>\d+)/$', EditarSeguimientoView.as_view(), name="cpb_editar_seguimiento"),     
    url(r'^cpb_facturar/(?P<id>\d+)/(?P<nro>\d+)/$',  cpb_facturar,name="cpb_facturar"),
    url(r'^cpb_facturar_afip/$',  cpb_facturar_afip,name="cpb_facturar_afip"),
    url(r'^cpb_facturar_afip_id/(?P<id>\d+)/$',  cpb_facturar_afip_id,name="cpb_facturar_afip_id"),

    url(r'^eliminar_detalles_fp_huerfanos/$', eliminar_detalles_fp_huerfanos, name="eliminar_detalles_fp_huerfanos"),   
    url(r'^recalcular_cpbs/$', recalcular_cpbs, name="recalcular_cpbs"),   
    url(r'^recalcular_precios/$', recalcular_precios, name="recalcular_precios"),  
    url(r'^recalcular_cobranzas/$', recalcular_cobranzas, name="recalcular_cobranzas"),   
    url(r'^recalcular_compras/$', recalcular_compras, name="recalcular_compras"),   
    url(r'^recalcular_presupuestos/$', recalcular_presupuestos, name="recalcular_presupuestos"),   


    url(r'^pto_vta/$', PtoVtaView.as_view(),name="pto_vta_listado"),
    url(r'^pto_vta/pto_vta_nuevo/$', PtoVtaCreateView.as_view(), name="pto_vta_nuevo"),
    url(r'^pto_vta/pto_vta_editar/(?P<id>\d+)/$', PtoVtaEditView.as_view(), name="pto_vta_editar"),
    # url(r'^pto_vta/pto_vta_eliminar/(?P<id>[\w-]+)/$', PtoVtaDeleteView.as_view(), name="pto_vta_eliminar"),
    url(r'^pto_vta_baja_reactivar/(?P<id>\d+)/$', pto_vta_baja_reactivar, name='pto_vta_baja_reactivar'),
    url(r'^pto_vta/pto_vta_numero_cambiar/(?P<id>\d+)/(?P<nro>\d+)/$', pto_vta_numero_cambiar, name="pto_vta_numero_cambiar"),
    
    url(r'^disponibilidades/$', DispoView.as_view(),name="disponibilidades_listado"),
    url(r'^disponibilidades/disponibilidades_nuevo/$', DispoCreateView.as_view(), name="disponibilidades_nuevo"),
    url(r'^disponibilidades/disponibilidades_editar/(?P<id>\d+)/$', DispoEditView.as_view(), name="disponibilidades_editar"),
    url(r'^disponibilidades/disponibilidades_eliminar/(?P<id>[\w-]+)/$', DispoDeleteView.as_view(), name="disponibilidades_eliminar"),
    url(r'^disponibilidades/(?P<id>\d+)/$', dispo_baja_reactivar, name='dispo_baja_reactivar'),    

    url(r'^seleccionar_cheques/$',  SeleccionarChequesView,name="seleccionar_cheques"), 
    url(r'^cobrar_depositar_cheques/$',  CobrarDepositarChequesView,name="cobrar_depositar_cheques"), 

    url(r'^imprimir_detalles/$',  imprimir_detalles,name="imprimir_detalles"), 

    url(r'^imprimirFacturaHTML/(?P<id>\d+)/$',imprimirFacturaHTML,name="imprimirFacturaHTML"),
    
    )