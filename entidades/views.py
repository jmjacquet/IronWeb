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
from general.views import VariablesMixin,ultimoNroId,getVariablesMixin
from usuarios.views import tiene_permiso
from general.utilidades import *
from modal.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
# from modal.views import Detailview
from .forms import EntidadesForm,EntidadesEditForm,VendedoresForm,ImportarEntidadesForm
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
    template_name = 'modal/entidades/form.html'

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
    template_name = 'modal/entidades/form.html'

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


@login_required
def ClientesDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_cuenta, id=id)
        if not tiene_permiso(request,'ent_clientes_abm'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('clientes_listado')     

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
    template_name = 'modal/entidades/form.html'

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
    template_name = 'modal/entidades/form.html'

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

@login_required
def ProveedoresDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_cuenta, id=id)
        if not tiene_permiso(request,'ent_proveedores_abm'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('proveedores_listado')   

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
    template_name = 'modal/entidades/form_vendedores.html'

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
    template_name = 'modal/entidades/form_vendedores.html'

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

@login_required
def VendedoresDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_cuenta, id=id)
        if not tiene_permiso(request,'ent_vendedores_abm'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('vendedores_listado') 

class VendedoresVerView(VariablesMixin,DetailView):
    model = egr_entidad
    pk_url_kwarg = 'id'
    context_object_name = 'entidad'
    template_name = 'entidades/detalle.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(VendedoresVerView, self).dispatch(*args, **kwargs)


############# IMPORTADOR CLIENTES / PROV ######################
import csv, io
import random
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

@login_required 
def importar_entidades(request):               
    context = {}
    context = getVariablesMixin(request) 
    if request.method == 'POST':
        form = ImportarEntidadesForm(request.POST,request.FILES,request=request)
        if form.is_valid(): 
            csv_file = form.cleaned_data['archivo']
            sobreescribir = form.cleaned_data['sobreescribir'] == 'S'
            empresa = form.cleaned_data['empresa']
            tipo_entidad = form.cleaned_data['tipo_entidad']            
            if not csv_file.name.endswith('.csv'):
                messages.error(request,'¡El archivo debe tener extensión .CSV!')
                return HttpResponseRedirect(reverse("importar_empleados"))
            
            if csv_file.multiple_chunks():
                messages.error(request,"El archivo es demasiado grande (%.2f MB)." % (csv_file.size/(1000*1000),))
                return HttpResponseRedirect(reverse("importar_empleados"))

            decoded_file = csv_file.read().decode("latin1").replace(",", "").replace("'", "")
            io_string = io.StringIO(decoded_file)
            reader = unicode_csv_reader(io_string)                
            #Id;Cliente;Email;Tel;Tel2;Direcci¢n;DNI;CUIT;Condici¢n de IVA;Raz¢n Social;Domicilio Fiscal;Localidad Fiscal;Provincia Fiscal;C¢digo Postal Fiscal;Usuario de Mercado Libre;Observaciones;Creado
            #Id;Proveedor;Email;Tel;Tel2;Direcci¢n;DNI;CUIT;Condici¢n de IVA;Raz¢n Social;Domicilio Fiscal;Localidad Fiscal;Provincia Fiscal;C¢digo Postal Fiscal;Observaciones;Creado;NombreProv
            cant=0
            next(reader) #Omito el Encabezado                            
            for index,line in enumerate(reader):                      
                campos = line[0].split(";")               
                
                cod = campos[0].strip().zfill(4)
                print cod
                if cod=='':
                    continue #Salta al siguiente                    
                
                empl = egr_entidad.objects.filter(codigo=cod,tipo_entidad=tipo_entidad).exists()
                if empl and not sobreescribir:
                    continue

                nombre = campos[9].strip().upper()
                email =   campos[2].strip()  #EMAIL
                telefono =   campos[3].strip()  #telefono
                telefono2 =   campos[4].strip()  #telefono2
                domicilio = campos[5].strip().upper()  #DOMICILIO
                dni = campos[6].strip().upper()  #DOMICILIO
                cuit = campos[7].strip().upper().replace("-", "").replace(".", "") #ART  

                cond_iva = campos[8].strip()
                if cond_iva=='Consumidor Final':
                    cond_iva=5
                elif cond_iva=='Responsable Inscripto':
                    cond_iva=1
                elif cond_iva=='Exento':
                    cond_iva=4
                else:
                    cond_iva=5

                tipo_doc = 99
                if cuit<>'':
                    tipo_doc = 80

                fact_razon_social = campos[9].strip().upper()
                fact_direccion = campos[10].strip().upper()
                localidad = campos[11].strip().upper()                    
                cp =   campos[12].strip()  #CP
                
                egr_entidad.objects.update_or_create(codigo=cod,tipo_entidad=tipo_entidad,empresa=empresa,defaults={'apellido_y_nombre':nombre,'fact_razon_social':fact_razon_social,'fact_direccion':fact_direccion,
                    'fact_telefono':telefono2,'tipo_doc':tipo_doc,'fact_cuit':cuit,'domicilio':domicilio,'nro_doc':dni,'telefono':telefono,'email':email,'cod_postal':cp,'localidad':localidad,'fact_categFiscal':cond_iva})                                                                 
                cant+=1                       
            messages.success(request, u'Se importó el archivo con éxito!<br>(%s Clientes creados/actualizados)'% cant )
            
    else:
        form = ImportarEntidadesForm(None,None,request=request)
    context['form'] = form    
    return render(request, 'entidades/importar_entidades.html',context)            