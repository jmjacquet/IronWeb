try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *
from django.conf import settings
import os
from views import *

urlpatterns = [
	 
 url(r'^cta_cte_clientes/(?P<id>\d+)/$', cta_cte_clientes, name="cta_cte_clientes"),    
 url(r'^cta_cte_clientes/$', cta_cte_clientes, name="cta_cte_clientes"),  
 url(r'^saldos_clientes/$', saldos_clientes.as_view(), name="saldos_clientes"),  

 url(r'^cta_cte_proveedores/(?P<id>\d+)/$', cta_cte_proveedores, name="cta_cte_proveedores"),    
 url(r'^cta_cte_proveedores/$', cta_cte_proveedores, name="cta_cte_proveedores"), 
 url(r'^saldos_proveedores/$', saldos_proveedores.as_view(), name="saldos_proveedores"),   

 url(r'^libro_iva_ventas/$', libro_iva_ventas, name="libro_iva_ventas"),   
 url(r'^libro_iva_compras/$', libro_iva_compras, name="libro_iva_compras"),

 url(r'^caja_diaria/$', caja_diaria.as_view(), name="caja_diaria"),   
 
 url(r'^saldos_cuentas/$', saldos_cuentas.as_view(), name="saldos_cuentas"),   

 url(r'^vencimientos_cpbs/$', vencimientos_cpbs.as_view(),name="vencimientos_cpbs"),

 url(r'^seguimiento_cheques/$', seguimiento_cheques.as_view(), name="seguimiento_cheques"),   

 url(r'^movimientos_stock/$', ProdHistoricoView.as_view(),name="movimientos_stock"),

 url(r'^rankings/$', RankingsView.as_view() ,name="rankings"), 

 url(r'^reporte_retenciones_imp/$', reporte_retenciones_imp, name="reporte_retenciones_imp"),

 url(r'^costo_producto_vendido/$', costo_producto_vendidoView.as_view(), name="costo_producto_vendido"),

 url(r'^comisiones_vendedores/$', comisiones_vendedoresView.as_view(),name="comisiones_vendedores"),

]