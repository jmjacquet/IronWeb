# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


def _make_entidad(**kwargs):
    """Create an egr_entidad instance without hitting the database."""
    from entidades.models import egr_entidad
    e = egr_entidad.__new__(egr_entidad)
    e.apellido_y_nombre = kwargs.get('apellido_y_nombre', 'Test User')
    e.fact_cuit = kwargs.get('fact_cuit', '')
    e.nro_doc = kwargs.get('nro_doc', '')
    e.fact_categFiscal = kwargs.get('fact_categFiscal', None)
    e.tipo_doc = kwargs.get('tipo_doc', 96)
    e.tipo_entidad = kwargs.get('tipo_entidad', 1)
    e.email = kwargs.get('email', '')
    return e


# ---------------------------------------------------------------------------
# get_categFiscal
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("categ,expected", [
    (1,  'RI'),
    (2,  'RNI'),
    (3,  'NR'),
    (4,  'EX'),
    (5,  'CF'),
    (6,  'MT'),
    (7,  'OT'),
    (99, 'OT'),
    (None, 'OT'),
])
def test_get_categFiscal(categ, expected):
    e = _make_entidad(fact_categFiscal=categ)
    assert e.get_categFiscal() == expected


# ---------------------------------------------------------------------------
# __unicode__ / detalle_entidad
# ---------------------------------------------------------------------------

def test_unicode_uppercase_name():
    e = _make_entidad(apellido_y_nombre='juan perez')
    result = e.__unicode__()
    assert result == result.upper()


def test_unicode_includes_name():
    e = _make_entidad(apellido_y_nombre='Empresa SA')
    assert 'EMPRESA SA' in e.__unicode__()


def test_unicode_with_cuit():
    e = _make_entidad(apellido_y_nombre='Empresa', fact_cuit='30-12345678-9')
    result = e.__unicode__()
    assert '30-12345678-9' in result


def test_unicode_no_cuit_falls_back_to_nro_doc():
    e = _make_entidad(apellido_y_nombre='Persona', fact_cuit='', nro_doc='12345678')
    result = e.__unicode__()
    assert '12345678' in result


def test_unicode_with_categ_fiscal_shows_code():
    e = _make_entidad(apellido_y_nombre='RI SA', fact_cuit='30123456789', fact_categFiscal=1)
    assert 'RI' in e.__unicode__()


def test_unicode_no_doc_no_cuit_just_name():
    e = _make_entidad(apellido_y_nombre='Simple', fact_cuit='', nro_doc='')
    result = e.__unicode__()
    assert 'SIMPLE' in result
    assert ' - ' not in result.replace('SIMPLE', '')


# ---------------------------------------------------------------------------
# get_entidad
# ---------------------------------------------------------------------------

def test_get_entidad_without_categ():
    e = _make_entidad(apellido_y_nombre='Empresa SRL', fact_categFiscal=None)
    assert e.get_entidad() == 'Empresa SRL'


def test_get_entidad_with_categ():
    e = _make_entidad(apellido_y_nombre='Empresa SRL', fact_categFiscal=5)
    result = e.get_entidad()
    assert 'Empresa SRL' in result
    assert '5' in result


# ---------------------------------------------------------------------------
# get_correo
# ---------------------------------------------------------------------------

def test_get_correo_with_email():
    e = _make_entidad(email='test@example.com')
    assert e.get_correo() == 'test@example.com'


def test_get_correo_without_email_returns_none():
    e = _make_entidad(email='')
    assert e.get_correo() is None


def test_get_correo_none_email_returns_none():
    e = _make_entidad()
    e.email = None
    assert e.get_correo() is None


# ---------------------------------------------------------------------------
# get_nro_doc_afip
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tipo_doc,nro_doc,fact_cuit,expected_nro", [
    (96, '12345678',    '30123456789', '12345678'),    # DNI → nro_doc
    (99, '11223344',    '30123456789', '11223344'),    # CF  → nro_doc
    (80, '20112233445', '30123456789', '30123456789'), # CUIT → fact_cuit
    (86, '20112233445', '30123456789', '30123456789'), # CUIL → fact_cuit
])
def test_get_nro_doc_afip(tipo_doc, nro_doc, fact_cuit, expected_nro):
    e = _make_entidad(tipo_doc=tipo_doc, nro_doc=nro_doc, fact_cuit=fact_cuit)
    nro, tipo = e.get_nro_doc_afip()
    assert nro == expected_nro
    assert tipo == tipo_doc


def test_get_nro_doc_afip_no_doc_returns_zero():
    e = _make_entidad(tipo_doc=80, nro_doc=None, fact_cuit=None)
    nro, _ = e.get_nro_doc_afip()
    assert nro == 0


def test_get_nro_doc_cuit_delegates_to_get_nro_doc_afip():
    e = _make_entidad(tipo_doc=80, nro_doc='ignore', fact_cuit='33693450239')
    assert e.get_nro_doc_cuit() == '33693450239'


# ---------------------------------------------------------------------------
# EntidadManager custom querysets  (need DB)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_entidad_manager_clientes_returns_only_tipo_1():
    from entidades.models import egr_entidad
    egr_entidad.objects.create(apellido_y_nombre='Cliente A', tipo_entidad=1, baja=False)
    egr_entidad.objects.create(apellido_y_nombre='Proveedor B', tipo_entidad=2, baja=False)
    egr_entidad.objects.create(apellido_y_nombre='Cliente Baja', tipo_entidad=1, baja=True)
    qs = list(egr_entidad.objects.clientes())
    assert len(qs) == 1
    assert qs[0].apellido_y_nombre == 'Cliente A'
    assert all(e.tipo_entidad == 1 for e in qs)
    assert all(not e.baja for e in qs)


@pytest.mark.django_db
def test_entidad_manager_proveedores_returns_only_tipo_2():
    from entidades.models import egr_entidad
    egr_entidad.objects.create(apellido_y_nombre='Proveedor X', tipo_entidad=2, baja=False)
    egr_entidad.objects.create(apellido_y_nombre='Cliente Y', tipo_entidad=1, baja=False)
    qs = list(egr_entidad.objects.proveedores())
    assert len(qs) == 1
    assert qs[0].apellido_y_nombre == 'Proveedor X'
    assert all(e.tipo_entidad == 2 for e in qs)


@pytest.mark.django_db
def test_entidad_manager_vendedores_returns_only_tipo_3():
    from entidades.models import egr_entidad
    egr_entidad.objects.create(apellido_y_nombre='Vendedor Z', tipo_entidad=3, baja=False)
    egr_entidad.objects.create(apellido_y_nombre='Cliente W', tipo_entidad=1, baja=False)
    qs = list(egr_entidad.objects.vendedores())
    assert len(qs) == 1
    assert qs[0].apellido_y_nombre == 'Vendedor Z'
    assert all(e.tipo_entidad == 3 for e in qs)
