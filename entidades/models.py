# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from dateutil.relativedelta import *
from general.utilidades import *
# from usuarios.models import usu_usuario


class EntidadManager(models.Manager):
    def clientes(self):
        return self.get_queryset().filter(tipo_entidad=1, baja=False)

    def proveedores(self):
        return self.get_queryset().filter(tipo_entidad=2, baja=False)

    def vendedores(self):
        return self.get_queryset().filter(tipo_entidad=3, baja=False)
# Tabla de la Base de Configuracion


class egr_entidad(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    apellido_y_nombre = models.CharField('Apellido y Nombre', max_length=200)
    codigo = models.CharField(u'Código', max_length=50, blank=True, null=True)
    tipo_doc = models.IntegerField(
        'Tipo Documento', choices=TIPO_DOC, default=99, blank=True, null=True)
    nro_doc = models.CharField(
        u'Documento', max_length=50, blank=True, null=True)
    domicilio = models.CharField(
        'Domicilio', max_length=200, blank=True, null=True)
    provincia = models.IntegerField(
        'Provincia', choices=PROVINCIAS, blank=True, null=True, default=12)
    localidad = models.CharField(
        'Localidad', max_length=100, blank=True, null=True)
    cod_postal = models.CharField('CP', max_length=50, blank=True, null=True)
    email = models.EmailField('Email', blank=True)
    telefono = models.CharField(
        u'Teléfono', max_length=50, blank=True, null=True)
    celular = models.CharField('Celular', max_length=50, blank=True, null=True)
    # cta_contable =

    tipo_entidad = models.IntegerField(
        choices=TIPO_ENTIDAD, blank=True, null=True, default=1)
    dcto_general = models.DecimalField(
        '% Dcto.Gral', max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    fact_razon_social = models.CharField(
        u'Razón Social', max_length=200, blank=True, null=True)
    fact_cuit = models.CharField('CUIT', max_length=50, blank=True, null=True)
    fact_direccion = models.CharField(
        u'Dirección', max_length=200, blank=True, null=True)
    fact_telefono = models.CharField(
        u'Teléfono', max_length=50, blank=True, null=True)
    fact_categFiscal = models.IntegerField(
        u'Categoría Fiscal', choices=CATEG_FISCAL, blank=True, null=True)
    # fact_tipo_cpb = models.IntegerField('Tipo CPB',choices=COMPROB_FISCAL, blank=True, null=True)
    cbu = models.CharField('CBU', max_length=100, blank=True, null=True)
    contacto = models.CharField(
        'Contacto', max_length=200, blank=True, null=True)
    observaciones = models.TextField('Observaciones', blank=True, null=True)
    baja = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modif = models.DateTimeField(auto_now=True)
    empresa = models.ForeignKey('general.gral_empresa', db_column='empresa',
                                blank=True, null=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey('usuarios.usu_usuario', db_column='usuario', blank=True,
                                null=True, related_name='usu_usuario_entidad', on_delete=models.SET_NULL)

    tope_cta_cte = models.DecimalField(
        'Tope CtaCte', max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    lista_precios_defecto = models.ForeignKey(
        'productos.prod_lista_precios', db_column='lista_precios_defecto', blank=True, null=True)  # Cliente/Pro

    contacto1_nombre = models.CharField(
        'Detalle Contacto 1', max_length=200, blank=True, null=True)
    contacto1_email = models.EmailField('Email', blank=True, null=True)
    contacto1_tel = models.CharField(
        u'Teléfono', max_length=50, blank=True, null=True)
    contacto2_nombre = models.CharField(
        'Detalle Contacto 2', max_length=200, blank=True, null=True)
    contacto2_email = models.EmailField('Email', blank=True, null=True)
    contacto2_tel = models.CharField(
        u'Teléfono', max_length=50, blank=True, null=True)
    contacto3_nombre = models.CharField(
        'Detalle Contacto 3', max_length=200, blank=True, null=True)
    contacto3_email = models.EmailField('Email', blank=True, null=True)
    contacto3_tel = models.CharField(
        u'Teléfono', max_length=50, blank=True, null=True)
    contacto4_nombre = models.CharField(
        'Detalle Contacto 4', max_length=200, blank=True, null=True)
    contacto4_email = models.EmailField('Email', blank=True, null=True)
    contacto4_tel = models.CharField(
        u'Teléfono', max_length=50, blank=True, null=True)
    contacto5_nombre = models.CharField(
        'Detalle Contacto 5', max_length=200, blank=True, null=True)
    contacto5_email = models.EmailField('Email', blank=True, null=True)
    contacto5_tel = models.CharField(
        u'Teléfono', max_length=50, blank=True, null=True)

    objects = EntidadManager()

    class Meta:
        db_table = 'egr_entidad'
        ordering = ['apellido_y_nombre', 'codigo']
    

    def __unicode__(self):
        entidad = u'%s' % self.apellido_y_nombre.upper()
        cuit = ''
        if self.fact_cuit == '':
            if self.nro_doc == '':
                cuit = ''
            else:
                cuit = u' - %s' % self.nro_doc
        elif self.fact_cuit:
            cuit = u' - %s' % self.fact_cuit

        categ_fiscal = ''
        if self.fact_categFiscal:
            categ_fiscal = ' - %s' % self.get_categFiscal()
        entidad = u'%s%s%s' % (entidad, cuit, categ_fiscal)
        return entidad.upper()

    detalle_entidad = property(__unicode__)

    def get_categFiscal(self):
        if self.fact_categFiscal == 1:
            return 'RI'
        elif self.fact_categFiscal == 2:
            return 'RNI'
        elif self.fact_categFiscal == 3:
            return 'NR'
        elif self.fact_categFiscal == 4:
            return 'EX'
        elif self.fact_categFiscal == 5:
            return 'CF'
        elif self.fact_categFiscal == 6:
            return 'MT'
        else:
            return 'OT'

    def get_entidad(self):
        entidad = u'%s' % (self.apellido_y_nombre)
        if self.fact_categFiscal:
            entidad = u'%s - %s' % (entidad, self.fact_categFiscal)

        return entidad

    def delete(self):
        # No borro comprobantes
        self.cpb_entidad.clear()
        self.cpb_vendedor.clear()
        super(egr_entidad, self).delete()

    def save(self, *args, **kwargs):
        self.apellido_y_nombre = self.apellido_y_nombre.upper()
        self.fecha_modif = hoy()
        self.fecha_creacion = hoy()
        super(egr_entidad, self).save()

    def get_listado(self):
        if self.tipo_entidad == 1:
            return reverse('clientes_listado')
        elif self.tipo_entidad == 2:
            return reverse('proveedores_listado')
        else:
            return reverse('vendedores_listado')

    def get_correo(self):
        if self.email:
            return str(self.email)
        else:
            return None

    def get_saldo_pendiente(self):
        from comprobantes.models import cpb_comprobante
        from django.db.models import Sum, F, DecimalField
        if self.tipo_entidad == 1:
            cpbCV = 'V'
        elif self.tipo_entidad == 2:
            cpbCV = 'C'
        else:
            return 0

        total = cpb_comprobante.objects.filter(entidad=self, cpb_tipo__usa_ctacte=True, cpb_tipo__compra_venta=cpbCV, estado__in=[
                                               1, 2]).aggregate(saldo=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['saldo'] or 0
        return total

    def get_nro_doc_afip(self):
        try:
            if self.tipo_doc in (96, 99):
                nro_doc = self.nro_doc
            elif self.tipo_doc == 80:
                nro_doc = self.fact_cuit
            else:
                nro_doc = self.fact_cuit
        except:
            nro_doc = self.nro_doc
        if not nro_doc:
            nro_doc = 0
        return nro_doc, self.tipo_doc

    def get_nro_doc_cuit(self):
        ndoc, _ = self.get_nro_doc_afip()
        return ndoc

