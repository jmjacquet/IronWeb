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
from comprobantes.views import puedeEditarCPB,puedeEliminarCPB,ultimoNro,buscarDatosProd
from general.forms import ConsultaCpbs,ConsultaCpbsCompras,pto_vta_habilitados_list
from django.utils.functional import curry 


class CPBCompraViewList(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'egresos/compras/cpb_compra_listado.html'
    context_object_name = 'comprobantes'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'cpb_compras'):
            return redirect(reverse('principal'))
        return super(CPBCompraViewList, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBCompraViewList, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCpbsCompras(self.request.POST or None)   
        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[1,2,3,9],estado__in=[1,2],cpb_tipo__compra_venta='C',empresa=empresa).order_by('-fecha_cpb','-id','-fecha_creacion').select_related('estado','cpb_tipo','entidad','vendedor')
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']   
            estado = form.cleaned_data['estado']
            letra = form.cleaned_data['letra']

            if int(estado) == 1:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[1,2,3,9],estado__in=[1,2,3],cpb_tipo__compra_venta='C',empresa=empresa).order_by('-fecha_cpb','-id','-fecha_creacion').select_related('estado','cpb_tipo','entidad','vendedor')
            elif int(estado) == 2:
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[1,2,3,9],estado__in=[3],cpb_tipo__compra_venta='C',empresa=empresa).order_by('-fecha_cpb','-id','-fecha_creacion').select_related('estado','cpb_tipo','entidad','vendedor')            
            if fdesde:
                comprobantes= comprobantes.filter(fecha_cpb__gte=fdesde)
            if fhasta:
                comprobantes= comprobantes.filter(fecha_cpb__lte=fhasta)
            
            if entidad:
                comprobantes= comprobantes.filter(entidad__apellido_y_nombre__icontains=entidad)

            if pto_vta:
                comprobantes= comprobantes.filter(pto_vta=pto_vta)
            if letra:
                comprobantes= comprobantes.filter(letra=letra) 
        else:
            comprobantes= comprobantes.filter(fecha_cpb__gte=inicioMesAnt(),fecha_cpb__lte=finMes())

        context['form'] = form
        context['comprobantes'] = comprobantes
        return context
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class CPBCompraDetalleFormSet(BaseInlineFormSet): 
    pass  
class CPBCompraPIFormSet(BaseInlineFormSet): 
    pass  
class CPBCompraFPFormSet(BaseInlineFormSet): 
    pass 
  

CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBCompraDetalleForm,formset=CPBCompraDetalleFormSet, can_delete=True,extra=0,min_num=1)
CPBPIFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_perc_imp,form=CPBCompraPercImpForm,formset=CPBCompraPIFormSet, can_delete=True,extra=0,min_num=1)  
CPBFPFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_fp,form=CPBFPForm,formset=CPBCompraFPFormSet, can_delete=True,extra=0,min_num=1)

class CPBCompraCreateView(VariablesMixin,CreateView):
    form_class = CPBCompraForm
    template_name = 'egresos/compras/cpb_compra_form.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_compras_abm'):
            return redirect(reverse('principal'))
        return super(CPBCompraCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBCompraCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['titulo'] = 'Nuevo Comprobante'
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBCompraCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBCompraDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBCompraPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        compras_detalle = CPBDetalleFormSet(prefix='formDetalle')
        compras_pi = CPBPIFormSet(prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,compras_detalle = compras_detalle,compras_pi=compras_pi,cpb_fp=cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBCompraDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBCompraPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        compras_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        compras_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and compras_detalle.is_valid() and compras_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, compras_detalle,compras_pi,cpb_fp)
        else:
            return self.form_invalid(form, compras_detalle,compras_pi,cpb_fp)        

    def form_valid(self, form, compras_detalle,compras_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        compras_detalle.instance = self.object
        compras_detalle.cpb_comprobante = self.object.id        
        compras_detalle.save()
        if compras_pi:
            compras_pi.instance = self.object
            compras_pi.cpb_comprobante = self.object.id 
            compras_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=12)
            nro = ultimoNro(12,self.object.pto_vta,"X",self.object.entidad)
            op = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",
                numero=nro,fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,
                importe_total=self.object.importe_total,estado=estado,usuario=self.object.usuario,empresa = self.object.empresa)
            op.save()
            cobranza = cpb_cobranza(cpb_comprobante=op,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = op
            cpb_fp.cpb_comprobante = op.id 
            
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)             
        messages.success(self.request, u'Los datos se guardaron con éxito!')

        return HttpResponseRedirect(reverse('cpb_compra_listado'))

    def form_invalid(self, form,compras_detalle,compras_pi,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,compras_detalle = compras_detalle,compras_pi=compras_pi,cpb_fp=cpb_fp))

class CPBCompraEditView(VariablesMixin,SuccessMessageMixin,UpdateView):
    form_class = CPBCompraForm
    template_name = 'egresos/compras/cpb_compra_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'      
    success_message = "CPB was created successfully"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_compras_abm'):
            return redirect(reverse('principal'))
        if not puedeEditarCPB(self.get_object().pk):
            messages.error(self.request, u'¡No puede editar un Comprobante con Pagos/Saldado!')
            return redirect(reverse('cpb_compra_listado'))
        return super(CPBCompraEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CPBCompraEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
     
    def get_initial(self):    
        initial = super(CPBCompraEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Comprobante '+str(self.get_object())
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)      
        #Si se edita queda en cuenta corriente
        form.condic_pago=1
        form.fields['condic_pago'].widget.attrs['disabled'] = True
        form.fields['entidad'].widget.attrs['disabled'] = True       
        form.fields['cpb_tipo'].widget.attrs['disabled'] = True
        importes=cobros_cpb(self.object.id)        
        form.fields['importe_cobrado'].initial = importes
        form.fields['cliente_categ_fiscal'].initial = self.object.entidad.fact_categFiscal
        form.fields['cliente_descuento'].initial = self.object.entidad.dcto_general
        CPBDetalleFormSet.form = staticmethod(curry(CPBCompraDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBCompraPercImpForm,request=request))        
        compras_detalle = CPBDetalleFormSet(instance=self.object,prefix='formDetalle')
        compras_pi = CPBPIFormSet(instance=self.object,prefix='formDetallePI')        
        return self.render_to_response(self.get_context_data(form=form,compras_detalle = compras_detalle,compras_pi=compras_pi))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBDetalleFormSet.form = staticmethod(curry(CPBCompraDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBCompraPercImpForm,request=request))        
        compras_detalle = CPBDetalleFormSet(self.request.POST,instance=self.object,prefix='formDetalle')        
        compras_pi = CPBPIFormSet(self.request.POST,instance=self.object,prefix='formDetallePI')        
        if form.is_valid() and compras_detalle.is_valid() and compras_pi.is_valid():
            return self.form_valid(form, compras_detalle,compras_pi)
        else:
            return self.form_invalid(form, compras_detalle,compras_pi) 
     
    def form_invalid(self, form,compras_detalle,compras_pi):                                                       
        return self.render_to_response(self.get_context_data(form=form,compras_detalle = compras_detalle,compras_pi=compras_pi))

    def form_valid(self, form, compras_detalle,compras_pi):
        self.object = form.save(commit=False)        
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        compras_detalle.instance = self.object
        compras_detalle.cpb_comprobante = self.object.id        
        compras_detalle.save()
        if compras_pi:
            compras_pi.instance = self.object
            compras_pi.cpb_comprobante = self.object.id 
            compras_pi.save()         
        recalcular_saldo_cpb(self.object.pk) 
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_compra_listado'))

class CPBCompraClonarCreateView(VariablesMixin,CreateView):
    form_class = CPBCompraForm
    template_name = 'egresos/compras/cpb_compra_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_compras_abm'):
            return redirect(reverse('principal'))
        return super(CPBCompraClonarCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(CPBCompraClonarCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['titulo'] = 'Nuevo Comprobante Compras - Clonar CPB: %s' % self.get_object()
        initial['request'] = self.request        
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBCompraClonarCreateView, self).get_form_kwargs()
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
            CPBDetalleFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBCompraDetalleForm,fk_name='cpb_comprobante',formset=CPBCompraDetalleFormSet, can_delete=True,extra=0,min_num=len(det))
        else:
            detalles = None       
        # ventas_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        # ventas_pi = CPBPIFormSet(prefix='formDetallePI')
        # cpb_fp = CPBFPFormSet(prefix='formFP')
        CPBDetalleFormSet.form = staticmethod(curry(CPBCompraDetalleForm,request=request))
        compras_detalle = CPBDetalleFormSet(prefix='formDetalle',initial=det)
        CPBPIFormSet.form = staticmethod(curry(CPBCompraPercImpForm,request=request))
        compras_pi = CPBPIFormSet(prefix='formDetallePI')
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        cpb_fp = CPBFPFormSet(prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,compras_detalle = compras_detalle,compras_pi=compras_pi,cpb_fp=cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBDetalleFormSet.form = staticmethod(curry(CPBCompraDetalleForm,request=request))
        CPBPIFormSet.form = staticmethod(curry(CPBCompraPercImpForm,request=request))
        CPBFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        compras_detalle = CPBDetalleFormSet(self.request.POST,prefix='formDetalle')
        compras_pi = CPBPIFormSet(self.request.POST,prefix='formDetallePI')
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        condic_pago = int(self.request.POST.get('condic_pago'))
        if form.is_valid() and compras_detalle.is_valid() and compras_pi.is_valid() and (cpb_fp.is_valid()or(condic_pago==1)):
            return self.form_valid(form, compras_detalle,compras_pi,cpb_fp)
        else:
            return self.form_invalid(form, compras_detalle,compras_pi,cpb_fp)        

    def form_valid(self, form, compras_detalle,compras_pi,cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        compras_detalle.instance = self.object
        compras_detalle.cpb_comprobante = self.object.id        
        compras_detalle.save()
        if compras_pi:
            compras_pi.instance = self.object
            compras_pi.cpb_comprobante = self.object.id 
            compras_pi.save() 
        
        if cpb_fp and (self.object.condic_pago>1):
            estado=cpb_estado.objects.get(pk=2)
            tipo_cpb=cpb_tipo.objects.get(pk=12)
            nro = ultimoNro(12,self.object.pto_vta,"X",self.object.entidad)
            op = cpb_comprobante(cpb_tipo=tipo_cpb,entidad=self.object.entidad,pto_vta=self.object.pto_vta,letra="X",
                numero=nro,fecha_cpb=self.object.fecha_cpb,importe_iva=self.object.importe_iva,
                importe_total=self.object.importe_total,estado=estado,empresa = empresa_actual(self.request))
            op.save()
            cobranza = cpb_cobranza(cpb_comprobante=op,cpb_factura=self.object,importe_total=self.object.importe_total,desc_rec=0)
            cobranza.save()
            cpb_fp.instance = op
            cpb_fp.cpb_comprobante = op.id             
            self.object.estado=estado
            cpb_fp.save() 
            self.object.save()

        recalcular_saldo_cpb(self.object.pk)        
        messages.success(self.request, u'Los datos se guardaron con éxito!')

        return HttpResponseRedirect(reverse('cpb_compra_listado'))

    def form_invalid(self, form,compras_detalle,compras_pi,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,compras_detalle = compras_detalle,compras_pi=compras_pi,cpb_fp=cpb_fp))



@login_required
def CPBCompraDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_compras_abm'):
            return redirect(reverse('principal'))
    if not puedeEliminarCPB(id):
            messages.error(request, u'¡No puede editar un Comprobante con Pagos/Saldado!')
            return redirect(reverse('cpb_compra_listado'))
    cpb.delete()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return redirect('cpb_compra_listado')


#*********************************************************************************

class CPBPagosViewList(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'egresos/ordenpago/cpb_rec_pago_listado.html'
    context_object_name = 'comprobantes'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'cpb_pagos'):
            return redirect(reverse('principal'))
        return super(CPBPagosViewList, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBPagosViewList, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCpbsCompras(self.request.POST or None,empresa=empresa,request=self.request)   
        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=7,empresa=empresa,estado__in=[1,2]).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']   
            estado = form.cleaned_data['estado']

            if int(estado) == 1:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=7,empresa=empresa,estado__in=[1,2,3]).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')
            elif int(estado) == 2:   
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=7,empresa=empresa,estado__in=[3]).order_by('-fecha_cpb','-id').select_related('estado','cpb_tipo','entidad')

            if fdesde:
                comprobantes= comprobantes.filter(Q(fecha_cpb__gte=fdesde))
            if fhasta:
                comprobantes= comprobantes.filter(Q(fecha_cpb__lte=fhasta))              

            if entidad:
                comprobantes= comprobantes.filter(entidad__apellido_y_nombre__icontains=entidad)            

            if pto_vta:
                comprobantes= comprobantes.filter(Q(pto_vta=pto_vta)) 
        else:
            comprobantes= comprobantes.filter(fecha_cpb__gte=inicioMesAnt(),fecha_cpb__lte=finMes())


        context['form'] = form
        context['comprobantes'] = comprobantes
        return context
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

class CPBPagosRetFormSet(BaseInlineFormSet): 
    pass
class CPBPagosFPFormSet(BaseInlineFormSet): 
    pass  
class CPBPagosCPBFormSet(BaseInlineFormSet): 
    pass  

PagosFPFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_fp,form=CPBFPForm,formset=CPBPagosFPFormSet, can_delete=True,extra=0,min_num=1)
PagosCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBPagoCPBForm,formset=CPBPagosCPBFormSet, can_delete=True,extra=0,min_num=1)
PagosRetFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_retenciones,form=CPBPagoRetForm,formset=CPBPagosRetFormSet, can_delete=True,extra=0,min_num=1)  


class CPBPagoCreateView(VariablesMixin,CreateView):
    form_class = CPBPagoForm
    template_name = 'egresos/ordenpago/cpb_rec_pago_form.html' 
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_pagos_abm'):
            return redirect(reverse('principal'))
        return super(CPBPagoCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBPagoCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self,**kwargs):
        kwargs = super(CPBPagoCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request                      
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        PagosFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        PagosRetFormSet.form = staticmethod(curry(CPBPagoRetForm,request=request))
        cpb_fp = PagosFPFormSet(prefix='formFP')        
        cpb_ret = PagosRetFormSet(prefix='formRet')        
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp,cpb_ret=cpb_ret))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        PagosFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        PagosRetFormSet.form = staticmethod(curry(CPBPagoRetForm,request=request))
        cpb_fp = PagosFPFormSet(self.request.POST,prefix='formFP')
        cpb_ret = PagosRetFormSet(self.request.POST,prefix='formRet')
        if form.is_valid() and cpb_fp.is_valid() and cpb_ret.is_valid():            
            return self.form_valid(form, cpb_fp,cpb_ret)
        else:
            return self.form_invalid(form, cpb_fp,cpb_ret)        

    def form_valid(self, form, cpb_fp, cpb_ret):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=2)
        self.object.estado=estado   
        self.object.letra='X'
        self.object.numero = ultimoNro(12,self.object.pto_vta,self.object.letra,self.object.entidad)
        tipo=cpb_tipo.objects.get(pk=12)
        self.object.cpb_tipo=tipo
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id
        cpb_fp.save()
        if cpb_ret:
            cpb_ret.instance = self.object
            cpb_ret.cpb_comprobante = self.object.id 
            cpb_ret.save() 
        for f in cpb_fp:
            datos = f.cleaned_data
            id= datos.get('origen')               
            if id:                
                cheque= cpb_comprobante_fp.objects.get(id=id)
                cpb=cpb_comprobante_fp.objects.get(id=f.instance.pk)
                cheque.mdcp_salida = cpb                
                cheque.save()                 
        recalcular_saldo_cpb(self.object.pk)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_pago_listado'))

    def form_invalid(self, form,cpb_fp,cpb_ret):                                                       
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp, cpb_ret=cpb_ret))

class CPBPagoEditView(VariablesMixin,CreateView):
    form_class = CPBPagoForm
    template_name = 'egresos/ordenpago/cpb_rec_pago_form.html' 
    model = cpb_comprobante   
    pk_url_kwarg = 'id'      
    success_message = "CPB was created successfully"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_pagos_abm'):
            return redirect(reverse('principal'))
        if not puedeEditarCPB(self.get_object().pk):
            messages.error(self.request, u'¡No puede editar un Comprobante asociado!')
            return redirect(reverse('cpb_pago_listado'))
        return super(CPBPagoEditView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBPagoEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)               
        form.fields['entidad'].widget.attrs['disabled'] = True
        form.fields['pto_vta'].widget.attrs['disabled'] = True                
        PagosFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        PagosRetFormSet.form = staticmethod(curry(CPBPagoRetForm,request=request))
        cpb_fp = PagosFPFormSet(instance=self.object,prefix='formFP')
        cpb_ret = PagosRetFormSet(instance=self.object,prefix='formRet')        
        cpbs_pagos=cpb_cobranza.objects.filter(cpb_comprobante=self.object.id,cpb_comprobante__estado__pk__lt=3)     
        
        PagosCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBPagoCPBForm,formset=CPBPagosCPBFormSet,extra=len(cpbs_pagos), can_delete=False,max_num=len(cpbs_pagos))
        d=[]
        for cpb in cpbs_pagos:
            c = cpb.cpb_factura
            entidad = c.entidad                                
            d.append({'detalle_cpb': c.get_cpb_tipo,'desc_rec':'0','importe_total':cpb.importe_total,'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})            
        cpbs = PagosCPBFormSet(prefix='formCPB',initial=d)                      
        return self.render_to_response(self.get_context_data(form=form,cpb_fp=cpb_fp,cpbs=cpbs,cpb_ret=cpb_ret))
        # if cpbs_pagos:
        #     PagosCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBPagoCPBForm,formset=CPBPagosCPBFormSet,extra=len(cpbs_pagos), can_delete=False,max_num=len(cpbs_pagos))
        #     d=[]
        #     for cpb in cpbs_pagos:
        #         c = cpb.cpb_factura
        #         entidad = c.entidad                                
        #         d.append({'detalle_cpb': c.get_cpb_tipo,'desc_rec':'0','importe_total':cpb.importe_total,'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})            
        #     cpbs = PagosCPBFormSet(prefix='formCPB',initial=d)                      
        #     return self.render_to_response(self.get_context_data(form=form,cpb_fp=cpb_fp,cpbs=cpbs))

        # return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        PagosFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        PagosRetFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        cpb_fp = PagosFPFormSet(self.request.POST,instance=self.object,prefix='formFP')
        cpb_ret = PagosRetFormSet(self.request.POST,instance=self.object,prefix='formRet')        
        cpbs = PagosCPBFormSet(self.request.POST,instance=self.object,prefix='formCPB')      
        if form.is_valid() and cpb_fp.is_valid() and cpb_ret.is_valid() and cpbs.is_valid():
            return self.form_valid(form, cpb_fp,cpbs,cpb_ret)
        else:
            return self.form_invalid(form, cpb_fp,cpbs,cpb_ret)        

    def form_valid(self, form, cpb_fp,cpbs,cpb_ret):
        self.object = form.save(commit=False)        
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id                
        cpb_fp.save()
        if cpb_ret:
            cpb_ret.instance = self.object
            cpb_ret.cpb_comprobante = self.object.id 
            cpb_ret.save() 
        for fp in cpb_fp:
            if fp.cleaned_data.get("origen"):
                origen = fp.cleaned_data.get("origen")
                c = cpb_comprobante_fp.objects.get(id=origen)
                c.mdcp_salida = fp.instance
                c.save()
        cpbs=cpb_cobranza.objects.filter(cpb_comprobante=self.object.id)
        for c in cpbs:            
            recalcular_saldo_cpb(c.cpb_factura.pk)               
        recalcular_saldo_cpb(self.object.pk)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_pago_listado'))

    def get_form_kwargs(self):
        kwargs = super(CPBPagoEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form,cpb_fp,cpbs,cpb_ret):                                                       
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp,cpbs=cpbs,cpb_ret=cpb_ret))
     
@login_required
def CPBPagoDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_pagos_abm'):
            return redirect(reverse('principal'))
    
    try:                
        fps = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb,mdcp_salida__isnull=False).values_list('mdcp_salida',flat=True)
    
        if (len(fps)>0):
            messages.error(request, u'¡El Comprobante posee movimientos de cobranza/depósito de Cheques asociados!. Verifique')
            return HttpResponseRedirect(cpb.get_listado())    

        # if (cpb.tiene_cobranzasREC_OP()):
        #     messages.error(request, u'¡El Comprobante posee movimientos de cobro/pago asociados!.Verifique')
        #     return HttpResponseRedirect(cpb.get_listado())
            
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

    return redirect('cpb_pago_listado')
  
###############################################################
class CPBPagarCreateView(VariablesMixin,CreateView):
    form_class = CPBPagoForm
    template_name = 'egresos/ordenpago/cpb_rec_pago_form.html'
    model = cpb_comprobante
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_compras_pagar'):
            return redirect(reverse('principal'))
        return super(CPBPagarCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBPagarCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self,**kwargs):
        kwargs = super(CPBPagarCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request                      
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        form.fields['entidad'].widget.attrs['disabled'] = True
        cpbs_pagos = request.session.get('cpbs_pagos', None)      
        entidad = None        
        total = Decimal(0.00)
        if cpbs_pagos:
            cpbs_pagos = json.loads(cpbs_pagos)                   
            PagosCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBPagoCPBForm,formset=CPBPagosCPBFormSet,extra=len(cpbs_pagos), can_delete=False,max_num=len(cpbs_pagos))
            d=[]
            for cpb in cpbs_pagos:
                c = cpb_comprobante.objects.get(id=cpb['id_cpb_factura'])
                entidad = c.entidad                                
                d.append({'detalle_cpb': c.get_cpb_tipo,'desc_rec':'0','importe_total':cpb['importe_total'],'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})            
                total += Decimal(cpb['importe_total'])
            cpbs = PagosCPBFormSet(prefix='formCPB',initial=d)
            if entidad:
                form.fields['entidad'].initial = entidad   

        else:
            PagosCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBPagoCPBForm,formset=CPBPagosCPBFormSet, can_delete=True,extra=0,min_num=1)
            cpbs = PagosCPBFormSet(prefix='formCPB')
        PagosFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        PagosRetFormSet.form = staticmethod(curry(CPBPagoRetForm,request=request))
        cpb_fp = PagosFPFormSet(prefix='formFP',initial=[{'importe':total}])        
        cpb_ret = PagosRetFormSet(prefix='formRet')        
        return self.render_to_response(self.get_context_data(form=form,cpb_fp=cpb_fp,cpbs=cpbs,cpb_ret=cpb_ret))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        PagosFPFormSet.form = staticmethod(curry(CPBFPForm,request=request))
        PagosRetFormSet.form = staticmethod(curry(CPBPagoRetForm,request=request))
        cpb_fp = PagosFPFormSet(self.request.POST,prefix='formFP')
        cpbs = PagosCPBFormSet(self.request.POST,prefix='formCPB')        
        cpb_ret = PagosRetFormSet(self.request.POST,prefix='formRet')        

        if form.is_valid() and cpb_fp.is_valid() and cpbs.is_valid()and cpb_ret.is_valid():            
            return self.form_valid(form, cpb_fp,cpbs,cpb_ret)
        else:
            return self.form_invalid(form, cpb_fp,cpbs, cpb_ret)        

    def form_valid(self, form, cpb_fp,cpbs,cpb_ret):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=2)
        self.object.estado=estado   
        self.object.letra='X'
        self.object.numero = ultimoNro(12,self.object.pto_vta,self.object.letra,self.object.entidad)
        tipo=cpb_tipo.objects.get(pk=12)
        self.object.cpb_tipo=tipo
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id
        cpb_fp.save()
        if cpb_ret:
            cpb_ret.instance = self.object
            cpb_ret.cpb_comprobante = self.object.id 
            cpb_ret.save()
        for fp in cpb_fp:
            if fp.cleaned_data['origen']:
                origen = fp.cleaned_data['origen']
                c = cpb_comprobante_fp.objects.get(id=origen)                
                c.mdcp_salida = fp.instance
                c.save()
        # estado=cpb_estado.objects.get(pk=2)
        # self.object.estado=estado        
        cpbs.instance = self.object
        c = cpb_comprobante.objects.get(id=self.object.id)
        cpbs.cpb_comprobante = c
        cpbs.desc_rec=0

        cpbs.save()
        for c in cpbs:            
            recalcular_saldo_cpb(c.instance.cpb_factura.pk) 
        limpiar_sesion(self.request)
        recalcular_saldo_cpb(self.object.pk)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_compra_listado'))

    def form_invalid(self, form,cpb_fp,cpbs,cpb_ret):                                                       
        cpbs_pagos = self.request.session.get('cpbs_pagos', None)      
        entidad = None                
        if cpbs_pagos:
            cpbs_pagos = json.loads(cpbs_pagos)                   
            PagosCPBFormSet = inlineformset_factory(cpb_comprobante, cpb_cobranza, fk_name='cpb_comprobante',form=CPBPagoCPBForm,formset=CPBPagosCPBFormSet,extra=len(cpbs_pagos), can_delete=False,max_num=len(cpbs_pagos))
            d=[]
            for cpb in cpbs_pagos:
                c = cpb_comprobante.objects.get(id=cpb['id_cpb_factura'])
                entidad = c.entidad                                
                d.append({'detalle_cpb': c.get_cpb_tipo,'desc_rec':'0','importe_total':cpb['importe_total'],'saldo':c.saldo,'id_cpb_factura':c.id,'cpb_factura':c})            
            cpbs = PagosCPBFormSet(prefix='formCPB',initial=d)
            if entidad:
                form.fields['entidad'].initial = entidad   
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp,cpbs=cpbs,cpb_ret=cpb_ret))

@login_required 
def CPBPagosSeleccionarView(request):        
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
            request.session['cpbs_pagos'] = d
            response = {'status': 1, 'message': "Ok"} # for ok        
        else:
            response = {'status': 0, 'message': "Verifique que los Totales no superen a los Saldos!"} 
            
        return HttpResponse(json.dumps(response,default=default), content_type='application/json')
    else:
        id_cpbs = request.GET.getlist('id_cpb')        
        cpbs = cpb_comprobante.objects.filter(id__in=id_cpbs).filter(Q(saldo__gt=0,cpb_tipo__id__in=[2,4,6,18]))    
        cant_cpbs = cpbs.count()        
        if cant_cpbs <= 0:
             return HttpResponseRedirect(reverse('cpb_venta_listado'))
        total=0
        d=[]        
        for c in cpbs:
            saldo = (c.saldo * c.cpb_tipo.signo_ctacte)
            total += saldo
            d.append({'detalle_cpb': c.get_cpb_tipo,'desc_rec':'0','importe_total':saldo,'saldo':saldo,'id_cpb_factura':c.id})
        CPBSFormSet = formset_factory(CPBSeleccionados, max_num=cant_cpbs,can_delete=False)        
        comprobantes = CPBSFormSet(prefix='comprobantes',initial=d)
        variables = RequestContext(request, {'comprobantes':comprobantes,'total':total})        
        return render_to_response("egresos/compras/detalle_cpbs.html", variables)

################################################################

               
#*********************************************************************************

class CPBRemitoDetalleFormSet(BaseInlineFormSet): 
    pass  

CPBRemitoDetalleFS = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,form=CPBRemitoDetalleForm,formset=CPBRemitoDetalleFormSet, can_delete=True,extra=0,min_num=1) 

class CPBRemitoCViewList(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'egresos/remitos/cpb_remito_listado.html'
    context_object_name = 'comprobantes'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'cpb_remitos'):
            return redirect(reverse('principal'))
        return super(CPBRemitoCViewList, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBRemitoCViewList, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCpbsCompras(self.request.POST or None,empresa=empresa,request=self.request)   
        comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=5,cpb_tipo__compra_venta='C',estado__in=[1,2],empresa=empresa).order_by('-fecha_cpb','-id').select_related('pto_vta','estado','cpb_tipo','entidad')
        if form.is_valid():                                
            entidad = form.cleaned_data['entidad']                                                              
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                 
            pto_vta = form.cleaned_data['pto_vta']   
            vendedor = form.cleaned_data['vendedor']                                                 
            estado = form.cleaned_data['estado']

            if int(estado) == 1:                
                comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=5,cpb_tipo__compra_venta='C',estado__in=[1,2,3],empresa=empresa).order_by('-fecha_cpb','-id').select_related('pto_vta','estado','cpb_tipo','entidad')

            if fdesde:
                comprobantes= comprobantes.filter(Q(fecha_cpb__gte=fdesde))
            if fhasta:
                comprobantes= comprobantes.filter(Q(fecha_cpb__lte=fhasta))  
            if entidad:
                comprobantes= comprobantes.filter(entidad__apellido_y_nombre__icontains=entidad)
                     
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
def CPBRemitoCDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_remitos'):
            return redirect(reverse('principal'))
    cpb.delete()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return redirect('cpb_remitoc_listado')

class CPBRemitoCCreateView(VariablesMixin,CreateView):
    form_class = CPBRemitoForm
    template_name = 'egresos/remitos/cpb_remito_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_remitos'):
            return redirect(reverse('principal'))
        return super(CPBRemitoCCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(CPBRemitoCCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(CPBRemitoCCreateView, self).get_form_kwargs()
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
        
        CPBRemitoDetalleFS = inlineformset_factory(cpb_comprobante, cpb_comprobante_detalle,fk_name='cpb_comprobante',form=CPBRemitoDetalleForm,formset=CPBRemitoDetalleFormSet, can_delete=True,extra=len(det),max_num=len(det),min_num=1)         
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))        
        remito_detalle = CPBRemitoDetalleFS(initial=det,prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)                               
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))        
        remito_detalle = CPBRemitoDetalleFS(self.request.POST,prefix='formDetalle')
        if form.is_valid() and remito_detalle.is_valid():
            return self.form_valid(form, remito_detalle)
        else:
            return self.form_invalid(form, remito_detalle)


    def form_valid(self, form, remito_detalle):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=1)
        self.object.estado=estado   
        tipo=cpb_tipo.objects.get(pk=9)
        self.object.empresa = empresa_actual(self.request)
        self.object.numero = ultimoNro(9,self.object.pto_vta,self.object.letra,self.object.entidad)
        self.object.usuario = usuario_actual(self.request)
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.cpb_tipo=tipo
        self.object.save()
        remito_detalle.instance = self.object
        remito_detalle.cpb_comprobante = self.object.id        
        remito_detalle.save() 
        messages.success(self.request, u'Los datos se guardaron con éxito!')       
        return HttpResponseRedirect(reverse('cpb_remitoc_listado'))

    def form_invalid(self, form,remito_detalle):                                                       
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle))
        
    def get_success_url(self):        
        return reverse('cpb_remitoc_listado')


class CPBRemitoCEditView(VariablesMixin,UpdateView):
    form_class = CPBRemitoForm
    template_name = 'egresos/remitos/cpb_remito_form.html' 
    model = cpb_comprobante
    pk_url_kwarg = 'id'  

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'cpb_remitos'):
            return redirect(reverse('principal'))
        return super(CPBRemitoCEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CPBRemitoEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))        
        remito_detalle = CPBRemitoDetalleFS(instance=self.object,prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        CPBRemitoDetalleFS.form = staticmethod(curry(CPBRemitoDetalleForm,request=request))        
        remito_detalle = CPBRemitoDetalleFS(self.request.POST,instance=self.object,prefix='formDetalle')        
        if form.is_valid() and remito_detalle.is_valid():
            return self.form_valid(form, remito_detalle)
        else:
            return self.form_invalid(form, remito_detalle)

    def form_invalid(self, form,remito_detalle):                                                       
        return self.render_to_response(self.get_context_data(form=form,remito_detalle = remito_detalle))

    def form_valid(self, form, remito_detalle):
        self.object = form.save(commit=False)        
        self.object.fecha_imputacion=self.object.fecha_cpb
        if not self.object.fecha_vto:
            self.object.fecha_vto=self.object.fecha_cpb
        self.object.save()
        remito_detalle.instance = self.object
        remito_detalle.cpb_comprobante = self.object.id        
        remito_detalle.save()
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('cpb_remitoc_listado'))

    def get_initial(self):    
        initial = super(CPBRemitoEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Remito '+str(self.get_object())   
        initial['request'] = self.request   
        return initial      

