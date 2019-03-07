# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
# from .utilidades import ESTADO,TIPO_CANCHA,TIPOUSR,ESTADO_CUOTA,TRIBUTO_CUOTA,TIPO_LOGIN
from django.contrib.auth.models import User
from datetime import datetime,date
from dateutil.relativedelta import *
from django.conf import settings
import os 
from .utilidades import *
from comprobantes.models import cpb_estado,cpb_tipo,cpb_comprobante
from general.models import gral_empresa
from usuarios.models import usu_usuario

import os
def get_image_name(instance, filename):
    f, ext = os.path.splitext(filename)    
    archivo = filename
    return os.path.join('empresa', archivo) 

class orden_pedido(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    empresa =  models.ForeignKey('general.gral_empresa', db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    cliente = models.ForeignKey('entidades.egr_entidad',db_column='cliente',related_name='op_cliente',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Proveedor
    vendedor = models.ForeignKey('entidades.egr_entidad',db_column='vendedor',related_name='op_vendedor',blank=True, null=True,on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add = True,blank=True, null=True)
    fecha = models.DateField('Fecha Orden')    
    fecha_vto = models.DateField('Fecha',blank=True, null=True)
    numero = models.CharField(u'Número',max_length=50)
    ped_mostrador = models.BooleanField('Mostrador',default=False)
    ped_webface = models.BooleanField('Web/Faceb',default=False)
    ped_comercial = models.BooleanField('Comercial',default=False)
    ped_email = models.BooleanField('Email',default=False)
    estado = models.ForeignKey(cpb_estado,related_name='op_estado',blank=True, null=True,on_delete=models.SET_NULL)
    impres_laser = models.BooleanField(u'Láser',default=False)
    impres_latex = models.BooleanField('Latex',default=False)
    impres_rotulado = models.BooleanField('Rotulado',default=False)
    impres_offset = models.BooleanField('Offset',default=False)
    impres_corporeo = models.BooleanField(u'Corpóreo',default=False)
    impres_disenio = models.BooleanField(u'Diseño',default=False)
    impres_ploteo_papel = models.BooleanField('Ploteo Papel',default=False)
    impres_facturero = models.BooleanField('Facturero',default=False)
    impres_sellos = models.BooleanField('Sellos',default=False)
    impres_imprbyn = models.BooleanField('Impr.B/N',default=False)
    term_cortado = models.BooleanField('Cortado',default=False)
    term_troquelado = models.BooleanField('Troquelado',default=False)
    term_abrochado = models.BooleanField('Abrochado',default=False)
    term_engomado = models.BooleanField('Engomado',default=False)
    term_plegado = models.BooleanField(u'Plegado',default=False)
    term_arandelas = models.BooleanField(u'Arandelas',default=False)
    term_bolsillos = models.BooleanField('Bolsillos',default=False)
    term_plastificado = models.BooleanField('Plastificado',default=False)
    term_imp_corte = models.BooleanField('Imp.y Corte',default=False)
    term_anillado = models.BooleanField('Anillado',default=False)
    archivo_enviado = models.CharField(u'Archivo/Medio',max_length=100,blank=True, null=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    hora_entrega = models.TimeField(blank=True, null=True)
    muestra_enviada = models.ForeignKey('entidades.egr_entidad',db_column='tercerizado',related_name='op_tercerizado',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Proveedor    
    firma_conformidad = models.BooleanField('Firmado/Aceptado',default=False)
    importe_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)#Suma de todo    
    detalle = models.TextField(max_length=1000, blank=True, null=True) # Field name made lowercase.    
    id_presupuesto = models.ForeignKey(cpb_comprobante,verbose_name=u'CPB', db_column='id_presupuesto',related_name='op_presupuesto',blank=True, null=True,on_delete=models.SET_NULL)
    fecha_pendiente = models.DateField('Fecha',blank=True, null=True)
    fecha_proceso = models.DateField('Fecha',blank=True, null=True)
    fecha_terminado = models.DateField('Fecha',blank=True, null=True)
    fecha_entregado = models.DateField('Fecha',blank=True, null=True)
    usuario = models.ForeignKey(usu_usuario,db_column='usuario',blank=True, null=True,related_name='op_usuario',on_delete=models.SET_NULL)
    id_venta = models.ForeignKey(cpb_comprobante,verbose_name=u'Venta', db_column='id_venta',related_name='op_venta',blank=True, null=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'trab_orden_pedido'

    def __unicode__(self):
        return u'%s' % (self.numero)  

    def _generaOT(self):        
        pedidos = orden_trabajo.objects.filter(orden_pedido=self)
        return not pedidos.exists() 

    generaOT = property(_generaOT)   


class orden_pedido_detalle(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    orden_pedido = models.ForeignKey('orden_pedido',verbose_name=u'Nº Orden', db_column='orden_pedido',blank=True, null=True)
    producto = models.ForeignKey('productos.prod_productos',db_column='producto',related_name='op_producto',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Proveedor
    cantidad = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=1)
    importe_unitario = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)        
    importe_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)    
    fecha_creacion = models.DateTimeField(auto_now_add = True)
    detalle = models.TextField(max_length=1000,blank=True, null=True) # Field name made lowercase. 
    origen_destino = models.ForeignKey('productos.prod_ubicacion',verbose_name='Origen/Destino', db_column='op_origen_destino',blank=True, null=True,on_delete=models.SET_NULL)  
    lista_precios = models.ForeignKey('productos.prod_lista_precios',db_column='lista_precios',related_name='op_lista_precios',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Pro
    class Meta:
        db_table = 'trab_op_detalle'
    
    def __unicode__(self):
        return u'%s-%s' % (self.producto,self.cantidad)                  

class orden_trabajo(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)    
    orden_pedido = models.ForeignKey('orden_pedido',verbose_name=u'Nº Orden', db_column='orden_pedido',blank=True, null=True,on_delete=models.SET_NULL)
    empresa =  models.ForeignKey('general.gral_empresa', db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    responsable = models.ForeignKey('entidades.egr_entidad',db_column='vendedor',related_name='ot_vendedor',blank=True, null=True,on_delete=models.SET_NULL)    
    fecha_creacion = models.DateTimeField(auto_now_add = True,blank=True, null=True)
    fecha = models.DateField('Fecha Orden')    
    fecha_estimada = models.DateField('Fecha Estimada',blank=True, null=True)
    numero = models.CharField(u'Número',max_length=50)
    estado = models.ForeignKey(cpb_estado,related_name='ot_estado',blank=True, null=True,on_delete=models.SET_NULL)    
    detalle = models.TextField(max_length=1000, blank=True, null=True) # Field name made lowercase.        
    fecha_terminado = models.DateField('Fecha',blank=True, null=True)
    usuario = models.ForeignKey(usu_usuario,db_column='usuario',blank=True, null=True,related_name='ot_usuario',on_delete=models.SET_NULL)
    class Meta:
        db_table = 'trab_orden_trabajo'

    def __unicode__(self):
        return u'%s' % (self.numero) 


class orden_trabajo_detalle(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    orden_trabajo = models.ForeignKey('orden_trabajo',verbose_name=u'Nº Orden', db_column='orden_trabajo',blank=True, null=True)
    producto = models.ForeignKey('productos.prod_productos',db_column='producto',related_name='ot_producto',blank=True, null=True,on_delete=models.SET_NULL) #Cliente/Proveedor
    cantidad = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=1)        
    fecha_creacion = models.DateTimeField(auto_now_add = True)
    detalle = models.TextField(max_length=1000,blank=True, null=True) # Field name made lowercase.   
    class Meta:
        db_table = 'trab_ot_detalle'
    
    def __unicode__(self):
        return u'%s-%s' % (self.producto,self.cantidad) 


class orden_colocacion(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    orden_trabajo = models.ForeignKey('orden_trabajo', db_column='id_orden_trabajo',related_name="ot_padre",blank=True, null=True,on_delete=models.SET_NULL)
    empresa =  models.ForeignKey('general.gral_empresa', db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    estado = models.ForeignKey(cpb_estado,related_name='oc_estado',blank=True, null=True,on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add = True,blank=True, null=True)
    fecha_colocacion = models.DateField(blank=True, null=True)
    hora_colocacion = models.TimeField(blank=True, null=True)    
    vendedor = models.ForeignKey('entidades.egr_entidad',db_column='vendedor',related_name='oc_vendedor',blank=True, null=True,on_delete=models.SET_NULL)
    colocador = models.ForeignKey('entidades.egr_entidad',db_column='colocador',related_name='oc_colocador',blank=True, null=True,on_delete=models.SET_NULL)  
    fecha_vto = models.DateField('Fecha',blank=True, null=True)
    numero = models.CharField(u'Número',max_length=50)        
    detalle = models.TextField(max_length=1000, blank=True, null=True) # Field name made lowercase.    
    fecha_colocado = models.DateField('Fecha',blank=True, null=True)
    usuario = models.ForeignKey(usu_usuario,db_column='usuario',blank=True, null=True,related_name='oc_usuario',on_delete=models.SET_NULL)
    class Meta:
        db_table = 'trab_orden_colocacion'

    def __unicode__(self):
        return u'%s' % (self.numero)  





from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver

@receiver(post_save, sender=orden_pedido,dispatch_uid="actualizar_ultimo_nro_op")
def actualizar_ultimo_nro_op(sender, instance,created, **kwargs):
   if created:
       nro=int(instance.numero)       
       tipo=cpb_tipo.objects.get(pk=15)
       tipo.ultimo_nro=nro
       tipo.save()   

