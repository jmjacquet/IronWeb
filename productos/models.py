# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from datetime import datetime,date
from dateutil.relativedelta import *
from django.conf import settings
import os 
from .utilidades import *
from general.utilidades import TIPO_IVA,TIPO_UNIDAD,empresas_habilitadas_list
from django.db.models import Sum,F,DecimalField

class gral_tipo_iva(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(max_length=100)       
    coeficiente = models.DecimalField(max_digits=5, decimal_places=3,default=0)
    id_afip = models.IntegerField(choices=TIPO_IVA) #(ver que la tupla pueda tener el id afip, dato y coef)   
    class Meta:
        db_table = 'gral_tipo_iva'

    def save(self):
        self.nombre = self.nombre.upper()
        super(gral_tipo_iva, self).save()
    
    def __unicode__(self):
        return u'%s' % (self.nombre)
        
class prod_lista_precios(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(max_length=100)
    default = models.BooleanField('Default',default=False)
    baja = models.BooleanField(default=False)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'prod_lista_precios'
        ordering = ['nombre']

    def save(self):
        self.nombre = self.nombre.upper()
        super(prod_lista_precios, self).save()
    
    def __unicode__(self):
        return u'%s' % (self.nombre)

class prod_ubicacion(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(max_length=100)   
    default = models.BooleanField('Por Defecto',default=False)
    baja = models.BooleanField(default=False)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'prod_ubicacion'
        ordering = ['nombre']

    def save(self):
        self.nombre = self.nombre.upper()
        super(prod_ubicacion, self).save()
    
    def __unicode__(self):
        return u'%s' % (self.nombre)

class prod_categoria(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(max_length=100)       
    baja = models.BooleanField(default=False)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'prod_categoria'
        ordering = ['nombre']
    
    def save(self):
        self.nombre = self.nombre.upper()
        super(prod_categoria, self).save()

    def __unicode__(self):
        return u'%s' % (self.nombre)

import os
def get_image_name(instance, filename):
    f, ext = os.path.splitext(filename)
    #archivo = '%s%s' % (instance.numero_documento, ext)
    archivo = filename
    return os.path.join('productos', archivo) 

class prod_productos(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField(u'Nombre/Descripción',max_length=100)
    codigo = models.CharField(u'Código',max_length=50,blank=True, null=True)
    codigo_barras = models.CharField(u'Código Barras',max_length=200,blank=True, null=True)
    categoria = models.ForeignKey(prod_categoria,verbose_name=u'Categoría', db_column='categoria',blank=True, null=True,on_delete=models.SET_NULL)
    tipo_producto = models.IntegerField('Tipo',choices=TIPO_PRODUCTO,default=1)
    mostrar_en = models.IntegerField('Mostrar en',choices=MOSTRAR_PRODUCTO,default=3)    
    unidad = models.IntegerField('Unidad',choices=TIPO_UNIDAD,default=0)
    llevar_stock = models.BooleanField('Llevar Stock',default=False)
    stock_negativo = models.BooleanField('Stock Negativo',default=True)    
    tasa_iva = models.ForeignKey(gral_tipo_iva,verbose_name='Tasa IVA', db_column='tasa_iva',blank=True, null=True,on_delete=models.SET_NULL)
    descripcion = models.TextField(blank=True, null=True)    
    ruta_img = models.ImageField(upload_to=get_image_name,db_column='ruta_img', max_length=100, blank=True) # Field name made lowercase.    
    baja = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add = True)
    fecha_modif = models.DateTimeField(auto_now = True)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    cta_ingreso =  models.ForeignKey('general.gral_plan_cuentas',db_column='cta_ingreso',related_name='prod_cta_ingreso',blank=True, null=True,on_delete=models.SET_NULL)
    cta_egreso =  models.ForeignKey('general.gral_plan_cuentas',db_column='cta_egreso',related_name='prod_cta_egreso',blank=True, null=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'prod_productos'
        ordering = ['nombre','codigo']
    
    def __unicode__(self):
        prod=u'%s' % (self.nombre)
        if self.codigo:
            prod = u'%s - %s' % (self.codigo,prod) 
        return prod    

    def save(self):
        self.nombre = self.nombre.upper()
        super(prod_productos, self).save()


class prod_producto_lprecios(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    producto = models.ForeignKey(prod_productos,db_column='producto',related_name='producto_lprecios',blank=True, null=True) #Cliente/Pro
    lista_precios = models.ForeignKey(prod_lista_precios,db_column='lista_precios',related_name='lista_precios',blank=True, null=True) #Cliente/Pro
    precio_costo = models.DecimalField('Precio Costo',max_digits=15, decimal_places=2,default=0,blank=True, null=True) 
    precio_cimp = models.DecimalField('Precio c/Imp.',max_digits=15, decimal_places=2,default=0,blank=True, null=True)
    coef_ganancia = models.DecimalField(max_digits=5, decimal_places=3,default=1)
    precio_venta = models.DecimalField('Precio Venta',max_digits=15, decimal_places=2,default=0,blank=True, null=True)
    class Meta:
        db_table = 'prod_producto_lprecios'
        ordering = ['producto__nombre','lista_precios']
    
    def __unicode__(self):
        return u'%s - %s - $ %s' % (self.lista_precios,self.producto.nombre,self.precio_venta)        



from comprobantes.models import cpb_comprobante_detalle
class prod_producto_ubicac(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    producto = models.ForeignKey(prod_productos,db_column='producto',related_name='producto_stock',blank=True, null=True) #Cliente/Pro
    ubicacion = models.ForeignKey(prod_ubicacion,db_column='ubicacion',related_name='ubicacion',blank=True, null=True) #Cliente/Pro    
    class Meta:
        db_table = 'prod_producto_ubicac'
        ordering = ['producto__nombre','ubicacion']
    
    def __unicode__(self):
        return u'%s (%s) [%s]' % (self.producto.nombre,self.ubicacion,TIPO_UNIDAD[self.producto.unidad])          

    def get_stock_(self):             
        total_stock = cpb_comprobante_detalle.objects.filter(cpb_comprobante__estado__in=[1,2],cpb_comprobante__cpb_tipo__usa_stock=True,\
            cpb_comprobante__empresa__id__in=empresas_habilitadas_list(self.ubicacion.empresa),producto__id=self.producto.id,origen_destino__id=self.ubicacion.id).aggregate(total=Sum(F('cantidad') *F('cpb_comprobante__cpb_tipo__signo_stock'),output_field=DecimalField()))['total'] or 0              
        # print total_stock.query
        return total_stock

    get_stock = property(get_stock_)




