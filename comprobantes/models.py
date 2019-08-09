# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from datetime import datetime,date
from dateutil.relativedelta import *
from django.conf import settings
import os 
from general.utilidades import *
from productos.models import prod_productos,gral_tipo_iva,prod_ubicacion,prod_lista_precios
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from django.dispatch import receiver
from entidades.models import egr_entidad

class cpb_estado(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(u'Nombre',max_length=100)
    color = models.CharField(u'Color',max_length=200,blank=True, null=True)   
    tipo = models.IntegerField(u'Tipo CPB',choices=TIPO_COMPROBANTE,default=1,blank=True, null=True)
    class Meta:
        db_table = 'cpb_estado'

    def __unicode__(self):
        return u'%s' % (self.nombre)   

class cpb_tipo(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(u'Nombre',max_length=100)    
    detalle = models.CharField(u'Detalle',max_length=100,blank=True, null=True) 
    codigo = models.CharField(u'Código',max_length=10,blank=True, null=True)    
    tipo = models.IntegerField(u'Tipo CPB',choices=TIPO_COMPROBANTE,default=1,blank=True, null=True)
    usa_pto_vta = models.BooleanField(u'Usa Pto Venta',default=False)#False para los cpb que no tienen el pto de venta por tabla, sino entero o copiado del CPB originante
    ultimo_nro = models.PositiveIntegerField(u'Último Nº',default=0,blank=True, null=True)#Usado para los cpb que son comunes a todos, ej remito, presupuesto, etc
    usa_forma_pago = models.BooleanField(u'Usa FP',default=True)
    signo_forma_pago = models.IntegerField(u'Signo FP',choices=SIGNO,default=1,blank=True, null=True)
    usa_ctacte = models.BooleanField(u'Usa Cta.Cte.',default=True)
    signo_ctacte = models.IntegerField(u'Signo Cta.Cte.',choices=SIGNO,default=1,blank=True, null=True)
    usa_stock = models.BooleanField(u'Usa Stock',default=True)
    signo_stock = models.IntegerField(u'Signo Stock',choices=SIGNO,default=1,blank=True, null=True)
    compra_venta = models.CharField(max_length=1, blank=True, null=True,default='V')
    libro_iva = models.BooleanField(u'Libro IVA',default=True)
    signo_libro_iva = models.IntegerField(u'Signo Libro IVA',default=1,blank=True, null=True)
    facturable = models.BooleanField(u'Facturable',default=True)
    baja = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add = True)
    fecha_modif = models.DateTimeField(auto_now = True)
    class Meta:
        db_table = 'cpb_tipo'
    
    def __unicode__(self):
        return u'%s' % (self.nombre)   

class cpb_nro_afip(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_tipo = models.IntegerField(u'Tipo CPB',choices=TIPO_COMPROBANTE,default=1,blank=True, null=True)
    letra = models.CharField(u'Letra',choices=COMPROB_FISCAL,max_length=1,blank=True, null=True)
    numero_afip = models.PositiveSmallIntegerField(u'Nº AFIP',blank=True, null=True)  
    class Meta:
        db_table = 'cpb_nro_afip'
    
    def __unicode__(self):
        return u'%s - %s --> %s' % (self.cpb_tipo,self.letra,self.numero_afip)  

class cpb_pto_vta(models.Model):
    id = models.IntegerField(u'Número',primary_key=True,db_index=True)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    numero = models.IntegerField(u'Número PV')        
    nombre = models.CharField(u'Nombre Punto Venta',max_length=50,blank=True, null=True)        
    es_sucursal = models.BooleanField(u'Es Sucursal',default=False)
    domicilio = models.CharField('Domicilio',max_length=200,blank=True, null=True)   
    provincia = models.IntegerField('Provincia',choices=PROVINCIAS, blank=True, null=True,default=12)
    localidad = models.CharField('Localidad',max_length=100,blank=True, null=True)   
    cod_postal = models.CharField('CP',max_length=50,blank=True, null=True)
    email = models.EmailField('Email',blank=True,null=True)
    telefono = models.CharField(u'Teléfono',max_length=50,blank=True, null=True)   
    celular = models.CharField('Celular',max_length=50,blank=True, null=True)   
    baja = models.BooleanField(default=False)    
    interno = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add = True)
    fecha_modif = models.DateTimeField(auto_now = True)
    #DATOS FISCALES
    fe_electronica = models.BooleanField(u'Factura Electrónica',default=False)
    categ_fiscal = models.IntegerField(u'Categoría Fiscal',choices=CATEG_FISCAL, blank=True, null=True)  
    cuit = models.CharField('CUIT',max_length=50)   
    iibb = models.CharField(u'Nº IIBB',max_length=50,blank=True, null=True)   
    fecha_inicio_activ = models.DateTimeField('Fecha Inicio Actividades',null=True)
    nombre_fantasia = models.CharField(u'Nombre Fantasía',max_length=200,blank=True, null=True)     
    ruta_logo = models.CharField(db_column='ruta_logo', max_length=100,null=True, blank=True) # Field name made lowercase.    
    tipo_logo_factura = models.IntegerField(u'Tipo Logotipo',choices=TIPO_LOGOTIPO, blank=True, null=True)  
    fe_crt = models.CharField('Nombre Archivo CRT',max_length=50,blank=True, null=True) 
    fe_key = models.CharField('Nombre Archivo Key',max_length=50,blank=True, null=True) 

    class Meta:
        db_table = 'cpb_pto_vta'      
    
    def __unicode__(self):
        return u'%s - %s' % ("{num:>05}".format(num=str(self.numero)),self.nombre)                  

    def get_numero(self):
        return u'%s' % ("{num:>05}".format(num=str(self.numero)))   

class cpb_pto_vta_numero(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_tipo = models.ForeignKey('comprobantes.cpb_tipo',verbose_name=u'Tipo CPB', db_column='cpb_tipo',blank=True, null=True)
    letra = models.CharField(u'Letra',choices=COMPROB_FISCAL,max_length=1,blank=True, null=True)
    cpb_pto_vta = models.ForeignKey('comprobantes.cpb_pto_vta',verbose_name=u'Punto Vta', db_column='cpb_pto_vta',blank=True, null=True,on_delete=models.SET_NULL)
    ultimo_nro = models.PositiveIntegerField(u'Último Nº',default=0,blank=True, null=True)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'cpb_pto_vta_numero'
    
    def __unicode__(self):
        return u'%s %s-%s-%s' % (self.cpb_tipo,self.letra,self.cpb_pto_vta.numero,self.ultimo_nro)

class cpb_comprobante(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_tipo = models.ForeignKey('comprobantes.cpb_tipo',verbose_name=u'Tipo CPB', db_column='cpb_tipo',blank=True, null=True)
    entidad = models.ForeignKey('entidades.egr_entidad',db_column='entidad',related_name='cpb_entidad',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Proveedor
    vendedor = models.ForeignKey('entidades.egr_entidad',db_column='vendedor',related_name='cpb_vendedor',blank=True, null=True,on_delete=models.SET_NULL)
    pto_vta = models.IntegerField(blank=True, null=True,db_column='pto_vta')
    #pto_vta = models.ForeignKey('cpb_pto_vta',blank=True, null=True,on_delete=models.SET_NULL)
    letra = models.CharField(u'Letra',choices=COMPROB_FISCAL,max_length=1,blank=True, null=True)
    numero = models.IntegerField(u'Número',blank=True, null=True)
    condic_pago = models.IntegerField(choices=CONDICION_PAGO, blank=True, null=True,default=1)
    fecha_creacion = models.DateTimeField(auto_now_add = True,blank=True, null=True)
    fecha_cpb = models.DateField('Fecha Comprobante')
    fecha_imputacion = models.DateField(blank=True, null=True)
    fecha_vto = models.DateField(blank=True, null=True)
    presup_tiempo_entrega =  models.CharField(u'Tiempo de Entrega',max_length=100,blank=True, null=True)
    presup_forma_pago =  models.CharField(u'Forma de Pago',max_length=200,blank=True, null=True)    
    presup_aprobacion =  models.ForeignKey('comprobantes.cpb_estado',related_name='presup_estado',blank=True, null=True,on_delete=models.SET_NULL)
    cae =  models.CharField(u'CAE',max_length=100,blank=True, null=True)
    cae_vto = models.DateField('CAE Vto.',blank=True, null=True)    
    importe_gravado = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Todo lo que tiene IVA
    importe_iva = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de los IVA
    importe_subtotal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de gravado+IVA
    importe_no_gravado = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de TiposIVA No Gravados
    importe_exento = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de TiposIVA Exentos
    importe_perc_imp = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de Percepciones e Impuestos
    importe_ret = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de Retenciones
    importe_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de todo
    estado = models.ForeignKey('comprobantes.cpb_estado',related_name='estado',blank=True, null=True,on_delete=models.SET_NULL)
    anulacion_motivo = models.CharField(u'Motivo Anulación',max_length=200,blank=True, null=True)
    anulacion_fecha = models.DateField(blank=True, null=True)
    observacion = models.TextField(max_length=500, blank=True, null=True) # Field name made lowercase.
    id_cpb_padre = models.ForeignKey('comprobantes.cpb_comprobante', db_column='id_cpb_padre',related_name="cpb_comprobante_padre",blank=True, null=True,on_delete=models.SET_NULL)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    usuario = models.ForeignKey('usuarios.usu_usuario',db_column='usuario',blank=True, null=True,related_name='usu_usuario_cpb',on_delete=models.SET_NULL)
    seguimiento = models.TextField(max_length=500, blank=True, null=True)
    fecha_envio_mail = models.DateField(blank=True, null=True)
    fecha_recepcion_mail = models.DateField(blank=True, null=True)
    cae_observaciones = models.TextField(max_length=1000, blank=True, null=True)
    cae_excepcion = models.TextField(max_length=1000, blank=True, null=True)
    cae_traceback = models.TextField(max_length=1000, blank=True, null=True)
    cae_xml_request = models.TextField(max_length=1000, blank=True, null=True)
    cae_xml_response = models.TextField(max_length=1000, blank=True, null=True)
    cae_errores = models.TextField(max_length=1000, blank=True, null=True)
    class Meta:
        db_table = 'cpb_comprobante'
    
    def __unicode__(self):
        return u'%s-%s-%s' % ("{num:>05}".format(num=str(self.pto_vta)),self.letra,"{num:>08}".format(num=str(self.numero)))              

    
    # def get_cpb(self):
    #     return u'%s-%s-%s' % ("{num:>04}".format(num=str(self.pto_vta)),self.letra,"{num:>08}".format(num=str(self.numero)))              

    @property
    def get_cpb(self):        
        return u'%s-%s-%s' % ("{num:>05}".format(num=str(self.pto_vta)),self.letra,"{num:>08}".format(num=str(self.numero)))              

    

    def get_pto_vta(self):
        try:
            pv= cpb_pto_vta.objects.get(numero=self.pto_vta,empresa=self.empresa)  
        except:
            return None
        return pv


    @property
    def estado_cpb(self):        
        #Si es presupuesto verifico que no esté vencido
        if self.cpb_tipo.tipo == 6:
            if (self.fecha_vto <= timezone.now().date()) and (self.estado.pk<12):
                e=cpb_estado.objects.get(pk=11)
            else:
                e=self.estado
        else:
            e=self.estado
        return e

    @property
    def estado_color(self):        
        if self.estado:
            return self.estado.color
    
    @property
    def seleccionable(self):        
        if self.cpb_tipo.compra_venta=='V':
            return (self.estado.id in [1,2]) and not(self.cae and (self.estado.id==2))
        elif self.cpb_tipo.compra_venta=='C':
            return (self.estado.id in [1,2])

    @property
    def vencimiento_cpb(self):        
        if self.fecha_vto:
            if (self.fecha_vto <= timezone.now().date()):
                e=cpb_estado.objects.get(pk=11)
            else:
                e=self.estado        
        else:
            e=self.estado        
        return e

    def get_nro_afip(self):
        try:
            c = cpb_nro_afip.objects.get(cpb_tipo=self.cpb_tipo.tipo,letra=self.letra)
        except:
            return None
        return c.numero_afip

    def get_numero(self):                
        return '%s-%s' % ("{num:>05}".format(num=str(self.pto_vta)),"{num:>08}".format(num=str(self.numero))) 

    @property
    def get_cpb_tipo(self):                
        return u'%s: %s-%s-%s ' % (self.cpb_tipo,"{num:>05}".format(num=str(self.pto_vta)),self.letra,"{num:>08}".format(num=str(self.numero)))

    def get_cobranzas(self):                
        cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=self,cpb_comprobante__estado__pk__lt=3).select_related('cpb_factura','cpb_factura__cpb_tipo','cpb_comprobante')
        return list(cobranzas)

    def tiene_cobranzas(self):                
        return cpb_cobranza.objects.filter(cpb_factura=self).count() > 0   

    def tiene_cobranzasREC_OP(self):                
        return cpb_cobranza.objects.filter(cpb_comprobante=self).count() > 0 
        
    def get_listado(self):        
        if self.cpb_tipo.pk in [1,3,5,14,20,23]:
            return reverse('cpb_venta_listado')
        elif self.cpb_tipo.pk in [2,4,6,18,19]:
            return reverse('cpb_compra_listado')
        elif self.cpb_tipo.pk in [8]:
            return reverse('cpb_remito_listado')
        elif self.cpb_tipo.pk in [9]:
            return reverse('cpb_remitoc_listado')
        elif self.cpb_tipo.pk in [7]:
            return reverse('cpb_rec_cobranza_listado')
        elif self.cpb_tipo.pk in [12]:
            return reverse('cpb_pago_listado')
        elif self.cpb_tipo.pk == 11:
            return reverse('cpb_presup_listado')
        elif self.cpb_tipo.pk in [13]:
            return reverse('movimientos_listado')
        else:
            return reverse('principal')

    def get_importe_total(self):
        signo = self.cpb_tipo.signo_ctacte
        if not self.importe_total:
            return 0
        if signo:
            return self.importe_total * signo
        else:
            return self.importe_total

    def get_importe_subtotal(self):
        signo = self.cpb_tipo.signo_ctacte
        if signo:
            return self.importe_subtotal * signo
        else:
            return self.importe_subtotal

    def get_importe_iva(self):
        signo = self.cpb_tipo.signo_ctacte
        if signo:
            return self.importe_iva * signo
        else:
            return self.importe_iva

    def get_saldo(self):
        signo = self.cpb_tipo.signo_ctacte
        if signo:
            return self.saldo * signo
        else:
            return self.saldo

    def get_importe_gravado(self):
        signo = self.cpb_tipo.signo_ctacte
        if signo:
            return self.importe_gravado * signo
        else:
            return self.importe_gravado

    def get_importe_no_gravado(self):
        signo = self.cpb_tipo.signo_ctacte
        if signo:
            return self.importe_no_gravado * signo
        else:
            return self.importe_no_gravado

    def get_importe_exento(self):
        signo = self.cpb_tipo.signo_ctacte
        if signo:
            return self.importe_exento * signo
        else:
            return self.importe_exento

    def get_importe_perc_imp(self):
        signo = self.cpb_tipo.signo_ctacte
        if signo:
            return self.importe_perc_imp * signo
        else:
            return self.importe_perc_imp
    
class cpb_comprobante_detalle(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_comprobante = models.ForeignKey('comprobantes.cpb_comprobante',verbose_name=u'CPB', db_column='cpb_comprobante',blank=True, null=True,on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.prod_productos',db_column='producto',related_name='producto',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Proveedor
    cantidad = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=1)
    tasa_iva = models.ForeignKey('productos.gral_tipo_iva',verbose_name='Tasa IVA', db_column='tasa_iva',blank=True, null=True,on_delete=models.SET_NULL)
    coef_iva = models.DecimalField(max_digits=5, decimal_places=3,default=0,blank=True, null=True)
    lista_precios = models.ForeignKey('productos.prod_lista_precios',db_column='lista_precios',related_name='cpb_lista_precios',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Pro
    importe_costo = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    importe_unitario = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    porc_dcto = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,default=0)
    importe_subtotal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    importe_iva = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    importe_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    origen_destino = models.ForeignKey('productos.prod_ubicacion',verbose_name='Origen/Destino', db_column='origen_destino',blank=True, null=True,on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add = True)
    detalle = models.TextField(max_length=500,blank=True, null=True) # Field name made lowercase.   
    class Meta:
        db_table = 'cpb_comprobante_detalle'
    
    def __unicode__(self):
        return u'%s-%s' % (self.producto,self.cantidad)          

    def get_precio_unit_iva(self):                
        #return self.importe_unitario * (1+self.coef_iva)
        return self.importe_unitario

    def get_movim_stock(self):                
        #return self.importe_unitario * (1+self.coef_iva)
        return self.cantidad * self.cpb_comprobante.cpb_tipo.signo_stock

class cpb_perc_imp(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(u'Nombre',max_length=100)
    descripcion = models.CharField(u'Descripción',max_length=200,blank=True, null=True)  
    codigo = models.CharField(u'Código',max_length=2,blank=True, null=True) 
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'cpb_perc_imp'
    
    def __unicode__(self):
        return u'%s' % (self.nombre)  

class cpb_comprobante_perc_imp(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_comprobante = models.ForeignKey('comprobantes.cpb_comprobante',verbose_name=u'CPB', db_column='cpb_comprobante',blank=True, null=True,on_delete=models.CASCADE)
    perc_imp = models.ForeignKey('comprobantes.cpb_perc_imp',db_column='perc_imp',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Proveedor    
    detalle = models.TextField(max_length=500,blank=True, null=True) # Field name made lowercase.   
    importe_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)    
    class Meta:
        db_table = 'cpb_comprobante_perc_imp'
    
    def __unicode__(self):
        return u'%s-%s' % (self.perc_imp,self.importe_total)  

class cpb_retenciones(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(u'Nombre',max_length=100)
    descripcion = models.CharField(u'Descripción',max_length=200,blank=True, null=True)  
    codigo = models.CharField(u'Código',max_length=2,blank=True, null=True) 
    grupo = models.IntegerField('Grupo',choices=TIPO_RETENCIONES, blank=True, null=True,default=1)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'cpb_retenciones'
    
    def __unicode__(self):
        return u'%s' % (self.nombre) 

class cpb_comprobante_retenciones(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_comprobante = models.ForeignKey('comprobantes.cpb_comprobante',verbose_name=u'CPB', db_column='cpb_comprobante',blank=True, null=True,on_delete=models.CASCADE)
    retencion = models.ForeignKey('comprobantes.cpb_retenciones',db_column='retencion',blank=True, null=True,on_delete=models.SET_NULL)
    ret_nrocpb = models.CharField(verbose_name=u'Nº Certif. Retención',max_length=30,blank=True, null=True)  #Número del certificado de retención recibido.
    ret_importe_isar = models.DecimalField(verbose_name=u'Importe Sujeto a Retención',max_digits=15, decimal_places=2, blank=True, null=True,default=0) # Importe neto sujeto a la retención sufrida.
    ret_fecha_cpb = models.DateField(verbose_name=u'Fecha Retención',blank=True, null=True) #Fecha del certificado de retención recibido.
    detalle = models.TextField(max_length=500,blank=True, null=True) 
    importe_total = models.DecimalField(u'Importe Retenido',max_digits=15, decimal_places=2, blank=True, null=True,default=0)# Valor de la retención.
    class Meta:
        db_table = 'cpb_comprobante_retenciones'
    
    def __unicode__(self):
        return u'%s-%s' % (self.retencion,self.importe_total) 

class cpb_comprobante_tot_iva(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_comprobante = models.ForeignKey('comprobantes.cpb_comprobante',verbose_name=u'CPB', db_column='cpb_comprobante',blank=True, null=True,on_delete=models.CASCADE)
    importe_base = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    tasa_iva = models.ForeignKey('productos.gral_tipo_iva',verbose_name='Tasa IVA', db_column='cpb_tasa_iva',blank=True, null=True)    
    importe_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)    
    class Meta:
        db_table = 'cpb_comprobante_tot_iva'
    
    def __unicode__(self):
        return u'%s-%s' % (self.tasa_iva,self.importe_total)  

class cpb_cobranza(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    #ID del RECIBO o de la ORDEN PAGO
    cpb_comprobante = models.ForeignKey('comprobantes.cpb_comprobante',verbose_name=u'CPB',related_name='cpb_cobranza_cpb', db_column='cpb_comprobante',blank=True, null=True,on_delete=models.CASCADE)
    #ID de la factura que voy a cancelar ya sea de COMPRA (para la ORDEN PAGO) o VENTA (para el RECIBO)
    cpb_factura = models.ForeignKey('comprobantes.cpb_comprobante',verbose_name=u'Factura',related_name='cpb_cobranza_factura', db_column='cpb_factura',blank=True, null=True,on_delete=models.CASCADE)
    importe_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)    
    #Descuento o Recargo que tuvo la factura
    desc_rec = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)    
    fecha_creacion = models.DateTimeField(auto_now_add = True)
    class Meta:
        db_table = 'cpb_cobranza'
    
    def __unicode__(self):
        return u'%s-%s-$ %s' % (self.cpb_comprobante,self.cpb_factura,self.importe_total)

class cpb_banco(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    codigo = models.CharField(u'Código',max_length=20,blank=True, null=True)    
    nombre = models.CharField(u'Nombre',max_length=100)    
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    baja = models.BooleanField(default=False)  
    class Meta:
        db_table = 'cpb_banco'
    
    def __unicode__(self):
        return u'%s - %s' % (self.codigo,self.nombre)   

class cpb_cuenta(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)    
    codigo = models.CharField(u'Código',max_length=100,blank=True, null=True)    
    nombre = models.CharField(u'Nombre',max_length=100,blank=True, null=True)
    nro_cuenta_bancaria = models.CharField(u'CBU',max_length=100,blank=True, null=True)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)        
    tipo = models.IntegerField(u'Tipo Cuenta',choices=TIPO_CTA_DISPO,default=0,blank=True, null=True)
    tipo_forma_pago = models.ForeignKey('comprobantes.cpb_tipo_forma_pago',db_column='tipo_forma_pago',related_name='tipo_fp',blank=True, null=True,on_delete=models.SET_NULL) 
    modificable = models.BooleanField(default=True)  
    baja = models.BooleanField(default=False)  
    banco = models.ForeignKey('comprobantes.cpb_banco',db_column='banco',related_name='cuenta_banco',blank=True, null=True,on_delete=models.SET_NULL) 
    class Meta:
        db_table = 'cpb_cuenta'
    
    def __unicode__(self):
        return u'%s - %s' % (self.codigo,self.nombre)   

class cpb_tipo_forma_pago(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    codigo = models.CharField(u'Código',max_length=10,blank=True, null=True)  
    nombre = models.CharField(u'Nombre',max_length=200,blank=True, null=True)  
    signo = models.IntegerField(u'Signo Cta.Cte.',choices=SIGNO,default=1,blank=True, null=True)
    cuenta = models.ForeignKey('comprobantes.cpb_cuenta',db_column='cuenta',related_name='fp_cuenta',blank=True, null=True,on_delete=models.SET_NULL) 
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)    
    baja = models.BooleanField(default=False)  
    class Meta:
        db_table = 'cpb_tipo_forma_pago'
    
    def __unicode__(self):
        return u'%s - %s' % (self.codigo,self.nombre) 

class cpb_comprobante_fp(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    cpb_comprobante = models.ForeignKey('comprobantes.cpb_comprobante',verbose_name=u'CPB', db_column='cpb_comprobante',blank=True, null=True,on_delete=models.CASCADE)
    tipo_forma_pago = models.ForeignKey('comprobantes.cpb_tipo_forma_pago',db_column='tipo_forma_pago',related_name='tipo_forma_pago',blank=True, null=True,on_delete=models.SET_NULL) 
    cta_egreso = models.ForeignKey('comprobantes.cpb_cuenta',db_column='cta_egreso',related_name='cta_egreso',blank=True, null=True,on_delete=models.SET_NULL) 
    cta_ingreso = models.ForeignKey('comprobantes.cpb_cuenta',db_column='cta_ingreso',related_name='cta_ingreso',blank=True, null=True,on_delete=models.SET_NULL) 
    mdcp_fecha = models.DateField('Fecha',blank=True, null=True)
    mdcp_banco = models.ForeignKey('comprobantes.cpb_banco',verbose_name='Banco', db_column='mdcp_banco',blank=True, null=True,on_delete=models.SET_NULL)
    mdcp_cheque = models.CharField(u'Cheque Nº',max_length=50,blank=True, null=True)  
    importe = models.DecimalField('Importe',max_digits=15, decimal_places=2, blank=True, null=True,default=0)    
    detalle = models.TextField(max_length=500,blank=True, null=True) # Field name made lowercase.   
    fecha_creacion = models.DateTimeField(auto_now_add = True)    
    mdcp_salida = models.ForeignKey('comprobantes.cpb_comprobante_fp',db_column='mdcp_salida',related_name='fp_mov_salida',blank=True, null=True,on_delete=models.SET_NULL)     
    class Meta:
        db_table = 'cpb_comprobante_fp'
    
    def __unicode__(self):
        descr = u'%s $ %s' % (self.tipo_forma_pago.nombre,self.importe)    
        if self.mdcp_banco and self.mdcp_fecha:
            descr = u'%s - %s %s %s %s' % (descr,datetime.strftime(self.mdcp_fecha,"%d/%m/%Y"),self.mdcp_banco,self.mdcp_cheque,self.detalle)         
        return descr

    def get_selCheque(self):
        if self.mdcp_cheque:
            nro = u' | Nº: %s' % (self.mdcp_cheque)
        else:
            nro = ''
        try:
            fecha = u' | Vencimiento: %s' % (datetime.strftime(self.mdcp_fecha,"%d/%m/%Y"))    
        except:
            fecha=''        
        try:            
            banco = ' | '+ str(self.mdcp_banco)
        except:
            banco = ''   
        try:
            descr =' | '+self.detalle
        except:
            descr=''

        return u'$ %s%s%s%s%s' % (self.importe,nro,fecha,banco,descr)

    def get_estadoCheque(self):        
        # cobrados = cheques.filter(cpb_comprobante__cpb_tipo__tipo=4,mdcp_salida__cpb_comprobante__cpb_tipo__tipo=8,cta_egreso__isnull=True,cta_ingreso=cta_cheques,mdcp_salida__isnull=False).order_by('-fecha_creacion','-mdcp_fecha',)
        # pagados = cheques.filter(cpb_comprobante__cpb_tipo__tipo=7,cta_egreso=cta_cheques,mdcp_salida__isnull=True).order_by('-fecha_creacion','-mdcp_fecha',)
        estado=''
        if self.cta_ingreso:
            if (self.cta_ingreso and (not self.cta_egreso)and(self.cta_ingreso.tipo==2)and(not self.mdcp_salida)):
                estado= 'EN CARTERA'
            elif ((not self.cta_egreso)and(self.cta_ingreso.tipo==2)and(self.cpb_comprobante.cpb_tipo.tipo==4)and(self.mdcp_salida.cpb_comprobante.cpb_tipo.tipo==8)):
                estado= 'COBRO/DEPOSITO'
            elif ((not self.cta_egreso)and(self.mdcp_salida)):
                estado= 'UTILIZADO'
        else:
            if self.cta_egreso:
                if((self.cta_egreso.tipo==2)and(not self.mdcp_salida)):
                    estado= 'PAGADO/DIFERIDO'                
        
        return estado

    def _get_origen(self):        
        cpb = cpb_comprobante_fp.objects.filter(mdcp_salida__id=self.id)[0]
        return cpb.cpb_comprobante

    get_origen = property(_get_origen)


######################################################################################################

def recalcular_saldo_cpb(idCpb):# pragma: no cover
    cpb=cpb_comprobante.objects.get(pk=idCpb)           
    #Recalculo los importes del comprobante
    importe_no_gravado = 0
    importe_exento = 0
    importe_gravado = 0
    importe_iva = 0
    importe_subtotal = 0
    importe_total = 0
    tot_perc_imp = 0    
    
    # Cobros y Pagos sólos no recalculan IVA ni detalles, etc
    if cpb.cpb_tipo.tipo in [4,7,8]:
        cpb.importe_gravado = importe_gravado    
        cpb.importe_iva = importe_iva
        cpb.importe_no_gravado = importe_no_gravado
        cpb.importe_exento = importe_exento        
        cpb.importe_perc_imp = 0    
        cpb.saldo = 0
        if cpb.cpb_tipo.tipo in [5]:
            cpb.importe_subtotal = importe_gravado + importe_no_gravado + importe_exento
            cpb.importe_total = importe_subtotal  + tot_perc_imp + importe_iva 
        cpb.save()

    elif cpb.cpb_tipo.tipo in [1,2,3,6,9,14]:
        cpb_detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)
        for c in cpb_detalles:
            if c.tasa_iva:
                if c.tasa_iva.pk==1:
                    importe_no_gravado = importe_no_gravado + c.importe_subtotal
                elif c.tasa_iva.pk==2:
                    importe_exento = importe_exento + c.importe_subtotal            
                else:
                    importe_gravado = importe_gravado + c.importe_subtotal
            else:
                importe_gravado = importe_gravado + c.importe_subtotal

            importe_iva = importe_iva + c.importe_iva
            
        
        try:
            tot_perc_imp = cpb_comprobante_perc_imp.objects.filter(cpb_comprobante=cpb).aggregate(sum=Sum('importe_total'))['sum']        
        except:
            tot_perc_imp = 0
        if not tot_perc_imp:
            tot_perc_imp = 0

        importe_subtotal = importe_gravado + importe_no_gravado + importe_exento

        importe_total = importe_subtotal  + tot_perc_imp + importe_iva 
            
        
        cpb.importe_gravado = importe_gravado    
        cpb.importe_iva = importe_iva
        cpb.importe_subtotal = importe_subtotal
        cpb.importe_no_gravado = importe_no_gravado
        cpb.importe_exento = importe_exento        
        cpb.importe_perc_imp = tot_perc_imp    
        cpb.importe_total = importe_total    


        #Las cobranzas/pagos activos del Comprobante de Venta/Compra
        cobranzas = cpb_cobranza.objects.filter(cpb_factura=cpb,cpb_comprobante__estado__pk__lt=3).aggregate(sum=Sum('importe_total'))
           
        importes = cobranzas['sum']    

        if not importes:
          total = cpb.importe_total
        else:
            #Suma segun el signo
            if cpb.cpb_tipo.usa_ctacte:
              total = (cpb.importe_total - Decimal(importes)*cpb.cpb_tipo.signo_ctacte)  
            else:
              total = (cpb.importe_total - Decimal(importes))
        
        cpb.saldo=total
        
        estado=cpb_estado.objects.get(pk=1)
        if (total == 0)and(cpb.estado.pk<3):
            estado=cpb_estado.objects.get(pk=2)        
                                
        cpb.estado=estado
        cpb.save()

        #regenero los totales de iva por comprobante
        cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=cpb).delete()
        coeficientes=cpb_detalles.filter(tasa_iva__id__gt=2).values('tasa_iva').annotate(importe_total=Sum('importe_iva'),importe_base=Sum('importe_subtotal'))
        
        for cc in coeficientes:
            tasa = gral_tipo_iva.objects.get(pk=cc['tasa_iva'])       
            cpb_ti = cpb_comprobante_tot_iva(cpb_comprobante=cpb,tasa_iva=tasa,importe_total=cc['importe_total'],importe_base=cc['importe_base'])
            cpb_ti.save()

def recalcular_saldos_cobranzas(idCpb):# pragma: no cover
    cpb=cpb_comprobante.objects.get(pk=idCpb)           
    importe_no_gravado = 0
    importe_exento = 0
    importe_gravado = 0
    importe_iva = 0
    importe_subtotal = 0
    importe_total = 0
    tot_perc_imp = 0    
    
    try:
        tot_perc_imp = cpb_comprobante_perc_imp.objects.filter(cpb_comprobante=cpb).aggregate(sum=Sum('importe_total'))['sum']        
    except:
        tot_perc_imp = 0
    if not tot_perc_imp:
        tot_perc_imp = 0

    importe_subtotal = importe_gravado + importe_no_gravado + importe_exento

    importe_total = importe_subtotal  + tot_perc_imp + importe_iva 
        
    
    cpb.importe_gravado = importe_gravado    
    cpb.importe_iva = importe_iva
    cpb.importe_subtotal = importe_subtotal
    cpb.importe_no_gravado = importe_no_gravado
    cpb.importe_exento = importe_exento        
    cpb.importe_perc_imp = tot_perc_imp    
    cpb.importe_total = importe_total    


    #Las cobranzas/pagos activos del Comprobante de Venta/Compra
    cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=cpb,cpb_comprobante__estado__pk__lt=3).aggregate(sum=Sum('importe_total'))
    print cobranzas       
    importes = cobranzas['sum']    

    if not importes:
      total = cpb.importe_total
    else:
        #Suma segun el signo
        if cpb.cpb_tipo.usa_ctacte:
          total = (cpb.importe_total - Decimal(importes)*cpb.cpb_tipo.signo_ctacte)  
        else:
          total = (cpb.importe_total - Decimal(importes))
    
    cpb.saldo=total
    
    estado=cpb_estado.objects.get(pk=1)
    if (total == 0)and(cpb.estado.pk<3):
        estado=cpb_estado.objects.get(pk=2)        
                            
    cpb.estado=estado
    cpb.save()


def ultimoNro(tipoCpb,ptoVenta,letra,entidad=None):    
    try:    
        tipo=cpb_tipo.objects.get(id=tipoCpb)
        if tipo.usa_pto_vta == True:            
            pv = cpb_pto_vta.objects.get(numero=ptoVenta.numero)
            pventa_tipoCpb, created = cpb_pto_vta_numero.objects.get_or_create(cpb_tipo=tipo,letra=letra,cpb_pto_vta=pv,empresa=pv.empresa)        
            if created:
                pventa_tipoCpb.ultimo_nro= 1
                pventa_tipoCpb.save()
                return 1                            
            nro = pventa_tipoCpb.ultimo_nro + 1
        else:
            nro = 1        
            if entidad:
                entidad = egr_entidad.objects.get(id=entidad)
                ult_cpb = cpb_comprobante.objects.filter(entidad=entidad,cpb_tipo=tipo,letra=letra,pto_vta=int(ptoVenta),empresa=entidad.empresa).order_by('numero').last()        
                if ult_cpb:
                        nro = ult_cpb.numero + 1                         
            else:
                nro = tipo.ultimo_nro + 1            
        return nro
    except:        
        #print 'error ultimo nro'
        tipo=cpb_tipo.objects.get(id=tipoCpb)
        nro = tipo.ultimo_nro
    return nro

def actualizar_stock(request,producto,ubicacion,id_tipo_cpb,cantidad):
    estado=cpb_estado.objects.get(pk=2)
    tipo_cpb=cpb_tipo.objects.get(pk=id_tipo_cpb)
    # pv=cpb_pto_vta.objects.get(pk=-1)
    pv=0
    recibo = cpb_comprobante(cpb_tipo=tipo_cpb,estado=estado,pto_vta=pv,letra="X",numero='{0:0{width}}'.format((ultimoNro(id_tipo_cpb,pv,"X")+1),width=8)
        ,fecha_cpb=hoy(),fecha_imputacion=hoy(),importe_iva=None,importe_total=None,usuario=usuario_actual(request),fecha_vto=hoy(),empresa = empresa_actual(request))
    recibo.save()

    detalle = cpb_comprobante_detalle(cpb_comprobante=recibo,producto=producto,cantidad=cantidad,tasa_iva=producto.tasa_iva,coef_iva=producto.tasa_iva.coeficiente,
                origen_destino=ubicacion,detalle=u'ACTUALIZACIÓN DE STOCK')
    detalle.save()

def actualizar_stock_multiple(request,prods,id_tipo_cpb,cantidad):
    estado=cpb_estado.objects.get(pk=2)
    tipo_cpb=cpb_tipo.objects.get(pk=id_tipo_cpb)
    # pv=cpb_pto_vta.objects.get(pk=-1)
    pv=0
    recibo = cpb_comprobante(cpb_tipo=tipo_cpb,estado=estado,pto_vta=pv,letra="X",numero='{0:0{width}}'.format((ultimoNro(id_tipo_cpb,pv,"X")+1),width=8)
        ,fecha_cpb=hoy(),fecha_imputacion=hoy(),importe_iva=None,importe_total=None,usuario=usuario_actual(request),fecha_vto=hoy(),empresa = empresa_actual(request))
    recibo.save()

    for p in prods:
        detalle = cpb_comprobante_detalle(cpb_comprobante=recibo,producto=p.producto,cantidad=cantidad,tasa_iva=p.producto.tasa_iva,coef_iva=p.producto.tasa_iva.coeficiente,
                origen_destino=p.ubicacion,detalle=u'ACTUALIZACIÓN DE STOCK')
        detalle.save()


from django.db.models.signals import post_save,post_delete

@receiver(post_save, sender=cpb_comprobante,dispatch_uid="actualizar_ultimo_nro")
def actualizar_ultimo_nro(sender, instance,created, **kwargs):
   if created:                         
       letra = instance.letra
       tipo=instance.cpb_tipo
       numero=instance.numero       
       if tipo.usa_pto_vta == True:
           pventa = cpb_pto_vta.objects.get(numero=instance.pto_vta,empresa=instance.empresa)              
           pventa_tipoCpb, created = cpb_pto_vta_numero.objects.get_or_create(cpb_tipo=tipo,letra=letra,cpb_pto_vta=pventa,empresa=instance.empresa)
           pventa_tipoCpb.ultimo_nro+= 1
           pventa_tipoCpb.save()     
       else:     
           if not tipo.facturable:           
            tipo.ultimo_nro = numero           
            tipo.save()

@receiver(post_save, sender=cpb_cobranza,dispatch_uid="actualizar_cobranza")
@receiver(post_delete, sender=cpb_cobranza,dispatch_uid="actualizar_cobranza")
def actualizar_cobranza(sender, instance, **kwargs):      
   if instance:  
    if instance.cpb_factura:
        recalcular_saldo_cpb(instance.cpb_factura.pk)   