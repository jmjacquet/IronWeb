# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import *
from .models import *
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView,DetailView
from django.conf import settings
from django.db.models import Count,Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,redirect
from django.contrib import messages
from general.views import VariablesMixin,ultimoNroId
from usuarios.views import tiene_permiso
from general.utilidades import *
from fm.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
# from modal.views import Detailview
from .forms import EntidadesForm,EntidadesEditForm,VendedoresForm
from django.http import JsonResponse

import json


class EntidadVerView(VariablesMixin,DetailView):
    model = egr_entidad
    pk_url_kwarg = 'id'
    context_object_name = 'entidad'
    template_name = 'entidades/detalle.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(EntidadVerView, self).dispatch(*args, **kwargs)
#************* CLIENTES **************
class ClientesView(VariablesMixin,ListView):
    model = egr_entidad
    template_name = 'entidades/lista_clientes.html'
    context_object_name = 'clientes'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_clientes'):
            return redirect(reverse('principal'))
        return super(ClientesView, self).dispatch(*args, **kwargs)

    def get_queryset(self):        
        entidades = egr_entidad.objects.filter(tipo_entidad=1,empresa=empresa_actual(self.request))
        usuario = usuario_actual(self.request)
        if habilitado_contador(usuario.tipoUsr):
            entidades = egr_entidad.objects.filter(tipo_entidad=1,empresa__id__in=empresas_habilitadas(self.request))
        return entidades


class ClientesCreateView(VariablesMixin,AjaxCreateView):
    form_class = EntidadesForm
    template_name = 'fm/entidades/form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_clientes_abm'):
            return redirect(reverse('principal'))
        return super(ClientesCreateView, self).dispatch(*args, **kwargs)
        
    def form_valid(self, form):                
        #form.instance.empresa = empresa_actual(self.request)
        form.instance.usuario = usuario_actual(self.request)
        if form.instance.fact_razon_social =='':
            form.instance.fact_razon_social = form.instance.apellido_y_nombre
        if form.instance.fact_cuit =='':
            form.fact_cuit = form.instance.nro_doc
        if form.instance.fact_direccion =='':
            form.instance.fact_direccion = form.instance.domicilio
        if form.instance.fact_telefono =='':
            form.instance.fact_telefono = form.instance.telefono
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(ClientesCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(ClientesCreateView, self).get_initial()                
        initial['codigo'] = '{0:0{width}}'.format((ultimoNroId(egr_entidad)+1),width=4)
        initial['tipo_entidad'] = 1
        initial['empresa'] = empresa_actual(self.request)
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(ClientesCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs  

    def form_invalid(self, form):                 
        return super(ClientesCreateView, self).form_invalid(form)

class ClientesEditView(VariablesMixin,AjaxUpdateView):
    form_class = EntidadesEditForm
    model = egr_entidad
    pk_url_kwarg = 'id'
    template_name = 'fm/entidades/form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_clientes_abm'):
            return redirect(reverse('principal'))
        return super(ClientesEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(ClientesEditView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ClientesEditView, self).form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(ClientesEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs  

    def get_initial(self):    
        initial = super(ClientesEditView, self).get_initial()                      
        return initial    

class ClientesDeleteView(VariablesMixin,AjaxDeleteView):
    model = egr_entidad
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_clientes_abm'):
            return redirect(reverse('principal'))
        messages.success(self.request, u'Los datos se eliminaron con éxito!')
        return super(ClientesDeleteView, self).dispatch(*args, **kwargs)

class ClientesVerView(VariablesMixin,DetailView):
    model = egr_entidad
    pk_url_kwarg = 'id'
    context_object_name = 'entidad'
    template_name = 'entidades/detalle.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(ClientesVerView, self).dispatch(*args, **kwargs)




#************* PROVEEDORES **************
class ProveedoresView(VariablesMixin,ListView):
    model = egr_entidad
    template_name = 'entidades/lista_proveedores.html'
    context_object_name = 'proveedores'    

    def get_queryset(self):        
        entidades = egr_entidad.objects.filter(tipo_entidad=2,empresa=empresa_actual(self.request))
        usuario = usuario_actual(self.request)
        if habilitado_contador(usuario.tipoUsr):
            entidades = egr_entidad.objects.filter(tipo_entidad=2,empresa__id__in=empresas_habilitadas(self.request))
        return entidades

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_proveedores'):
            return redirect(reverse('principal'))
        return super(ProveedoresView, self).dispatch(*args, **kwargs)

class ProveedoresCreateView(VariablesMixin,AjaxCreateView):
    form_class = EntidadesForm
    template_name = 'fm/entidades/form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_proveedores_abm'):
            return redirect(reverse('principal'))
        return super(ProveedoresCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                
        form.instance.empresa = empresa_actual(self.request)
        form.instance.usuario = usuario_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(ProveedoresCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(ProveedoresCreateView, self).get_initial()               
        initial['codigo'] = '{0:0{width}}'.format((ultimoNroId(egr_entidad)+1),width=4)
        initial['tipo_entidad'] = 2
        initial['empresa'] = empresa_actual(self.request)
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(ProveedoresCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs  

    def form_invalid(self, form):         
        return super(ProveedoresCreateView, self).form_invalid(form)

class ProveedoresEditView(VariablesMixin,AjaxUpdateView):
    form_class = EntidadesEditForm
    model = egr_entidad
    pk_url_kwarg = 'id'
    template_name = 'fm/entidades/form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_proveedores_abm'):
            return redirect(reverse('principal'))
        return super(ProveedoresEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(ProveedoresEditView, self).form_valid(form)

    def form_invalid(self, form):         
        return super(ProveedoresEditView, self).form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(ProveedoresEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs  

class ProveedoresDeleteView(VariablesMixin,AjaxDeleteView):
    model = egr_entidad
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_proveedores_abm'):
            return redirect(reverse('principal'))
        messages.success(self.request, u'Los datos se eliminaron con éxito!')
        return super(ProveedoresDeleteView, self).dispatch(*args, **kwargs)

class ProveedoresVerView(VariablesMixin,DetailView):
    model = egr_entidad
    pk_url_kwarg = 'id'
    context_object_name = 'entidad'
    template_name = 'entidades/detalle.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(ProveedoresVerView, self).dispatch(*args, **kwargs)


#************* VENDEDORES **************
class VendedoresView(VariablesMixin,ListView):
    model = egr_entidad
    template_name = 'entidades/lista_vendedores.html'
    context_object_name = 'vendedores'    

    def get_queryset(self):        
        entidades = egr_entidad.objects.filter(tipo_entidad=3,empresa=empresa_actual(self.request))
        usuario = usuario_actual(self.request)
        if habilitado_contador(usuario.tipoUsr):
            entidades = egr_entidad.objects.filter(tipo_entidad=3,empresa__id__in=empresas_habilitadas(self.request))
        return entidades

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_vendedores'):
            return redirect(reverse('principal'))
        return super(VendedoresView, self).dispatch(*args, **kwargs)

class VendedoresCreateView(VariablesMixin,AjaxCreateView):
    form_class = VendedoresForm
    template_name = 'fm/entidades/form_vendedores.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_vendedores_abm'):
            return redirect(reverse('principal'))
        return super(VendedoresCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                
        #form.instance.empresa = empresa_actual(self.request)
        form.instance.usuario = usuario_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(VendedoresCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(VendedoresCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs  

    def get_initial(self):    
        initial = super(VendedoresCreateView, self).get_initial()               
        initial['codigo'] = '{0:0{width}}'.format((ultimoNroId(egr_entidad)+1),width=4)
        initial['tipo_entidad'] = 3
        initial['empresa'] = empresa_actual(self.request)
        initial['request'] = self.request        
        return initial    

class VendedoresEditView(VariablesMixin,AjaxUpdateView):
    form_class = VendedoresForm
    model = egr_entidad
    pk_url_kwarg = 'id'
    template_name = 'fm/entidades/form_vendedores.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_vendedores_abm'):
            return redirect(reverse('principal'))
        return super(VendedoresEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(VendedoresEditView, self).form_valid(form)


    def get_initial(self):    
        initial = super(VendedoresEditView, self).get_initial()                      
        return initial    

    def get_form_kwargs(self):
        kwargs = super(VendedoresEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class VendedoresDeleteView(VariablesMixin,AjaxDeleteView):
    model = egr_entidad
    pk_url_kwarg = 'id'       

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'ent_vendedores_abm'):
            return redirect(reverse('principal'))
        messages.success(self.request, u'Los datos se eliminaron con éxito!')
        return super(VendedoresDeleteView, self).dispatch(*args, **kwargs)

class VendedoresVerView(VariablesMixin,DetailView):
    model = egr_entidad
    pk_url_kwarg = 'id'
    context_object_name = 'entidad'
    template_name = 'entidades/detalle.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(VendedoresVerView, self).dispatch(*args, **kwargs)