# -*- coding: utf-8 -*-
import json
import logging
import os

try:
    from urllib2 import Request, urlopen, HTTPError, URLError
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

from django.conf import settings

logger = logging.getLogger(__name__)

AFIP_SDK_API_URL = 'https://app.afipsdk.com/api/v1'
AFIP_SDK_SDK_VERSION = '1.2.0'
AFIP_SDK_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)


class AfipSDKError(Exception):
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super(AfipSDKError, self).__init__(message)


class AfipSDKClient(object):
    """
    Cliente REST para AFIP SDK (https://app.afipsdk.com).

    Usa el access_token (AFIP_SDK_API_KEY) para autenticarse y delega
    toda la gestion del TA (token+sign) al servicio de AFIP SDK.

    Uso basico::

        client = AfipSDKClient(cuit='20300000000')
        monedas = client.get_currencies()
    """

    def __init__(self, cuit, environment=None, access_token=None, cert=None,
                 key=None):
        """
        Args:
            cuit: CUIT del contribuyente (str o int, sin guiones).
            environment: 'dev' o 'prod'. Por defecto 'dev'.
            access_token: Token de AFIP SDK. Si es None, se lee de
                          AFIP_SDK_API_KEY en settings.
            cert: Certificado del contribuyente. Puede ser el contenido PEM,
                  un alias ya registrado en la consola de AFIP SDK o la ruta
                  a un archivo local con el certificado (se lee su contenido).
            key: Clave privada del contribuyente. Acepta los mismos formatos
                 que cert.
        """
        self.cuit = str(cuit).replace('-', '')
        self.environment = environment or 'dev'
        self.access_token = access_token or getattr(
            settings, 'AFIP_SDK_API_KEY', ''
        )
        self.cert = cert
        self.key = key
        if not self.access_token:
            raise AfipSDKError(
                'AFIP_SDK_API_KEY no configurado en settings o .env'
            )

    def _request(self, endpoint, payload):
        """POST a la API de AFIP SDK."""
        url = '%s/%s' % (AFIP_SDK_API_URL, endpoint)
        data = json.dumps(payload).encode('utf-8')

        req = Request(url, data=data)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', AFIP_SDK_USER_AGENT)
        req.add_header('Authorization', 'Bearer %s' % self.access_token)
        req.add_header('sdk-version-number', AFIP_SDK_SDK_VERSION)
        req.add_header('sdk-library', 'python')
        req.add_header('sdk-environment', self.environment)

        try:
            resp = urlopen(req, timeout=30)
            body = resp.read().decode('utf-8')
            return json.loads(body)
        except HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            logger.error(
                'AFIP SDK HTTP %s en %s: %s', e.code, endpoint, body
            )
            raise AfipSDKError(
                'Error HTTP %s: %s' % (e.code, body),
                status_code=e.code,
                response=body,
            )
        except URLError as e:
            logger.error('AFIP SDK connection error: %s', e)
            raise AfipSDKError('Error de conexion: %s' % e)

    def _request_ws(self, method, wsid, params=None):
        """POST a /api/v1/afip/requests (llamada a WS de ARCA)."""
        payload = {
            'environment': self.environment,
            'method': method,
            'wsid': wsid,
            'params': params or {},
        }
        return self._request('afip/requests', payload)

    def _get_ta(self, wsid):
        """Obtiene Token+Sign (TA) para un web service dado."""
        payload = {
            'environment': self.environment,
            'tax_id': self.cuit,
            'wsid': wsid,
        }
        if self.cert:
            payload['cert'] = self._cert_value(self.cert)
        if self.key:
            payload['key'] = self._cert_value(self.key)
        return self._request('afip/auth', payload)

    @staticmethod
    def _cert_value(value):
        """Si value es un archivo existente, devuelve su contenido.

        Si no, lo devuelve tal cual (puede ser contenido PEM, base64
        o un alias ya registrado en la consola de AFIP SDK).
        """
        if os.path.isfile(value):
            try:
                with open(value, 'r') as f:
                    return f.read()
            except (IOError, OSError):
                return value
        return value

    def _wsfe_params(self, extra=None):
        """Arma el bloque Auth + params para WSFE."""
        ta = self._get_ta('wsfe')
        auth = {
            'Token': ta['token'],
            'Sign': ta['sign'],
            'Cuit': self.cuit,
        }
        params = {'Auth': auth}
        if extra:
            params.update(extra)
        return params

    # ------------------------------------------------------------------
    #  Facturacion electronica (wsfe) — consultas parametricas
    # ------------------------------------------------------------------

    def get_voucher_types(self):
        """Tipos de comprobantes disponibles (FEParamGetTiposCbte)."""
        return self._request_ws(
            'FEParamGetTiposCbte', 'wsfe', self._wsfe_params()
        )

    def get_concept_types(self):
        """Tipos de conceptos (FEParamGetTiposConcepto)."""
        return self._request_ws(
            'FEParamGetTiposConcepto', 'wsfe', self._wsfe_params()
        )

    def get_document_types(self):
        """Tipos de documentos (FEParamGetTiposDoc)."""
        return self._request_ws(
            'FEParamGetTiposDoc', 'wsfe', self._wsfe_params()
        )

    def get_aliquot_types(self):
        """Tipos de alicuotas IVA (FEParamGetTiposIva)."""
        return self._request_ws(
            'FEParamGetTiposIva', 'wsfe', self._wsfe_params()
        )

    def get_currencies(self):
        """Tipos de monedas (FEParamGetTiposMonedas)."""
        return self._request_ws(
            'FEParamGetTiposMonedas', 'wsfe', self._wsfe_params()
        )

    def get_exchange_rate(self, currency_id, date):
        """Cotizacion de una moneda en una fecha (FEParamGetCotizacion).

        Args:
            currency_id: Codigo de moneda (ej. 'DOL').
            date: Fecha en formato 'aaaammdd'.
        """
        params = self._wsfe_params({
            'MonId': currency_id,
            'FchCotiz': date,
        })
        return self._request_ws(
            'FEParamGetCotizacion', 'wsfe', params
        )

    def get_option_types(self):
        """Tipos de opcionales (FEParamGetTiposOpcional)."""
        return self._request_ws(
            'FEParamGetTiposOpcional', 'wsfe', self._wsfe_params()
        )

    def get_tax_types(self):
        """Tipos de tributos (FEParamGetTiposTributos)."""
        return self._request_ws(
            'FEParamGetTiposTributos', 'wsfe', self._wsfe_params()
        )

    def get_iva_condition_types(self):
        """Condiciones frente al IVA del receptor (FEParamGetCondicionIvaReceptor)."""
        return self._request_ws(
            'FEParamGetCondicionIvaReceptor', 'wsfe', self._wsfe_params()
        )

    def get_sales_points(self):
        """Puntos de venta configurados (FEParamGetPtosVenta)."""
        return self._request_ws(
            'FEParamGetPtosVenta', 'wsfe', self._wsfe_params()
        )

    def get_last_voucher(self, pto_vta, tipo_cpb):
        """Ultimo comprobante autorizado (FECompUltimoAutorizado)."""
        params = self._wsfe_params({
            'PtoVta': pto_vta,
            'CbteTipo': tipo_cpb,
        })
        return self._request_ws(
            'FECompUltimoAutorizado', 'wsfe', params
        )

    def wsfe_server_status(self):
        """Estado del servidor WSFE (FEDummy)."""
        return self._request_ws('FEDummy', 'wsfe', {})

    # ------------------------------------------------------------------
    #  Padron / Constancia de inscripcion
    # ------------------------------------------------------------------

    def get_taxpayer_details(self, tax_id):
        """Datos de un contribuyente en el padron (getPersona_v2).

        Args:
            tax_id: CUIT a consultar (str o int, sin guiones).
        """
        ta = self._get_ta('ws_sr_constancia_inscripcion')
        params = {
            'token': ta['token'],
            'sign': ta['sign'],
            'cuitRepresentada': self.cuit,
            'idPersona': int(str(tax_id).replace('-', '')),
        }
        return self._request_ws(
            'getPersona_v2', 'ws_sr_constancia_inscripcion', params
        )

    def padron_server_status(self):
        """Estado del servidor del padron."""
        return self._request_ws(
            'dummy', 'ws_sr_constancia_inscripcion', {}
        )
