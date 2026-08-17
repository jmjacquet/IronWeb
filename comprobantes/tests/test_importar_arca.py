# -*- coding: utf-8 -*-
u"""Parseo del CSV de ARCA. No toca la base: sólo las funciones puras."""
from __future__ import unicode_literals

import datetime
import io
from decimal import Decimal

import pytest

from comprobantes.importar_arca import a_decimal, a_entero, a_fecha, leer_filas

CSV_RECIBIDOS = (
    u'Fecha;Tipo;Punto de Venta;Número Desde;Número Hasta;Cód. Autorización;'
    u'Tipo Doc. Emisor;Nro. Doc. Emisor;Denominación Emisor;Tipo Cambio;Moneda;'
    u'Imp. Neto Gravado;Imp. Neto No Gravado;Imp. Op. Exentas;Otros Tributos;IVA;Imp. Total\n'
    u'2026-07-03;1;00004;00000123;00000123;72345678901234;80;30712345678;'
    u'ACME SA;1,00;PES;100.000,00;0,00;0,00;0,00;21.000,00;121.000,00\n'
)


@pytest.mark.parametrize('texto,esperado', [
    ('121.000,00', Decimal('121000.00')),   # formato ARCA
    ('1234.56', Decimal('1234.56')),        # punto decimal
    ('0,00', Decimal('0')),
    ('', Decimal('0')),
    ('basura', Decimal('0')),
])
def test_a_decimal(texto, esperado):
    assert a_decimal(texto) == esperado


def test_a_decimal_no_confunde_miles_con_decimales():
    # El bug clásico: 100.000,00 no puede volverse 100.00
    assert a_decimal('100.000,00') == Decimal('100000')


@pytest.mark.parametrize('texto,esperado', [
    ('2026-07-03', datetime.date(2026, 7, 3)),
    ('03/07/2026', datetime.date(2026, 7, 3)),
    ('20260703', datetime.date(2026, 7, 3)),
    ('', None),
])
def test_a_fecha(texto, esperado):
    assert a_fecha(texto) == esperado


def test_a_entero_ignora_ceros_y_simbolos():
    assert a_entero('00000123') == 123
    assert a_entero('') == 0


def test_leer_filas_mapea_encabezados_con_acentos():
    fila = leer_filas(io.StringIO(CSV_RECIBIDOS))[0]
    assert fila['tipo'] == '1'
    assert fila['nro_doc'] == '30712345678'      # "Nro. Doc. Emisor" -> nro_doc
    assert fila['denominacion'] == 'ACME SA'
    assert a_decimal(fila['total']) == Decimal('121000')
    assert a_decimal(fila['iva']) == Decimal('21000')


def test_leer_filas_acepta_emitidos_con_receptor():
    csv_emitidos = CSV_RECIBIDOS.replace('Emisor', 'Receptor')
    fila = leer_filas(io.StringIO(csv_emitidos))[0]
    assert fila['nro_doc'] == '30712345678'


def test_leer_filas_vacio():
    assert leer_filas(io.StringIO(u'')) == []


# Variante real "montos expresados en pesos": UTF-8, encabezados citados,
# acentos, y una columna por alícuota en vez de un único total de IVA.
CSV_CON_ALICUOTAS = (
    u'"Fecha de Emisión";"Tipo de Comprobante";"Punto de Venta";"Número Desde";'
    u'"Número Hasta";"Cód. Autorización";"Tipo Doc. Receptor";"Nro. Doc. Receptor";'
    u'"Denominación Receptor";"Tipo Cambio";"Moneda";"Imp. Neto Gravado IVA 0%";'
    u'"IVA 2,5%";"Imp. Neto Gravado IVA 2,5%";"IVA 5%";"Imp. Neto Gravado IVA 5%";'
    u'"IVA 10,5%";"Imp. Neto Gravado IVA 10,5%";"IVA 21%";"Imp. Neto Gravado IVA 21%";'
    u'"IVA 27%";"Imp. Neto Gravado IVA 27%";"Imp. Neto Gravado Total";'
    u'"Imp. Neto No Gravado";"Imp. Op. Exentas";"Otros Tributos";"Total IVA";"Imp. Total"\n'
    u'2026-02-13;1;1;1;1;86084432547392;80;30715665871;PRP GESTION MEDICA SRL;1,00;$;;;;;;;;'
    u'630000,00;3000000,00;;;3000000,00;0,00;0,00;0,00;630000,00;3630000,00\n'
)


def test_leer_filas_variante_con_alicuotas():
    fila = leer_filas(io.BytesIO(CSV_CON_ALICUOTAS.encode('utf-8')))[0]
    assert a_fecha(fila['fecha']) == datetime.date(2026, 2, 13)   # "Fecha de Emisión"
    assert a_entero(fila['numero_desde']) == 1                    # "Número Desde"
    assert fila['cae'] == '86084432547392'                        # "Cód. Autorización"
    assert fila['denominacion'] == 'PRP GESTION MEDICA SRL'
    assert a_decimal(fila['gravado']) == Decimal('3000000')       # "Imp. Neto Gravado Total"
    assert a_decimal(fila['iva']) == Decimal('630000')            # "Total IVA"
    assert a_decimal(fila['neto_21']) == Decimal('3000000')
    assert a_decimal(fila['iva_21']) == Decimal('630000')
    assert fila['moneda'] == '$'


def test_leer_filas_utf8_no_se_lee_como_latin1():
    # Si se decodifica mal, "Fecha de Emisión" deja de matchear y la fecha queda vacía
    fila = leer_filas(io.BytesIO(CSV_CON_ALICUOTAS.encode('utf-8')))[0]
    assert fila.get('fecha'), 'los encabezados con acento no se mapearon'
