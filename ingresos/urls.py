from django.conf.urls import *

from views import *

urlpatterns = patterns(
    "ingresos.views",
    url(r"^buscarDatosProd/$", "buscarDatosProd", name="buscarDatosProd"),
    url(r"^ventas/$", CPBSVentasList.as_view(), name="cpb_venta_listado"),
    url(r"^ventas/nuevo/$", CPBVentaCreateView.as_view(), name="cpb_venta_nuevo"),
    url(
        r"^ventas/nuevoPresup/(?P<id>\d+)/$",
        CPBVentaPresupCreateView.as_view(),
        name="cpb_venta_presup_nuevo",
    ),
    url(r"^ventas/nuevoNC/(?P<id>\d+)/$", CPBVentaNCCreateView.as_view(), name="cpb_venta_nc_nuevo"),
    url(
        r"^ventas/nuevoOP/(?P<id>\d+)/$", CPBVentaOPCreateView.as_view(), name="cpb_venta_orden_pedido_nuevo"
    ),
    url(r"^ventas/editar/(?P<id>\d+)/$", CPBVentaEditView.as_view(), name="cpb_venta_editar"),
    url(r"^ventas/eliminar/(?P<id>\d+)/$", CPBVentaDeleteView, name="cpb_venta_eliminar"),
    url(r"^ventas/unificar/$", CPBVentaUnificarView.as_view(), name="cpb_venta_unificar"),
    url(r"^ventas/clonar/(?P<id>\d+)/$", CPBVentaClonarCreateView.as_view(), name="cpb_venta_clonar"),
    url(r"^remitos/$", CPBRemitoViewList.as_view(), name="cpb_remito_listado"),
    url(r"^remitos/nuevo/$", CPBRemitoCreateViewNew.as_view(), name="cpb_remito_nuevo_vacio"),
    url(r"^remitos/nuevo/(?P<id>\d+)/$", CPBRemitoCreateView.as_view(), name="cpb_remito_nuevo"),
    url(r"^remitos/editar/(?P<id>\d+)/$", CPBRemitoEditView.as_view(), name="cpb_remito_editar"),
    url(r"^remitos/eliminar/(?P<id>\d+)/$", CPBRemitoDeleteView, name="cpb_remito_eliminar"),
    url(r"^cobranza/$", CPBRecCobranzaViewList.as_view(), name="cpb_rec_cobranza_listado"),
    url(r"^cobranza/nuevo/$", CPBRecCobranzaCreateView.as_view(), name="cpb_rec_cobranza_nuevo"),
    url(r"^cobranza/editar/(?P<id>\d+)/$", CPBRecCobranzaEditView.as_view(), name="cpb_rec_cobranza_editar"),
    url(r"^cobranza/eliminar/(?P<id>\d+)/$", CPBRecCobranzaDeleteView, name="cpb_rec_cobranza_eliminar"),
    url(
        r"^cpb_rec_cobranza/nuevo_cobro/$", CPBCobrarCreateView.as_view(), name="cpb_rec_cobranza_nuevo_cobro"
    ),
    url(r"^cobranza/comprobantes/$", CPBCobrosSeleccionarView, name="cpb_cobro_comprobantes"),
    url(r"^presup/$", CPBPresupViewList.as_view(), name="cpb_presup_listado"),
    url(r"^presup/nuevo/$", CPBPresupCreateView.as_view(), name="cpb_presup_nuevo"),
    url(r"^presup/nuevo_lite/$", CPBPresupLiteCreateView.as_view(), name="cpb_presup_lite_nuevo"),
    url(r"^presup/editar/(?P<id>\d+)/$", CPBPresupEditView.as_view(), name="cpb_presup_editar"),
    url(r"^presup/eliminar/(?P<id>\d+)/$", CPBPresupDeleteView, name="cpb_presup_eliminar"),
    url(r"^presup_aprobacion/(?P<id>\d+)/(?P<estado>\d+)/$", presup_aprobacion, name="presup_aprobacion"),
    url(
        r"^presup_anular_reactivar/(?P<id>\d+)/(?P<estado>\d+)/$",
        presup_anular_reactivar,
        name="presup_anular_reactivar",
    ),
    url(r"^liqprod/nuevo/$", CPBLiqProdCreateView.as_view(), name="cpb_liqprod_nuevo"),
    url(r"^liqprod/editar/(?P<id>\d+)/$", CPBLiqProdEditView.as_view(), name="cpb_liqprod_editar"),
    url(r"^liqprod/eliminar/(?P<id>\d+)/$", CPBLiqProdDeleteView, name="cpb_liqprod_eliminar"),
)
