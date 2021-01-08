# -*- coding: utf-8 -*-
from datetime import datetime, timedelta,date
import calendar
from django.contrib import messages
from django.conf import settings
from django.contrib.messages import constants as message_constants
from django.forms import Widget
from django.utils.safestring import mark_safe
import json
from decimal import *
# from settings import ENTIDAD_DIR,MEDIA_ROOT,PROJECT_ROOT
from django.core.files.storage import default_storage


label_todos = 'Todos/as'

SINO = (    
    (0, u''),
    (1, u'S'),
    (2, u'N'),
)

SINO_ = (    
    (1, u'S'),
    (2, u'N'),
)

TIPO_USR = (
    (0, u'Administrador'),
    (1, u'Cliente/Usuario'),
    (2, u'Vendedor/Empleado'),
    (3, u'Contador'),
)

def habilitado_contador(tipo_usr):
    return tipo_usr in [0,3]
    
TIPO_CTA = (
    (0, u'Padre'),
    (1, u'Ingreso'),
    (2, u'Egreso'),
)

TIPO_CTA_DISPO = (
    (0, u'CAJA'),
    (1, u'BANCO'),
    (2, u'ALMACENA VALOR'),
    (3, u'INTERNO'),
)

ESTADO_ = (
 (0,'ACTIVOS'), 
 (1,'TODOS'), 
 (2,'ANULADOS'),
)

COMPROB_FISCAL_X = (('X', 'X'),)


CATEG_FISCAL = (
(1, 'IVA Responsable Inscripto'),          
(2, 'Responsable No Inscripto'),          
(3, 'IVA No Responsable'),  
(4, 'IVA Sujeto Exento'),  
(5, 'Consumidor Final'),  
(6, 'Monotributista'),  
(7, 'No Categorizado'),
(8, 'Proveedor Exterior'),  
(9, 'Consumidor Exterior'),  
(10,'IVA Liberado-Ley19.640'),  
(11,u'IVA RI – Ag. Percepción'),  
(12,'Eventual'),  
(13,'Monotributista Social'),  
(14,'Eventual Social'),  
)

TIPO_DOC = (    
(80,'CUIT'),
(86,'CUIL'),
(87,'CDI'),
(89,'LE'),
(90,'LC'),
(91,'CI Extr.'),
(92,'En trámite'),
(93,'Acta Nac.'),
(94,'Pasaporte'),
(95,'CI'),
(96,'DNI'),
(99,'CF'),
(30,'C.Migr.'),
(88,'Usado Anses'),
)

ESTADO_CPB = (    
    (1, 'PENDIENTE'),
    (2, 'COBRADO')
)

FACTURAS_X = (    
    (0, 'SI'),
    (1, 'NO')
)

TIPO_COMPROBANTE = (
    (1,'Factura'),
    (2,u'Nota Crédito'),
    (3,u'Nota Débito'),
    (4,'Recibo Cobro'),
    (5,'Remito'),
    (6,'Presupuesto'),
    (7,'Orden de Pago'),
    (8,'Movimiento/Ajuste Interno'),
    (9,'Otros'),
    (10,'Nota Pedido'),
    (11,'Orden Trabajo'),
    (12,u'Orden Colocación'),
    (13,u'Movimientos Stock'),
    (14,u'Liquido Producto'),
    (21,u'Factura Crédito Electrónica'),    
    (22,u'Nota Débito Electrónica'),
    (23,u'Nota Crédito Electrónica'),
    (24,u'Saldo Inicial'),
)

COMPROB_FISCAL = (
('A', 'A'),          
('B', 'B'),  
('C', 'C'),  
('M', 'M'),  
('E', 'E'),  
('X', 'X'), 
)

COMPROB_FISCAL_ = (
('', ''),
('A', 'A'),          
('B', 'B'),  
('C', 'C'),  
('M', 'M'),  
('E', 'E'),  
('X', 'X'), 
)

CONDICION_PAGO = (    
    (1, 'A Cuenta Corriente'),
    (2, 'Pago/Saldo Total'),
)

TIPO_LOGOTIPO = (    
    (1, 'Sin LOGOTIPO'),
    (2, 'Con LOGOTIPO total'),
    (3, 'Con LOGOTIPO y detalles'),    
)

SIGNO = (
    (1,'+'),
    (-1,'-'),
)

TIPO_LISTA = (    
    (1, 'Venta'),
    (2, 'Compra'),
)

MONEDA = (    
    (1, 'Pesos'),
    (2, u'Dólares'),
)

TIPO_UNIDAD = (    
    (0, 'u.'),
    (1, u'm'),
    (2, u'm2'),
    (3, u'm3'),
    (4, u'cm'),
    (5, u'cm2'),
    (6, u'cm3'),
    (7, u'mm'),
    (8, u'mm2'),
    (9, u'mm3'),
    (10, u'gr'),
    (11, u'Kg'),
    (12, u'lts'),
    (13, u'par'),
    (14, u'doc'),
    (15, u'km'),
    (16, u'ton'),

)

TIPO_ENTIDAD = (    
    (1, 'Cliente'),
    (2, 'Proveedor'),
    (3, 'Empleado'),
)

TIPO_IVA = (
    
    (1,'No Gravado'),
    (2,'Exento'),
    (3,'0%'),
    (4,'10,50%'),
    (5,'21%'),
    (6,'27%'),
    (9,'2,50%'),
    (8,'5%'),
    
)


OTROS_TRIBUTOS = (
(1,'Impuestos nacionales'),
(2,'Impuestos provinciales'),
(3,'Impuestos municipales'),
(4,'Impuestos internos'),
(99,'Otros'),
)

  
PROVINCIAS = (
(0,u'CABA'),
(1,'Buenos Aires'),
(2,'Catamarca'),
(3,u'Córdoba'),
(4,'Corrientes'),
(5,u'Entre Ríos'),
(6,'Jujuy'),
(7,'Mendoza'),
(8,'La Rioja'),
(9,'Salta'),
(10,'San Juan'),
(11,'San Luis'),
(12,'Santa Fe'),
(13,'Santiago del Estero'),
(14,u'Tucumán'),
(16,'Chaco'),
(17,'Chubut'),
(18,'Formosa'),
(19,'Misiones'),
(20,u'Neuquén'),
(21,'La Pampa'),
(22,'Río Negro'),
(23,'Santa Cruz'),
(24,'Tierra del Fuego/Antártida/Islas Malvinas'),
)            

ANIOS = (
    ('2018', '2018'),
    ('2017', '2017'),
    ('2016', '2016'),
    ('2015', '2015'),
    ('2014', '2014'),
    ('2013', '2013'),
    ('2012', '2012'),
    ('2011', '2011'),
    ('2010', '2010'),
)

MESES = (
    ('1', 'Ene'),
    ('2', 'Feb'),
    ('3', 'Mar'),
    ('4', 'Abr'),
    ('5', 'May'),
    ('6', 'Jun'),
    ('7', 'Jul'),
    ('8', 'Ago'),
    ('9', 'Sep'),
    ('10','Oct'),
    ('11','Nov'),
    ('12','Dic'),
)

PERIODOS = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
)

TIPO_RETENCIONES = (
(1,'Ganancias'),
(2,'IIBB'),
(3,'Retenc. Bancarias'),
(4,'IVA'),
(5,'Seguridad Social'),
(6,'Otros'),
)

# URL_API = "https://soa.afip.gob.ar/sr-padron/v2/persona/"
URL_API = "http://afip.grupoguadalupe.com.ar/?cuit="
EMAIL_CONTACTO = 'contacto@ironweb.com.ar'

def usuario_actual(request):    
    return request.user.userprofile.id_usuario

def empresa_actual(request):    
    return request.user.userprofile.id_usuario.empresa

#Incluye la empresa del usuario + la empresa 1 universal
def empresas_habilitadas(request):    
    e = empresa_actual(request)
    lista = [int(e.id),1]   
    return lista

def empresas_habilitadas_list(empresa):    
    e = empresa
    lista = [int(e.id),1]   
    return lista

def tipo_comprob_fiscal(id):
    if id==6:
        COMPROB_FISCAL = (('C', 'C'),('X', 'X'))
    elif id==1:
        COMPROB_FISCAL = (('A', 'A'),('B', 'B'),('X', 'X') )
    else:
        COMPROB_FISCAL = (('A', 'A'),('B', 'B'),('C', 'C'),('X', 'X') )
    return COMPROB_FISCAL

def facturacion_cliente_letra(letra, cliente_categ,empresa_categ):
    #RI        
    if empresa_categ==1:
        #RI
        if cliente_categ==1:
            return (letra in ['A','E','M'])
        else:
            return (letra in ['B'])
    else:
        return (letra in ['C'])

def nofacturac_cliente_letra(letra, cliente_categ,empresa_categ):
    #RI    
    if empresa_categ==1:
        #RI
        if cliente_categ==1:
            return (letra in ['A','E','M','X'])
        else:
            return (letra in ['B','X'])
    else:
        return (letra in ['C','X'])

def get_letra(cliente_categ,empresa_categ):
    #RI
    if empresa_categ==1:
        #RI
        if cliente_categ==1:
            return 'A'
        else:
            return 'B'
    else:
        return 'C'

def popover_html(label, content):
    return label + ' &nbsp;<i class="fa fa-question-circle recargarDatos" data-toggle="tooltip" data-placement="top" title="'+ content +'"></i>'

class PrependWidget(Widget):
    def __init__(self, base_widget, data, *args, **kwargs):
        u"""Initialise widget and get base instance"""
        super(PrependWidget, self).__init__(*args, **kwargs)
        self.base_widget = base_widget(*args, **kwargs)
        self.data = data

    def render(self, name, value, attrs=None):
        u"""Render base widget and add bootstrap spans"""
        field = self.base_widget.render(name, value, attrs)
        return mark_safe((
            u'<div class="input-group">'
            u'    <span class="input-group-addon">%(data)s</span>%(field)s'
            u'</div>'
        ) % {'field': field, 'data': self.data})

class PostPendWidget(Widget):
    def __init__(self, base_widget, data,tooltip, *args, **kwargs):
        u"""Initialise widget and get base instance"""
        super(PostPendWidget, self).__init__(*args, **kwargs)
        self.base_widget = base_widget(*args, **kwargs)
        self.data = data
        self.tooltip = tooltip

    def render(self, name, value, attrs=None):
        field = self.base_widget.render(name, value, attrs)
        return mark_safe((
            u'<div class="input-group">'
            u'    %(field)s<span class="input-group-addon" title="%(tooltip)s">%(data)s</span>'
            u'</div>'
        ) % {'field': field, 'data': self.data,'tooltip':self.tooltip})

class PostPendWidgetBuscar(Widget):
    def __init__(self, base_widget, data,tooltip, *args, **kwargs):
        u"""Initialise widget and get base instance"""
        super(PostPendWidgetBuscar, self).__init__(*args, **kwargs)
        self.base_widget = base_widget(*args, **kwargs)
        self.data = data
        self.tooltip = tooltip

    def render(self, name, value, attrs=None):
        field = self.base_widget.render(name, value, attrs)
        return mark_safe((
            u'<div class="input-group">'
            u'    %(field)s<span class="input-group-addon btnBuscar" type="button" id="Buscar" title="%(tooltip)s"><strong>%(data)s</strong></span>'
            u''
            u'</div>'
        ) % {'field': field, 'data': self.data,'tooltip':self.tooltip})     

class PrePendWidgetBoton(Widget):
    def __init__(self, base_widget, data,tooltip,id, *args, **kwargs):
        u"""Initialise widget and get base instance"""
        super(PrePendWidgetBoton, self).__init__(*args, **kwargs)
        self.base_widget = base_widget(*args, **kwargs)
        self.data = data
        self.tooltip = tooltip
        self.id = id

    def render(self, name, value, attrs=None):
        field = self.base_widget.render(name, value, attrs)
        return mark_safe((
            u'<div class="input-group">'
            u'    <span class="input-group-addon btnBuscar" type="button" id="%(id)s" title="%(tooltip)s"><strong>%(data)s</strong></span>%(field)s'
            u'</div>'
        ) % {'field': field, 'data': self.data,'tooltip':self.tooltip,'id': self.id})     

# def digVerificador(num):
#     lista = list(num)
#     pares= lista[1::2]
#     impares= lista[0::2]
    
#     totPares = 0
#     totImpares = 0

#     for i in pares:
#         totPares=totPares+int(i*3)

#     for i in impares:
#         totImpares=totImpares+int(i)
 
#     final = totImpares+totPares

#     while (final > 9):
#         cad=str(final)
#         tot=0
#         for i in cad:
#             tot=tot+int(i)
#         final=tot

#     return final

def digVerificador(codigo):
        "Rutina para el cálculo del dígito verificador 'módulo 10'"
        # http://www.consejo.org.ar/Bib_elect/diciembre04_CT/documentos/rafip1702.htm
        # Etapa 1: comenzar desde la izquierda, sumar todos los caracteres ubicados en las posiciones impares.
        codigo = codigo.strip()
        if not codigo or not codigo.isdigit():
            return ''
        etapa1 = sum([int(c) for i,c in enumerate(codigo) if not i%2])
        # Etapa 2: multiplicar la suma obtenida en la etapa 1 por el número 3
        etapa2 = etapa1 * 3
        # Etapa 3: comenzar desde la izquierda, sumar todos los caracteres que están ubicados en las posiciones pares.
        etapa3 = sum([int(c) for i,c in enumerate(codigo) if i%2])
        # Etapa 4: sumar los resultados obtenidos en las etapas 2 y 3.
        etapa4 = etapa2 + etapa3
        # Etapa 5: buscar el menor número que sumado al resultado obtenido en la etapa 4 dé un número múltiplo de 10. Este será el valor del dígito verificador del módulo 10.
        digito = 10 - (etapa4 - (int(etapa4 / 10) * 10))
        if digito == 10:
            digito = 0
        return str(digito)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]        


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)    


def limpiar_sesion(request):
    if 'cpbs_cobranza' in request.session:
        del request.session['cpbs_cobranza']     

    if 'cpbs_pagos' in request.session:
        del request.session['cpbs_pagos']     

    if 'cheques' in request.session:
        del request.session['cheques']  


# def fmt_fact(self, tipo_cbte, punto_vta, cbte_nro):
#         "Formatear tipo, letra y punto de venta y número de factura"
#         n = "%04d-%08d" % (int(punto_vta), int(cbte_nro))
#         t, l = tipo_cbte, ''
#         for k,v in self.tipos_fact.items():
#             if int(tipo_cbte) in k:
#                 t = v
#         for k,v in self.letras_fact.items():
#             if int(int(tipo_cbte)) in k:
#                 l = v
#         return t, l, n



def inicioMes():
    hoy=date.today()
    hoy = date(hoy.year,hoy.month,1)
    return hoy

def hoy():
    return date.today()    

def inicioMesAnt():
    hoy=inicioMes()
    dia =hoy - timedelta(days=30)
    return dia

def finMes():
    hoy=date.today()
    hoy = date(hoy.year,hoy.month,calendar.monthrange(hoy.year, hoy.month)[1])
    return hoy

def ultimo_semestre():
    hoy = date.today()
    fecha = hoy - timedelta(days=180)
    return fecha

def ultimo_anio():
    hoy = date.today()
    fecha = hoy - timedelta(days=365)
    return fecha

import re

def mobile(request):
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]        


def validar_cuit(cuit):
    # validaciones minimas    
    if not cuit:
        return False
    if len(cuit) < 11:
        return False

    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    cuit = cuit.replace("-", "") # remuevo las barras

    # calculo el digito verificador:
    aux = 0
    for i in xrange(10):
        aux += int(cuit[i]) * base[i]

    aux = 11 - (aux - (int(aux / 11) * 11))

    if aux == 11:
        aux = 0
    if aux == 10:
        aux = 9

    return aux == int(cuit[10])


import os
def get_image_name(instance, filename):
    f, ext = os.path.splitext(filename)
    #archivo = '%s%s' % (instance.numero_documento, ext)
    archivo = filename
    return os.path.join('empresa', archivo) 
    

MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger',}


