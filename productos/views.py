# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import *
from .models import *
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView,DetailView
from django.conf import settings
from django.db.models import Count,Sum,F
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,redirect
from django.contrib import messages
from general.views import VariablesMixin,ultimoNroId
from fm.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
from .forms import *
from django.forms.models import inlineformset_factory,BaseInlineFormSet,formset_factory
from django.utils.functional import curry 
from usuarios.views import tiene_permiso
from django.utils.functional import curry 
from django.db.models.expressions import RawSQL
from comprobantes.models import actualizar_stock_multiple,actualizar_stock
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def coeficiente_iva(request):
    id = request.GET['id']
    if not id:
        coef = {'tiva':0}
    else:
        try:
            tiva = gral_tipo_iva.objects.get(pk=id) 
            coef = {'tiva':tiva.coeficiente}
        except:
            coef = {'tiva':0}
    return HttpResponse( json.dumps(coef,cls=DjangoJSONEncoder), content_type='application/json' ) 

#************* PRODUCTOS **************
class ProductosView(VariablesMixin,ListView):
    model = prod_productos
    template_name = 'productos/lista_productos.html'
    context_object_name = 'productos'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'prod_productos'):
            return redirect(reverse('principal'))
        return super(ProductosView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductosView, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaProds(self.request.POST or None)   
        productos = prod_productos.objects.filter(empresa__id__in=empresas_habilitadas(self.request),baja=False).select_related('categoria','tasa_iva')
        if form.is_valid():                                
            nombre = form.cleaned_data['nombre']                                                              
            estado = form.cleaned_data['estado']

            if int(estado) == 1:                
                productos = prod_productos.objects.all().select_related('categoria','tasa_iva')
            if nombre:
                productos= productos.filter(Q(nombre__icontains=nombre))
            
        context['form'] = form
        context['productos'] = productos
        return context
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class PSFormSet(BaseInlineFormSet): 
    pass

class PPFormSet(BaseInlineFormSet): 
    pass


prod_precios_FormSet = inlineformset_factory(prod_productos, prod_producto_lprecios,form=Producto_ListaPreciosForm,formset=PPFormSet, can_delete=True,extra=0,min_num=1)  

class ProductosCreateView(VariablesMixin,CreateView):
    form_class = ProductosForm
    template_name = 'productos/producto_form.html' 
    model = prod_productos
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'prod_productos_abm'):
            return redirect(reverse('principal'))
        return super(ProductosCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):    
        initial = super(ProductosCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'
        initial['codigo'] = '{0:0{width}}'.format((ultimoNroId(prod_productos)+1),width=4)        
        initial['request'] = self.request
        return initial   

    def get_form_kwargs(self):
        kwargs = super(ProductosCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        prod_precios_FormSet.form = staticmethod(curry(Producto_ListaPreciosForm,request=request))
        prod_precios = prod_precios_FormSet(prefix='formPrecios')                   
        return self.render_to_response(self.get_context_data(form=form,prod_precios = prod_precios))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)               
        prod_precios_FormSet.form = staticmethod(curry(Producto_ListaPreciosForm,request=request))
        prod_precios = prod_precios_FormSet(self.request.POST,prefix='formPrecios')        
        if form.is_valid() and prod_precios.is_valid():
            return self.form_valid(form, prod_precios)
        else:
            return self.form_invalid(form, prod_precios)        

    def form_valid(self, form, prod_precios):
        self.object = form.save(commit=False)        
        self.object.empresa = empresa_actual(self.request)        
        self.object.save()
        
        if prod_precios:
            prod_precios.instance = self.object
            prod_precios.producto = self.object.id        
            prod_precios.save()

        stock = form.cleaned_data.get('stock')
        ppedido = form.cleaned_data.get('ppedido')
        ubicacion = form.cleaned_data.get('ubicacion')
        if not stock:            
            stock=1
        if not ppedido:
            ppedido=0
        ubi_prod = prod_producto_ubicac(producto=self.object,ubicacion=ubicacion,punto_pedido=ppedido)
        ubi_prod.save()
        actualizar_stock(self.request,self.object,ubicacion,21,stock)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        
        return HttpResponseRedirect(reverse('productos_listado'))

    def form_invalid(self, form, prod_precios):                                                       
        return self.render_to_response(self.get_context_data(form=form,prod_precios = prod_precios))
    
class ProductosEditView(VariablesMixin,UpdateView):
    form_class = ProductosForm
    template_name = 'productos/producto_form.html' 
    model = prod_productos
    pk_url_kwarg = 'id'  

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):                    
        if not tiene_permiso(self.request,'prod_productos_abm'):
            return redirect(reverse('principal'))
        return super(ProductosEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ProductosEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
     
    def get_initial(self):    
        initial = super(ProductosEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'        
        initial['request'] = self.request
        return initial 


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)                      
        prod_precios_FormSet.form = staticmethod(curry(Producto_ListaPreciosForm,request=request))
        prod_precios = prod_precios_FormSet(instance=self.object,prefix='formPrecios')        
        return self.render_to_response(self.get_context_data(form=form,prod_precios = prod_precios))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)          
        prod_precios_FormSet.form = staticmethod(curry(Producto_ListaPreciosForm,request=request))
        prod_precios = prod_precios_FormSet(self.request.POST,instance=self.object,prefix='formPrecios')        
        if form.is_valid() and prod_precios.is_valid():
            return self.form_valid(form, prod_precios)
        else:
            return self.form_invalid(form, prod_precios)       
     
    def form_invalid(self, form, prod_precios):                                                       
        return self.render_to_response(self.get_context_data(form=form,prod_precios = prod_precios))


    def form_valid(self, form, prod_precios):
        self.object = form.save(commit=False)        
        self.object.save()
        if prod_precios:
            prod_precios.instance = self.object
            prod_precios.producto = self.object.id        
            prod_precios.save()        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('productos_listado'))

class ProductosDeleteView(VariablesMixin,AjaxDeleteView):
    model = prod_productos
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'prod_productos_abm'):
            return redirect(reverse('principal'))
        return super(ProductosDeleteView, self).dispatch(*args, **kwargs)

class ProductosVerView(VariablesMixin,DetailView):
    model = prod_productos
    pk_url_kwarg = 'id'
    context_object_name = 'producto'
    template_name = 'productos/detalle_producto.html'        

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        return super(ProductosVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductosVerView, self).get_context_data(**kwargs)
        try:
            prod_stock = prod_producto_ubicac.objects.filter(producto=self.object)            
        except prod_stock.DoesNotExist:
            prod_stock = None         

        try:
            prod_precios = prod_producto_lprecios.objects.filter(producto=self.object)            
        except prod_precios.DoesNotExist:
            prod_precios = None        
            
        context['prod_precios'] = prod_precios
        context['prod_stock'] = prod_stock
        return context

@login_required
def producto_baja_reactivar(request,id):
    prod = prod_productos.objects.get(pk=id) 
    prod.baja = not prod.baja
    prod.save()               
    return HttpResponseRedirect(reverse('productos_listado'))

#************* CATEGORIAS **************
class CategoriasView(VariablesMixin,ListView):
    model = prod_categoria
    template_name = 'productos/lista_categorias.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        try:            
            queryset = prod_categoria.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = prod_categoria.objects.none()
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(CategoriasView, self).dispatch(*args, **kwargs)

class CategoriasCreateView(VariablesMixin,AjaxCreateView):
    form_class = CategoriasForm
    template_name = 'fm/productos/form_2.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(CategoriasCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(CategoriasCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(CategoriasCreateView, self).get_initial()               
        return initial    

class CategoriasEditView(VariablesMixin,AjaxUpdateView):
    form_class = CategoriasForm
    model = prod_categoria
    pk_url_kwarg = 'id'
    template_name = 'fm/productos/form_2.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(CategoriasEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form): 
        messages.success(self.request, u'Los datos se guardaron con éxito!')       
        return super(CategoriasEditView, self).form_valid(form)


    def get_initial(self):    
        initial = super(CategoriasEditView, self).get_initial()                      
        return initial    

class CategoriasDeleteView(VariablesMixin,AjaxDeleteView):
    model = prod_categoria
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(CategoriasDeleteView, self).dispatch(*args, **kwargs)

class CategoriasVerView(VariablesMixin,DetailView):
    model = prod_categoria
    pk_url_kwarg = 'id'
    context_object_name = 'categoria'
    template_name = 'productos/detalle_categoria.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        return super(CategoriasVerView, self).dispatch(*args, **kwargs)

@login_required
def categoria_baja_reactivar(request,id):
    cat = prod_categoria.objects.get(pk=id) 
    cat.baja = not cat.baja
    cat.save()               
    return HttpResponseRedirect(reverse('categorias_listado'))


#************* DEPOSITOS **************
class DepositosView(VariablesMixin,ListView):
    model = prod_ubicacion
    template_name = 'productos/lista_depositos.html'
    context_object_name = 'depositos'    

    def get_queryset(self):
        try:            
            queryset = prod_ubicacion.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = prod_ubicacion.objects.none()
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(DepositosView, self).dispatch(*args, **kwargs)

class DepositosCreateView(VariablesMixin,AjaxCreateView):
    form_class = UbicacionForm
    template_name = 'fm/productos/form_depo.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(DepositosCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(DepositosCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(DepositosCreateView, self).get_initial()               
        return initial    

class DepositosEditView(VariablesMixin,AjaxUpdateView):
    form_class = UbicacionForm
    model = prod_ubicacion
    pk_url_kwarg = 'id'
    template_name = 'fm/productos/form_depo.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(DepositosEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(DepositosEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(DepositosEditView, self).get_initial()                      
        return initial    

class DepositosDeleteView(VariablesMixin,AjaxDeleteView):
    model = prod_ubicacion
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(DepositosDeleteView, self).dispatch(*args, **kwargs)

@login_required
def deposito_baja_reactivar(request,id):
    dep = prod_ubicacion.objects.get(pk=id) 
    dep.baja = not dep.baja
    dep.save()               
    return HttpResponseRedirect(reverse('depositos_listado'))

#************* Lista Precios **************
class LPreciosView(VariablesMixin,ListView):
    model = prod_lista_precios
    template_name = 'productos/lista_lprecios.html'
    context_object_name = 'lista_precios'

    def get_queryset(self):
        try:            
            queryset = prod_lista_precios.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = prod_lista_precios.objects.none()
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(LPreciosView, self).dispatch(*args, **kwargs)

class LPreciosCreateView(VariablesMixin,AjaxCreateView):
    form_class = ListaPreciosForm
    template_name = 'fm/productos/form_lprecios.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(LPreciosCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(LPreciosCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(LPreciosCreateView, self).get_initial()               
        return initial    

class LPreciosEditView(VariablesMixin,AjaxUpdateView):
    form_class = ListaPreciosForm
    model = prod_lista_precios
    pk_url_kwarg = 'id'
    template_name = 'fm/productos/form_lprecios.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(LPreciosEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(LPreciosEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(LPreciosEditView, self).get_initial()                      
        return initial    

class LPreciosDeleteView(VariablesMixin,AjaxDeleteView):
    model = prod_lista_precios
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(LPreciosDeleteView, self).dispatch(*args, **kwargs)

@login_required
def lprecios_baja_reactivar(request,id):
    lp = prod_lista_precios.objects.get(pk=id) 
    lp.baja = not lp.baja
    lp.save()               
    return HttpResponseRedirect(reverse('lista_precios_listado'))

#************* Lista Precios **************

class ProdLPreciosView(VariablesMixin,ListView):
    model = prod_producto_lprecios
    template_name = 'productos/producto_precios.html'
    context_object_name = 'precios'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(ProdLPreciosView, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProdLPreciosView, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        fecha = date.today()
        
        form = ConsultaLPreciosProd(self.request.POST or None,request=self.request)           
        precios = prod_producto_lprecios.objects.none()
        
        if form.is_valid():                                
            precios = prod_producto_lprecios.objects.filter(producto__empresa=empresa,lista_precios__empresa__in=empresas_habilitadas(self.request)).select_related('producto','producto__categoria').order_by('producto','lista_precios')
            producto = form.cleaned_data['producto']                                                              
            lista_precios = form.cleaned_data['lista_precios']                                                              
            categoria = form.cleaned_data['categoria']   
            tipo_prod = form.cleaned_data['tipo_prod']                                                 
            mostrar_en = form.cleaned_data['mostrar_en']
                    
            if int(tipo_prod)>0:                
                precios= precios.filter(Q(producto__tipo_producto=tipo_prod)) 
            if int(mostrar_en)>0:                
                precios= precios.filter(Q(producto__mostrar_en=mostrar_en)) 
            if producto:
                precios = precios.filter(Q(producto__nombre__icontains=producto))
            if categoria:
                precios= precios.filter(Q(producto__categoria=categoria))            
            if lista_precios:
                precios= precios.filter(Q(lista_precios=lista_precios))

        context['form'] = form
        context['precios'] = precios
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)    

class ProdLPreciosEditView(VariablesMixin,AjaxUpdateView):
    form_class = Producto_EditarPrecioForm
    model = prod_producto_lprecios
    pk_url_kwarg = 'id'
    template_name = 'fm/productos/form_precio_prod.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('prod_precios_listado'))
        return super(ProdLPreciosEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):            
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(ProdLPreciosEditView, self).form_valid(form)


    def get_initial(self):    
        initial = super(ProdLPreciosEditView, self).get_initial()                      
        return initial          

def actualizar_precios(tipo_op,tipo_precio,valor,porc,coef,lista,recalcular):   
   try: 
    if lista:
        precios = prod_producto_lprecios.objects.filter(id__in=lista)
    else:
        precios = prod_producto_lprecios.objects.filter(producto__baja=False)
    
    precios2 = precios
    #Reemplazar Valor
    if tipo_op == 0:                
        if tipo_precio==0:
            cant = precios.update(precio_venta=valor) 
        elif tipo_precio==1:
            cant = precios.update(precio_costo=valor) 
        elif tipo_precio==2:
            cant = precios.update(precio_cimp=valor)  
    #Sumar $
    elif tipo_op==1:        
        if tipo_precio==0:
            cant = precios.update(precio_venta=F('precio_venta')+valor) 
        elif tipo_precio==1:
            cant = precios.update(precio_costo=F('precio_costo')+valor) 
        elif tipo_precio==2:
            cant = precios.update(precio_cimp=F('precio_cimp')+valor)
    #sumar %
    elif tipo_op==2:        
        cc = 1+(porc/float(100))        
        if cc>0:
            if tipo_precio==0:
                cant = precios.update(precio_venta=F('precio_venta')*cc)                 
            elif tipo_precio==1:
                cant = precios.update(precio_costo=F('precio_costo')*cc) 
            elif tipo_precio==2:
                cant = precios.update(precio_cimp=F('precio_cimp')*cc)
    elif tipo_op==3:
        cant = precios.update(coef_ganancia=coef,precio_venta=F('precio_venta')*coef)

    if recalcular and(tipo_op<3):
        for p in precios2:
            
            if p.producto.tasa_iva.coeficiente:
                coef_iva = p.producto.tasa_iva.coeficiente + 1
            else:
                coef_iva = 1
            if tipo_precio==1:
                p.precio_cimp=p.precio_costo*coef_iva
                p.precio_venta=p.precio_costo*coef_iva*(p.coef_ganancia+1)
            elif tipo_precio==2:
                p.precio_venta=p.precio_cimp*(p.coef_ganancia+1)
            p.save()
    
   except:
    cant = 0 
   return cant

@login_required 
def prod_precios_actualizar(request):        
    limpiar_sesion(request)    
    if request.method == 'POST' and request.is_ajax():                                       
        lista = request.POST.getlist('id')                        
        form = ActualizarPrecioForm(request.POST or None)     
        
        if form.is_valid():                                   
            tipo_operacion = int(form.cleaned_data['tipo_operacion'])                                                              
            tipo_precio = int(form.cleaned_data['tipo_precio'])                                                              
            valor = form.cleaned_data['valor']
            porc = int(form.cleaned_data['porc']) 
            coeficiente = form.cleaned_data['coeficiente']
            recalcular = form.cleaned_data['recalcular']                                                             
            cant = actualizar_precios(tipo_operacion,tipo_precio,valor,porc,coeficiente,lista,recalcular)                            
            response = {'cant': cant, 'message': "Se actualizaron exitosamente."} # for ok        
        else:            
            response = {'cant': 0, 'message': "¡Verifique los datos ingresados!"} 
        # except:
        #     response = {'cant': 0, 'message': "¡No se actualizaron Precios!"} 
            
        return HttpResponse(json.dumps(response,default=default), content_type='application/json')
    else:    
        form = ActualizarPrecioForm(None)          
        variables = RequestContext(request, {'form':form})        
        return render_to_response("productos/actualizar_precios.html", variables)


#************* PRods Stock **************

class ProdStockView(VariablesMixin,ListView):
    model = prod_producto_ubicac
    template_name = 'productos/producto_stock.html'
    context_object_name = 'productos'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(ProdStockView, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProdStockView, self).get_context_data(**kwargs)
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 

        fecha = date.today()
        
        form = ConsultaStockProd(self.request.POST or None,request =self.request )   

        productos = prod_producto_ubicac.objects.none()
        
        if form.is_valid():                                
            producto = form.cleaned_data['producto']                                                              
            ubicacion = form.cleaned_data['ubicacion']                                                              
            categoria = form.cleaned_data['categoria']   
            tipo_prod = int(form.cleaned_data['tipo_prod'])             
            lleva_stock = form.cleaned_data['lleva_stock']                         
            stock_pp = int(form.cleaned_data['stock_pp'])                         
            productos = prod_producto_ubicac.objects.filter(producto__empresa__id__in=empresas_habilitadas(self.request)).select_related('producto','producto__categoria')            
        
            if producto:
                productos = productos.filter(producto__nombre__icontains=producto)
            if tipo_prod>0:                
                productos= productos.filter(producto__tipo_producto=tipo_prod)
            if int(lleva_stock)>0:
                lleva= (int(lleva_stock)==1)                
                productos= productos.filter(producto__llevar_stock=lleva)
            if categoria:
                productos= productos.filter(producto__categoria=categoria)                     
            if ubicacion:
                productos = productos.filter(ubicacion=ubicacion)                       
            if stock_pp>0:
                if stock_pp==1:
                    ids = [p.id for p in productos if p.get_reposicion()]
                else:
                    ids = [p.id for p in productos if not p.get_reposicion()]
                productos = productos.filter(id__in=ids)
                       
        context['form'] = form
        context['productos'] = productos
        return context
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)     

class ProdStockCreateView(VariablesMixin,AjaxCreateView):
    form_class = Producto_StockForm
    template_name = 'fm/productos/form_stock_prod.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('prod_stock_listado'))
        return super(ProdStockCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                               
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(ProdStockCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ProdStockCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):    
        initial = super(ProdStockCreateView, self).get_initial()               
        return initial  

class ProdStockEditView(VariablesMixin,AjaxUpdateView):
    form_class = Producto_StockForm
    model = prod_producto_ubicac
    pk_url_kwarg = 'id'
    template_name = 'fm/productos/form_stock_prod.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('prod_stock_listado'))
        return super(ProdStockEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):            
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(ProdStockEditView, self).form_valid(form)


    def get_initial(self):    
        initial = super(ProdStockEditView, self).get_initial()                      
        return initial     



@login_required 
def prod_stock_actualizar(request):        
    limpiar_sesion(request)    
    if request.method == 'POST' and request.is_ajax():                                       
        lista = request.POST.getlist('id')                        
        form = ActualizarStockForm(request.POST or None)     
        if lista:
            prods = prod_producto_ubicac.objects.filter(id__in=lista)
        else:
            prods = prod_producto_ubicac.objects.filter(producto__baja=False)
        
        if form.is_valid():                                   
            tipo_operacion = int(form.cleaned_data['tipo_operacion'])                                                              
            valor = form.cleaned_data['valor']
            if tipo_operacion>0:
                actualizar_stock_multiple(request,prods,tipo_operacion,valor) 
            else:
                prods.update(punto_pedido=valor) 
            cant=len(prods)

            response = {'cant': cant, 'message': "Se actualizaron exitosamente."} # for ok        
        else:
            response = {'cant': 0, 'message': "¡Verifique los datos ingresados!"} 
        # except:
        #     response = {'cant': 0, 'message': "¡No se actualizaron Precios!"} 
            
        return HttpResponse(json.dumps(response,default=default), content_type='application/json')
    else:    
        form = ActualizarStockForm(None)          
        variables = RequestContext(request, {'form':form})        
        return render_to_response("productos/actualizar_stock.html", variables)

@login_required 
def prod_stock_nuevo(request):        
    limpiar_sesion(request)    
    if request.method == 'POST':                                       
        form = CrearStockForm(request.POST or None,request=request)             
        
        if form.is_valid():                                   
            producto = form.cleaned_data['producto']
            ubicacion = form.cleaned_data['ubicacion']
            valor = form.cleaned_data['valor']
            ppedido = form.cleaned_data['ppedido']
            existe_prod_stock = prod_producto_ubicac.objects.filter(producto=producto,ubicacion=ubicacion).exists()
            if existe_prod_stock:
                response = {'cant': 0, 'message': "¡El producto ya tiene asignado Stock!"} 
            else:
                ubi_prod = prod_producto_ubicac(producto=producto,ubicacion=ubicacion,punto_pedido=ppedido)
                ubi_prod.save()            
                actualizar_stock(request,producto,ubicacion,21,valor)            
                response = {'cant': 1, 'message': "Se actualizaron exitosamente."} # for ok        
        else:
            response = {'cant': 0, 'message': "¡Verifique los datos ingresados!"} 
       
            
        return HttpResponse(json.dumps(response,default=default), content_type='application/json')
    else:    
        form = CrearStockForm(None,request=request)          
        variables = RequestContext(request, {'form':form})        
        return render_to_response("productos/nuevo_stock.html", variables)


@login_required 
def prod_stock_generar(request):        
    prods=prod_productos.objects.all()
    for p in prods:        
        dep = prod_ubicacion.objects.get(pk=1) 
        up = prod_producto_ubicac.objects.filter(producto=p,ubicacion=dep)
        if not up:
            ubi_prod = prod_producto_ubicac(producto=p,ubicacion=dep,punto_pedido=0)
            ubi_prod.save()
    return HttpResponseRedirect(reverse('principal'))
    
