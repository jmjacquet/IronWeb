from django.conf.urls import *
from views import *

urlpatterns = patterns('entidades.views',
                       url(r'^clientes/$', ClientesView.as_view(),
                           name="clientes_listado"),
                       url(r'^clientes/cliente_nuevo/$',
                           ClientesCreateView.as_view(), name="cliente_nuevo"),
                       url(r'^clientes/cliente_editar/(?P<id>\d+)/$',
                           ClientesEditView.as_view(), name="cliente_editar"),
                       url(r'^clientes/cliente_eliminar/(?P<id>[\w-]+)/$',
                           ClientesDeleteView, name="cliente_eliminar"),
                       url(r'^clientes/cliente_ver/(?P<id>\d+)/$',
                           ClientesVerView.as_view(), name="cliente_ver"),

                       url(r'^proveedores/$', ProveedoresView.as_view(),
                           name="proveedores_listado"),
                       url(r'^proveedores/proveedor_nuevo/$',
                           ProveedoresCreateView.as_view(), name="proveedor_nuevo"),
                       url(r'^proveedores/proveedor_editar/(?P<id>\d+)/$',
                           ProveedoresEditView.as_view(), name="proveedor_editar"),
                       url(r'^proveedores/proveedor_eliminar/(?P<id>[\w-]+)/$',
                           ProveedoresDeleteView, name="proveedor_eliminar"),
                       url(r'^proveedores/proveedor_ver/(?P<id>\d+)/$',
                           ProveedoresVerView.as_view(), name="proveedor_ver"),

                       url(r'^vendedores/$', VendedoresView.as_view(),
                           name="vendedores_listado"),
                       url(r'^vendedores/vendedor_nuevo/$',
                           VendedoresCreateView.as_view(), name="vendedor_nuevo"),
                       url(r'^vendedores/vendedor_editar/(?P<id>\d+)/$',
                           VendedoresEditView.as_view(), name="vendedor_editar"),
                       url(r'^vendedores/vendedor_eliminar/(?P<id>[\w-]+)/$',
                           VendedoresDeleteView, name="vendedor_eliminar"),
                       url(r'^vendedores/vendedor_ver/(?P<id>\d+)/$',
                           VendedoresVerView.as_view(), name="vendedor_ver"),

                       url(r'^entidad_ver/(?P<id>\d+)/$',
                           EntidadVerView.as_view(), name="entidad_ver"),

                       url(r'^importar_entidades/$', importar_entidades,
                           name="importar_entidades"),
                       )
