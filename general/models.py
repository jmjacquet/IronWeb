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
from .utilidades import COMPROB_FISCAL,CATEG_FISCAL,PROVINCIAS,TIPO_CTA,TIPO_LOGOTIPO,get_image_name
from django.core.files.storage import default_storage

#Tabla de la Base de Configuracion


class gral_afip_categorias(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)    
    letra = models.CharField(u'Letra',choices=COMPROB_FISCAL,max_length=1,blank=True, null=True)
    importe = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,default=0)
    class Meta:
        db_table = 'gral_afip_categorias'
    
    def __unicode__(self):
        return u'%s' % self.letra

class gral_empresa(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    nombre = models.CharField('Nombre',max_length=100)    
    categ_fiscal = models.IntegerField(u'Categoría Fiscal',choices=CATEG_FISCAL, blank=True, null=True)  
    cuit = models.CharField('CUIT',max_length=50)   
    iibb = models.CharField(u'Nº IIBB',max_length=50,blank=True, null=True)   
    fecha_inicio_activ = models.DateTimeField('Fecha Inicio Actividades',null=True)
    domicilio = models.CharField('Domicilio',max_length=200,blank=True, null=True)   
    provincia = models.IntegerField('Provincia',choices=PROVINCIAS, blank=True, null=True,default=12)
    localidad = models.CharField('Localidad',max_length=100,blank=True, null=True)   
    cod_postal = models.CharField('CP',max_length=50,blank=True, null=True)
    email = models.EmailField('Email')
    telefono = models.CharField(u'Teléfono',max_length=50,blank=True, null=True)   
    celular = models.CharField('Celular',max_length=50,blank=True, null=True)   
    baja = models.BooleanField(default=False)
    fecha_creacion = models.DateField(auto_now_add = True)
    
    nombre_fantasia = models.CharField(u'Nombre Fantasía',max_length=200)    
    dias_vencimiento_cpbs = models.IntegerField(u'Días Vencimiento CPBS', blank=True, null=True,default=0)
    
    pprincipal_aviso_tareas = models.BooleanField(u'Tareas Pendientes al inicio',default=False)
    pprincipal_panel_cpbs = models.BooleanField(u'Panel Últimos CPBs',default=False)
    pprincipal_estadisticas = models.BooleanField(u'Panel Estadísticas',default=False)
    fp_facturas = models.BooleanField(u'Mostrar FP en Facturas',default=True)

    barra_busq_meses_atras = models.IntegerField(blank=True, null=True,default=2)
    pto_vta_defecto =  models.ForeignKey('comprobantes.cpb_pto_vta',verbose_name=u'Pto. Venta x Defecto',db_column='pto_vta_defecto',blank=True, null=True,on_delete=models.SET_NULL)    
    fe_crt = models.CharField('Nombre Archivo CRT',max_length=50,blank=True, null=True) 
    fe_key = models.CharField('Nombre Archivo Key',max_length=50,blank=True, null=True) 
    homologacion = models.BooleanField(u'Modo HOMOLOGACIÓN',default=True)

    mail_cuerpo = models.CharField(u'Cuerpo del Email (envío de Comprobantes)',max_length=500,blank=True, null=True)   
    mail_servidor = models.CharField(u'Servidor SMTP',max_length=100, blank=True)
    mail_puerto = models.IntegerField(u'Puerto',blank=True, null=True,default=587)      
    mail_usuario =models.CharField('Usuario',max_length=100, blank=True)
    mail_password =models.CharField('Password',max_length=100, blank=True)

    afip_categoria =  models.ForeignKey('general.gral_afip_categorias',verbose_name=u'Categoría AFIP (si corresponde)',db_column='afip_categoria',blank=True, null=True,on_delete=models.SET_NULL)    

    ruta_logo = models.ImageField(upload_to=get_image_name,db_column='ruta_logo', max_length=100,null=True, blank=True) # Field name made lowercase.    
    tipo_logo_factura = models.IntegerField(u'Tipo Logotipo',choices=TIPO_LOGOTIPO, blank=True, null=True)  

    class Meta:
        db_table = 'gral_empresa'

    def __unicode__(self):
        return u'%s' % (self.nombre_fantasia)

    def get_dias_venc(self):
        if self.dias_vencimiento_cpbs:
            return self.dias_vencimiento_cpbs
        else:
             return 0    

    def get_datos_mail(self):
        d= {}
        d['mail_cuerpo']= self.mail_cuerpo or u'Estimado/as les envío por este medio el comprobante solicitado.'
        d['mail_servidor']= self.mail_servidor or settings.EMAIL_HOST
        d['mail_puerto']= int(self.mail_puerto) or int(settings.EMAIL_PORT)
        d['mail_usuario']= self.mail_usuario or settings.EMAIL_HOST_USER
        d['mail_password']= self.mail_password or settings.EMAIL_HOST_PASSWORD  
        d['mail_origen']= d['mail_usuario']+'@ironweb.com.ar'
            
        return d

  

class gral_tareas(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)    
    estado = models.CharField(u'Estado',max_length=50,blank=True, null=True)     
    title = models.CharField(u'Título',max_length=200,blank=True, null=True)    
    detalle = models.TextField('Detalle',blank=True, null=True)  
    respuesta = models.CharField(u'Respuesta',max_length=500,blank=True, null=True) 
    color = models.CharField(u'Color',max_length=200,blank=True, null=True)   
    usuario_creador = models.ForeignKey('usuarios.usu_usuario',db_column='usuario_creador',blank=True, null=True,related_name='usuario_creador',on_delete=models.SET_NULL)    
    usuario_asignado = models.ForeignKey('usuarios.usu_usuario',db_column='usuario_asignado',blank=True, null=True,related_name='usuario_asignado',on_delete=models.SET_NULL)            
    fecha = models.DateTimeField(default=datetime.now)    
    fecha_creacion = models.DateField(auto_now=True)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'gral_tareas'

    def __unicode__(self):
        return u'%s %s : %s' % (self.fecha,self.usuario_asignado,self.title)


class gral_plan_cuentas(models.Model):
    id = models.AutoField(primary_key=True,db_index=True)
    codigo = models.CharField(max_length=100)       
    nombre = models.CharField(max_length=100)       
    tipo = models.IntegerField(choices=TIPO_CTA, blank=True, null=True)
    padre = models.ForeignKey('general.gral_plan_cuentas', db_column='padre',related_name="plan_ctas_padre",blank=True, null=True,on_delete=models.SET_NULL)
    baja = models.BooleanField(default=False)
    empresa =  models.ForeignKey('general.gral_empresa',db_column='empresa',blank=True, null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'gral_plan_cuentas'
        ordering = ['codigo','nombre']
    
    def __unicode__(self):
        return u'%s %s' % (self.codigo,self.nombre)




