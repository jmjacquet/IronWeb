# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

import pytest

try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch, PropertyMock


def _make_cpb_tipo(tipo=1, compra_venta='V', signo_ctacte=1, usa_ctacte=True):
    cpb_tipo = MagicMock()
    cpb_tipo.tipo = tipo
    cpb_tipo.compra_venta = compra_venta
    cpb_tipo.signo_ctacte = signo_ctacte
    cpb_tipo.usa_ctacte = usa_ctacte
    return cpb_tipo


def _make_estado(pk, color='green'):
    estado = MagicMock()
    estado.id = pk
    estado.pk = pk
    estado.color = color
    return estado


def _make_cpb(**kwargs):
    from comprobantes.models import cpb_comprobante
    cpb = cpb_comprobante.__new__(cpb_comprobante)
    cpb.pto_vta = kwargs.get('pto_vta', 1)
    cpb.letra = kwargs.get('letra', 'A')
    cpb.numero = kwargs.get('numero', 1)
    cpb.importe_total = kwargs.get('importe_total', Decimal('0'))
    cpb.importe_subtotal = kwargs.get('importe_subtotal', Decimal('0'))
    cpb.importe_iva = kwargs.get('importe_iva', Decimal('0'))
    cpb.importe_gravado = kwargs.get('importe_gravado', Decimal('0'))
    cpb.importe_no_gravado = kwargs.get('importe_no_gravado', Decimal('0'))
    cpb.importe_exento = kwargs.get('importe_exento', Decimal('0'))
    cpb.importe_perc_imp = kwargs.get('importe_perc_imp', Decimal('0'))
    cpb.saldo = kwargs.get('saldo', Decimal('0'))
    cpb.cae = kwargs.get('cae', None)
    cpb.cpb_tipo = kwargs.get('cpb_tipo', _make_cpb_tipo())
    cpb.estado = kwargs.get('estado', _make_estado(1))
    return cpb


# ---------------------------------------------------------------------------
# cpb_pto_vta.get_numero
# ---------------------------------------------------------------------------

def _make_pto_vta(numero):
    from comprobantes.models import cpb_pto_vta
    pv = cpb_pto_vta.__new__(cpb_pto_vta)
    pv.numero = numero
    return pv


@pytest.mark.parametrize("numero,expected", [
    (1,      '    1'),
    (12345,  '12345'),
    (9,      '    9'),
    (99999,  '99999'),
])
def test_cpb_pto_vta_get_numero(numero, expected):
    pv = _make_pto_vta(numero)
    assert pv.get_numero() == expected


# ---------------------------------------------------------------------------
# cpb_comprobante.get_cpb  (property)
# ---------------------------------------------------------------------------

def test_get_cpb_format_contains_letra():
    cpb = _make_cpb(pto_vta=1, letra='B', numero=5)
    assert 'B' in cpb.get_cpb


def test_get_cpb_pads_pto_vta_to_5_digits():
    cpb = _make_cpb(pto_vta=1, letra='A', numero=1)
    assert '    1' in cpb.get_cpb


def test_get_cpb_pads_numero_to_8_digits():
    cpb = _make_cpb(pto_vta=1, letra='A', numero=100)
    assert '00000100' in cpb.get_cpb


def test_get_cpb_separator_dashes():
    cpb = _make_cpb(pto_vta=1, letra='A', numero=1)
    parts = cpb.get_cpb.split('-')
    assert len(parts) == 3


# ---------------------------------------------------------------------------
# cpb_comprobante.get_numero
# ---------------------------------------------------------------------------

def test_get_numero_contains_padded_pto_vta():
    cpb = _make_cpb(pto_vta=3, numero=500)
    assert '    3' in cpb.get_numero()


def test_get_numero_contains_padded_numero():
    cpb = _make_cpb(pto_vta=1, numero=500)
    assert '00000500' in cpb.get_numero()


# ---------------------------------------------------------------------------
# cpb_comprobante.get_importe_total
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("importe,signo,expected", [
    (Decimal('100'), 1,  Decimal('100')),
    (Decimal('100'), -1, Decimal('-100')),
    (None,           1,  0),
    (Decimal('0'),   1,  0),
])
def test_get_importe_total(importe, signo, expected):
    cpb = _make_cpb(importe_total=importe, cpb_tipo=_make_cpb_tipo(signo_ctacte=signo))
    assert cpb.get_importe_total() == expected


# ---------------------------------------------------------------------------
# cpb_comprobante.get_importe_subtotal
# ---------------------------------------------------------------------------

def test_get_importe_subtotal_applies_sign():
    cpb = _make_cpb(importe_subtotal=Decimal('200'), cpb_tipo=_make_cpb_tipo(signo_ctacte=-1))
    assert cpb.get_importe_subtotal() == Decimal('-200')


def test_get_importe_subtotal_none_returns_zero():
    cpb = _make_cpb()
    cpb.importe_subtotal = None
    assert cpb.get_importe_subtotal() == 0


# ---------------------------------------------------------------------------
# cpb_comprobante.get_importe_iva
# ---------------------------------------------------------------------------

def test_get_importe_iva_applies_sign():
    cpb = _make_cpb(importe_iva=Decimal('21'), cpb_tipo=_make_cpb_tipo(signo_ctacte=1))
    assert cpb.get_importe_iva() == Decimal('21')


def test_get_importe_iva_none_returns_zero():
    cpb = _make_cpb()
    cpb.importe_iva = None
    assert cpb.get_importe_iva() == 0


# ---------------------------------------------------------------------------
# cpb_comprobante.get_saldo
# ---------------------------------------------------------------------------

def test_get_saldo_applies_sign():
    cpb = _make_cpb(saldo=Decimal('50'), cpb_tipo=_make_cpb_tipo(signo_ctacte=-1))
    assert cpb.get_saldo() == Decimal('-50')


def test_get_saldo_none_returns_zero():
    cpb = _make_cpb()
    cpb.saldo = None
    assert cpb.get_saldo() == 0


# ---------------------------------------------------------------------------
# cpb_comprobante.estado_color
# ---------------------------------------------------------------------------

def test_estado_color_returns_color():
    estado = _make_estado(pk=1, color='blue')
    cpb = _make_cpb(estado=estado)
    assert cpb.estado_color == 'blue'


def test_estado_color_none_estado_returns_none():
    cpb = _make_cpb()
    cpb.estado = None
    assert cpb.estado_color is None


# ---------------------------------------------------------------------------
# cpb_comprobante.seleccionable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cv,estado_id,cae,expected", [
    ('V', 1, None,    True),   # venta, pendiente, sin CAE → seleccionable
    ('V', 2, None,    True),   # venta, estado 2, sin CAE → seleccionable (CAE check only blocks estado==2)
    ('V', 2, 'CAE1',  False),  # venta, cobrado, CON CAE → NO seleccionable
    ('V', 3, None,    False),  # venta, estado 3 → NO
    ('C', 1, None,    True),   # compra estado 1 → seleccionable
    ('C', 2, 'CAE1',  True),   # compra estado 2 con CAE → seleccionable
    ('C', 3, None,    False),  # compra estado 3 → NO
])
def test_seleccionable(cv, estado_id, cae, expected):
    cpb = _make_cpb(
        cae=cae,
        cpb_tipo=_make_cpb_tipo(compra_venta=cv),
        estado=_make_estado(pk=estado_id),
    )
    assert cpb.seleccionable is expected


# ---------------------------------------------------------------------------
# cpb_comprobante.get_importe_gravado / no_gravado / exento / perc_imp
# ---------------------------------------------------------------------------

def test_get_importe_gravado_applies_sign():
    cpb = _make_cpb(importe_gravado=Decimal('300'), cpb_tipo=_make_cpb_tipo(signo_ctacte=1))
    assert cpb.get_importe_gravado() == Decimal('300')


def test_get_importe_no_gravado_none_zero():
    cpb = _make_cpb()
    cpb.importe_no_gravado = None
    assert cpb.get_importe_no_gravado() == 0


def test_get_importe_exento_applies_sign():
    cpb = _make_cpb(importe_exento=Decimal('50'), cpb_tipo=_make_cpb_tipo(signo_ctacte=-1))
    assert cpb.get_importe_exento() == Decimal('-50')


def test_get_importe_perc_imp_none_zero():
    cpb = _make_cpb()
    cpb.importe_perc_imp = None
    assert cpb.get_importe_perc_imp() == 0


# ---------------------------------------------------------------------------
# cpb_comprobante_detalle.get_costo_total  (property)
# ---------------------------------------------------------------------------

def _make_detalle(cantidad, importe_costo):
    from comprobantes.models import cpb_comprobante_detalle
    d = cpb_comprobante_detalle.__new__(cpb_comprobante_detalle)
    d.cantidad = Decimal(str(cantidad))
    d.importe_costo = Decimal(str(importe_costo))
    d.coef_iva = Decimal('0.21')
    d.importe_total = Decimal('0')
    return d


def test_get_costo_total():
    d = _make_detalle(3, 10)
    assert d.get_costo_total == Decimal('30')


def test_get_costo_cimp_total():
    d = _make_detalle(2, 100)
    # 2 * 100 * (1 + 0.21) = 242
    assert d.get_costo_cimp_total == Decimal('200') * Decimal('1.21')
