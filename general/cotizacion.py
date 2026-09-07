# -*- coding: utf-8 -*-
import json
import logging
import urllib2
from decimal import Decimal

from django.core.cache import cache

logger = logging.getLogger(__name__)

MONEDAS_LOCALES = {'ARS'}
MONEDA_DOLAR = 'USD'
URL_API_DOLAR = 'https://dolarapi.com/v1/dolares/oficial'
CACHE_KEY = 'cotizacion_dolar'
CACHE_TTL = 20 * 60


def aplica_cotizacion(moneda_cpb, moneda_lista):
    return bool(moneda_cpb and moneda_lista
                and moneda_cpb.codigo in MONEDAS_LOCALES
                and moneda_lista.codigo == MONEDA_DOLAR)


def get_cotizacion_dolar():
    valor = cache.get(CACHE_KEY)
    if valor:
        return valor
    try:
        req = urllib2.Request(URL_API_DOLAR)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36')
        req.add_header('Accept', 'application/json')
        response = urllib2.urlopen(req, timeout=10)
        data = json.loads(response.read())
        valor = Decimal(str(data['venta']))
        cache.set(CACHE_KEY, valor, CACHE_TTL)
        cache.set(CACHE_KEY + '_ultima', valor, None)
        return valor
    except Exception as e:
        logger.error(e)
        logger.exception('No se pudo obtener la cotizacion del dolar desde %s', URL_API_DOLAR)
        return cache.get(CACHE_KEY + '_ultima') or Decimal(1)
