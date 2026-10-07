# -*- coding: utf-8 -*-
import json
import logging
import os

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from general.utilidades import empresa_actual
from general.views import VariablesMixin
from afip_sdk.client import AfipSDKClient, AfipSDKError

logger = logging.getLogger(__name__)


class AfipSDKTestView(VariablesMixin, TemplateView):
    template_name = 'afip_sdk/afip_test.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AfipSDKTestView, self).dispatch(*args, **kwargs)


def _get_cuit_empresa(request):
    """Obtiene el CUIT de la empresa activa de la sesion."""
    empresa = empresa_actual(request)
    if not empresa or not empresa.cuit:
        return None
    return empresa.cuit


def _afip_sdk_client(request):
    """Arma un AfipSDKClient para la empresa activa con su cert/key."""
    empresa = empresa_actual(request)
    cert = key = None
    if empresa.fe_crt:
        cert = os.path.join(settings.CERTIFICADOS_PATH, empresa.fe_crt)
    if empresa.fe_key:
        key = os.path.join(settings.CERTIFICADOS_PATH, empresa.fe_key)
    environment = 'dev' if empresa.homologacion else 'prod'
    return AfipSDKClient(
        cuit=empresa.cuit, cert=cert, key=key, environment=environment,
    )


def _json_response(data, status=200):
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        content_type='application/json',
        status=status,
    )


def _error_response(message, status=400):
    return _json_response({'error': message}, status=status)


@login_required
@require_GET
def cuit_info(request):
    """Consulta el padron de AFIP para un CUIT.

    GET /afip_sdk/cuit_info/?cuit=20300000000

    Devuelve los datos del contribuyente mas la categoria fiscal
    derivada de sus impuestos inscriptos.
    """
    cuit = request.GET.get('cuit', '').strip()
    if not cuit:
        return _error_response('Parametro cuit requerido')

    cuit = cuit.replace('-', '')
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)

    try:
        client = _afip_sdk_client(request)
        data = client.get_taxpayer_details(cuit)
    except AfipSDKError as e:
        logger.warning('AFIP SDK error en cuit_info: %s', e.message)
        return _error_response(e.message, 502)

    if data is None:
        return _json_response(None)

    # Mapear impuestos a categoria fiscal (misma logica que general/views.py)
    impuestos = data.get('impuesto', []) or []
    ids = []
    for imp in impuestos:
        if isinstance(imp, dict):
            ids.append(imp.get('idImpuesto'))
    if 10 in ids or 11 in ids or 30 in ids:
        cat = 1  # IVA Responsable Inscripto
    elif 20 in ids:
        cat = 6  # Monotributista
    elif 32 in ids:
        cat = 4  # IVA Sujeto Exento
    elif 33 in ids:
        cat = 2  # Responsable No Inscripto
    else:
        cat = 5  # Consumidor Final
    data['categoria'] = cat

    return _json_response(data)


@login_required
@require_GET
def monedas(request):
    """Tipos de monedas disponibles en AFIP.

    GET /afip_sdk/monedas/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_currencies()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def cotizacion_moneda(request):
    """Cotizacion de una moneda en una fecha.

    GET /afip_sdk/cotizacion/?moneda=DOL&fecha=20250221
    """
    moneda = request.GET.get('moneda', '').strip().upper()
    fecha = request.GET.get('fecha', '').strip()
    if not moneda or not fecha:
        return _error_response('Parametros moneda y fecha requeridos')

    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_exchange_rate(moneda, fecha)
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def tipos_comprobante(request):
    """Tipos de comprobantes disponibles.

    GET /afip_sdk/tipos_comprobante/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_voucher_types()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def tipos_documento(request):
    """Tipos de documentos disponibles.

    GET /afip_sdk/tipos_documento/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_document_types()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def tipos_iva(request):
    """Tipos de alicuotas IVA disponibles.

    GET /afip_sdk/tipos_iva/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_aliquot_types()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def tipos_tributos(request):
    """Tipos de tributos disponibles.

    GET /afip_sdk/tipos_tributos/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_tax_types()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def condicion_iva_receptor(request):
    """Condiciones frente al IVA del receptor.

    GET /afip_sdk/condicion_iva_receptor/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_iva_condition_types()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def tipos_concepto(request):
    """Tipos de conceptos disponibles.

    GET /afip_sdk/tipos_concepto/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_concept_types()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def tipos_opcionales(request):
    """Tipos de opcionales disponibles.

    GET /afip_sdk/tipos_opcionales/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_option_types()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def puntos_venta(request):
    """Puntos de venta configurados en AFIP.

    GET /afip_sdk/puntos_venta/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_sales_points()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)


@login_required
@require_GET
def ultimo_comprobante(request):
    """Ultimo comprobante autorizado en un punto de venta y tipo.

    GET /afip_sdk/ultimo_comprobante/?pto_vta=1&tipo=6
    """
    pto_vta = request.GET.get('pto_vta')
    tipo = request.GET.get('tipo')
    if not pto_vta or not tipo:
        return _error_response('Parametros pto_vta y tipo requeridos')

    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.get_last_voucher(int(pto_vta), int(tipo))
    except (ValueError, AfipSDKError) as e:
        return _error_response(str(e), 502)
    return _json_response(data)


@login_required
@require_GET
def estado_servidor(request):
    """Estado del servidor WSFE.

    GET /afip_sdk/estado_servidor/
    """
    empresa_cuit = _get_cuit_empresa(request)
    if not empresa_cuit:
        return _error_response('No se encontro CUIT de empresa activa', 500)
    try:
        client = _afip_sdk_client(request)
        data = client.wsfe_server_status()
    except AfipSDKError as e:
        return _error_response(e.message, 502)
    return _json_response(data)
