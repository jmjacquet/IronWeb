from django.conf.urls import *
from django.conf import settings
import os
from views import *
from django.views.generic import RedirectView,TemplateView

urlpatterns = patterns('productos.views',
	
    url(r'^coeficiente_iva/$', coeficiente_iva,name="coeficiente_iva"),

    url(r'^$', ProductosView.as_view(),name="productos_listado"),
    url(r'^producto_nuevo/$', ProductosCreateView.as_view(), name="producto_nuevo"),
    url(r'^producto_editar/(?P<id>\d+)/$', ProductosEditView.as_view(), name="producto_editar"),
    url(r'^producto_eliminar/(?P<id>[\w-]+)/$', ProductosDeleteView.as_view(), name="producto_eliminar"),
    url(r'^producto_ver/(?P<id>\d+)/$', ProductosVerView.as_view(), name="producto_ver"),
    
    url(r'^categorias/$', CategoriasView.as_view(),name="categorias_listado"),
    url(r'^categorias/categoria_nuevo/$', CategoriasCreateView.as_view(), name="categoria_nuevo"),
    url(r'^categorias/categoria_editar/(?P<id>\d+)/$', CategoriasEditView.as_view(), name="categoria_editar"),
    url(r'^categorias/categoria_eliminar/(?P<id>[\w-]+)/$', CategoriasDeleteView.as_view(), name="categoria_eliminar"),
    url(r'^categorias/categoria_ver/(?P<id>\d+)/$', CategoriasVerView.as_view(), name="categoria_ver"),

    url(r'^depositos/$', DepositosView.as_view(),name="depositos_listado"),
    url(r'^depositos/depositos_nuevo/$', DepositosCreateView.as_view(), name="depositos_nuevo"),
    url(r'^depositos/depositos_editar/(?P<id>\d+)/$', DepositosEditView.as_view(), name="depositos_editar"),
    url(r'^depositos/depositos_eliminar/(?P<id>[\w-]+)/$', DepositosDeleteView.as_view(), name="depositos_eliminar"),

    url(r'^lista_precios/$', LPreciosView.as_view(),name="lista_precios_listado"),
    url(r'^lista_precios/lista_precios_nuevo/$', LPreciosCreateView.as_view(), name="lista_precios_nuevo"),
    url(r'^lista_precios/lista_precios_editar/(?P<id>\d+)/$', LPreciosEditView.as_view(), name="lista_precios_editar"),
    url(r'^lista_precios/lista_precios_eliminar/(?P<id>[\w-]+)/$', LPreciosDeleteView.as_view(), name="lista_precios_eliminar"),

    url(r'^producto_baja_reactivar/(?P<id>\d+)/$', producto_baja_reactivar, name='producto_baja_reactivar'),
    url(r'^categoria_baja_reactivar/(?P<id>\d+)/$', categoria_baja_reactivar, name='categoria_baja_reactivar'),
    url(r'^deposito_baja_reactivar/(?P<id>\d+)/$', deposito_baja_reactivar, name='deposito_baja_reactivar'),
    url(r'^lprecios_baja_reactivar/(?P<id>\d+)/$', lprecios_baja_reactivar, name='lprecios_baja_reactivar'),

    url(r'^prod_precios/$', ProdLPreciosView.as_view(),name="prod_precios_listado"),
    url(r'^prod_precios_editar/(?P<id>\d+)/$', ProdLPreciosEditView.as_view(),name="prod_precios_editar"),
    url(r'^prod_precios_actualizar/$', prod_precios_actualizar,name="prod_precios_actualizar"),

    url(r'^prod_stock/$', ProdStockView.as_view(),name="prod_stock_listado"),
    url(r'^prod_stock_nuevo/$', prod_stock_nuevo,name="prod_stock_nuevo"),
    url(r'^prod_stock_editar/(?P<id>\d+)/$', ProdStockEditView.as_view(),name="prod_stock_editar"),
    url(r'^prod_stock_actualizar/$', prod_stock_actualizar,name="prod_stock_actualizar"),

    url(r'^prod_stock_generar/$', prod_stock_generar,name="prod_stock_generar"),

    )