# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest
from django.core.cache import cache

from general import cotizacion

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


def _moneda(codigo):
    m = MagicMock()
    m.codigo = codigo
    return m


@pytest.fixture(autouse=True)
def limpiar_cache():
    cache.clear()
    yield
    cache.clear()


def test_aplica_solo_venta_local_con_lista_en_dolares():
    assert cotizacion.aplica_cotizacion(_moneda('ARS'), _moneda('USD'))
    assert not cotizacion.aplica_cotizacion(_moneda('USD'), _moneda('USD'))
    assert not cotizacion.aplica_cotizacion(_moneda('ARS'), _moneda('ARS'))
    assert not cotizacion.aplica_cotizacion(None, _moneda('USD'))
    assert not cotizacion.aplica_cotizacion(_moneda('ARS'), None)


def test_get_cotizacion_lee_api_y_cachea():
    resp = MagicMock()
    resp.read.return_value = b'{"compra": 1300, "venta": 1350.5, "nombre": "Oficial"}'
    with patch.object(cotizacion.urllib2, 'urlopen', return_value=resp) as urlopen:
        assert cotizacion.get_cotizacion_dolar() == Decimal('1350.5')
        assert cotizacion.get_cotizacion_dolar() == Decimal('1350.5')
        assert urlopen.call_count == 1


def test_get_cotizacion_usa_ultimo_valor_si_falla_api():
    cache.set(cotizacion.CACHE_KEY + '_ultima', Decimal('1200'), None)
    with patch.object(cotizacion.urllib2, 'urlopen', side_effect=IOError('down')):
        assert cotizacion.get_cotizacion_dolar() == Decimal('1200')


def test_get_cotizacion_devuelve_uno_sin_api_ni_historial():
    with patch.object(cotizacion.urllib2, 'urlopen', side_effect=IOError('down')):
        assert cotizacion.get_cotizacion_dolar() == Decimal(1)
