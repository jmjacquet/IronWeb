# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import json
from datetime import date, timedelta
from decimal import Decimal

import pytest

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from general.utilidades import (
    DecimalEncoder,
    ValuesQuerySetToDict,
    default,
    digVerificador,
    empresas_habilitadas_list,
    facturacion_cliente_letra,
    finMes,
    get_letra,
    habilitado_contador,
    hoy,
    inicioMes,
    inicioMesAnt,
    limpiar_sesion,
    nofacturac_cliente_letra,
    popover_html,
    tipo_comprob_fiscal,
    ultimo_anio,
    ultimo_semestre,
    validar_cuit,
)


# ---------------------------------------------------------------------------
# habilitado_contador
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tipo_usr,expected", [
    (0, True),   # Administrador
    (3, True),   # Contador
    (1, False),  # Cliente/Usuario
    (2, False),  # Vendedor
    (99, False), # desconocido
])
def test_habilitado_contador(tipo_usr, expected):
    assert habilitado_contador(tipo_usr) is expected


# ---------------------------------------------------------------------------
# tipo_comprob_fiscal
# ---------------------------------------------------------------------------

def test_tipo_comprob_fiscal_monotributista_only_C_and_X():
    letras = [l[0] for l in tipo_comprob_fiscal(6)]
    assert 'C' in letras
    assert 'X' in letras
    assert 'A' not in letras
    assert 'B' not in letras


def test_tipo_comprob_fiscal_ri_has_A_B_no_C():
    letras = [l[0] for l in tipo_comprob_fiscal(1)]
    assert 'A' in letras
    assert 'B' in letras
    assert 'C' not in letras


def test_tipo_comprob_fiscal_other_has_A_B_C_X():
    letras = [l[0] for l in tipo_comprob_fiscal(5)]
    assert set(['A', 'B', 'C', 'X']).issubset(set(letras))


def test_tipo_comprob_fiscal_returns_tuple_of_pairs():
    result = tipo_comprob_fiscal(1)
    assert isinstance(result, tuple)
    for item in result:
        assert len(item) == 2 and item[0] == item[1]


# ---------------------------------------------------------------------------
# facturacion_cliente_letra
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("letra,cli_categ,emp_categ,expected", [
    ('A', 1, 1, True),   # RI empresa, RI cliente → A válida
    ('E', 1, 1, True),   # RI empresa, RI cliente → E válida
    ('M', 1, 1, True),   # RI empresa, RI cliente → M válida
    ('B', 1, 1, False),  # RI empresa, RI cliente → B inválida
    ('B', 5, 1, True),   # RI empresa, CF cliente → B válida
    ('A', 5, 1, False),  # RI empresa, CF cliente → A inválida
    ('C', 5, 6, True),   # Mono empresa → C válida
    ('A', 5, 6, False),  # Mono empresa → A inválida
    ('B', 5, 6, False),  # Mono empresa → B inválida
])
def test_facturacion_cliente_letra(letra, cli_categ, emp_categ, expected):
    assert facturacion_cliente_letra(letra, cli_categ, emp_categ) is expected


# ---------------------------------------------------------------------------
# nofacturac_cliente_letra
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("letra,cli_categ,emp_categ,expected", [
    ('X', 1, 1, True),   # RI/RI → X válida
    ('A', 1, 1, True),   # RI/RI → A válida
    ('C', 1, 1, False),  # RI/RI → C inválida
    ('B', 5, 1, True),   # RI/CF → B válida
    ('X', 5, 1, True),   # RI/CF → X válida
    ('A', 5, 1, False),  # RI/CF → A inválida
    ('C', 1, 6, True),   # Mono → C válida
    ('X', 1, 6, True),   # Mono → X válida
    ('A', 1, 6, False),  # Mono → A inválida
])
def test_nofacturac_cliente_letra(letra, cli_categ, emp_categ, expected):
    assert nofacturac_cliente_letra(letra, cli_categ, emp_categ) is expected


# ---------------------------------------------------------------------------
# get_letra
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cli_categ,emp_categ,expected", [
    (1, 1, 'A'),  # RI empresa + RI cliente → A
    (5, 1, 'B'),  # RI empresa + CF cliente → B
    (6, 1, 'B'),  # RI empresa + MT cliente → B
    (5, 6, 'C'),  # Mono empresa → C
    (1, 6, 'C'),  # Mono empresa, RI cliente → C
])
def test_get_letra(cli_categ, emp_categ, expected):
    assert get_letra(cli_categ, emp_categ) == expected


def test_get_letra_always_single_char():
    for emp in [1, 6]:
        for cli in [1, 5, 6]:
            result = get_letra(cli, emp)
            assert len(result) == 1
            assert result in ('A', 'B', 'C')


# ---------------------------------------------------------------------------
# digVerificador  (módulo 10 – dígito verificador bancario)
# ---------------------------------------------------------------------------

def test_digVerificador_empty_returns_empty():
    assert digVerificador('') == ''


def test_digVerificador_whitespace_only_returns_empty():
    assert digVerificador('   ') == ''


def test_digVerificador_non_digit_returns_empty():
    assert digVerificador('abc') == ''


def test_digVerificador_alphanumeric_returns_empty():
    assert digVerificador('abc123') == ''


def test_digVerificador_single_zero():
    # etapa1=0, etapa2=0, etapa3=0 → 10-0=10 → 0
    assert digVerificador('0') == '0'


def test_digVerificador_single_one():
    # etapa1=1, etapa2=3, etapa3=0, etapa4=3 → 10-3=7
    assert digVerificador('1') == '7'


def test_digVerificador_two_digits_known_value():
    # "12": etapa1=1, etapa2=3, etapa3=2, etapa4=5 → 10-5=5
    assert digVerificador('12') == '5'


def test_digVerificador_result_is_single_digit():
    for code in ('1234567890', '9876543210', '1111111111', '0000000000'):
        result = digVerificador(code)
        assert len(result) == 1
        assert result.isdigit()


def test_digVerificador_result_never_ten():
    for code in ('0', '1', '10', '100', '12345678901234'):
        assert digVerificador(code) != '10'


def test_digVerificador_strips_whitespace():
    assert digVerificador('  12  ') == digVerificador('12')


def test_digVerificador_etapa4_multiple_of_10_returns_zero():
    # "31": etapa1=3, etapa2=9, etapa3=1, etapa4=10 → digito=10 → remapped to 0
    assert digVerificador('31') == '0'


# ---------------------------------------------------------------------------
# validar_cuit
# ---------------------------------------------------------------------------

def test_validar_cuit_none_returns_false():
    assert validar_cuit(None) is False


def test_validar_cuit_empty_returns_false():
    assert validar_cuit('') is False


def test_validar_cuit_too_short_returns_false():
    assert validar_cuit('1234567890') is False


def test_validar_cuit_valid_no_dashes():
    # 33-69345023-9 verified manually
    assert validar_cuit('33693450239') is True


def test_validar_cuit_valid_with_dashes():
    assert validar_cuit('33-69345023-9') is True


def test_validar_cuit_valid_monotributista():
    # 20-12345678-6 verified manually
    assert validar_cuit('20123456786') is True


def test_validar_cuit_wrong_check_digit_returns_false():
    assert validar_cuit('33693450230') is False


def test_validar_cuit_dashes_same_as_without():
    assert validar_cuit('33-69345023-9') == validar_cuit('33693450239')


# ---------------------------------------------------------------------------
# Date utilities
# ---------------------------------------------------------------------------

def test_hoy_returns_today():
    assert hoy() == date.today()


def test_inicioMes_is_first_day():
    result = inicioMes()
    today = date.today()
    assert result.day == 1
    assert result.month == today.month
    assert result.year == today.year


def test_finMes_is_last_day():
    result = finMes()
    today = date.today()
    last = calendar.monthrange(today.year, today.month)[1]
    assert result.day == last
    assert result.month == today.month


def test_finMes_after_inicioMes():
    assert finMes() > inicioMes()


def test_inicioMesAnt_before_inicioMes():
    assert inicioMesAnt() < inicioMes()


def test_inicioMesAnt_approx_30_days_before():
    diff = inicioMes() - inicioMesAnt()
    assert abs(diff.days - 30) <= 1


def test_ultimo_semestre_is_180_days_ago():
    assert ultimo_semestre() == date.today() - timedelta(days=180)


def test_ultimo_anio_is_365_days_ago():
    assert ultimo_anio() == date.today() - timedelta(days=365)


# ---------------------------------------------------------------------------
# empresas_habilitadas_list
# ---------------------------------------------------------------------------

def test_empresas_habilitadas_list_contains_empresa_id():
    empresa = MagicMock()
    empresa.id = 5
    assert 5 in empresas_habilitadas_list(empresa)


def test_empresas_habilitadas_list_always_contains_1():
    empresa = MagicMock()
    empresa.id = 10
    assert 1 in empresas_habilitadas_list(empresa)


def test_empresas_habilitadas_list_length_is_two():
    empresa = MagicMock()
    empresa.id = 3
    assert len(empresas_habilitadas_list(empresa)) == 2


def test_empresas_habilitadas_list_exact_values():
    empresa = MagicMock()
    empresa.id = 7
    assert empresas_habilitadas_list(empresa) == [7, 1]


# ---------------------------------------------------------------------------
# limpiar_sesion
# ---------------------------------------------------------------------------

def test_limpiar_sesion_removes_cpbs_cobranza():
    req = MagicMock()
    req.session = {'cpbs_cobranza': [1, 2]}
    limpiar_sesion(req)
    assert 'cpbs_cobranza' not in req.session


def test_limpiar_sesion_removes_cpbs_pagos():
    req = MagicMock()
    req.session = {'cpbs_pagos': [3]}
    limpiar_sesion(req)
    assert 'cpbs_pagos' not in req.session


def test_limpiar_sesion_removes_cheques():
    req = MagicMock()
    req.session = {'cheques': [5]}
    limpiar_sesion(req)
    assert 'cheques' not in req.session


def test_limpiar_sesion_preserves_other_keys():
    req = MagicMock()
    req.session = {'cpbs_cobranza': [], 'user_id': 42}
    limpiar_sesion(req)
    assert req.session['user_id'] == 42


def test_limpiar_sesion_empty_session_no_error():
    req = MagicMock()
    req.session = {}
    limpiar_sesion(req)  # must not raise


def test_limpiar_sesion_removes_all_three():
    req = MagicMock()
    req.session = {'cpbs_cobranza': [], 'cpbs_pagos': [], 'cheques': []}
    limpiar_sesion(req)
    assert not any(k in req.session for k in ('cpbs_cobranza', 'cpbs_pagos', 'cheques'))


# ---------------------------------------------------------------------------
# default / DecimalEncoder / ValuesQuerySetToDict
# ---------------------------------------------------------------------------

def test_default_converts_decimal_to_string():
    assert default(Decimal('10.5')) == '10.5'


def test_default_non_decimal_raises_type_error():
    with pytest.raises(TypeError):
        default('not a decimal')


def test_decimal_encoder_converts_decimal_to_float():
    enc = DecimalEncoder()
    assert enc.default(Decimal('9.99')) == 9.99


def test_decimal_encoder_non_decimal_raises_type_error():
    enc = DecimalEncoder()
    with pytest.raises(TypeError):
        enc.default('string')


def test_decimal_encoder_in_json_dumps():
    result = json.dumps({'price': Decimal('9.99')}, cls=DecimalEncoder)
    assert '9.99' in result


def test_values_queryset_to_dict_returns_list():
    assert ValuesQuerySetToDict([{'a': 1}]) == [{'a': 1}]


def test_values_queryset_to_dict_empty():
    assert ValuesQuerySetToDict([]) == []


# ---------------------------------------------------------------------------
# popover_html
# ---------------------------------------------------------------------------

def test_popover_html_contains_label():
    assert 'Etiqueta' in popover_html('Etiqueta', 'Contenido')


def test_popover_html_contains_content_in_title():
    assert 'Mi tooltip' in popover_html('Label', 'Mi tooltip')


def test_popover_html_has_fa_icon():
    assert 'fa-question-circle' in popover_html('Label', 'Content')
