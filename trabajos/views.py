# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import *
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView,DetailView
from django.conf import settings
from django.db.models import Count,Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,redirect
from fm.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
from django.forms.models import inlineformset_factory,BaseInlineFormSet,formset_factory
from django.contrib import messages
import json
import urllib
from .forms import *
from .models import *
from general.utilidades import *
from general.views import VariablesMixin
from general.models import gral_empresa
from usuarios.views import tiene_permiso
from comprobantes.views import ultimoNro
from comprobantes.models import cpb_comprobante,cpb_comprobante_detalle
from django.utils.functional import curry 

def ultimaOrden(tipoCpb):    
    try:    
        tipo=cpb_tipo.objects.get(id=tipoCpb)                
    except:        
        return 0
    return tipo.ultimo_nro
      
class OPView(VariablesMixin,ListView):
    model = orden_pedido
    template_name = 'trabajos/orden_pedido/op_listado.html'
    context_object_name = 'orden_pedido'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        if not tiene_permiso(self.request,'trab_pedidos'):
            return redirect(reverse('principal'))
        return super(OPView, self).dispatch(*args, **kwargs)

    def get_queryset(self):        
        return orden_pedido.objects.filter(empresa=empresa_actual(self.request)).order_by('-fecha','-fecha_creacion').select_related('cliente','estado','vendedor')

    def get_context_data(self, **kwargs):
        context = super(OPView, self).get_context_data(**kwargs)
        return context

class OPDetalleFormSet(BaseInlineFormSet): 
    pass  

OPDetalleFS = inlineformset_factory(orden_pedido, orden_pedido_detalle,form=OPDetalleForm,formset=OPDetalleFormSet, can_delete=True,extra=0,min_num=1)

class OPCreateView(VariablesMixin,CreateView):
    form_class = OPForm
    template_name = 'trabajos/orden_pedido/op_form.html' 
    model = orden_pedido
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'trab_pedidos'):
            return redirect(reverse('principal'))
        return super(OPCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(OPCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['numero'] = '{0:0{width}}'.format((ultimaOrden(15)+1),width=8)
        initial['titulo'] = 'Nuevo Comprobante'
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(OPCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        OPDetalleFS.form = staticmethod(curry(OPDetalleForm,request=request))
        op_detalle = OPDetalleFS(prefix='formDetalle')        
        return self.render_to_response(self.get_context_data(form=form,op_detalle = op_detalle))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        OPDetalleFS.form = staticmethod(curry(OPDetalleForm,request=request))       
        op_detalle = OPDetalleFS(self.request.POST,prefix='formDetalle')
        
        if form.is_valid() and op_detalle.is_valid():
            return self.form_valid(form, op_detalle)
        else:
            return self.form_invalid(form, op_detalle)        

    def form_valid(self, form, op_detalle):
        self.object = form.save(commit=False)        
        # estado=cpb_estado.objects.get(pk=100)
        # self.object.estado=estado   
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        self.object.save()
        op_detalle.instance = self.object
        op_detalle.orden_pedido = self.object.id        
        op_detalle.save()        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('orden_pedido_listado'))

    def form_invalid(self, form,op_detalle):                                                       
        return self.render_to_response(self.get_context_data(form=form,op_detalle = op_detalle))

class OPPresupCreateView(VariablesMixin,CreateView):
    form_class = OPForm
    template_name = 'trabajos/orden_pedido/op_form.html' 
    model = orden_pedido
    pk_url_kwarg = 'id'   

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'trab_pedidos'):
            return redirect(reverse('principal'))
        return super(OPPresupCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(OPPresupCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'                
        initial['numero'] = '{0:0{width}}'.format((ultimaOrden(15)+1),width=8)
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(OPPresupCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()        
        form = self.get_form(form_class)        
        id = self.kwargs['id']       
        id_presupuesto =  cpb_comprobante.objects.get(pk=id)    
        if id_presupuesto:
            form.fields['id_presupuesto'].initial = id_presupuesto.pk
            form.fields['cliente'].initial = id_presupuesto.entidad
            detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante=id_presupuesto)
            det=[]        
            for c in detalles:            
                det.append({'producto': c.producto,'cantidad':c.cantidad,'detalle':c.detalle,'importe_unitario':c.importe_unitario,
                 'importe_total':c.importe_total})                                    
            OPDetalleFS = inlineformset_factory(orden_pedido, orden_pedido_detalle,form=OPDetalleForm,formset=OPDetalleFormSet, can_delete=True,extra=len(det),min_num=1)
        else:
            detalles = None       
        OPDetalleFS.form = staticmethod(curry(OPDetalleForm,request=request))
        op_detalle = OPDetalleFS(prefix='formDetalle',initial=det)           
        return self.render_to_response(self.get_context_data(form=form,op_detalle = op_detalle))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        OPDetalleFS.form = staticmethod(curry(OPDetalleForm,request=request))
        op_detalle = OPDetalleFS(self.request.POST,prefix='formDetalle')        
        if form.is_valid() and op_detalle.is_valid():
            return self.form_valid(form, op_detalle)
        else:
            return self.form_invalid(form,op_detalle)        

    def form_valid(self, form, op_detalle):
        self.object = form.save(commit=False)        
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        self.object.save()
        op_detalle.instance = self.object
        op_detalle.orden_pedido = self.object.id        
        op_detalle.save()                
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('orden_pedido_listado'))

    def form_invalid(self, form,op_detalle):                                                       
        return self.render_to_response(self.get_context_data(form=form,op_detalle = op_detalle))


class OPEditView(VariablesMixin,UpdateView):
    form_class = OPForm
    template_name = 'trabajos/orden_pedido/op_form.html' 
    model = orden_pedido
    pk_url_kwarg = 'id'          

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'trab_pedidos'):
            return redirect(reverse('principal'))
        return super(OPEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(OPEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
     
    def get_initial(self):    
        initial = super(OPEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Orden '+str(self.get_object())        
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)      
        form.condic_pago=1        
        form.fields['cliente'].widget.attrs['disabled'] = True        
        form.fields['numero'].widget.attrs['disabled'] = True                
        OPDetalleFS.form = staticmethod(curry(OPDetalleForm,request=request))
        op_detalle = OPDetalleFS(instance=self.object,prefix='formDetalle')        
        return self.render_to_response(self.get_context_data(form=form,op_detalle = op_detalle))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        OPDetalleFS.form = staticmethod(curry(OPDetalleForm,request=request))
        op_detalle = OPDetalleFS(self.request.POST,instance=self.object,prefix='formDetalle')        
        if form.is_valid() and op_detalle.is_valid():
            return self.form_valid(form, op_detalle)
        else:          
            return self.form_invalid(form, op_detalle)        
     
    def form_invalid(self, form,op_detalle):                                                       
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)      
        form.fields['cliente'].widget.attrs['disabled'] = True        
        form.fields['numero'].widget.attrs['disabled'] = True          
        return self.render_to_response(self.get_context_data(form=form,op_detalle = op_detalle))

    def form_valid(self, form, op_detalle):
        self.object = form.save(commit=False)                        
        self.object.save()
        op_detalle.instance = self.object
        op_detalle.orden_pedido = self.object.id        
        op_detalle.save()
        messages.success(self.request, u'Los datos se guardaron con éxito!')  
        return HttpResponseRedirect(reverse('orden_pedido_listado'))


class OPDeleteView(AjaxDeleteView):
    model = orden_pedido
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'trab_pedidos'):
            return redirect(reverse('principal'))
        return super(OPDeleteView, self).dispatch(*args, **kwargs)

@login_required 
def imprimirNotaPedido(request,id):   
    pedido = orden_pedido.objects.get(id=id)        
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = gral_empresa.objects.get(id=settings.ENTIDAD_ID)        
    except gral_empresa.DoesNotExist:
        config = None        
    detalle_pedido = orden_pedido_detalle.objects.filter(orden_pedido=pedido)
        
    cobranzas = None
    cantidad = 0
    
    
    codigo_letra = None
    
    cantidad = detalle_pedido.count() + cantidad

    context = Context()    
    fecha = datetime.now()    
    # context['detalle_comprobante'] = detalle_comprobante    
    from easy_pdf.rendering import render_to_pdf_response   
    template = 'general/facturas/nota_pedido.html'                        
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirOrdenTrabajo(request,id):   
    trabajo = orden_trabajo.objects.get(id=id)        
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = gral_empresa.objects.get(id=settings.ENTIDAD_ID)        
    except gral_empresa.DoesNotExist:
        config = None        
    detalle_trabajo = orden_trabajo_detalle.objects.filter(orden_trabajo=trabajo)
    pedido = trabajo.orden_pedido    
    cobranzas = None
    cantidad = 0
    
    
    codigo_letra = None
    
    cantidad = detalle_trabajo.count()

    context = Context()    
    fecha = datetime.now()    
    # context['detalle_comprobante'] = detalle_comprobante    
    from easy_pdf.rendering import render_to_pdf_response   
    template = 'general/facturas/orden_trabajo.html'                        
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirOrdenColocacion(request,id):   
    pedido = orden_pedido.objects.get(id=id)        
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = gral_empresa.objects.get(id=settings.ENTIDAD_ID)        
    except gral_empresa.DoesNotExist:
        config = None        
    detalle_pedido = orden_pedido_detalle.objects.filter(orden_pedido=pedido)
        
    cobranzas = None
    cantidad = 0
    
    
    codigo_letra = None
    
    cantidad = detalle_pedido.count() + cantidad

    context = Context()    
    fecha = datetime.now()    
    # context['detalle_comprobante'] = detalle_comprobante    
    from easy_pdf.rendering import render_to_pdf_response   
    template = 'general/facturas/nota_pedido.html'                        
    return render_to_pdf_response(request, template, locals())


class OPEstadoEditView(VariablesMixin,AjaxUpdateView):
    form_class = OPEstadoForm
    model = orden_pedido
    pk_url_kwarg = 'id'
    template_name = 'fm/trabajos/formEstadoOP.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'trab_pedidos'):
            return redirect(reverse('principal'))
        return super(OPEstadoEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        self.object = form.save(commit=False) 
        estado = self.object.estado
        
        if estado is None:
            self.object.fecha_pendiente=None
            self.object.fecha_proceso=None
            self.object.fecha_terminado=None
        elif estado.pk == 102:
            self.object.fecha_proceso=datetime.now()
        elif estado.pk == 103:
            self.object.fecha_terminado=datetime.now()
        elif estado.pk == 104:
            self.object.fecha_entregado=datetime.now()
        elif estado.pk == 100:
            self.object.fecha_pendiente=datetime.now()


        # estado=cpb_estado.objects.get(pk=100)
        # self.object.estado=estado       
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(OPEstadoEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(OPEstadoEditView, self).get_initial()                      
        return initial 


class OPVerView(VariablesMixin,DetailView):
    model = orden_pedido
    pk_url_kwarg = 'id'
    context_object_name = 'pedido'
    template_name = 'general/facturas/detalle_op.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(OPVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(OPVerView, self).get_context_data(**kwargs)
        try:
            config = gral_empresa.objects.get(id=settings.ENTIDAD_ID)        
        except gral_empresa.DoesNotExist:
            config = None        
        op = self.object
        context['config'] = config
        detalle_pedido = orden_pedido_detalle.objects.filter(orden_pedido=op)       
        context['detalle_pedido'] = detalle_pedido       
        return context



# ***********************************************************************        

class OTDetalleFormSet(BaseInlineFormSet): 
    pass  

OTDetalleFS = inlineformset_factory(orden_trabajo, orden_trabajo_detalle,form=OTDetalleForm,formset=OTDetalleFormSet, can_delete=True,extra=0,min_num=1)

class OTView(VariablesMixin,ListView):
    model = orden_trabajo
    template_name = 'trabajos/orden_trabajo/ot_listado.html'
    context_object_name = 'orden_trabajo'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        if not tiene_permiso(self.request,'trab_trabajos'):
            return redirect(reverse('principal'))
        return super(OTView, self).dispatch(*args, **kwargs)

    def get_queryset(self):        
        return orden_trabajo.objects.filter(empresa=empresa_actual(self.request)).order_by('-fecha','-fecha_creacion').select_related('orden_pedido','responsable','estado')

    def get_context_data(self, **kwargs):
        context = super(OTView, self).get_context_data(**kwargs)
        return context


class OTCreateView(VariablesMixin,CreateView):
    form_class = OTForm
    template_name = 'trabajos/orden_trabajo/ot_form.html' 
    model = orden_trabajo
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'trab_trabajos'):
            return redirect(reverse('principal'))
        return super(OTCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(OTCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        return initial   

    def get_form_kwargs(self):
        kwargs = super(OTCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # cpb=self.get_object() 
        id = self.kwargs['id']       
        op = orden_pedido.objects.get(id=id)    
        pedido = op
        pedido_detalles = orden_pedido_detalle.objects.filter(orden_pedido=op)   
        form.fields['orden_pedido'].initial = op.pk        
        form.fields['numero'].initial = op.numero  
        OTDetalleFS.form = staticmethod(curry(OTDetalleForm,request=request))
        ot_detalle = OTDetalleFS(prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,ot_detalle = ot_detalle,pedido=pedido,pedido_detalles=pedido_detalles))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)                               
        OTDetalleFS.form = staticmethod(curry(OTDetalleForm,request=request))
        ot_detalle = OTDetalleFS(request.POST,prefix='formDetalle')
        if form.is_valid() and ot_detalle.is_valid():
            return self.form_valid(form, ot_detalle)
        else:
            return self.form_invalid(form, ot_detalle)


    def form_valid(self, form, ot_detalle):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=100)
        self.object.estado=estado           
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        id = self.kwargs['id']       
        op = orden_pedido.objects.get(id=id)            
        estado_op=cpb_estado.objects.get(pk=103)
        op.estado = estado_op
        op.fecha_terminado=datetime.now()
        op.save() 
        self.object.orden_pedido=op
        self.object.save()
        ot_detalle.instance = self.object
        ot_detalle.orden_trabajo = self.object.id        
        ot_detalle.save() 
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        #Pongo la OP en Produccion 

        return HttpResponseRedirect(reverse('orden_trabajo_listado'))

    def form_invalid(self, form,ot_detalle):                                                       
        id = self.kwargs['id']       
        op = orden_pedido.objects.get(id=id)    
        pedido = op
        pedido_detalles = orden_pedido_detalle.objects.filter(orden_pedido=op)   
        form.fields['orden_pedido'].initial = op.pk        
        form.fields['numero'].initial = op.numero  
        OTDetalleFS.form = staticmethod(curry(OTDetalleForm,request=self.request))
        ot_detalle = OTDetalleFS(self.request.POST,prefix='formDetalle')
        return self.render_to_response(self.get_context_data(form=form,ot_detalle = ot_detalle,pedido=pedido,pedido_detalles=pedido_detalles))
        
    def get_success_url(self):        
        return reverse('orden_trabajo_listado')

class OTEditView(VariablesMixin,UpdateView):
    form_class = OTForm
    template_name = 'trabajos/orden_trabajo/ot_form.html' 
    model = orden_trabajo
    pk_url_kwarg = 'id'          

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'trab_trabajos'):
            return redirect(reverse('principal'))
        return super(OTEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(OTEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
     
    def get_initial(self):    
        initial = super(OTEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Orden '+str(self.get_object())        
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)      
        cpb=self.get_object() 
       
        pedido = cpb.orden_pedido
        pedido_detalles = orden_pedido_detalle.objects.filter(orden_pedido=pedido)   
        form.fields['orden_pedido'].initial = pedido.pk                        
        form.fields['numero'].widget.attrs['disabled'] = True                
        OTDetalleFS.form = staticmethod(curry(OTDetalleForm,request=request))
        ot_detalle = OTDetalleFS(instance=self.object,prefix='formDetalle')        

        pedido = cpb.orden_pedido
        pedido_detalles = orden_pedido_detalle.objects.filter(orden_pedido=pedido)   
        form.fields['orden_pedido'].initial = pedido.pk        

        return self.render_to_response(self.get_context_data(form=form,ot_detalle = ot_detalle,pedido=pedido,pedido_detalles=pedido_detalles))


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        cpb=self.get_object()        
        pedido = cpb.orden_pedido
        pedido_detalles = orden_pedido_detalle.objects.filter(orden_pedido=pedido)   
        OTDetalleFS.form = staticmethod(curry(OTDetalleForm,request=request))
        ot_detalle = OTDetalleFS(request.POST,instance=self.object,prefix='formDetalle')  
        if form.is_valid() and ot_detalle.is_valid():
            return self.form_valid(form, ot_detalle,pedido=pedido,pedido_detalles=pedido_detalles)
        else:          
            return self.form_invalid(form, ot_detalle,pedido=pedido,pedido_detalles=pedido_detalles)        
     
    def form_invalid(self, form,ot_detalle,pedido,pedido_detalles):                                                       
        self.object = self.get_object()
        form_class = self.get_form_class()        
        form = self.get_form(form_class)      
        form.fields['numero'].widget.attrs['disabled'] = True
        OTDetalleFS.form = staticmethod(curry(OTDetalleForm,request=self.request))
        ot_detalle = OTDetalleFS(self.request.POST,prefix='formDetalle')          
        return self.render_to_response(self.get_context_data(form=form,ot_detalle = ot_detalle,pedido=pedido,pedido_detalles=pedido_detalles))

    def form_valid(self, form, ot_detalle,pedido,pedido_detalles):
        self.object = form.save(commit=False)                        
        self.object.orden_pedido = pedido
        self.object.save()
        ot_detalle.instance = self.object
        ot_detalle.orden_trabajo = self.object.id        
        ot_detalle.save()  
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('orden_trabajo_listado'))

class OTDeleteView(VariablesMixin,AjaxDeleteView):
    model = orden_trabajo
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'trab_trabajos'):
            return redirect(reverse('principal'))
        return super(OTDeleteView, self).dispatch(*args, **kwargs)

class OTVerView(VariablesMixin,DetailView):
    model = orden_trabajo
    pk_url_kwarg = 'id'
    context_object_name = 'trabajo'
    template_name = 'general/facturas/detalle_ot.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(OTVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(OTVerView, self).get_context_data(**kwargs)
        try:
            config = gral_empresa.objects.get(id=settings.ENTIDAD_ID)        
        except gral_empresa.DoesNotExist:
            config = None        
        op = self.object
        context['config'] = config
        detalle_trabajo = orden_trabajo_detalle.objects.filter(orden_trabajo=op)       
        context['detalle'] = detalle_trabajo       
        return context


class OTEstadoEditView(VariablesMixin,AjaxUpdateView):
    form_class = OPEstadoForm
    model = orden_trabajo
    pk_url_kwarg = 'id'
    template_name = 'fm/trabajos/formEstadoOP.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'trab_trabajos'):
            return redirect(reverse('principal'))
        return super(OTEstadoEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        self.object = form.save(commit=False) 
        estado = self.object.estado        
        if estado is None:
            self.object.fecha_terminado=None
        elif estado.pk == 103:
            self.object.fecha_terminado=datetime.now()                    
        else:
            self.object.fecha_terminado=None 
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(OTEstadoEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(OTEstadoEditView, self).get_initial()                      
        return initial 
# ***********************************************************************        

class OCView(VariablesMixin,ListView):
    model = orden_colocacion
    template_name = 'trabajos/orden_colocacion/oc_listado.html'
    context_object_name = 'orden_colocacion'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        if not tiene_permiso(self.request,'trab_colocacion'):
            return redirect(reverse('principal'))
        return super(OCView, self).dispatch(*args, **kwargs)

    def get_queryset(self):        
        return orden_colocacion.objects.filter(empresa=empresa_actual(self.request)).order_by('-fecha_colocacion','-fecha_creacion').select_related('orden_trabajo','vendedor','colocador','estado')

    def get_context_data(self, **kwargs):
        context = super(OCView, self).get_context_data(**kwargs)
        return context


class OCCreateView(VariablesMixin,CreateView):
    form_class = OCForm
    template_name = 'trabajos/orden_colocacion/oc_form.html' 
    model = orden_colocacion
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'trab_colocacion'):
            return redirect(reverse('principal'))
        return super(OCCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(OCCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        return initial   

    def get_form_kwargs(self):
        kwargs = super(OCCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        id = self.kwargs['id']       
        ot = orden_trabajo.objects.get(id=id)    
        trabajo = ot  
        pedido = ot.orden_pedido
        pedido_detalles = orden_pedido_detalle.objects.filter(orden_pedido=pedido)   
        trabajo_detalles = orden_trabajo_detalle.objects.filter(orden_trabajo=trabajo)   
        form.fields['orden_trabajo'].initial = trabajo.pk        
        form.fields['numero'].initial = trabajo.numero          
        return self.render_to_response(self.get_context_data(form=form,trabajo=trabajo,pedido_detalles=pedido_detalles,trabajo_detalles=trabajo_detalles))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)                                       
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=100)
        self.object.estado=estado           
        self.object.empresa = empresa_actual(self.request)        
        self.object.usuario = usuario_actual(self.request)
        id = self.kwargs['id']       
        ot = orden_trabajo.objects.get(id=id)            
        estado_ot=cpb_estado.objects.get(pk=103)
        ot.estado = estado_ot
        ot.save() 
        self.object.orden_trabajo=ot        
        self.object.save()       
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('orden_colocacion_listado'))

    def form_invalid(self, form,ot_detalle):                                                       
        id = self.kwargs['id']       
        ot = orden_trabajo.objects.get(id=id)    
        trabajo = ot
        pedido = ot.orden_pedido
        pedido_detalles = orden_pedido_detalle.objects.filter(orden_pedido=pedido)   
        trabajo_detalles = orden_trabajo_detalle.objects.filter(orden_trabajo=trabajo)  
        form.fields['orden_pedido'].initial = trabajo.pk        
        form.fields['numero'].initial = trabajo.numero          
        return self.render_to_response(self.get_context_data(form=form,trabajo=trabajo,pedido_detalles=pedido_detalles,trabajo_detalles=trabajo_detalles))
        
    def get_success_url(self):        
        return reverse('orden_colocacion_listado')

class OCEditView(VariablesMixin,UpdateView):
    form_class = OCForm
    template_name = 'trabajos/orden_colocacion/oc_form.html' 
    model = orden_colocacion
    pk_url_kwarg = 'id'     

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'trab_colocacion'):
            return redirect(reverse('principal'))
        return super(OCEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(OCEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
     
    def get_initial(self):    
        initial = super(OCEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['titulo'] = 'Editar Orden '+str(self.get_object())        
        initial['request'] = self.request
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        orden = self.get_object()        
        ot = orden.orden_trabajo
        trabajo = ot
        trabajo_detalles = orden_trabajo_detalle.objects.filter(orden_trabajo=trabajo)   
        form.fields['orden_trabajo'].initial = trabajo.pk        
        form.fields['numero'].widget.attrs['disabled'] = True                
        return self.render_to_response(self.get_context_data(form=form,trabajo=trabajo,trabajo_detalles=trabajo_detalles))
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)        
        orden = self.get_object()        
        ot = orden.orden_trabajo
        trabajo = ot
        trabajo_detalles = orden_trabajo_detalle.objects.filter(orden_trabajo=trabajo)              
        if form.is_valid():
            return self.form_valid(form,trabajo=trabajo,trabajo_detalles=trabajo_detalles)
        else:          
            return self.form_invalid(form,trabajo=trabajo,trabajo_detalles=trabajo_detalles)        
     
    def form_invalid(self, form,trabajo,trabajo_detalles):                                                       
        self.object = self.get_object()
        form_class = self.get_form_class()        
        form = self.get_form(form_class)      
        form.fields['numero'].widget.attrs['disabled'] = True          
        return self.render_to_response(self.get_context_data(form,trabajo=trabajo,trabajo_detalles=trabajo_detalles))

    def form_valid(self, form,trabajo,trabajo_detalles):
        self.object = form.save(commit=False)                        
        self.object.orden_trabajo = trabajo
        self.object.save()        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('orden_colocacion_listado'))

class OCDeleteView(VariablesMixin,AjaxDeleteView):
    model = orden_colocacion
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'trab_colocacion'):
            return redirect(reverse('principal'))
        return super(OCDeleteView, self).dispatch(*args, **kwargs)

class OCVerView(VariablesMixin,DetailView):
    model = orden_colocacion
    pk_url_kwarg = 'id'
    context_object_name = 'colocacion'
    template_name = 'general/facturas/detalle_oc.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(OCVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(OCVerView, self).get_context_data(**kwargs)
        try:
            config = gral_empresa.objects.get(id=settings.ENTIDAD_ID)        
        except gral_empresa.DoesNotExist:
            config = None        
        trabajo = self.object.orden_trabajo
        context['config'] = config
        trabajo = orden_trabajo.objects.get(pk=trabajo.pk)       
        context['trabajo'] = trabajo       
        op_detalle = orden_pedido_detalle.objects.filter(orden_pedido=trabajo.orden_pedido)       
        context['orden_pedido_detalle'] = op_detalle  
        return context        

class OCEstadoEditView(VariablesMixin,AjaxUpdateView):
    form_class = OPEstadoForm
    model = orden_colocacion
    pk_url_kwarg = 'id'
    template_name = 'fm/trabajos/formEstadoOP.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'trab_colocacion'):
            return redirect(reverse('principal'))
        return super(OCEstadoEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        self.object = form.save(commit=False) 
        estado = self.object.estado        
        if estado is None:
            self.object.fecha_colocado=None
        elif estado.pk == 104:
            self.object.fecha_colocado=datetime.now()                    
        else:
            self.object.fecha_colocado=None 
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(OCEstadoEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(OCEstadoEditView, self).get_initial()                      
        return initial         