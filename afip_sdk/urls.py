# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.AfipSDKTestView.as_view(), name='afip_sdk_test'),
    url(r'^cuit_info/$', views.cuit_info, name='afip_sdk_cuit_info'),
    url(r'^monedas/$', views.monedas, name='afip_sdk_monedas'),
    url(r'^cotizacion/$', views.cotizacion_moneda, name='afip_sdk_cotizacion'),
    url(r'^tipos_comprobante/$', views.tipos_comprobante, name='afip_sdk_tipos_comprobante'),
    url(r'^tipos_documento/$', views.tipos_documento, name='afip_sdk_tipos_documento'),
    url(r'^tipos_iva/$', views.tipos_iva, name='afip_sdk_tipos_iva'),
    url(r'^tipos_tributos/$', views.tipos_tributos, name='afip_sdk_tipos_tributos'),
    url(r'^condicion_iva_receptor/$', views.condicion_iva_receptor, name='afip_sdk_condicion_iva_receptor'),
    url(r'^tipos_concepto/$', views.tipos_concepto, name='afip_sdk_tipos_concepto'),
    url(r'^tipos_opcionales/$', views.tipos_opcionales, name='afip_sdk_tipos_opcionales'),
    url(r'^puntos_venta/$', views.puntos_venta, name='afip_sdk_puntos_venta'),
    url(r'^ultimo_comprobante/$', views.ultimo_comprobante, name='afip_sdk_ultimo_comprobante'),
    url(r'^estado_servidor/$', views.estado_servidor, name='afip_sdk_estado_servidor'),
]
