# -*- coding: utf-8 -*-
u"""Importación de comprobantes desde el CSV de ARCA (Portal IVA > Mis Comprobantes)."""
from __future__ import unicode_literals

import csv
import datetime
import re
import unicodedata
from decimal import Decimal, InvalidOperation

from django.db import transaction

from comprobantes.models import (cpb_comprobante, cpb_comprobante_detalle,
                                 cpb_comprobante_tot_iva, cpb_estado, cpb_nro_afip,
                                 cpb_pto_vta, cpb_tipo)
from entidades.models import egr_entidad
from general.models import gral_moneda
from productos.models import gral_tipo_iva

# ARCA rotula la contraparte como "Emisor" en Recibidos y "Receptor" en Emitidos.
CAMPOS = {
    'fecha': 'fecha',
    'fechadeemision': 'fecha',
    'tipo': 'tipo',
    'tipodecomprobante': 'tipo',
    'puntodeventa': 'pto_vta',
    'numerodesde': 'numero_desde',
    'numerohasta': 'numero_hasta',
    'codautorizacion': 'cae',
    'tipodocemisor': 'tipo_doc',
    'tipodocreceptor': 'tipo_doc',
    'nrodocemisor': 'nro_doc',
    'nrodocreceptor': 'nro_doc',
    'denominacionemisor': 'denominacion',
    'denominacionreceptor': 'denominacion',
    'tipocambio': 'cotizacion',
    'moneda': 'moneda',
    'impnetogravado': 'gravado',
    'impnetogravadototal': 'gravado',
    'impnetonogravado': 'no_gravado',
    'impopexentas': 'exento',
    'otrostributos': 'otros_tributos',
    'iva': 'iva',
    'totaliva': 'iva',
    'imptotal': 'total',
    # Desglose por alícuota (export "montos expresados en pesos")
    'impnetogravadoiva0': 'neto_0',
    'impnetogravadoiva25': 'neto_25',
    'iva25': 'iva_25',
    'impnetogravadoiva5': 'neto_5',
    'iva5': 'iva_5',
    'impnetogravadoiva105': 'neto_105',
    'iva105': 'iva_105',
    'impnetogravadoiva21': 'neto_21',
    'iva21': 'iva_21',
    'impnetogravadoiva27': 'neto_27',
    'iva27': 'iva_27',
}

# (columna neto, columna IVA, id_afip de gral_tipo_iva)
ALICUOTAS = (
    ('neto_0', None, 3),
    ('neto_25', 'iva_25', 9),
    ('neto_5', 'iva_5', 8),
    ('neto_105', 'iva_105', 4),
    ('neto_21', 'iva_21', 5),
    ('neto_27', 'iva_27', 6),
)

# ARCA usa el símbolo, no el código ISO que guarda gral_moneda
MONEDAS = {'$': 'ARS', 'PES': 'ARS', 'U$S': 'USD', 'DOL': 'USD'}

FORMATOS_FECHA = ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y%m%d')


def _clave(texto):
    sin_acentos = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]', '', sin_acentos.lower())


def a_decimal(texto):
    u"""Acepta 1.234,56 (formato ARCA) y 1234.56."""
    txt = (texto or '').strip().replace(' ', '')
    if not txt:
        return Decimal(0)
    if ',' in txt and '.' in txt:
        # El separador decimal es el que aparece último
        txt = txt.replace('.', '') if txt.rfind(',') > txt.rfind('.') else txt.replace(',', '')
    txt = txt.replace(',', '.')
    try:
        return Decimal(txt)
    except InvalidOperation:
        return Decimal(0)


def a_fecha(texto):
    txt = (texto or '').strip()
    for formato in FORMATOS_FECHA:
        try:
            return datetime.datetime.strptime(txt, formato).date()
        except ValueError:
            continue
    return None


def a_entero(texto):
    digitos = re.sub(r'[^0-9]', '', texto or '')
    return int(digitos) if digitos else 0


def leer_filas(archivo):
    u"""Devuelve una lista de dicts con las claves canónicas de CAMPOS."""
    contenido = archivo.read()
    if isinstance(contenido, bytes):
        # ARCA exporta en UTF-8; los CSV viejos vienen en latin1
        try:
            contenido = contenido.decode('utf-8-sig')
        except UnicodeDecodeError:
            contenido = contenido.decode('latin1')
    lineas = [l for l in contenido.splitlines() if l.strip()]
    if not lineas:
        return []

    delimitador = ';' if lineas[0].count(';') >= lineas[0].count(',') else ','
    lector = csv.reader([l.encode('utf-8') for l in lineas], delimiter=str(delimitador))
    encabezado = [CAMPOS.get(_clave(c.decode('utf-8'))) for c in next(lector)]

    filas = []
    for linea in lector:
        fila = {}
        for clave, valor in zip(encabezado, linea):
            if clave:
                fila[clave] = valor.decode('utf-8').strip()
        if fila.get('tipo'):
            filas.append(fila)
    return filas


def tasa_para(gravado, iva):
    u"""Mis Comprobantes trae un único total de IVA, así que se deduce la alícuota."""
    tasas = [t for t in gral_tipo_iva.objects.all() if t.coeficiente > 0]
    if gravado > 0 and tasas:
        coeficiente = iva / gravado
        return min(tasas, key=lambda t: abs(t.coeficiente - coeficiente))
    return gral_tipo_iva.objects.filter(id_afip=3).first()


def _buscar_tipo(codigo_afip, compra_venta):
    nro = cpb_nro_afip.objects.filter(numero_afip=codigo_afip).first()
    if not nro:
        return None, None
    # libro_iva descarta los no fiscales (ej. "FACTURA VENTA X") que comparten tipo
    tipo = cpb_tipo.objects.filter(tipo=nro.cpb_tipo, compra_venta=compra_venta,
                                   libro_iva=True, baja=False).order_by('pk').first()
    return tipo, nro.letra


def _buscar_moneda(token):
    codigo = MONEDAS.get((token or '').strip(), (token or '').strip())
    return gral_moneda.objects.filter(codigo=codigo).first()


def _buscar_entidad(fila, empresa, tipo_entidad):
    cuit = re.sub(r'[^0-9]', '', fila.get('nro_doc') or '')
    nombre = (fila.get('denominacion') or '').strip().upper() or u'SIN IDENTIFICAR'
    if not cuit:
        return None
    entidad = egr_entidad.objects.filter(fact_cuit=cuit, tipo_entidad=tipo_entidad,
                                         empresa=empresa).first()
    if not entidad:
        entidad = egr_entidad.objects.create(
            apellido_y_nombre=nombre, fact_razon_social=nombre, fact_cuit=cuit,
            nro_doc=cuit, tipo_doc=a_entero(fila.get('tipo_doc')) or 80,
            tipo_entidad=tipo_entidad, empresa=empresa)
    return entidad


def _tasa(id_afip):
    return gral_tipo_iva.objects.filter(id_afip=id_afip).first()


def _agrupar_por_alicuota(fila, gravado, iva, no_gravado, exento, total):
    u"""[(tasa_iva, base, iva)] — base de las alícuotas y de los detalles."""
    grupos = []
    for col_neto, col_iva, id_afip in ALICUOTAS:
        base = a_decimal(fila.get(col_neto))
        monto = a_decimal(fila.get(col_iva)) if col_iva else Decimal(0)
        if base or monto:
            grupos.append((_tasa(id_afip), base, monto))
    # Export sin columnas por alícuota: se deduce del total
    if not grupos and (gravado or iva):
        grupos.append((tasa_para(gravado, iva), gravado, iva))
    if no_gravado:
        grupos.append((_tasa(1), no_gravado, Decimal(0)))
    if exento:
        grupos.append((_tasa(2), exento, Decimal(0)))
    # Todo comprobante lleva al menos una fila, incluso si viene en cero
    if not grupos:
        grupos.append((_tasa(3), total, Decimal(0)))
    return grupos


def _crear_alicuotas(comprobante, grupos):
    for tasa, base, monto in grupos:
        cpb_comprobante_tot_iva.objects.create(
            cpb_comprobante=comprobante, importe_base=base,
            tasa_iva=tasa, importe_total=monto)


def _crear_detalles(comprobante, grupos, otros, total, descripcion):
    u"""Sin producto ni lista de precios: no mueve stock ni valida moneda.

    ARCA redondea y sus componentes no siempre suman el Imp. Total. La diferencia
    se absorbe en la última fila para que un recálculo posterior (lo dispara el
    signal de cobranzas) reproduzca el total original en vez de correrlo centavos.
    """
    filas = list(grupos)
    suma = sum(base + monto for _, base, monto in filas) + otros
    ajuste = total - suma
    ultima = len(filas) - 1
    for indice, (tasa, base, monto) in enumerate(filas):
        if indice == ultima:
            monto += ajuste
        cpb_comprobante_detalle.objects.create(
            cpb_comprobante=comprobante,
            cantidad=1,
            tasa_iva=tasa,
            coef_iva=tasa.coeficiente if tasa else 0,
            importe_unitario=base,
            importe_subtotal=base,
            importe_iva=monto,
            importe_total=base + monto,
            detalle=descripcion)


@transaction.atomic
def importar(archivo, empresa, compra_venta, usuario=None):
    u"""compra_venta: 'C' para Recibidos (compras), 'V' para Emitidos (ventas)."""
    tipo_entidad = 2 if compra_venta == 'C' else 1
    estado = cpb_estado.objects.filter(pk=1).first()
    resultado = {'creados': 0, 'omitidos': 0, 'errores': []}

    for nro_linea, fila in enumerate(leer_filas(archivo), start=2):
        codigo_afip = a_entero(fila.get('tipo'))
        tipo, letra = _buscar_tipo(codigo_afip, compra_venta)
        if not tipo:
            resultado['errores'].append(
                u'Línea %s: tipo de comprobante AFIP %s sin equivalente en el sistema.'
                % (nro_linea, codigo_afip))
            continue

        fecha = a_fecha(fila.get('fecha'))
        if not fecha:
            resultado['errores'].append(
                u'Línea %s: fecha inválida (%s).' % (nro_linea, fila.get('fecha')))
            continue

        pto_vta = a_entero(fila.get('pto_vta'))
        numero = a_entero(fila.get('numero_desde'))
        # El signal actualizar_ultimo_nro exige que el punto de venta exista
        if tipo.usa_pto_vta and not cpb_pto_vta.objects.filter(
                numero=pto_vta, empresa=empresa).exists():
            resultado['errores'].append(
                u'Línea %s: no existe el punto de venta %s en la empresa. Créelo y reimporte.'
                % (nro_linea, pto_vta))
            continue

        if cpb_comprobante.objects.filter(empresa=empresa, cpb_tipo=tipo, letra=letra,
                                          pto_vta=pto_vta, numero=numero).exists():
            resultado['omitidos'] += 1
            continue

        gravado = a_decimal(fila.get('gravado'))
        iva = a_decimal(fila.get('iva'))
        no_gravado = a_decimal(fila.get('no_gravado'))
        exento = a_decimal(fila.get('exento'))
        otros = a_decimal(fila.get('otros_tributos'))
        total = a_decimal(fila.get('total'))
        cotizacion = a_decimal(fila.get('cotizacion')) or Decimal(1)

        # El rango Desde-Hasta agrupa comprobantes a consumidor final en una sola línea
        numero_hasta = a_entero(fila.get('numero_hasta'))
        observacion = u'Importado de ARCA'
        if numero_hasta and numero_hasta != numero:
            observacion += u' (rango %s a %s)' % (numero, numero_hasta)

        comprobante = cpb_comprobante.objects.create(
            cpb_tipo=tipo,
            entidad=_buscar_entidad(fila, empresa, tipo_entidad),
            pto_vta=pto_vta,
            letra=letra,
            numero=numero,
            fecha_cpb=fecha,
            fecha_vto=fecha,
            fecha_imputacion=fecha,
            cae=(fila.get('cae') or '').strip() or None,
            importe_gravado=gravado,
            importe_iva=iva,
            importe_subtotal=gravado + iva,
            importe_no_gravado=no_gravado,
            importe_exento=exento,
            importe_perc_imp=otros,
            importe_total=total,
            moneda=_buscar_moneda(fila.get('moneda')),
            cotizacion=cotizacion,
            estado=estado,
            observacion=observacion,
            empresa=empresa,
            usuario=usuario,
            # Sin detalles que cobrar/pagar, el saldo es el total del comprobante
            saldo=total,
        )
        grupos = _agrupar_por_alicuota(fila, gravado, iva, no_gravado, exento, total)
        _crear_alicuotas(comprobante, grupos)
        _crear_detalles(comprobante, grupos, otros, total,
                        u'%s %s %s' % (tipo.nombre, letra, comprobante.get_numero()))
        resultado['creados'] += 1

    return resultado
