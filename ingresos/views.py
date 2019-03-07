# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import render, redirect, get_object_or_404,render_to_response,HttpResponseRedirect,HttpResponse
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView,DetailView,DeleteView
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from datetime import datetime,date,timedelta
from django.utils import timezone
from dateutil.relativedelta import *
from .forms import *
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from django.db.models import Q,Sum,Count
from comprobantes.models import *
import json
from decimal import *
from fm.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
from django.contrib import messages
from general.utilidades import *
from general.views import VariablesMixin
from usuarios.views import tiene_permiso
from django.forms.models import inlineformset_factory,BaseInlineFormSet,formset_factory
from productos.models import prod_productos
from django.contrib.messages.views import SuccessMessageMixin
from django.core.serializers.json import DjangoJSONEncoder
from comprobantes.views import puedeEditarCPB,puedeEliminarCPB,ultimoNro,buscarDatosProd,presup_aprobacion,cobros_cpb,cpb_anular_reactivar
from general.forms import ConsultaCpbs,ConsultaCpbsCompras,pto_vta_habilitados,pto_vta_habilitados_list
from django.utils.functional import curry 
from trabajos.models import orden_pedido,orden_pedido_detalle


class CPBSVentasList(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'ingresos/ventas/cpb_venta_listado.html'
    context_object_name = 'comprobantes'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'cpb_ventas'):
            return redirect(reverse('principal'))
        return super(CPBSVentasList, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBSVentasList, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCpbs(self.request.POST or None,empresa=empresa,request=self.request)   
        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[1,2,3,9,14],cpb_tipo__compra_venta='V',estado__in=[1,2],empresa=empresa,pto_vta__in=pto_vta_habilitados_list(self.request))
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']   
            vendedor = form.cleaned_data['vendedor']                                                 
            estado = form.cleaned_data['estado']
            letra = form.cleaned_data['letra']
            cae = form.cleaned_data['cae']

            
            if int(estado) == 1:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__compra_venta='V',estado__in=[1,2,3],empresa=empresa)
            elif int(estado) == 2:
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__compra_venta='V',estado__in=[3],empresa=empresa)

            if int(cae)!=0:
                no_tiene = (cae=='2')                
                comprobantes= comprobantes.filter(cae_vto__isnull=no_tiene)

            if fdesde:
                comprobantes= comprobantes.filter(fecha_cpb__gte=fdesde)
            if fhasta:
                comprobantes= comprobantes.filter(fecha_cpb__lte=fhasta)  
            if entidad:
                comprobantes= comprobantes.filter(entidad__apellido_y_nombre__icontains=entidad)
            if vendedor:
                comprobantes= comprobantes.filter(vendedor=vendedor)
            if pto_vta:
                comprobantes= comprobantes.filter(pto_vta=pto_vta) 
            if letra:
                comprobantes= comprobantes.filter(letra=letra) 
        else:
            comprobantes= comprobantes.filter(fecha_cpb__gte=inicioMesAnt(),fecha_cpb__lte=finMes())

        context['form'] = form
        context['comprobantes'] = comprobantes.select_related('estado','cpb_tipo','entidad','vendedor','empresa','id_cpb_padre').order_by('-fecha_cpb','-fecha_creacion','-id')
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

class CPBVentaDetalleFormSet(BaseInlineFormSet): 
    pass  
class CPBVentaPIFormSet(BaseInlineFormSet): 
    pass  
class CPBVentaFPFormSet(BaseInlineFormSet): 
    pass 

CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBVentaDetalleForm,formset=CPBVentaDetalleFormSet, can_delete=True,extra=0,min_num=1,can_order=True)
CPBPIFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_perc_imp,form=CPBVentaPercImpForm,formset=CPBVentaPIFormSet, can_delete=True,extra=0,min_num=1)  
CPBFPFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_fp,form=CPBFPForm,formset=CPBVentaFPFormSet, can_delete=True,extra=0,min_num=1)


class CPBVentaCreateView(VariablesMixin,CreateView):
    form_class = CPBVentaForm
    template_name = 'ingresos/ventas/cpb_venta_form.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
        return super(CPBVentaCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(CPBVentaCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['titulo'] = 'Nuevo Comprobante'
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBVentaCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)               
        if not tiene_permiso(self.request,'cpb_ventas_cobrar'):
            form.condic_pago=1
            form.fields['condic_pago'].widget.attrs['disabled'] = True
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        ventas_detalle = CPBDetalleFormSet(prefix='formDetalle')        
        ventas_pi = CPBPIFormSet(prefix='formDetallePI')        
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

    
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        ventas_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        ventas_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and ventas_detalle.is_valid() and ventas_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, ventas_detalle,ventas_pi,cpb_fp)
        else:
            return self.form_invalid(form, ventas_detalle,ventas_pi,cpb_fp)        

    def form_valid(self, form, ventas_detalle,ventas_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)       
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        ventas_detalle.instance = self.object
        ventas_detalle.cpb_comprobante = self.object.id        
        ventas_detalle.save()
        if ventas_pi:
            ventas_pi.instance = self.object
            ventas_pi.cpb_comprobante = self.object.id 
            ventas_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=7)
            nro = ultimoNro(7,self.object.pto_vta,"X")
            recibo = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",
                numero=nro,fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,
                importe_total=self.object.importe_total,estado=estado,usuario=self.object.usuario,fecha_vto=self.object.fecha_cpb,empresa = self.object.empresa)
            recibo.save()
            cobranza = cpb_cobranza(cpb_comprobante=recibo,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = recibo
            cpb_fp.cpb_comprobante = recibo.id 
            
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)        
        messages.success(self.request, u'Los datos se guardaron con éxito!')

        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,ventas_detalle,ventas_pi,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

class CPBVentaPresupCreateView(VariablesMixin,CreateView):
    form_class = CPBVentaForm
    template_name = 'ingresos/ventas/cpb_venta_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
        return super(CPBVentaPresupCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(CPBVentaPresupCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['titulo'] = 'Nuevo Comprobante Ventas - Presupuesto Nro: %s' % self.get_object()
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBVentaPresupCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        cpb=self.get_object()       
        if cpb:
            form.fields['id_cpb_padre'].initial = cpb.pk
            form.fields['pto_vta'].initial = cpb.pto_vta
            form.fields['entidad'].initial = cpb.entidad
            detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)
            det=[]        
            for c in detalles:            
                det.append({'producto': c.producto,'cantidad':c.cantidad,'detalle':c.detalle,'porc_dcto':c.porc_dcto,'tasa_iva':c.tasa_iva,
                    'coef_iva':c.coef_iva,'lista_precios':c.lista_precios,'importe_costo':c.importe_costo,'importe_unitario':c.importe_unitario,
                    'importe_subtotal':c.importe_subtotal,'importe_iva':c.importe_iva,'importe_total':c.importe_total,'origen_destino':c.origen_destino})                        
            CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBVentaDetalleForm,fk_name='cpb_comprobante',formset=CPBVentaDetalleFormSet, can_delete=True,extra=0,min_num=len(det))
        else:
            detalles = None       
        # ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        # ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        # cpb_fp = CPBFPFormSet(prefix='formFP')
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        ventas_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        ventas_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and ventas_detalle.is_valid() and ventas_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, ventas_detalle,ventas_pi,cpb_fp)
        else:
            return self.form_invalid(form, ventas_detalle,ventas_pi,cpb_fp)        

    def form_valid(self, form, ventas_detalle,ventas_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        ventas_detalle.instance = self.object
        ventas_detalle.cpb_comprobante = self.object.id        
        ventas_detalle.save()
        if ventas_pi:
            ventas_pi.instance = self.object
            ventas_pi.cpb_comprobante = self.object.id 
            ventas_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=7)
            recibo = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",numero=ultimoNro(7,self.object.pto_vta,"X"),id_cpb_padre=self.object,
                fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,importe_total=self.object.importe_total,estado=estado,usuario=self.object.usuario,fecha_vto=self.object.fecha_cpb,empresa=empresa_actual(self.request))
            recibo.save()
            cobranza = cpb_cobranza(cpb_comprobante=recibo,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = recibo
            cpb_fp.cpb_comprobante = recibo.id 
            
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)        
        messages.success(self.request, u'Los datos se guardaron con éxito!')

        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,ventas_detalle,ventas_pi,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

class CPBVentaNCCreateView(VariablesMixin,CreateView):
    form_class = CPBVentaForm
    template_name = 'ingresos/ventas/cpb_venta_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
        return super(CPBVentaNCCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(CPBVentaNCCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['titulo'] = 'Nueva Nota Crédito - CPB Venta Nro: %s' % self.get_object()
        initial['request'] = self.request         
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBVentaNCCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        cpb=self.get_object()       
        if cpb:
            form.fields['id_cpb_padre'].initial = cpb.pk
            form.fields['pto_vta'].initial = cpb.pto_vta
            form.fields['entidad'].initial = cpb.entidad
            form.fields['cpb_tipo'].queryset = cpb_tipo.objects.filter(compra_venta='V',baja=False,tipo__in=[2,3])
            detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)
            det=[]        
            for c in detalles:            
                det.append({'producto': c.producto,'cantidad':c.cantidad,'detalle':c.detalle,'porc_dcto':c.porc_dcto,'tasa_iva':c.tasa_iva,
                    'coef_iva':c.coef_iva,'lista_precios':c.lista_precios,'importe_costo':c.importe_costo,'importe_unitario':c.importe_unitario,
                    'importe_subtotal':c.importe_subtotal,'importe_iva':c.importe_iva,'importe_total':c.importe_total,'origen_destino':c.origen_destino})                        
            CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBVentaDetalleForm,fk_name='cpb_comprobante',formset=CPBVentaDetalleFormSet, can_delete=True,extra=0,min_num=len(det))
        else:
            detalles = None       
        # ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        # ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        # cpb_fp = CPBFPFormSet(prefix='formFP')
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        ventas_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        ventas_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and ventas_detalle.is_valid() and ventas_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, ventas_detalle,ventas_pi,cpb_fp)
        else:
            return self.form_invalid(form, ventas_detalle,ventas_pi,cpb_fp)        

    def form_valid(self, form, ventas_detalle,ventas_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb

        self.object.id_cpb_padre=self.get_object()
        self.object.save()
        ventas_detalle.instance = self.object
        ventas_detalle.cpb_comprobante = self.object.id        
        ventas_detalle.save()
        if ventas_pi:
            ventas_pi.instance = self.object
            ventas_pi.cpb_comprobante = self.object.id 
            ventas_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=7)
            recibo = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",numero=ultimoNro(7,self.object.pto_vta,"X"),id_cpb_padre=self.object,
                fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,importe_total=self.object.importe_total,estado=estado,usuario=self.object.usuario,fecha_vto=self.object.fecha_cpb,)
            recibo.save()
            cobranza = cpb_cobranza(cpb_comprobante=recibo,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = recibo
            cpb_fp.cpb_comprobante = recibo.id 
            
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)        
        messages.success(self.request, u'Los datos se guardaron con éxito!')

        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,ventas_detalle,ventas_pi,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

class CPBVentaOPCreateView(VariablesMixin,CreateView):
    form_class = CPBVentaForm
    template_name = 'ingresos/ventas/cpb_venta_form.html' 
    model = cpb_comprobante
    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
        return super(CPBVentaOPCreateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return get_object_or_404(orden_pedido, pk=self.kwargs.get('id',None))

    def get_initial(self):    
        initial = super(CPBVentaOPCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['titulo'] = u'Nuevo Comprobante Ventas - Orden de Pedido Nº: %s' % self.get_object()
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBVentaOPCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        orden=self.get_object() 
        if orden:
            form.fields['entidad'].initial = orden.cliente
            form.fields['vendedor'].initial = orden.vendedor
            form.fields['observacion'].initial = u'Orden de Pedido Nº: %s' % orden.numero
            detalles = orden_pedido_detalle.objects.filter(orden_pedido=orden)
            letra=get_letra(orden.cliente.fact_categFiscal,empresa_actual(self.request).categ_fiscal)
            det=[]        
            for c in detalles:                                            
                p = buscarPrecioProd(c.producto,letra,c.cantidad,c.importe_unitario)                
                det.append({'producto': c.producto,'cantidad':c.cantidad,'detalle':c.detalle,'porc_dcto':0,'tasa_iva':c.producto.tasa_iva,
                    'coef_iva':c.producto.tasa_iva.coeficiente,'lista_precios':c.lista_precios,'importe_iva':p['importe_iva'],
                    'origen_destino':c.origen_destino,'importe_subtotal':p['importe_subtotal'],'importe_unitario':p['precio'],'importe_total':p['importe_total']})                                        
            CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBVentaDetalleForm,fk_name='cpb_comprobante',formset=CPBVentaDetalleFormSet, can_delete=True,extra=0,min_num=len(det))
        else:
            detalles = None       

        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        ventas_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        ventas_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and ventas_detalle.is_valid() and ventas_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, ventas_detalle,ventas_pi,cpb_fp)
        else:
            return self.form_invalid(form, ventas_detalle,ventas_pi,cpb_fp)        

    def form_valid(self, form, ventas_detalle,ventas_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb        
        self.object.save()        
        orden=self.get_object() 
        orden.id_venta=self.object        
        orden.save()
        ventas_detalle.instance = self.object
        ventas_detalle.cpb_comprobante = self.object.id        
        ventas_detalle.save()
        
        if ventas_pi:
            ventas_pi.instance = self.object
            ventas_pi.cpb_comprobante = self.object.id 
            ventas_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=7)
            recibo = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",numero=ultimoNro(7,self.object.pto_vta,"X"),id_cpb_padre=self.object,
                fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,importe_total=self.object.importe_total,estado=estado,usuario=self.object.usuario,fecha_vto=self.object.fecha_cpb,)
            recibo.save()
            cobranza = cpb_cobranza(cpb_comprobante=recibo,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = recibo
            cpb_fp.cpb_comprobante = recibo.id 
            
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)        
        messages.success(self.request, u'Los datos se guardaron con éxito!')

        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,ventas_detalle,ventas_pi,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))


class CPBVentaUnificarView(VariablesMixin,CreateView):
    form_class = CPBVentaForm
    template_name = 'ingresos/ventas/cpb_venta_form.html' 
    model = cpb_comprobante    
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal')) 
        return super(CPBVentaUnificarView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBVentaUnificarView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self,**kwargs):
        kwargs = super(CPBVentaUnificarView, self).get_form_kwargs()
        kwargs['request'] = self.request                      
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        form.fields['entidad'].widget.attrs['disabled'] = True                       
        id_cpbs = request.GET.getlist('id_cpb',None)
        cpbs = cpb_comprobante.objects.filter(id__in=id_cpbs)
        if cpbs:
            cpb = cpbs[0]            
            form.fields['pto_vta'].initial = cpb.pto_vta
            form.fields['entidad'].initial = cpb.entidad
            #cargo cada uno de los detalles en un solo cpb
            det=[]
            for f in cpbs:
                detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante=f)
                for c in detalles:            
                    det.append({'producto': c.producto,'cantidad':c.cantidad,'detalle':c.detalle,'porc_dcto':c.porc_dcto,'tasa_iva':c.tasa_iva,
                        'coef_iva':c.coef_iva,'lista_precios':c.lista_precios,'importe_costo':c.importe_costo,'importe_unitario':c.importe_unitario,
                        'importe_subtotal':c.importe_subtotal,'importe_iva':c.importe_iva,'importe_total':c.importe_total,'origen_destino':c.origen_destino,'comprobante_original':int(c.cpb_comprobante.id)})                        
            CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBVentaDetalleForm,fk_name='cpb_comprobante',formset=CPBVentaDetalleFormSet, can_delete=True,extra=0,min_num=len(det))
        else:
            return redirect(reverse('cpb_venta_listado')) 

        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        ventas_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        ventas_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and ventas_detalle.is_valid() and ventas_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, ventas_detalle,ventas_pi,cpb_fp)
        else:
            return self.form_invalid(form, ventas_detalle,ventas_pi,cpb_fp)     

    def form_valid(self, form, ventas_detalle,ventas_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        ventas_detalle.instance = self.object
        id_cpbs = self.request.GET.getlist('id_cpb',None)
        ventas_detalle.cpb_comprobante = self.object.id 
        ventas_detalle.save()
        
        if ventas_pi:
            ventas_pi.instance = self.object
            ventas_pi.cpb_comprobante = self.object.id 
            ventas_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=7)
            recibo = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",numero=ultimoNro(7,self.object.pto_vta,"X"),id_cpb_padre=self.object,
                fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,importe_total=self.object.importe_total,estado=estado,usuario=self.object.usuario,fecha_vto=self.object.fecha_cpb,)
            recibo.save()
            cobranza = cpb_cobranza(cpb_comprobante=recibo,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = recibo
            cpb_fp.cpb_comprobante = recibo.id 
            
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)        

        #Anulo los cpbs anteriores   
        for i in id_cpbs:
            cpb_anular_reactivar(self.request,i,3,'Unificado en CPB:%s'%self.object.numero)    

        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,ventas_detalle,ventas_pi,cpb_fp):                                                              
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

class CPBVentaEditView(VariablesMixin,UpdateView):
    form_class = CPBVentaForm
    template_name = 'ingresos/ventas/cpb_venta_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
       if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
       if not puedeEditarCPB(self.get_object().pk):
            messages.error(self.request, u'¡No puede editar un Comprobante Saldado/Facturado!')
            return redirect(reverse('cpb_venta_listado'))
       return super(CPBVentaEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CPBVentaEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
     
    def get_initial(self):    
        initial = super(CPBVentaEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Comprobante '+str(self.get_object())        
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)      
        form.condic_pago=1
        form.fields['condic_pago'].widget.attrs['disabled'] = True
        form.fields['entidad'].widget.attrs['disabled'] = True
        form.fields['pto_vta'].widget.attrs['disabled'] = True
        form.fields['letra'].widget.attrs['disabled'] = True
        form.fields['numero'].widget.attrs['disabled'] = True
        form.fields['cpb_tipo'].widget.attrs['disabled'] = True        
        importes=cobros_cpb(self.object.id)        
        form.fields['importe_cobrado'].initial = importes
        form.fields['cliente_categ_fiscal'].initial = self.object.entidad.fact_categFiscal
        form.fields['cliente_descuento'].initial = self.object.entidad.dcto_general      

        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        ventas_detalle = CPBDetalleFormSet(instance=self.object,prefix='formDetalle')
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        ventas_pi = CPBPIFormSet(instance=self.object,prefix='formDetallePI')       

        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))        
        ventas_detalle = CPBDetalleFormSet(self.request.POST,instance=self.object,prefix='formDetalle')        
        ventas_pi = CPBPIFormSet(self.request.POST,instance=self.object,prefix='formDetallePI')                
        if form.is_valid() and ventas_detalle.is_valid() and ventas_pi.is_valid():
            return self.form_valid(form, ventas_detalle,ventas_pi)
        else:
            return self.form_invalid(form, ventas_detalle,ventas_pi) 
     
    def form_invalid(self, form,ventas_detalle,ventas_pi):                                                       
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)      
        form.condic_pago=1
        form.fields['condic_pago'].widget.attrs['disabled'] = True
        form.fields['entidad'].widget.attrs['disabled'] = True
        form.fields['pto_vta'].widget.attrs['disabled'] = True
        form.fields['letra'].widget.attrs['disabled'] = True
        form.fields['numero'].widget.attrs['disabled'] = True
        form.fields['cpb_tipo'].widget.attrs['disabled'] = True        
        importes=cobros_cpb(self.object.id)        
        form.fields['importe_cobrado'].initial = importes
        form.fields['cliente_categ_fiscal'].initial = self.object.entidad.fact_categFiscal
        form.fields['cliente_descuento'].initial = self.object.entidad.dcto_general
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi))

    def form_valid(self, form, ventas_detalle,ventas_pi):
        self.object = form.save(commit=False)
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb+timezone.timedelta(days=dias_vencimiento)                
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        ventas_detalle.instance = self.object
        ventas_detalle.cpb_comprobante = self.object.id                
        ventas_detalle.save()        
        if ventas_pi:
            ventas_pi.instance = self.object
            ventas_pi.cpb_comprobante = self.object.id 
            ventas_pi.save()                         
        recalcular_saldo_cpb(self.object.pk) 
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_venta_listado'))

class CPBVentaClonarCreateView(VariablesMixin,CreateView):
    form_class = CPBVentaForm
    template_name = 'ingresos/ventas/cpb_venta_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
        return super(CPBVentaClonarCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(CPBVentaClonarCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['titulo'] = 'Nuevo Comprobante Ventas - Clonar CPB: %s' % self.get_object()
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBVentaClonarCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        cpb=self.get_object()       
        if cpb:
            form.fields['id_cpb_padre'].initial = cpb.pk
            form.fields['pto_vta'].initial = cpb.pto_vta
            form.fields['cpb_tipo'].initial = cpb.cpb_tipo
            form.fields['entidad'].initial = cpb.entidad
            detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)
            det=[]        
            for c in detalles:            
                det.append({'producto': c.producto,'cantidad':c.cantidad,'detalle':c.detalle,'porc_dcto':c.porc_dcto,'tasa_iva':c.tasa_iva,
                    'coef_iva':c.coef_iva,'lista_precios':c.lista_precios,'importe_costo':c.importe_costo,'importe_unitario':c.importe_unitario,
                    'importe_subtotal':c.importe_subtotal,'importe_iva':c.importe_iva,'importe_total':c.importe_total,'origen_destino':c.origen_destino})                        
            CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBVentaDetalleForm,fk_name='cpb_comprobante',formset=CPBVentaDetalleFormSet, can_delete=True,extra=0,min_num=len(det))
        else:
            detalles = None       
        # ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        # ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        # cpb_fp = CPBFPFormSet(prefix='formFP')
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBVentaDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBVentaPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        ventas_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        ventas_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and ventas_detalle.is_valid() and ventas_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, ventas_detalle,ventas_pi,cpb_fp)
        else:
            return self.form_invalid(form, ventas_detalle,ventas_pi,cpb_fp)        

    def form_valid(self, form, ventas_detalle,ventas_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        ventas_detalle.instance = self.object
        ventas_detalle.cpb_comprobante = self.object.id        
        ventas_detalle.save()
        if ventas_pi:
            ventas_pi.instance = self.object
            ventas_pi.cpb_comprobante = self.object.id 
            ventas_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=7)
            recibo = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",numero=ultimoNro(7,self.object.pto_vta,"X"),id_cpb_padre=self.object,
                fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,importe_total=self.object.importe_total,estado=estado,usuario=self.object.usuario,fecha_vto=self.object.fecha_cpb,empresa=empresa_actual(self.request))
            recibo.save()
            cobranza = cpb_cobranza(cpb_comprobante=recibo,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = recibo
            cpb_fp.cpb_comprobante = recibo.id 
            
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,ventas_detalle,ventas_pi,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,ventas_detalle = ventas_detalle,ventas_pi=ventas_pi,cpb_fp=cpb_fp))


@login_required
def CPBVentaDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
    if not puedeEliminarCPB(id):
            messages.error(request, u'¡No puede editar un Comprobante Saldado/Facturado!')
            return redirect(reverse('cpb_venta_listado'))
    cpb.delete()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return redirect('cpb_venta_listado')


#*********************************************************************************
class CPBRemitoDetalleFormSet(BaseInlineFormSet): 
    pass  

CPBRemitoDetalleFS = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBRemitoDetalleForm,formset=CPBRemitoDetalleFormSet, can_delete=True,extra=0,min_num=1) 

class CPBRemitoViewList(VariablesMixin,ListView):    
    model = cpb_comprobante
    template_name = 'ingresos/remitos/cpb_remito_listado.html'
    context_object_name = 'comprobantes'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)
        if not tiene_permiso(self.request,'cpb_remitos'):
            return redirect(reverse('principal'))        
        return super(CPBRemitoViewList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBRemitoViewList, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCpbsCompras(self.request.POST or None,empresa=empresa,request=self.request)   
        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=5,cpb_tipo__compra_venta='V',estado__in=[1,2],pto_vta__in=pto_vta_habilitados_list(self.request),empresa=empresa).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']   
            vendedor = form.cleaned_data['vendedor']                                                 
            estado = form.cleaned_data['estado']

            if int(estado) == 1:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=5,cpb_tipo__compra_venta='V',estado__in=[1,2,3],empresa=empresa).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
            if fdesde:
                comprobantes= comprobantes.filter(Q(fecha_cpb__gte=fdesde))
            if fhasta:
                comprobantes= comprobantes.filter(Q(fecha_cpb__lte=fhasta))  
            if entidad:
                comprobantes= comprobantes.filter(Q(entidad__apellido_y_nombre__icontains=entidad))            
            if pto_vta:
                comprobantes= comprobantes.filter(Q(pto_vta=pto_vta)) 
        else:
            comprobantes= comprobantes.filter(fecha_cpb__gte=inicioMesAnt(),fecha_cpb__lte=finMes())

        context['form'] = form
        context['comprobantes'] = comprobantes
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)
    

@login_required
def CPBRemitoDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_remitos_abm'):
            return redirect(reverse('principal'))
    cpb.delete()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return redirect('cpb_remito_listado')


class CPBRemitoCreateView(VariablesMixin,CreateView):
    form_class = CPBRemitoForm
    template_name = 'ingresos/remitos/cpb_remito_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_remitos_abm'):
            return redirect(reverse('principal'))    
        return super(CPBRemitoCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBRemitoCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBRemitoCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        cpb=self.get_object()        
        form.fields['id_cpb_padre'].initial = cpb.pk
        form.fields['pto_vta'].initial = cpb.pto_vta        
        form.fields['entidad'].initial = cpb.entidad                
        detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)        
        det=[]        
        for c in detalles:            
            det.append({'producto': c.producto,'cantidad':c.cantidad,'detalle':c.detalle})                        
        CPBRemitoDetalleFS = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,fk_name='cpb_comprobante',form=CPBRemitoDetalleForm,formset=CPBRemitoDetalleFormSet, can_delete=True,max_num=len(det),extra=len(det),min_num=len(det))         
        
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))
        remito_detalle = CPBRemitoDetalleFS(initial=det,prefix='formDetalle')
                
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle,cpb=cpb))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)  
        cpb=self.get_object()                               
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))
        remito_detalle = CPBRemitoDetalleFS(self.request.POST,prefix='formDetalle')
        if form.is_valid() and remito_detalle.is_valid():
            return self.form_valid(form, remito_detalle)
        else:
            return self.form_invalid(form, remito_detalle,cpb)


    def form_valid(self, form, remito_detalle):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        tipo=cpb_tipo.objects.get(pk=8)
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        self.object.numero =  self.get_object().numero
        self.object.letra = 'X'
        self.object.pto_vta = self.get_object().pto_vta
        self.object.cpb_tipo=tipo
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.id_cpb_padre=self.get_object() 
        self.object.save()
        remito_detalle.instance = self.object
        remito_detalle.cpb_comprobante = self.object.id        
        remito_detalle.save()        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_remito_listado'))

    def form_invalid(self, form,remito_detalle,cpb):
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle,cpb=cpb))
        
    def get_success_url(self):        
        return reverse('cpb_remito_listado')


class CPBRemitoEditView(VariablesMixin,UpdateView):
    form_class = CPBRemitoForm
    template_name = 'ingresos/remitos/cpb_remito_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'  

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not tiene_permiso(self.request,'cpb_remitos_abm'):
            return redirect(reverse('principal'))     
        return super(CPBRemitoEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CPBRemitoEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class) 
        cpb=self.object.id_cpb_padre       
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))
        remito_detalle = CPBRemitoDetalleFS(instance=self.object,prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle,cpb=cpb))
  
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class) 
        cpb=self.object.id_cpb_padre       
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))
        remito_detalle = CPBRemitoDetalleFS(self.request.POST,instance=self.object,prefix='formDetalle')        
        if form.is_valid() and remito_detalle.is_valid():
            return self.form_valid(form, remito_detalle)
        else:
            return self.form_invalid(form, remito_detalle,cpb)

    def form_invalid(self, form,remito_detalle,cpb):                                                       
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle,cpb=cpb))

    def form_valid(self, form, remito_detalle):
        self.object = form.save(commit=False)        
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        remito_detalle.instance = self.object
        remito_detalle.cpb_comprobante = self.object.id        
        remito_detalle.save()
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_remito_listado'))

    def get_initial(self):    
        initial = super(CPBRemitoEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Remito '+str(self.get_object())      
        initial['request'] = self.request
        return initial      


#*********************************************************************************

class CPBPresupDetalleFormSet(BaseInlineFormSet):
    pass
 
CPBDetallePresupFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBPresupDetalleForm,formset=CPBPresupDetalleFormSet, can_delete=True,extra=0,min_num=1)

CPBDetallePresupLiteFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBPresupLiteDetalleForm,formset=CPBPresupDetalleFormSet, can_delete=True,extra=0,min_num=1)


class CPBPresupViewList(VariablesMixin,ListView):    
    model = cpb_comprobante
    template_name = 'ingresos/presupuesto/cpb_presup_listado.html'
    context_object_name = 'comprobantes'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'cpb_presupuestos'):
            return redirect(reverse('principal'))    
        return super(CPBPresupViewList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBPresupViewList, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCpbsCompras(self.request.POST or None,empresa=empresa,request=self.request)   
        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=6,empresa=empresa,estado__in=[1,2],pto_vta__in=pto_vta_habilitados_list(self.request)).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']   
            vendedor = form.cleaned_data['vendedor']                                                 
            estado = form.cleaned_data['estado']

            if int(estado) == 1:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=6,empresa=empresa,estado__in=[1,2,3]).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
            if fdesde:
                comprobantes= comprobantes.filter(Q(fecha_cpb__gte=fdesde))
            if fhasta:
                comprobantes= comprobantes.filter(Q(fecha_cpb__lte=fhasta))  
            if entidad:
                comprobantes= comprobantes.filter(Q(entidad__apellido_y_nombre__icontains=entidad))
            if vendedor:
                comprobantes= comprobantes.filter(Q(vendedor=vendedor))
            if pto_vta:
                comprobantes= comprobantes.filter(Q(pto_vta=pto_vta)) 
        else:
            comprobantes= comprobantes.filter(fecha_cpb__gte=inicioMesAnt(),fecha_cpb__lte=finMes())

        context['form'] = form
        context['comprobantes'] = comprobantes
        return context
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

@login_required
def CPBPresupDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_presupuestos'):
            return redirect(reverse('principal'))
    cpb.delete()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return redirect('cpb_presup_listado')

class CPBPresupCreateView(VariablesMixin,CreateView):
    form_class = CPBPresupForm
    template_name = 'ingresos/presupuesto/cpb_presup_form.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not tiene_permiso(self.request,'cpb_presup_abm'):
            return redirect(reverse('principal'))     

        if mobile(self.request):
            return redirect(reverse('cpb_presup_lite_nuevo'))     

        return super(CPBPresupCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(CPBPresupCreateView, self).get_initial()                
        initial['tipo_form'] = 'ALTA'
        initial['request'] = self.request        
        return initial   


    def get_form_kwargs(self):
        kwargs = super(CPBPresupCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBDetallePresupFormSet.form = staticmethod(curry(CPBPresupDetalleForm,request=request))
        presup_detalle = CPBDetallePresupFormSet(prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,presup_detalle = presup_detalle))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        CPBDetallePresupFormSet.form = staticmethod(curry(CPBPresupDetalleForm,request=request))
        presup_detalle = CPBDetallePresupFormSet(self.request.POST,prefix='formDetalle')
        if form.is_valid() and presup_detalle.is_valid():
            return self.form_valid(form, presup_detalle)
        else:
            return self.form_invalid(form, presup_detalle)


    def form_valid(self, form, presup_detalle):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado        
        tipo=cpb_tipo.objects.get(pk=11)       
        self.object.cpb_tipo=tipo
        self.object.presup_aprobacion=estado 
        self.object.numero = ultimoNro(11,self.object.pto_vta,self.object.letra)
        self.object.empresa = empresa_actual(self.request)                
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        presup_detalle.instance = self.object
        presup_detalle.cpb_comprobante = self.object.id        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        presup_detalle.save()

        recalcular_saldo_cpb(self.object.pk)              
        return HttpResponseRedirect(reverse('cpb_presup_listado'))

    def form_invalid(self, form,presup_detalle):                                                       
        return self.render_to_response(self.get_context_data(form=form,presup_detalle = presup_detalle))
        
    def get_success_url(self):
        # msj=u"Se há enviado un mail de confirmación. \nPor favor revise su casilla de correo y siga las instrucciones para obtener su contraseña."
        # messages.add_message(self.request, messages.SUCCESS,u'%s' % (msj))   
        return reverse('cpb_presup_listado')

class CPBPresupEditView(VariablesMixin,UpdateView):
    form_class = CPBPresupForm
    template_name = 'ingresos/presupuesto/cpb_presup_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'  

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not tiene_permiso(self.request,'cpb_presup_abm'):
            return redirect(reverse('principal'))             

        return super(CPBPresupEditView, self).dispatch(*args, **kwargs)
        
    def get_form_kwargs(self):
        kwargs = super(CPBPresupEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class) 
        form.fields['entidad'].widget.attrs['disabled'] = True
        form.fields['pto_vta'].widget.attrs['disabled'] = True
        form.fields['letra'].widget.attrs['disabled'] = True        
        CPBDetallePresupFormSet.form = staticmethod(curry(CPBPresupDetalleForm,request=request))
        presup_detalle = CPBDetallePresupFormSet(instance=self.object,prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,presup_detalle = presup_detalle))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBDetallePresupFormSet.form = staticmethod(curry(CPBPresupDetalleForm,request=request))
        presup_detalle = CPBDetallePresupFormSet(self.request.POST,instance=self.object,prefix='formDetalle')
        if form.is_valid() and presup_detalle.is_valid():
            return self.form_valid(form, presup_detalle)
        else:
            return self.form_invalid(form, presup_detalle)

    def form_invalid(self, form,presup_detalle):                                                       
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)    
        form.fields['entidad'].widget.attrs['disabled'] = True
        form.fields['pto_vta'].widget.attrs['disabled'] = True
        form.fields['letra'].widget.attrs['disabled'] = True        
        return self.render_to_response(self.get_context_data(form=form,presup_detalle = presup_detalle))

    def form_valid(self, form, presup_detalle):
        self.object = form.save(commit=False)         
        self.object.estado=self.object.estado   
        self.object.tipo=11
        self.object.fecha_imputacion=self.object.fecha_cpb                       
        self.object.save()
        presup_detalle.instance = self.object
        presup_detalle.cpb_comprobante = self.object.id        
        presup_detalle.save() 
        recalcular_saldo_cpb(self.object.pk)             
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_presup_listado'))

    def get_initial(self):    
        initial = super(CPBPresupEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'
        initial['request'] = self.request
        return initial              
    
class CPBPresupLiteCreateView(VariablesMixin,CreateView):
    form_class = CPBPresupLiteForm
    template_name = 'ingresos/presupuesto/cpb_presup_form_lite.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not tiene_permiso(self.request,'cpb_presup_abm'):
            return redirect(reverse('principal'))     

        if not mobile(self.request):
            return redirect(reverse('cpb_presup_nuevo'))   
        return super(CPBPresupLiteCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(CPBPresupLiteCreateView, self).get_initial()                
        initial['tipo_form'] = 'ALTA'
        initial['request'] = self.request        
        return initial   


    def get_form_kwargs(self):
        kwargs = super(CPBPresupLiteCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBDetallePresupLiteFormSet.form = staticmethod(curry(CPBPresupLiteDetalleForm,request=request))
        presup_detalle = CPBDetallePresupLiteFormSet(prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,presup_detalle = presup_detalle))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        CPBDetallePresupLiteFormSet.form = staticmethod(curry(CPBPresupLiteDetalleForm,request=request))
        presup_detalle = CPBDetallePresupLiteFormSet(self.request.POST,prefix='formDetalle')
        if form.is_valid() and presup_detalle.is_valid():
            return self.form_valid(form, presup_detalle)
        else:
            return self.form_invalid(form, presup_detalle)


    def form_valid(self, form, presup_detalle):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado        
        tipo=cpb_tipo.objects.get(pk=11)       
        self.object.cpb_tipo=tipo
        self.object.presup_aprobacion=estado
        self.object.numero = ultimoNro(11,self.object.pto_vta,self.object.letra)
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        presup_detalle.instance = self.object
        presup_detalle.cpb_comprobante = self.object.id        
        presup_detalle.save()
        recalcular_saldo_cpb(self.object.pk)              
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_presup_listado'))

    def form_invalid(self, form,presup_detalle):                                                       
        return self.render_to_response(self.get_context_data(form=form,presup_detalle = presup_detalle))
        
    def get_success_url(self):
        # msj=u"Se há enviado un mail de confirmación. \nPor favor revise su casilla de correo y siga las instrucciones para obtener su contraseña."
        # messages.add_message(self.request, messages.SUCCESS,u'%s' % (msj))   
        return reverse('cpb_presup_listado')
################################################################

class CPBRecCobranzaViewList(VariablesMixin,ListView):    
    model = cpb_comprobante
    template_name = 'ingresos/cobranzas/cpb_rec_cobranza_listado.html'
    context_object_name = 'comprobantes'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)
        if not tiene_permiso(self.request,'cpb_cobranzas'):
            return redirect(reverse('principal'))            
        return super(CPBRecCobranzaViewList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBRecCobranzaViewList, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCpbs(self.request.POST or None,empresa=empresa,request=self.request)   
        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=4,empresa=empresa,estado__in=[1,2],pto_vta__in=pto_vta_habilitados_list(self.request)).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']   
            vendedor = form.cleaned_data['vendedor']                                                 
            estado = form.cleaned_data['estado']

            if int(estado) == 1:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=4,empresa=empresa,estado__in=[1,2,3]).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
            elif int(estado) == 2:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=4,empresa=empresa,estado__in=[3]).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')                

            if fdesde:
                comprobantes= comprobantes.filter(Q(fecha_cpb__gte=fdesde))
            if fhasta:
                comprobantes= comprobantes.filter(Q(fecha_cpb__lte=fhasta))  
            if entidad:
                comprobantes= comprobantes.filter(Q(entidad__apellido_y_nombre__icontains=entidad))
            if vendedor:
                comprobantes= comprobantes.filter(Q(vendedor=vendedor))
            if pto_vta:
                comprobantes= comprobantes.filter(Q(pto_vta=pto_vta)) 
        else:
            comprobantes= comprobantes.filter(fecha_cpb__gte=inicioMesAnt(),fecha_cpb__lte=finMes())

        context['form'] = form
        context['comprobantes'] = comprobantes
        return context
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

class CPBRecCobranzaFPFormSet(BaseInlineFormSet): 
    pass  
class CPBReciboCPBFormSet(BaseInlineFormSet): 
    pass  

RecCobranzaFPFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_fp,form=CPBRecFPForm,formset=CPBRecCobranzaFPFormSet, can_delete=True,extra=0,min_num=1)
RecCobranzaCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBRecCPBForm,formset=CPBReciboCPBFormSet, can_delete=True,extra=0,min_num=1)
#ReciboRetFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_perc_imp,form=CPBVentaPercImpForm,formset=CPBReciboRetFormSet, can_delete=True,extra=0,min_num=1)  

class CPBRecCobranzaCreateView(VariablesMixin,CreateView):
    form_class = CPBRecCobranzaForm
    template_name = 'ingresos/cobranzas/cpb_rec_cobranza_form.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_cobranzas_abm'):
            return redirect(reverse('principal'))      
        return super(CPBRecCobranzaCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBRecCobranzaCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['request'] = self.request       
        return initial   

    def get_form_kwargs(self,**kwargs):
        kwargs = super(CPBRecCobranzaCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request              
        
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        RecCobranzaFPFormSet.form = staticmethod(curry(CPBRecFPForm,request=request))
        cpb_fp = RecCobranzaFPFormSet(prefix='formFP')        
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        RecCobranzaFPFormSet.form = staticmethod(curry(CPBRecFPForm,request=request))
        cpb_fp = RecCobranzaFPFormSet(self.request.POST,prefix='formFP')
        if form.is_valid() and cpb_fp.is_valid():            
            return self.form_valid(form, cpb_fp)
        else:
            return self.form_invalid(form, cpb_fp)        

    def form_valid(self, form, cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=2)
        self.object.estado=estado   
        self.object.letra='X'        
        self.object.numero = ultimoNro(7,self.object.pto_vta,self.object.letra)
        tipo=cpb_tipo.objects.get(pk=7)
        self.object.cpb_tipo=tipo
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id       
        cpb_fp.save() 
        recalcular_saldo_cpb(self.object.pk)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_rec_cobranza_listado'))

    def form_invalid(self, form,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp))

class CPBRecCobranzaEditView(VariablesMixin,CreateView):
    form_class = CPBRecCobranzaForm
    template_name = 'ingresos/cobranzas/cpb_rec_cobranza_form.html' 
    model = cpb_comprobante   
    pk_url_kwarg = 'id'      
    success_message = "CPB was created successfully"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_cobranzas_abm'):
            return redirect(reverse('principal'))  
        if not puedeEditarCPB(self.get_object().pk):
            messages.error(self.request, u'¡No puede editar un Comprobante Saldado/Facturado!')
            return redirect(reverse('cpb_rec_cobranza_listado'))
        return super(CPBRecCobranzaEditView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBRecCobranzaEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)               
        form.fields['entidad'].widget.attrs['disabled'] = True
        form.fields['pto_vta'].widget.attrs['disabled'] = True                
        RecCobranzaFPFormSet.form = staticmethod(curry(CPBRecFPForm,request=request))
        cpb_fp = RecCobranzaFPFormSet(instance=self.object,prefix='formFP')
        cpbs_cobro=cpb_cobranza.objects.filter(cpb_comprobante=self.object.id)     
        RecCobranzaCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBRecCPBForm,formset=CPBReciboCPBFormSet, can_delete=False,extra=len(cpbs_cobro),max_num=len(cpbs_cobro))
        d=[]
        for cpb in cpbs_cobro:
            c = cpb.cpb_factura
            entidad = c.entidad                                
            d.append({'detalle_cpb': c.get_cpb_tipo(),'desc_rec':'0','importe_total':cpb.importe_total,'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})                    
        cpbs = RecCobranzaCPBFormSet(prefix='formCPB',initial=d)      
        return self.render_to_response(self.get_context_data(form=form,cpb_fp=cpb_fp,cpbs=cpbs))
        
        # if cpbs_cobro:
        #     RecCobranzaCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBRecCPBForm,formset=CPBReciboCPBFormSet, can_delete=False,extra=len(cpbs_cobro),max_num=len(cpbs_cobro))
        #     d=[]
        #     for cpb in cpbs_cobro:
        #         c = cpb.cpb_factura
        #         entidad = c.entidad                                
        #         d.append({'detalle_cpb': c.get_cpb_tipo(),'desc_rec':'0','importe_total':cpb.importe_total,'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})            
        #     cpbs = RecCobranzaCPBFormSet(prefix='formCPB',initial=d)      
        #     return self.render_to_response(self.get_context_data(form=form,cpb_fp=cpb_fp,cpbs=cpbs))
        # else:     
        #     return self.render_to_response(self.get_context_data(form=form,cpb_fp=cpb_fp,cpbs=None))        

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        RecCobranzaFPFormSet.form = staticmethod(curry(CPBRecFPForm,request=request))
        cpb_fp = RecCobranzaFPFormSet(self.request.POST,instance=self.object,prefix='formFP')
        cpbs = RecCobranzaCPBFormSet(self.request.POST,instance=self.object,prefix='formCPB')        
        if form.is_valid() and cpb_fp.is_valid() and cpbs.is_valid():            
            return self.form_valid(form, cpb_fp,cpbs)
        else:
            return self.form_invalid(form, cpb_fp,cpbs)        
       

    def form_valid(self, form, cpb_fp,cpbs):
        self.object = form.save(commit=False)                
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id        

        cpb_fp.save()
        cpbs=cpb_cobranza.objects.filter(cpb_comprobante=self.object.id)
        for c in cpbs:            
            recalcular_saldo_cpb(c.cpb_factura.pk)                    
        recalcular_saldo_cpb(self.object.pk)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_rec_cobranza_listado'))

    def get_form_kwargs(self):
        kwargs = super(CPBRecCobranzaEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form,cpb_fp,cpbs):                                                       
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp,cpbs=cpbs))


@login_required
def CPBRecCobranzaDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_cobranzas_abm'):
            return redirect(reverse('principal'))
    try:                
        fps = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb,mdcp_salida__isnull=False).values_list('mdcp_salida',flat=True)
    
        if (len(fps)>0):
            messages.error(request, u'¡El Comprobante posee movimientos de cobranza/depósito de Cheques asociados!. Verifique')
            return HttpResponseRedirect(cpb.get_listado())    
            
        else:
            #traigo los fps de los recibos asociados        
            pagos = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb).values_list('id',flat=True)
            id_pagos = [int(x) for x in pagos]            
            cpbs = cpb_comprobante_fp.objects.filter(mdcp_salida__in=id_pagos)

            for c in cpbs:
                c.mdcp_salida = None
                c.save()                       
        cpb.delete()
        messages.success(request, u'Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'No se pudo eliminar el Comprobante!')
    
    return redirect('cpb_rec_cobranza_listado')


###############################################################
class CPBCobrarCreateView(VariablesMixin,CreateView):
    form_class = CPBRecCobranzaForm
    template_name = 'ingresos/cobranzas/cpb_rec_cobranza_form.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_cobranzas_abm'):
            return redirect(reverse('principal'))  
        return super(CPBCobrarCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBCobrarCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self,**kwargs):
        kwargs = super(CPBCobrarCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request                      
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        form.fields['entidad'].widget.attrs['disabled'] = True                       
        cpbs_cobro = request.session.get('cpbs_cobranza', None)              
        entidad = None   
        total = Decimal(0.00)     
        if cpbs_cobro:
            cpbs_cobro = json.loads(cpbs_cobro)             
            RecCobranzaCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBRecCPBForm,formset=CPBReciboCPBFormSet,extra=len(cpbs_cobro), can_delete=False,max_num=len(cpbs_cobro))
            d=[]
            for cpb in cpbs_cobro:
                c = cpb_comprobante.objects.get(id=cpb['id_cpb_factura'])
                entidad = c.entidad                
                d.append({'detalle_cpb': c.get_cpb_tipo(),'desc_rec':'0','importe_total':cpb['importe_total'],'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})            
                total += Decimal(cpb['importe_total'])
            cpbs = RecCobranzaCPBFormSet(prefix='formCPB',initial=d)
            if entidad:
                form.fields['entidad'].initial = entidad   

        else:
            RecCobranzaCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBRecCPBForm,formset=CPBReciboCPBFormSet, can_delete=True,extra=0,min_num=1)
            cpbs = RecCobranzaCPBFormSet(prefix='formCPB')

        RecCobranzaFPFormSet.form = staticmethod(curry(CPBRecFPForm,request=request))
        cpb_fp = RecCobranzaFPFormSet(prefix='formFP',initial=[{'importe':total}]) 
        return self.render_to_response(self.get_context_data(form=form,cpb_fp=cpb_fp,cpbs=cpbs))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        RecCobranzaFPFormSet.form = staticmethod(curry(CPBRecFPForm,request=request))
        cpb_fp = RecCobranzaFPFormSet(self.request.POST,prefix='formFP')
        cpbs = RecCobranzaCPBFormSet(self.request.POST,prefix='formCPB')        
                
        if form.is_valid() and cpb_fp.is_valid() and cpbs.is_valid():            
            return self.form_valid(form, cpb_fp,cpbs)
        else:
            return self.form_invalid(form, cpb_fp,cpbs)        

    def form_valid(self, form, cpb_fp,cpbs):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=2)
        self.object.estado=estado   
        self.object.letra='X'        
        self.object.numero =ultimoNro(7,self.object.pto_vta,self.object.letra)
        tipo=cpb_tipo.objects.get(pk=7)
        self.object.cpb_tipo=tipo
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id
        # estado=cpb_estado.objects.get(pk=2)
        # self.object.estado=estado        
        cpbs.instance = self.object        
        c = cpb_comprobante.objects.get(id=self.object.id)
        cpbs.cpb_comprobante = c
        cpbs.desc_rec=0
        cpb_fp.save()
        cpbs.save()
        for c in cpbs:            
            recalcular_saldo_cpb(c.instance.cpb_factura.pk) 
        limpiar_sesion(self.request)
        recalcular_saldo_cpb(self.object.pk)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,cpb_fp,cpbs):                                                       
        cpbs_cobro = self.request.session.get('cpbs_cobranza', None)              
        entidad = None        
        if cpbs_cobro:
            cpbs_cobro = json.loads(cpbs_cobro)             
            RecCobranzaCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBRecCPBForm,formset=CPBReciboCPBFormSet,extra=len(cpbs_cobro), can_delete=False,max_num=len(cpbs_cobro))
            d=[]
            for cpb in cpbs_cobro:
                c = cpb_comprobante.objects.get(id=cpb['id_cpb_factura'])
                entidad = c.entidad                
                d.append({'detalle_cpb': c.get_cpb_tipo(),'desc_rec':'0','importe_total':cpb['importe_total'],'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})            
            cpbs = RecCobranzaCPBFormSet(prefix='formCPB',initial=d)
            if entidad:
                form.fields['entidad'].initial = entidad   
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp,cpbs=cpbs))

@login_required 
def CPBCobrosSeleccionarView(request):        
    limpiar_sesion(request)
    if request.method == 'POST' and request.is_ajax():                               
        CPBSFormSet = formset_factory(CPBSeleccionados,extra=0)        
        comprobantes = CPBSFormSet(request.POST,prefix='comprobantes')         
        if comprobantes.is_valid():                                   
            d=[]
            for c in comprobantes:
                f = c.cleaned_data                  
                d.append({'detalle_cpb':f['detalle_cpb'],'desc_rec':'0','id_cpb_factura':f['id_cpb_factura'],'importe_total':f['importe_total'],'saldo':f['saldo']})                        
            d = json.dumps(d,default=default)
            request.session['cpbs_cobranza'] = d
            response = {'status': 1, 'message': "Ok"} # for ok        
        else:
            response = {'status': 0, 'message': "Verifique que los Totales no superen a los Saldos!"} 
            
        return HttpResponse(json.dumps(response,default=default), content_type='application/json')
    else:
        id_cpbs = request.GET.getlist('id_cpb')        
        cpbs = cpb_comprobante.objects.filter(id__in=id_cpbs).filter(Q(saldo__gt=0,cpb_tipo__id__in=[1,3,5,14]))        
        cant_cpbs = cpbs.count()    
        if cant_cpbs <= 0:
             return HttpResponseRedirect(reverse('cpb_venta_listado'))
        total=0
        d=[]        
        for c in cpbs:            
            saldo = (c.saldo * c.cpb_tipo.signo_ctacte)
            total += saldo
            d.append({'detalle_cpb': c.get_cpb_tipo(),'desc_rec':'0','importe_total':saldo,'saldo':saldo,'id_cpb_factura':c.id})
        CPBSFormSet = formset_factory(CPBSeleccionados, max_num=cant_cpbs,can_delete=False)
        comprobantes = CPBSFormSet(prefix='comprobantes',initial=d)
        variables = RequestContext(request, {'comprobantes':comprobantes,'total':total})        
        return render_to_response("ingresos/ventas/detalle_cpbs.html", variables)

#############################################################
#   LIQ PROD
#############################################################

class CPBLiqProdCreateView(VariablesMixin,CreateView):
    form_class = CPBLiqProdForm
    template_name = 'ingresos/liqprod/cpb_liqprod_form.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
        return super(CPBLiqProdCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBLiqProdCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['titulo'] = 'Nuevo Comprobante'
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBLiqProdCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBLiqProdDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBLiqProdPercImpForm,request=request))        
        liqprod_detalle = CPBDetalleFormSet(prefix='formDetalle')
        liqprod_pi = CPBPIFormSet(prefix='formDetallePI')        
        return self.render_to_response(self.get_context_data(form=form,liqprod_detalle = liqprod_detalle,liqprod_pi=liqprod_pi))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBLiqProdDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBLiqProdPercImpForm,request=request))        
        liqprod_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        liqprod_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')                
        if form.is_valid() and liqprod_detalle.is_valid() and liqprod_pi.is_valid():
            return self.form_valid(form, liqprod_detalle,liqprod_pi)
        else:
            return self.form_invalid(form, liqprod_detalle,liqprod_pi)        

    def form_valid(self, form, liqprod_detalle,liqprod_pi):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.condic_pago = 1
        self.object.save()
        liqprod_detalle.instance = self.object
        liqprod_detalle.cpb_comprobante = self.object.id        
        liqprod_detalle.save()
        if liqprod_pi:
            liqprod_pi.instance = self.object
            liqprod_pi.cpb_comprobante = self.object.id 
            liqprod_pi.save() 
        
        recalcular_saldo_cpb(self.object.pk)             
        messages.success(self.request, u'Los datos se guardaron con éxito!')

        return HttpResponseRedirect(reverse('cpb_venta_listado'))

    def form_invalid(self, form,liqprod_detalle,liqprod_pi):                                                       
        return self.render_to_response(self.get_context_data(form=form,liqprod_detalle = liqprod_detalle,liqprod_pi=liqprod_pi))

class CPBLiqProdEditView(VariablesMixin,SuccessMessageMixin,UpdateView):
    form_class = CPBLiqProdForm
    template_name = 'ingresos/liqprod/cpb_liqprod_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'      
    success_message = "CPB was created successfully"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
        if not puedeEditarCPB(self.get_object().pk):
            messages.error(self.request, u'¡No puede editar un Comprobante con Pagos/Saldado!')
            return redirect(reverse('cpb_ventas_listado'))
        return super(CPBLiqProdEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CPBLiqProdEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
     
    def get_initial(self):    
        initial = super(CPBLiqProdEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Comprobante '+str(self.get_object())
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)      
        form.fields['entidad'].widget.attrs['disabled'] = True       
        form.fields['cpb_tipo'].widget.attrs['disabled'] = True                
        form.fields['cliente_categ_fiscal'].initial = self.object.entidad.fact_categFiscal
        form.fields['cliente_descuento'].initial = self.object.entidad.dcto_general
        CPBDetalleFormSet.form = staticmethod(curry(CPBLiqProdDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBLiqProdPercImpForm,request=request))        
        liqprod_detalle = CPBDetalleFormSet(instance=self.object,prefix='formDetalle')
        liqprod_pi = CPBPIFormSet(instance=self.object,prefix='formDetallePI')        
        return self.render_to_response(self.get_context_data(form=form,liqprod_detalle = liqprod_detalle,liqprod_pi=liqprod_pi))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBDetalleFormSet.form = staticmethod(curry(CPBLiqProdDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBLiqProdPercImpForm,request=request))        
        liqprod_detalle = CPBDetalleFormSet(self.request.POST,instance=self.object,prefix='formDetalle')        
        liqprod_pi = CPBPIFormSet(self.request.POST,instance=self.object,prefix='formDetallePI')        
        if form.is_valid() and liqprod_detalle.is_valid() and liqprod_pi.is_valid():
            return self.form_valid(form, liqprod_detalle,liqprod_pi)
        else:
            return self.form_invalid(form, liqprod_detalle,liqprod_pi) 
     
    def form_invalid(self, form,liqprod_detalle,liqprod_pi):                                                       
        return self.render_to_response(self.get_context_data(form=form,liqprod_detalle = liqprod_detalle,liqprod_pi=liqprod_pi))

    def form_valid(self, form, liqprod_detalle,liqprod_pi):
        self.object = form.save(commit=False)        
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb        
        self.object.save()
        liqprod_detalle.instance = self.object
        liqprod_detalle.cpb_comprobante = self.object.id        
        liqprod_detalle.save()
        if liqprod_pi:
            liqprod_pi.instance = self.object
            liqprod_pi.cpb_comprobante = self.object.id 
            liqprod_pi.save()         
        recalcular_saldo_cpb(self.object.pk) 
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_venta_listado'))


@login_required
def CPBLiqProdDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_ventas_abm'):
            return redirect(reverse('principal'))
    if not puedeEliminarCPB(id):
            messages.error(request, u'¡No puede editar un Comprobante Saldado/Facturado!')
            return redirect(reverse('cpb_venta_listado'))
    cpb.delete()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return redirect('cpb_venta_listado')
