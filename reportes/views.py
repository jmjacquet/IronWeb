# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import render, redirect, get_object_or_404,render_to_response,HttpResponseRedirect,HttpResponse
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView,DetailView
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from datetime import datetime,date,timedelta
from django.utils import timezone
from dateutil.relativedelta import *
from .forms import *
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from django.db.models import Q,Sum,Count,FloatField,Func
from comprobantes.models import *
import json
from decimal import *
from fm.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
from django.contrib import messages
from general.utilidades import *
from general.views import VariablesMixin,getVariablesMixin
from general.forms import pto_vta_habilitados,pto_vta_habilitados_list
from usuarios.views import tiene_permiso
from django.forms.models import inlineformset_factory,BaseInlineFormSet,formset_factory
from productos.models import prod_productos
from django.contrib.messages.views import SuccessMessageMixin
from django.core.serializers.json import DjangoJSONEncoder
from comprobantes.views import ultimoNro,buscarDatosProd,presup_aprobacion,cobros_cpb
from django.db.models import DateTimeField, ExpressionWrapper, F,DecimalField

################################################################
def cuenta_corriente(request,compra_venta,entidad,fdesde,fhasta,estado,empresa):
    #Cta_cte Clientes
    
    cpbs = cpb_comprobante.objects.filter(cpb_tipo__usa_ctacte=True,cpb_tipo__compra_venta=compra_venta,empresa=empresa).select_related('estado','cpb_tipo','entidad').order_by('entidad__apellido_y_nombre','fecha_cpb','cpb_tipo__tipo')
    if entidad:
               cpbs= cpbs.filter(entidad=entidad)    
    if int(estado) == 0:                
        cpbs=cpbs.filter(estado__in=[1,2])                
    elif int(estado) == 2:                
        cpbs=cpbs.filter(estado__in=[3])
    else:                
        cpbs=cpbs.filter(estado__in=[1,2,3])
    if fdesde:                
        cpbs=cpbs.filter(fecha_cpb__gte=fdesde)          
    if fhasta:                
        cpbs=cpbs.filter(fecha_cpb__lte=fhasta) 

    return cpbs

@login_required 
def cta_cte_clientes(request,id=None):
    limpiar_sesion(request)
    if not tiene_permiso(request,'rep_cta_cte'):
            return redirect(reverse('principal'))  
    context = {}
    context = getVariablesMixin(request)    
    try:
        empresa = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        empresa = None 

    form = ConsultaCtaCteCliente(request.POST or None,empresa=empresa,id=id,request=request)   
        
    cpbs = None
    total_debe = 0  
    total_haber = 0
    total_ctacte_debe = 0    
    total_ctacte_haber = 0
    saldo_anterior_debe = 0  
    saldo_anterior_haber = 0
    saldo_anterior = 0 
    fecha = date.today()
    datos = []       

    inicial = (request.method == 'GET')and id    

    if form.is_valid() or inicial:                                
        if inicial:
            entidad = egr_entidad.objects.get(id=id)
            fdesde = inicioMes()
            fhasta = hoy()
            estado = 0
        else:
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']   
            estado = form.cleaned_data['estado']                         
                
        cpbs = cuenta_corriente(request,'V',entidad,None,None,estado,empresa)
                
        try:
            total_debe = cpbs.filter(cpb_tipo__tipo__in=[1,3,9]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0
            total_haber = cpbs.filter(cpb_tipo__tipo__in=[2,4]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0

        except:
            total_debe = 0  
            total_haber = 0             
        
        cpbs = cuenta_corriente(request,'V',entidad,fdesde,fhasta,estado,empresa)

        try:
            total_ctacte_debe = cpbs.filter(cpb_tipo__tipo__in=[1,3,9]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0          
            total_ctacte_haber = cpbs.filter(cpb_tipo__tipo__in=[2,4]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0          
        except:
            total_ctacte_debe = 0    
            total_ctacte_haber = 0

        try:
            saldo_anterior_debe = total_debe - total_ctacte_debe        
            saldo_anterior_haber = total_haber - total_ctacte_haber  
            saldo_anterior = saldo_anterior_debe - saldo_anterior_haber               
        except:
            saldo_anterior_debe = 0  
            saldo_anterior_haber = 0
            saldo_anterior = 0
        
        saldo = saldo_anterior
        for i in cpbs:
                saldo += (i.importe_total*i.cpb_tipo.signo_ctacte)
                
                datos.append(
                    {
                        'estado_id':i.estado.pk,
                        'estado_color':i.estado.color,
                        'fecha_cpb': i.fecha_cpb,
                        'cpb_tipo': i.cpb_tipo,
                        'observacion':i.observacion,                        
                        'signo_ctacte':i.cpb_tipo.signo_ctacte,
                        'cpb_tipo.tipo': i.cpb_tipo.tipo,
                        'id':i.id,
                        'get_cpb':i.get_cpb,
                        'cpb_tipo.nombre':i.cpb_tipo.nombre,
                        'fecha_vto':i.fecha_vto,
                        'importe_total':i.importe_total,
                        'saldo': saldo,
                    }
                )
    context['form'] = form
    context['cpbs'] = datos
    context['fecha'] = fecha
    context['total_debe'] = total_debe
    context['total_haber'] = total_haber
    context['total_ctacte_debe'] = total_ctacte_debe
    context['total_ctacte_haber'] = total_ctacte_haber
    context['saldo_anterior_debe'] = saldo_anterior_debe
    context['saldo_anterior_haber'] = saldo_anterior_haber
    context['saldo_anterior'] = saldo_anterior

    return render(request,'reportes/cta_cte/cta_cte_clientes.html',context )

class saldos_clientes(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'reportes/cta_cte/saldos_clientes.html'
    context_object_name = 'cpbs'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'rep_saldos'):
            return redirect(reverse('principal'))  
        return super(saldos_clientes, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(saldos_clientes, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaSaldosClientes(self.request.POST or None,empresa=empresa,request=self.request)            
        fecha = date.today()
        totales = None
        
        if form.is_valid():                                
            
            cpbs = cpb_comprobante.objects.filter(pto_vta__in=pto_vta_habilitados_list(self.request),cpb_tipo__usa_ctacte=True,cpb_tipo__compra_venta='V',empresa=empresa,estado__in=[1,2]).select_related('entidad')
            entidad = form.cleaned_data['entidad']                                                                           
            if entidad:
               cpbs= cpbs.filter(entidad=entidad)            
            totales = cpbs.values('entidad','entidad__apellido_y_nombre','entidad__codigo','entidad__fact_cuit').annotate(saldo=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField())).order_by('-saldo','entidad__apellido_y_nombre')


        context['form'] = form        
        context['fecha'] = fecha
        context['totales'] = totales
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

################################################################

@login_required 
def cta_cte_proveedores(request,id=None):
         
        limpiar_sesion(request)        
        if not tiene_permiso(request,'rep_cta_cte'):
            return redirect(reverse('principal'))          

        context = {}
        context = getVariablesMixin(request)    
        try:
            empresa = empresa_actual(request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCtaCteProv(request.POST or None,empresa=empresa,id=id,request=request)   
        cpbs = None
        total_debe = 0  
        total_haber = 0
        total_ctacte_debe = 0    
        total_ctacte_haber = 0
        saldo_anterior_debe = 0  
        saldo_anterior_haber = 0
        saldo_anterior = 0 
        fecha = date.today()
        datos = [] 
        inicial = (request.method == 'GET')and id    

        if form.is_valid() or inicial:                                 
            if inicial:
                entidad = egr_entidad.objects.get(id=id)
                fdesde = inicioMes()
                fhasta = hoy()
                estado = 0
            else:
                entidad = form.cleaned_data['entidad']                                                              
                fdesde = form.cleaned_data['fdesde']   
                fhasta = form.cleaned_data['fhasta']   
                estado = form.cleaned_data['estado']                  
                    
            #cpbs = cpb_comprobante.objects.filter(entidad=entidad,cpb_tipo__usa_ctacte=True,cpb_tipo__compra_venta='C',empresa=empresa).select_related('cpb_tipo','entidad','pto_vta').order_by('entidad__apellido_y_nombre','fecha_cpb','cpb_tipo__tipo')
            cpbs = cuenta_corriente(request,'C',entidad,None,None,estado,empresa)            
            if int(estado) == 0:                
                cpbs=cpbs.filter(estado__in=[1,2])                
            elif int(estado) == 2:                
                cpbs=cpbs.filter(estado__in=[3])
            else:                
                cpbs=cpbs.filter(estado__in=[1,2,3])

            try:
                total_debe = cpbs.filter(cpb_tipo__tipo__in=[1,3,9]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0          
                total_haber = cpbs.filter(cpb_tipo__tipo__in=[2,7]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0             
            except:
                total_debe = 0  
                total_haber = 0  

            cpbs = cuenta_corriente(request,'C',entidad,fdesde,fhasta,estado,empresa)          
                        
            try:
                total_ctacte_debe = cpbs.filter(cpb_tipo__tipo__in=[1,3,9]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0          
                total_ctacte_haber = cpbs.filter(cpb_tipo__tipo__in=[2,7]).aggregate(sum=Sum(F('importe_total'), output_field=DecimalField()))['sum'] or 0
            except:
                total_ctacte_debe = 0
                total_ctacte_haber = 0    

            try:
                saldo_anterior_debe = total_debe - total_ctacte_debe        
                saldo_anterior_haber = total_haber - total_ctacte_haber  
                saldo_anterior = saldo_anterior_haber - saldo_anterior_debe
            except:
                saldo_anterior_debe = 0  
                saldo_anterior_haber = 0
                saldo_anterior = 0

            saldo = saldo_anterior
            for i in cpbs:
                    saldo += (i.importe_total*i.cpb_tipo.signo_ctacte)
                    
                    datos.append(
                        {
                            'estado_id':i.estado.pk,
                            'estado_color':i.estado.color,
                            'fecha_cpb': i.fecha_cpb,
                            'cpb_tipo': i.cpb_tipo,
                            'observacion':i.observacion,                        
                            'signo_ctacte':i.cpb_tipo.signo_ctacte,
                            'cpb_tipo.tipo': i.cpb_tipo.tipo,
                            'id':i.id,
                            'get_cpb':i.get_cpb,
                            'cpb_tipo.nombre':i.cpb_tipo.nombre,
                            'fecha_vto':i.fecha_vto,
                            'importe_total':i.importe_total,
                            'saldo': saldo,
                        }
                    )

        context['form'] = form
        context['cpbs'] = datos
        context['fecha'] = fecha
        context['total_debe'] = total_debe
        context['total_haber'] = total_haber
        context['total_ctacte_debe'] = total_ctacte_debe
        context['total_ctacte_haber'] = total_ctacte_haber
        context['saldo_anterior_debe'] = saldo_anterior_debe
        context['saldo_anterior_haber'] = saldo_anterior_haber
        context['saldo_anterior'] = saldo_anterior
        return render(request,'reportes/cta_cte/cta_cte_proveedores.html',context )
    

class saldos_proveedores(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'reportes/cta_cte/saldos_proveedores.html'
    context_object_name = 'cpbs'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'rep_saldos'):
            return redirect(reverse('principal'))  
        return super(saldos_proveedores, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(saldos_proveedores, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 

        form = ConsultaSaldosProv(self.request.POST or None,empresa=empresa,request=self.request)            
        fecha = date.today()        
        totales = None
        if form.is_valid():                                
            cpbs = cpb_comprobante.objects.filter(cpb_tipo__usa_ctacte=True,cpb_tipo__compra_venta='C',empresa=empresa,estado__in=[1,2]).select_related('entidad')
            entidad = form.cleaned_data['entidad']                                                                           
            if entidad:
               cpbs= cpbs.filter(entidad=entidad)            
            totales = cpbs.values('entidad','entidad__apellido_y_nombre','entidad__codigo','entidad__fact_cuit').annotate(saldo=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField())).order_by('-saldo','entidad__apellido_y_nombre')


        context['form'] = form        
        context['fecha'] = fecha
        context['totales'] = totales
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)
             
################################################################

import StringIO
def generarCITI(cpbs,ventas_compras,tipo_archivo):
    #ventascompras = V/C
    #tipo_archivo = cpbs/alicuotas
    #import time
    #start = time.time()
    archivo = StringIO.StringIO()
    nafip = None
    if (ventas_compras=='V'):
       if tipo_archivo=='cpbs': 
        for c in cpbs:
            nafip=c.get_nro_afip()
            if nafip==None:
                continue
            linea=""
            linea += str(c.fecha_imputacion.strftime("%Y%m%d")).encode('utf-8').rjust(8, "0") #FECHA
            linea += str(nafip).encode('utf-8').rjust(3, "0") #CODIGO CPB AFIP
            linea += str(c.pto_vta).encode('utf-8').rjust(5, "0") #PTO VTA
            linea += str(c.numero).encode('utf-8').rjust(20, "0") #NRO CPB
            linea += str(c.numero).encode('utf-8').rjust(20, "0") #NRO CPB HASTA
            
            tipo_doc=c.entidad.tipo_doc
            if tipo_doc == 99:
                nro_doc = 0
            elif tipo_doc == 96:
                nro_doc = c.entidad.nro_doc
            elif tipo_doc == 80:    
                nro_doc = c.entidad.fact_cuit
            else:
                nro_doc = c.entidad.fact_cuit
            linea += str(tipo_doc).encode('utf-8').rjust(2, "0") #TIPO DOC
            linea += str(nro_doc)[:20].encode('utf-8').rjust(20, "0") #nro DOC/cuit
            linea += (c.entidad.apellido_y_nombre)[:30].encode('utf-8').ljust(30, " ") #nombre
            linea += str(c.importe_total).encode('utf-8').replace(".","").rjust(15, "0") #importe_total
            linea += str(c.importe_no_gravado).encode('utf-8').replace(".","").rjust(15, "0") #importe_ng
            linea += str(0).replace(".","").rjust(15, "0") #perc_nc
            linea += str(c.importe_exento).encode('utf-8').replace(".","").rjust(15, "0") #importe_exento
            linea += str(0).replace(".","").rjust(15, "0") #perc_impuestosNac
            linea += str(0).replace(".","").rjust(15, "0") #perc_IIBB
            linea += str(0).replace(".","").rjust(15, "0") #perc_impMunicip
            linea += str(0).replace(".","").rjust(15, "0") #importe_impuestosInt
            linea += str('PES').encode('utf-8') #Moneda
            linea += str('0001000000').encode('utf-8')#tipo_cambio
            try:
                cpb_iva = cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=c)
                cant_alic = len(cpb_iva)
                informa = len(cpb_iva.filter(tasa_iva__id_afip__lte=3))>0
                cod_op = ' '
                if informa:
                    if c.importe_exento>0:
                        cod_op = 'E'
                    else:
                        cod_op = 'N'
            except:
                cant_alic = 0
                cod_op = 'N'
            linea += str(cant_alic).encode('utf-8').rjust(1, "0") #cant_alic_iva
            linea += str(cod_op).encode('utf-8')#cod_operacion
            linea += str(0).replace(".","").rjust(15, "0") #otrosTributos
            linea += str(c.fecha_imputacion.strftime("%Y%m%d")).encode('utf-8').rjust(8, "0") #FECHA_VTO
            
            archivo.write(linea+'\r\n')

       elif tipo_archivo=='alicuotas':
         for c in cpbs:
            nafip=c.get_nro_afip()
            if nafip==None:
                continue
            cpb_iva = cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=c)
            for ci in cpb_iva:            
                linea="" 
                linea += str(nafip).encode('utf-8').rjust(3, "0") #CODIGO CPB AFIP
                linea += str(c.pto_vta).encode('utf-8').rjust(5, "0") #PTO VTA
                linea += str(c.numero).encode('utf-8').rjust(20, "0") #NRO CPB                
                linea += str(ci.importe_base).encode('utf-8').replace(".","").rjust(15, "0") #importe_neto
                linea += str(ci.tasa_iva.id_afip).encode('utf-8').rjust(4, "0") #CODIGO IVA AFIP
                linea += str(ci.importe_total).encode('utf-8').replace(".","").rjust(15, "0") #importe IVA            
                archivo.write(linea+'\r\n')     
    else:
        if tipo_archivo=='cpbs':
         for c in cpbs:
            nafip=c.get_nro_afip()
            if nafip==None:
                continue
            linea=""
            linea += str(c.fecha_imputacion.strftime("%Y%m%d")).encode('utf-8').rjust(8, "0") #FECHA
            linea += str(nafip).encode('utf-8').rjust(3, "0") #CODIGO CPB AFIP
            linea += str(c.pto_vta).encode('utf-8').rjust(5, "0") #PTO VTA
            linea += str(c.numero).encode('utf-8').rjust(20, "0") #NRO CPB
            linea += str('').encode('utf-8').ljust(16, " ") #NRO DESPACHO IMPORTACION
            
            tipo_doc=c.entidad.tipo_doc
            if tipo_doc == 99:
                nro_doc = 0
            elif tipo_doc == 96:
                nro_doc = c.entidad.nro_doc
            elif tipo_doc == 80:    
                nro_doc = c.entidad.fact_cuit
            else:
                nro_doc = c.entidad.fact_cuit
            linea += str(tipo_doc).encode('utf-8').rjust(2, "0") #TIPO DOC
            linea += str(nro_doc)[:20].encode('utf-8').rjust(20, "0") #nro DOC/cuit
            linea += (c.entidad.apellido_y_nombre)[:30].encode('utf-8').ljust(30, " ") #nombre
            linea += str(c.importe_total).replace(".","").encode('utf-8').rjust(15, "0") #importe_total
            linea += str(c.importe_no_gravado).encode('utf-8').replace(".","").rjust(15, "0") #importe_ng            
            linea += str(c.importe_exento).encode('utf-8').replace(".","").rjust(15, "0") #importe_exento
            linea += str(0).replace(".","").rjust(15, "0") #perc_impuestosNac
            linea += str(0).replace(".","").rjust(15, "0") #perc_impuestosNac
            linea += str(0).replace(".","").rjust(15, "0") #perc_IIBB
            linea += str(0).replace(".","").rjust(15, "0") #perc_impMunicip
            linea += str(0).replace(".","").rjust(15, "0") #importe_impuestosInt
            linea += str('PES').encode('utf-8') #Moneda
            linea += str('0001000000').encode('utf-8')#tipo_cambio            
            try:
                cpb_iva = cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=c)
                cant_alic = len(cpb_iva)
                informa = len(cpb_iva.filter(tasa_iva__id_afip__lte=3))>0
                cod_op = ' '
                if informa:
                    if c.importe_exento>0:
                        cod_op = 'E'
                    else:
                        cod_op = 'N'
            except:
                cant_alic = 0
                cod_op = 'N'
            linea += str(cant_alic).encode('utf-8').rjust(1, "0") #cant_alic_iva
            linea += str(cod_op).encode('utf-8')#cod_operacion
            linea += str(0).replace(".","").rjust(15, "0") #credFiscalComputable
            linea += str(0).replace(".","").rjust(15, "0") #otrosTributos
            linea += str(0).rjust(11, "0") #CUIT emisor/receptor
            linea += str('').encode('utf-8').ljust(30, " ") #Nombre emisor/receptor
            linea += str(0).replace(".","").rjust(15, "0") #IVA comision            
            
            archivo.write(linea+'\r\n')
        elif tipo_archivo=='alicuotas':         
         for c in cpbs:
            nafip=c.get_nro_afip()
            if nafip==None:
                continue
            cpb_iva = cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=c)
            tipo_doc=c.entidad.tipo_doc
            if tipo_doc == 99:
                nro_doc = 0
            elif tipo_doc == 96:
                nro_doc = c.entidad.nro_doc
            elif tipo_doc == 80:    
                nro_doc = c.entidad.fact_cuit
            else:
                nro_doc = c.entidad.fact_cuit
            for ci in cpb_iva:            
                linea="" 
                linea += str(nafip).encode('utf-8').rjust(3, "0") #CODIGO CPB AFIP
                linea += str(c.pto_vta).encode('utf-8').rjust(5, "0") #PTO VTA
                linea += str(c.numero).encode('utf-8').rjust(20, "0") #NRO CPB                
                linea += str(tipo_doc).encode('utf-8').rjust(2, "0") #TIPO DOC
                linea += str(nro_doc).encode('utf-8').rjust(20, "0") #nro DOC/cuit
                linea += str(ci.importe_base).encode('utf-8').replace(".","").rjust(15, "0") #importe_neto
                linea += str(ci.tasa_iva.id_afip).encode('utf-8').rjust(4, "0") #CODIGO IVA AFIP
                linea += str(ci.importe_total).encode('utf-8').replace(".","").rjust(15, "0") #importe IVA            
                archivo.write(linea+'\r\n')        

    
    contents = archivo.getvalue()
    archivo.close()
    end=time.time() - start
    #print end
    return contents


@login_required 
def libro_iva_ventas(request):    
    limpiar_sesion(request)
    if not tiene_permiso(request,'rep_libro_iva'):
            return redirect(reverse('principal'))  
    context = {}
    context = getVariablesMixin(request)    
    try:
        empresa = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        empresa = None 
    form = ConsultaLibroIVAVentas(request.POST or None,request=request)            
    fecha = date.today()
    cpbs = None
    if form.is_valid():                                
        entidad = form.cleaned_data['entidad']                                                              
        fdesde = form.cleaned_data['fdesde']   
        fhasta = form.cleaned_data['fhasta']   
        estado = form.cleaned_data['estado']
        pto_vta = form.cleaned_data['pto_vta']  
        fact_x = form.cleaned_data['fact_x']  
        cae = form.cleaned_data['cae']  
        total = 0                    
        cpbs = cpb_comprobante.objects.filter(cpb_tipo__compra_venta='V',pto_vta__in=pto_vta_habilitados_list(request),cpb_tipo__tipo__in=[1,2,3,9,14],empresa=empresa,fecha_imputacion__gte=fdesde,fecha_imputacion__lte=fhasta).exclude(letra='X')\
            .select_related('cpb_tipo','entidad')\
            .only('id','pto_vta','letra','numero','fecha_imputacion','cpb_tipo__codigo','cpb_tipo__nombre','cpb_tipo__tipo','cpb_tipo__signo_ctacte','cae_vto','cae',\
            'entidad__id','entidad__apellido_y_nombre','entidad__tipo_entidad','entidad__codigo','entidad__fact_cuit','entidad__nro_doc','entidad__fact_categFiscal',\
            'importe_gravado','importe_iva','importe_perc_imp','importe_no_gravado','importe_exento','importe_total')\
            .order_by('-fecha_imputacion','-id','entidad__codigo','entidad__apellido_y_nombre','cpb_tipo__tipo')            
            
        
        if int(estado) == 0:                
            cpbs=cpbs.filter(estado__in=[1,2])                
        elif int(estado) == 2:                
            cpbs=cpbs.filter(estado__in=[3])
        else:                
            cpbs=cpbs.filter(estado__in=[1,2,3])
        
        if entidad:
                cpbs= cpbs.filter(entidad__apellido_y_nombre__icontains=entidad)
        
        if pto_vta:
               cpbs= cpbs.filter(pto_vta=pto_vta)        

        if int(cae)!=0:
            no_tiene = (cae=='2')                
            cpbs= cpbs.filter(cae_vto__isnull=no_tiene)
        
        if int(fact_x)==1:
            cpbs= cpbs.filter(cpb_tipo__libro_iva=True)
               
        if ('cpbs' in request.POST)and(cpbs):                
            response = HttpResponse(generarCITI(cpbs,'V','cpbs'),content_type='text/plain')
            response['Content-Disposition'] = 'attachment;filename="CITI_VENTAS_CBTE.txt"'
            return response 
        elif ('alicuotas' in request.POST)and(cpbs):
            response = HttpResponse(generarCITI(cpbs,'V','alicuotas'),content_type='text/plain')
            response['Content-Disposition'] = 'attachment;filename="CITI_VENTAS_ALICUOTAS.txt"'
            return response 
        
    context['form'] = form
    context['cpbs'] = cpbs
    context['fecha'] = fecha          
    return render(request,'reportes/contables/libro_iva_ventas.html',context )

@login_required                    
def libro_iva_compras(request):

    if not tiene_permiso(request,'rep_libro_iva'):
            return redirect(reverse('principal'))  
    context = {}
    context = getVariablesMixin(request)    
    try:
        empresa = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        empresa = None 
    form = ConsultaLibroIVACompras(request.POST or None,request=request)            
    fecha = date.today()
    cpbs = None
    if form.is_valid():                                
        entidad = form.cleaned_data['entidad']                                                              
        fdesde = form.cleaned_data['fdesde']   
        fhasta = form.cleaned_data['fhasta']   
        estado = form.cleaned_data['estado'] 
        fact_x = form.cleaned_data['fact_x']  
        pto_vta = form.cleaned_data['pto_vta'] 
                
        cpbs = cpb_comprobante.objects.filter(cpb_tipo__libro_iva=True,pto_vta__in=pto_vta_habilitados_list(request),cpb_tipo__tipo__in=[1,2,3,9],cpb_tipo__compra_venta='C',empresa=empresa,fecha_imputacion__gte=fdesde,fecha_imputacion__lte=fhasta)\
            .select_related('cpb_tipo','entidad')\
            .only('id','pto_vta','letra','numero','fecha_imputacion','cpb_tipo__codigo','cpb_tipo__nombre','cpb_tipo__tipo','cpb_tipo__signo_ctacte','cae_vto','cae',\
            'entidad__id','entidad__apellido_y_nombre','entidad__tipo_entidad','entidad__codigo','entidad__fact_cuit','entidad__nro_doc','entidad__fact_categFiscal',\
            'importe_gravado','importe_iva','importe_perc_imp','importe_no_gravado','importe_exento','importe_total')\
            .order_by('-fecha_imputacion','-id','entidad__codigo','entidad__apellido_y_nombre','cpb_tipo__tipo')
        
        if int(estado) == 0:                
            cpbs=cpbs.filter(estado__in=[1,2])                
        elif int(estado) == 2:                
            cpbs=cpbs.filter(estado__in=[3])
        else:                
            cpbs=cpbs.filter(estado__in=[1,2,3])
        if entidad:
                cpbs= cpbs.filter(entidad__apellido_y_nombre__icontains=entidad)
        if pto_vta:
               cpbs= cpbs.filter(pto_vta=pto_vta)                   

        if int(fact_x)==1:
            cpbs= cpbs.filter(cpb_tipo__libro_iva=True).exclude(letra='X')
        
        if ('cpbs' in request.POST)and(cpbs):                
            response = HttpResponse(generarCITI(cpbs,'C','cpbs'),content_type='text/plain')
            response['Content-Disposition'] = 'attachment;filename="CITI_COMPRAS_CBTE.txt"'
            return response 
        elif ('alicuotas' in request.POST)and(cpbs):
            response = HttpResponse(generarCITI(cpbs,'C','alicuotas'),content_type='text/plain')
            response['Content-Disposition'] = 'attachment;filename="CITI_COMPRAS_ALICUOTAS.txt"'
            return response 

    context['form'] = form
    context['cpbs'] = cpbs
    context['fecha'] = fecha          
    return render(request,'reportes/contables/libro_iva_compras.html',context )


################################################################

class caja_diaria(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'reportes/contables/caja_diaria.html'
    context_object_name = 'cpbs'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'rep_caja_diaria'):
            return redirect(reverse('principal'))  
        return super(caja_diaria, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(caja_diaria, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCajaDiaria(self.request.POST or None,empresa=empresa,request=self.request)            
        fecha = date.today()
        ingresos = None
        egresos = None
        ingresos_resumen = None
        egresos_resumen = None
        ingresos_cta_resumen = None
        egresos_cta_resumen = None
        ingresos_total = 0
        egresos_total = 0
        ingresos_cta_total = 0
        egresos_cta_total = 0

        if form.is_valid():                                
            tipo_forma_pago = form.cleaned_data['tipo_forma_pago']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']   
            pto_vta = form.cleaned_data['pto_vta'] 
            cuenta = form.cleaned_data['cuenta']             
            
            ingresos = cpb_comprobante_fp.objects.filter(cpb_comprobante__empresa=empresa,mdcp_fecha__gte=fdesde,mdcp_fecha__lte=fhasta,cpb_comprobante__estado__in=[1,2],cta_ingreso__isnull=False,mdcp_salida__isnull=True)
            egresos = cpb_comprobante_fp.objects.filter(cpb_comprobante__empresa=empresa,mdcp_fecha__gte=fdesde,mdcp_fecha__lte=fhasta,cpb_comprobante__estado__in=[1,2],cta_egreso__isnull=False,mdcp_salida__isnull=True)
            ingresos = ingresos.select_related('cpb_comprobante','cpb_comprobante__cpb_tipo','cta_ingreso','mdcp_banco','tipo_forma_pago')
            egresos = egresos.select_related('cpb_comprobante','cpb_comprobante__cpb_tipo','cta_egreso','mdcp_banco','tipo_forma_pago')

            if tipo_forma_pago:
                   ingresos= ingresos.filter(tipo_forma_pago=tipo_forma_pago)
                   egresos= egresos.filter(tipo_forma_pago=tipo_forma_pago)
            if pto_vta:
                   ingresos= ingresos.filter(cpb_comprobante__pto_vta=pto_vta)
                   egresos= egresos.filter(cpb_comprobante__pto_vta=pto_vta)            

            

            ingresos_resumen = ingresos.values('tipo_forma_pago__id','tipo_forma_pago__codigo','tipo_forma_pago__nombre')\
                            .annotate( saldo=Sum(ExpressionWrapper(F("importe"), output_field=FloatField())) )
            ingresos_total = ingresos.aggregate(ingresos_total=Sum('importe'))
            egresos_resumen = egresos.values('tipo_forma_pago__id','tipo_forma_pago__codigo','tipo_forma_pago__nombre')\
                            .annotate( saldo=Sum(ExpressionWrapper(F("importe"), output_field=FloatField())) )
            egresos_total = egresos.aggregate(egresos_total=Sum('importe'))
            
            if cuenta:
                   ingresos= ingresos.filter(cta_ingreso=cuenta)
                   egresos= egresos.filter(cta_egreso=cuenta)
                   
            ingresos_cta_resumen = ingresos.values('cta_ingreso__id','cta_ingreso__codigo','cta_ingreso__nombre').annotate( saldo=Sum(ExpressionWrapper(F("importe"), output_field=FloatField())) )
            ingresos_cta_total = ingresos.aggregate(ingresos_cta_total=Sum('importe'))
            egresos_cta_resumen = egresos.values('cta_egreso__id','cta_egreso__codigo','cta_egreso__nombre').annotate( saldo=Sum(ExpressionWrapper(F("importe"), output_field=FloatField())) )
            egresos_cta_total = egresos.aggregate(egresos_total=Sum('importe'))
        context['form'] = form
        context['ingresos'] = ingresos
        context['egresos'] = egresos
        context['ingresos_resumen'] = ingresos_resumen
        context['egresos_resumen'] = egresos_resumen
        context['ingresos_cta_resumen'] = ingresos_cta_resumen
        context['egresos_cta_resumen'] = egresos_cta_resumen
        context['ingresos_total'] = ingresos_total
        context['egresos_total'] = egresos_total
        context['ingresos_cta_total'] = ingresos_cta_total
        context['egresos_cta_total'] = egresos_cta_total
        context['fecha'] = fecha        
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)
        

################################################################

class saldos_cuentas(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'reportes/contables/cuentas.html'
    context_object_name = 'cpbs'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'rep_saldos_cuentas'):
            return redirect(reverse('principal'))  
        return super(saldos_cuentas, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(saldos_cuentas, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaSaldosCuentas(self.request.POST or None,empresa=empresa,request=self.request)   
        cpbs = None
        fecha = date.today()
        datos = []
        if form.is_valid():                                            
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']   
            cuenta = form.cleaned_data['cuenta']                                             
            pto_vta = form.cleaned_data['pto_vta'] 
            
            ctas = cpb_cuenta.objects.filter(empresa=empresa,baja=False)

            if cuenta:
                ctas = ctas.filter(id=cuenta.id)           
            
            for cta in ctas:
                
                cpbs = cpb_comprobante_fp.objects.filter(cpb_comprobante__empresa=empresa,cpb_comprobante__estado__in=[1,2],cpb_comprobante__fecha_cpb__lte=fhasta).select_related('cpb_comprobante','cpb_comprobante__cpb_tipo','cta_egreso','cta_ingreso','tipo_forma_pago').order_by('cpb_comprobante__fecha_cpb','id')                
                if pto_vta:
                    cpbs = cpbs.filter(cpb_comprobante__pto_vta=pto_vta)
                
                debe=0
                haber=0
                saldo=0
                saldo_cpb=0
                detalles = []
                                
                cpbs_debe = cpbs.filter(cta_ingreso=cta)
                cpbs_haber= cpbs.filter(cta_egreso=cta) 
                debe = cpbs_debe.aggregate(sum=Sum(F('importe'), output_field=DecimalField()))['sum'] or 0  
                haber = cpbs_haber.aggregate(sum=Sum(F('importe'), output_field=DecimalField()))['sum'] or 0  
               
                cpbs= cpbs_debe | cpbs_haber
                cpbs = cpbs.order_by('cpb_comprobante__fecha_cpb')
               
                
                # cpbs = cpbs.filter(cpb_comprobante__fecha_cpb__gte=fdesde)
                cpbs_anteriores = cpbs.filter(mdcp_fecha__lte=fdesde)
                cpbs_detalles = cpbs.filter(mdcp_fecha__gt=fdesde,mdcp_fecha__lte=fhasta)  
                cpbs_posteriores = cpbs.filter(mdcp_fecha__gt=fhasta)                 

                debe_ant= cpbs_anteriores.filter(cta_ingreso=cta).aggregate(sum=Sum(F('importe'), output_field=DecimalField()))['sum'] or 0  
                haber_ant = cpbs_anteriores.filter(cta_egreso=cta).aggregate(sum=Sum(F('importe'), output_field=DecimalField()))['sum'] or 0         
                debe_pos= 0
                haber_pos = cpbs_posteriores.filter(cta_egreso=cta).aggregate(sum=Sum(F('importe'), output_field=DecimalField()))['sum'] or 0         
                                
                saldo_inicial = debe_ant - haber_ant
                saldo_futuro = debe_pos - haber_pos                
                  
                if saldo_inicial != 0:                                
                    detalles.append(
                            {
                            'fecha':fdesde,
                            'tipo':'',
                            'nro_cpb':'SALDO ANTERIOR',
                            'debe': debe_ant,
                            'haber':haber_ant,
                            'saldo': saldo_inicial,
                            }
                        )
                    saldo_cpb = saldo_inicial
                for c in cpbs_detalles:
                    debe_cpb=0
                    haber_cpb=0
                                        
                    if c.cta_ingreso == cta:
                        debe_cpb = c.importe                        
                    
                    if c.cta_egreso == cta:
                        haber_cpb = c.importe                                            

                    saldo_cpb += (debe_cpb-haber_cpb)

                    detalles.append(
                        {
                        'fecha':c.mdcp_fecha,
                        'tipo':c.cpb_comprobante.cpb_tipo,
                        'nro_cpb':c.cpb_comprobante.get_cpb,
                        'fp':c.tipo_forma_pago,
                        'mdcp_cheque':c.mdcp_cheque,
                        'debe':debe_cpb,
                        'haber':haber_cpb,
                        'saldo': saldo_cpb,
                        }
                    )
                if saldo_futuro != 0:                                
                    detalles.append(
                            {
                            'fecha':fhasta,
                            'tipo':'',
                            'nro_cpb':'COMPROMISOS A FUTURO',
                            'debe': debe_pos,
                            'haber':haber_pos,
                            'saldo': saldo_futuro,
                            }
                        )
                    saldo_cpb += saldo_futuro

                saldo = debe - haber 
                datos.append(
                    {
                        'id_cuenta':cta.id,
                        'cuenta':cta,
                        'debe':debe,
                        'haber':haber,
                        'saldo': saldo,
                        'detalles': detalles,                        
                    }
                )
                    
        context['form'] = form
        context['datos'] = datos
        context['fecha'] = fecha
        return context

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

################################################################

class vencimientos_cpbs(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'reportes/varios/vencimientos_cpbs.html'
    context_object_name = 'cpbs'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        # if not tiene_permiso(self.request,'rep_caja_diaria'):
        #     return redirect(reverse('principal'))  
        return super(vencimientos_cpbs, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(vencimientos_cpbs, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaVencimientos(self.request.POST or None,empresa=empresa,request=self.request)            
        fecha = date.today()        

        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[1,2,3,4,5,6,7,9,14],empresa=empresa).order_by('-fecha_vto','-fecha_cpb','-id')\
        .select_related('estado','entidad','cpb_tipo','vendedor')\
        .only('id','pto_vta','letra','numero','importe_total','fecha_cpb','estado','fecha_vto','cpb_tipo__codigo','cpb_tipo__nombre','cpb_tipo__tipo','cpb_tipo__signo_ctacte','cae_vto','cae','observacion','seguimiento','vendedor__apellido_y_nombre',\
            'entidad__id','entidad__apellido_y_nombre','entidad__tipo_entidad','entidad__codigo','entidad__fact_cuit','entidad__nro_doc','entidad__fact_categFiscal')
                
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']               
            estado = form.cleaned_data['estado']
            tipo_cpb = form.cleaned_data['tipo_cpb']
            cae = form.cleaned_data['cae']  

            if int(estado) == 0:                
                comprobantes=comprobantes.filter(estado__in=[1,2])                
            elif int(estado) == 2:                
                comprobantes=comprobantes.filter(estado__in=[3])
            else:                
                comprobantes=comprobantes.filter(estado__in=[1,2,3])                  

            if tipo_cpb:                
                comprobantes=comprobantes.filter(cpb_tipo=tipo_cpb)  

            if fdesde:
                comprobantes= comprobantes.filter(fecha_cpb__gte=fdesde)
            if fhasta:
                comprobantes= comprobantes.filter(fecha_cpb__lte=fhasta)
            if entidad:
                comprobantes= comprobantes.filter(entidad__apellido_y_nombre__icontains=entidad)           
            if pto_vta:
                comprobantes= comprobantes.filter(pto_vta=pto_vta)            

            if int(cae)!=0:
                no_tiene = (cae=='2')                
                comprobantes= comprobantes.filter(cae_vto__isnull=no_tiene)           
        else:
            comprobantes = None

        context['form'] = form
        context['comprobantes'] = comprobantes
        context['fecha'] = fecha        
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

################################################################

class seguimiento_cheques(VariablesMixin,ListView):
    model = cpb_comprobante    
    template_name = 'reportes/contables/seguimiento_cheques.html'
    context_object_name = 'cpbs'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        # if not tiene_permiso(self.request,'rep_caja_diaria'):
        #     return redirect(reverse('principal'))  
        return super(seguimiento_cheques, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(seguimiento_cheques, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        
        fecha = hoy()
        
        form = ConsultaHistStockProd(self.request.POST or None,empresa=empresa,request=self.request)   
        
        cheques = cpb_comprobante_fp.objects.filter(cpb_comprobante__empresa=empresa,tipo_forma_pago__cuenta__tipo=2,cpb_comprobante__estado__in=[1,2]).order_by('-fecha_creacion','-mdcp_fecha')\
            .select_related('cpb_comprobante','cta_ingreso','cta_egreso','tipo_forma_pago','mdcp_banco','cpb_comprobante__cpb_tipo','cpb_comprobante__entidad','mdcp_salida__cta_ingreso','mdcp_salida__cpb_comprobante__cpb_tipo')
        
        if form.is_valid():
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                              
            cheques = cheques.filter(mdcp_fecha__gte=fdesde,mdcp_fecha__lte=fhasta)
            
        cta_cheques = cpb_cuenta.objects.filter(tipo=2)     
        cartera = cheques.filter(cta_egreso__isnull=True,cta_ingreso__in=cta_cheques,mdcp_salida__isnull=True).order_by('-mdcp_fecha','-fecha_creacion')
        cobrados = cheques.filter(cpb_comprobante__cpb_tipo__tipo=4,mdcp_salida__cpb_comprobante__cpb_tipo__tipo=8,cta_egreso__isnull=True,cta_ingreso__in=cta_cheques,mdcp_salida__isnull=False).order_by('-fecha_creacion','-mdcp_fecha',)
        pagados = cheques.filter(cpb_comprobante__cpb_tipo__tipo=7,cta_egreso__in=cta_cheques,mdcp_salida__isnull=True).order_by('-fecha_creacion','-mdcp_fecha',)
        cheques = cartera | cobrados | pagados


        context['form'] = form 
        context['cheques'] = cheques
        context['cartera'] = cartera
        context['pagados'] = pagados
        context['cobrados'] = cobrados
        context['fecha'] = fecha        
        return context
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

################################################################

class ProdHistoricoView(VariablesMixin,ListView):
    model = cpb_comprobante_detalle
    template_name = 'reportes/varios/historico_productos.html'
    context_object_name = 'movimientos'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(ProdHistoricoView, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProdHistoricoView, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        fecha = date.today()
        
        form = ConsultaHistStockProd(self.request.POST or None,empresa=empresa,request=self.request)   

        movimientos = cpb_comprobante_detalle.objects.none()
        #movimientos = cpb_comprobante_detalle.objects.filter(cpb_comprobante__empresa=empresa,cpb_comprobante__fecha_cpb=hoy()).select_related('producto','cpb_comprobante').order_by('producto')
        
        if form.is_valid():                                            
            producto = form.cleaned_data['producto']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']       
            
            movimientos = cpb_comprobante_detalle.objects.filter(cpb_comprobante__estado__in=[1,2],cpb_comprobante__cpb_tipo__usa_stock=True,cpb_comprobante__empresa=empresa,cpb_comprobante__fecha_cpb__gte=fdesde,cpb_comprobante__fecha_cpb__lte=fhasta).order_by('-cpb_comprobante__fecha_cpb','-producto')        
            
            if producto:
                movimientos = movimientos.filter(Q(producto__nombre__icontains=producto))

            movimientos=movimientos.select_related('cpb_comprobante','cpb_comprobante__cpb_tipo','producto','producto__categoria')
                       
        context['form'] = form
        context['movimientos'] = movimientos
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)         

################################################################

class RankingsView(VariablesMixin,TemplateView):
    template_name = 'reportes/varios/rankings.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        # if not tiene_permiso(self.request,'rep_caja_diaria'):
        #     return redirect(reverse('principal'))  
        return super(RankingsView, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(RankingsView, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        

        form = ConsultaRankings(self.request.POST or None,empresa=empresa,request=self.request)            
        fecha = date.today()        

        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[1,2,3,9],estado__in=[1,2])        
        
        meses = list()
        import locale        
        locale.setlocale(locale.LC_ALL, '')
        for m in MESES:
            meses.append(m[1])
        
        ventas_deuda = list()
        ventas_pagos = list()
        compras_deuda = list()
        compras_pagos = list()
        fdesde = ultimo_anio()
        fhasta = hoy()
        if form.is_valid():                                            
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']                           
          
            if fdesde:
                comprobantes= comprobantes.filter(fecha_cpb__gte=fdesde)            
            if fhasta:
                comprobantes= comprobantes.filter(fecha_cpb__lte=fhasta)           
            if pto_vta:
                comprobantes= comprobantes.filter(pto_vta=pto_vta)            

        else:
            
            context['productos_vendidos'] = None
            context['productos_comprados'] = None
            context['ranking_vendedores'] =  None
            context['ranking_clientes'] =  None
            context['ranking_proveedores'] =  None

        context['form'] = form
        context['fecha'] = fecha        
        context['fdesde'] = fdesde
        context['fhasta'] = fhasta
        
        if comprobantes:
            
            cpbs = comprobantes.annotate(m=Month('fecha_cpb')).values('m')        
            ventas = cpbs.filter(cpb_tipo__compra_venta='V').annotate(pendiente=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'),output_field=DecimalField()),saldado=Sum((F('importe_total')-F('saldo'))*F('cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by(F('m'))
            compras = cpbs.filter(cpb_tipo__compra_venta='C').annotate(pendiente=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'),output_field=DecimalField()),saldado=Sum((F('importe_total')-F('saldo'))*F('cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by(F('m'))

            for v in ventas:
                ventas_deuda.append(v['pendiente'])
                ventas_pagos.append(v['saldado'])

            for c in compras:
                compras_deuda.append(c['pendiente'])
                compras_pagos.append(c['saldado'])
            



            cpb_detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante__in=comprobantes)
            productos_vendidos = cpb_detalles.filter(cpb_comprobante__cpb_tipo__compra_venta='V')
            productos_vendidos_total = productos_vendidos.aggregate(sum=Sum(F('importe_total')*F('cpb_comprobante__cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
            productos_vendidos = productos_vendidos.values('producto__nombre').annotate(tot=Sum(F('importe_total')*F('cpb_comprobante__cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by('-tot')[:10]
            context['productos_vendidos'] = productos_vendidos

            productos_comprados = cpb_detalles.filter(cpb_comprobante__cpb_tipo__compra_venta='C')
            productos_comprados_total = productos_comprados.aggregate(sum=Sum(F('importe_total')*F('cpb_comprobante__cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
            productos_comprados = productos_comprados.values('producto__nombre').annotate(tot=Sum(F('importe_total')*F('cpb_comprobante__cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by('-tot')[:10]
            context['productos_comprados'] = productos_comprados
                    
            ranking_vendedores = comprobantes.values('vendedor__apellido_y_nombre').annotate(tot=Sum(F('importe_total'),output_field=DecimalField())).order_by('-tot')[:10]
            context['ranking_vendedores'] = ranking_vendedores

            ranking_clientes = comprobantes.filter(cpb_tipo__compra_venta='V').values('entidad__apellido_y_nombre').annotate(tot=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by('-tot')[:10]
            context['ranking_clientes'] = ranking_clientes

            ranking_proveedores = comprobantes.filter(cpb_tipo__compra_venta='C').values('entidad__apellido_y_nombre').annotate(tot=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by('-tot')[:10]
            context['ranking_proveedores'] = ranking_proveedores

        context['meses']= json.dumps(meses,cls=DecimalEncoder)       
        context['ventas_deuda']=  json.dumps(ventas_deuda,cls=DecimalEncoder)
        context['ventas_pagos']=  json.dumps(ventas_pagos,cls=DecimalEncoder)
        context['compras_deuda']= json.dumps(compras_deuda,cls=DecimalEncoder)
        context['compras_pagos']= json.dumps(compras_pagos,cls=DecimalEncoder)

        return context

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)



from django.http import JsonResponse

def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]

class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()

@login_required
def ver_grafico(request):
    productos_vendidos = cpb_comprobante_detalle.objects.filter(cpb_comprobante__cpb_tipo__compra_venta='V',cpb_comprobante__cpb_tipo__tipo__in=[1,2,3,9],cpb_comprobante__estado__in=[1,2],cpb_comprobante__fecha_cpb__year=hoy().year)
    productos_vendidos_total = productos_vendidos.aggregate(sum=Sum(F('cantidad')*F('cpb_comprobante__cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
    productos_vendidos = productos_vendidos.values('producto__nombre').annotate(tot=Sum(F('cantidad')*F('cpb_comprobante__cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by('-tot')[:20]
    

    # comprobantes = cpb_comprobante.objects.filter(pto_vta__in=pto_vta_habilitados(request),cpb_tipo__tipo__in=[1,2,3,9],estado__in=[1,2],fecha_cpb__year=2018)
    # comprobantes = comprobantes.annotate(m=Month('fecha_cpb')).values('cpb_tipo__compra_venta','m')\
    #         .annotate(cant=Count('id'),total=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by(F('m'),F('cpb_tipo__compra_venta'))        
    productos_vendidos = ValuesQuerySetToDict(productos_vendidos)

  
    #return JsonResponse(json.dumps(ventas, cls=DjangoJSONEncoder))            
    return HttpResponse( json.dumps(productos_vendidos, cls=DjangoJSONEncoder), content_type='application/json' )  




