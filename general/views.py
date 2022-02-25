# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import *
from django.views.generic.base import ContextMixin
from easy_pdf.rendering import render_to_pdf_response, render_to_pdf

from .models import *
from .utilidades import *
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView
from django.conf import settings
from django.db.models import Q,Sum,Count,F
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,redirect
from modal.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
from django.contrib import messages
import json
import urllib
from .forms import EmpresaForm,TareasForm,pto_vta_habilitados,pto_vta_habilitados_list
from comprobantes.models import cpb_comprobante,cpb_comprobante_detalle
from entidades.models import egr_entidad
from productos.models import prod_productos,prod_producto_lprecios
from trabajos.models import orden_pedido,orden_trabajo
from usuarios.views import tiene_permiso,ver_permisos
from django.db.models import DecimalField,Func
from django.core.serializers.json import DjangoJSONEncoder

##############################################
#   Mixin para cargar las Vars de sistema    #
##############################################

def ultimoNroId(tabla):
    try:
        ultimo = tabla.objects.latest('id').id
    except tabla.DoesNotExist:
        return 0
    return ultimo

@login_required 
def buscarDatosAPICUIT(request):      
   try:                            
    cuit = request.GET['cuit']
    data = urllib.urlopen(URL_API+cuit).read()    
    d = json.loads(data) 

    imp = [x['idImpuesto'] for x in d['impuesto']]    
    if (10 in imp):
        id_cat=1
    elif (11 in imp):
        id_cat=1
    elif (30 in imp):
        id_cat=1
    elif (20 in imp):
        id_cat=6
    elif (32 in imp):
        id_cat=4
    elif (33 in imp):
        id_cat=2
    else:
        id_cat=5
    d.update({'categoria': id_cat})        
   except:
    d= []
   return HttpResponse( json.dumps(d), content_type='application/json' ) 

@login_required 
def buscarDatosEmpresa(request):      
   d= {}
   try:
       empresa = empresa_actual(request)   
       d['nombre']= empresa.nombre
       d['categ_fiscal']= empresa.categ_fiscal
       d['cuit']= empresa.cuit
       d['iibb']= empresa.iibb
       d['fecha_inicio_activ']= str(empresa.fecha_inicio_activ)
       d['domicilio']= empresa.domicilio
       d['provincia']= empresa.provincia
       d['localidad']= empresa.localidad
       d['cod_postal']= empresa.cod_postal
       d['email']= empresa.email
       d['telefono']= empresa.telefono
       d['celular']= empresa.celular

       d['nombre_fantasia']= empresa.nombre_fantasia
       d['ruta_logo']= empresa.ruta_logo
       d['tipo_logo_factura']= empresa.tipo_logo_factura
   except:
       pass
   return HttpResponse( json.dumps(d,cls=DecimalEncoder), content_type='application/json' ) 



class VariablesMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(VariablesMixin, self).get_context_data(**kwargs)
        context.update(self._get_variables_mixin(context.get('request') or self.request))
        return context

    def _get_variables_mixin(self, request):
        context = {}
        context['ENTIDAD_ID'] = settings.ENTIDAD_ID
        context['ENTIDAD_DIR'] = settings.ENTIDAD_DIR
        usr= request.user
        try:
            context['usuario'] = usuario_actual(request)
        except:
            context['usuario'] = None
        try:
            context['usr'] = usr
        except:
            context['usr'] = None
        try:
            empresa = empresa_actual(request)
            context['empresa'] = empresa
            context['homologacion'] = empresa.homologacion
        except gral_empresa.DoesNotExist:
            context['empresa'] = None
            context['homologacion'] = True
        try:
            tipo_usr = usr.userprofile.id_usuario.tipoUsr
            context['tipo_usr'] = tipo_usr
            context['habilitado_contador'] = habilitado_contador(tipo_usr)
        except:
            context['tipo_usr'] = 1
            context['habilitado_contador'] = False

        permisos_grupo = ver_permisos(request)
        context['permisos_grupo'] = permisos_grupo
        context['permisos_ingresos'] = ('cpb_ventas' in permisos_grupo)or('cpb_cobranzas' in permisos_grupo)or('cpb_remitos' in permisos_grupo)or('cpb_presupuestos' in permisos_grupo)or('cpb_liqprod_abm' in permisos_grupo)
        context['permisos_egresos'] = ('cpb_compras' in permisos_grupo)or('cpb_pagos' in permisos_grupo)or('cpb_movimientos' in permisos_grupo)
        context['permisos_trabajos'] = ('trab_pedidos' in permisos_grupo)or('trab_trabajos' in permisos_grupo)or('trab_colocacion' in permisos_grupo)
        context['permisos_rep_ingr_egr'] = ('rep_cta_cte_clientes' in permisos_grupo)or('rep_saldos_clientes' in permisos_grupo)or('rep_cta_cte_prov' in permisos_grupo)or('rep_saldos_prov' in permisos_grupo)or('rep_varios' in permisos_grupo)
        context['permisos_rep_contables'] = ('rep_libro_iva' in permisos_grupo)or('rep_libro_iva' in permisos_grupo)or('reporte_retenciones_imp' in permisos_grupo)
        context['permisos_rep_finanzas'] = ('rep_caja_diaria' in permisos_grupo)or('rep_seguim_cheques' in permisos_grupo)or('rep_saldos_cuentas' in permisos_grupo)
        context['permisos_entidades'] = ('ent_clientes' in permisos_grupo)or('ent_proveedores' in permisos_grupo)or('ent_vendedores' in permisos_grupo)
        context['permisos_productos'] = ('prod_productos' in permisos_grupo)or('prod_productos_abm' in permisos_grupo)
        context['sitio_mobile'] = mobile(request)
        context['hoy'] = hoy()
        context['EMAIL_CONTACTO'] = EMAIL_CONTACTO
        return context


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()

class Year(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR from %(expressions)s)'
    output_field = models.IntegerField()

class PrincipalView(VariablesMixin,TemplateView):
    template_name = 'index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PrincipalView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PrincipalView, self).get_context_data(**kwargs)            
        usr= usuario_actual(self.request)
        
        fecha_desde = ultimo_anio()
        fecha_hoy = hoy()
        pvs = pto_vta_habilitados_list(self.request)
        empresas = empresas_habilitadas(self.request)
        
        comprobantes = cpb_comprobante.objects.filter(estado__in=[1,2]).filter(fecha_cpb__range=[fecha_desde, fecha_hoy],empresa=empresa_actual(self.request))
        
        ventas = comprobantes.filter(cpb_tipo__compra_venta='V',pto_vta__in=pvs,cpb_tipo__tipo__in=[1,2,3,9,21,22,23])
        total_ventas_mensual = ventas.filter(fecha_cpb__range=[inicioMes(), fecha_hoy])
        total_ventas_mensual = total_ventas_mensual.aggregate(sum=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
        total_ventas = ventas.aggregate(sum=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
        context['total_ventas'] = total_ventas            
        context['total_ventas_mensual'] = total_ventas_mensual


        deuda_cobrar_total = ventas.aggregate(sum=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0        
        deuda_cobrar_mensual = ventas.filter(fecha_cpb__range=[inicioMes(), fecha_hoy]).aggregate(sum=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0                    
        context['deuda_cobrar_total'] = deuda_cobrar_total
        context['deuda_cobrar_mensual'] = deuda_cobrar_mensual
        
        porc_cobrar_total = 0
        porc_cobrar_mensual = 0
        if total_ventas > 0:
            porc_cobrar_total=(deuda_cobrar_total/total_ventas)*100                        
        if total_ventas_mensual > 0:
            porc_cobrar_mensual=(deuda_cobrar_mensual/total_ventas_mensual)*100    
        context['porc_cobrar_mensual'] = porc_cobrar_mensual
        context['porc_cobrar_total'] = porc_cobrar_total
        
        compras = comprobantes.filter(cpb_tipo__compra_venta='C',cpb_tipo__tipo__in=[1,2,3,9,21,22,23])
        total_compras = compras.aggregate(sum=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
        context['total_compras'] = total_compras
        total_compras_mensual = compras.filter(fecha_cpb__range=[inicioMes(), fecha_hoy]).aggregate(sum=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
        context['total_compras_mensual'] = total_compras_mensual
                   
        deuda_pagar_total = compras.aggregate(sum=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0      
        deuda_pagar_mensual = compras.filter(fecha_cpb__range=[inicioMes(), fecha_hoy]).aggregate(sum=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0      
        context['deuda_pagar_total'] = deuda_pagar_total            
        context['deuda_pagar_mensual'] = deuda_pagar_mensual            
        
        porc_pagar_total = 0
        porc_pagar_mensual = 0
        if total_compras > 0:
            porc_pagar_total=(deuda_pagar_total/total_compras)*100                        
        if total_compras_mensual > 0:
            porc_pagar_mensual=(deuda_pagar_mensual/total_compras_mensual)*100    
        context['porc_pagar_total'] = porc_pagar_total
        context['porc_pagar_mensual'] = porc_pagar_mensual
        
        context['ultimas_ventas'] = ventas.filter(cpb_tipo__id__in=[1,3,5,14]).order_by('-fecha_cpb','-fecha_creacion','-id').select_related('entidad','cpb_tipo','estado')[:10]
        context['ultimas_compras'] = compras.filter(cpb_tipo__id__in=[2,4,6,18],estado__in=[1,2]).order_by('-fecha_cpb','-fecha_creacion','-id').select_related('entidad','cpb_tipo','estado')[:10]
        # context['ultimos_presup'] = comprobantes.filter(cpb_tipo__id=11).order_by('-fecha_cpb','-fecha_creacion','-id').select_related('entidad','cpb_tipo','estado','presup_aprobacion','presup_aprobacion')[:10]
        
        if usr.tipoUsr==0:
            context['tareas'] = gral_tareas.objects.filter(empresa__id__in=empresas).select_related('usuario_creador','usuario_asignado').order_by('-fecha','-fecha_creacion','-id')                
        else:    
            context['tareas'] = gral_tareas.objects.filter(empresa__id__in=empresas).filter(Q(usuario_asignado=usr)|Q(usuario_asignado__isnull=True)).select_related('usuario_creador','usuario_asignado').order_by('-fecha','-fecha_creacion','-id')        
        
        
        comprobantes = comprobantes.filter(cpb_tipo__tipo__in=[1,2,3,9,21,22,23]).distinct().annotate(m=Month('fecha_cpb'),anio=Year('fecha_cpb')).order_by(F('anio'),F('m')).values('m','anio')        

        meses_cpbs = comprobantes.values_list('m','anio')

        meses = list()
        import locale        
        locale.setlocale(locale.LC_ALL, '')
        

        ventas_deuda = list()
        ventas_pagos = list()
        compras_deuda = list()
        compras_pagos = list()
        
        for m in meses_cpbs:                        
            meses.append(MESES[m[0]-1][1]+' '+str(m[1])[2:4]+"'")
            ventas = comprobantes.filter(cpb_tipo__compra_venta='V',anio=m[1],m=m[0]).annotate(pendiente=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'),output_field=DecimalField()),saldado=Sum((F('importe_total')-F('saldo'))*F('cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by(F('anio'),F('m'))
            compras = comprobantes.filter(cpb_tipo__compra_venta='C',anio=m[1],m=m[0]).annotate(pendiente=Sum(F('saldo')*F('cpb_tipo__signo_ctacte'),output_field=DecimalField()),saldado=Sum((F('importe_total')-F('saldo'))*F('cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by(F('anio'),F('m'))
            if ventas:
                ventas_deuda.append(ventas[0].get('pendiente',Decimal(0.00)))
                ventas_pagos.append(ventas[0].get('saldado',Decimal(0.00)))
            else:
                ventas_deuda.append(Decimal(0.00))
                ventas_pagos.append(Decimal(0.00))
            
            if compras:
                compras_deuda.append(compras[0].get('pendiente',Decimal(0.00)))
                compras_pagos.append(compras[0].get('saldado',Decimal(0.00)))            
            else:
                compras_deuda.append(Decimal(0.00))
                compras_pagos.append(Decimal(0.00))
            
        context['meses']= json.dumps(meses,cls=DecimalEncoder)
       
        context['ventas_deuda']=  json.dumps(ventas_deuda,cls=DecimalEncoder)
        context['ventas_pagos']=  json.dumps(ventas_pagos,cls=DecimalEncoder)
        context['compras_deuda']= json.dumps(compras_deuda,cls=DecimalEncoder)
        context['compras_pagos']= json.dumps(compras_pagos,cls=DecimalEncoder)

        context['hoy'] = fecha_hoy
        context['fecha_desde'] = fecha_desde

        productos_vendidos = cpb_comprobante_detalle.objects.filter(cpb_comprobante__pto_vta__in=pvs,cpb_comprobante__cpb_tipo__compra_venta='V',cpb_comprobante__cpb_tipo__tipo__in=[1,2,3,9,21,22,23],cpb_comprobante__estado__in=[1,2],cpb_comprobante__fecha_cpb__range=[fecha_desde, fecha_hoy])
        productos_vendidos_total = productos_vendidos.aggregate(sum=Sum(F('importe_total')*F('cpb_comprobante__cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0 
        productos_vendidos = productos_vendidos.values('producto__nombre').annotate(tot=Sum(F('importe_total')*F('cpb_comprobante__cpb_tipo__signo_ctacte'),output_field=DecimalField())).order_by('-tot')[:10]
        context['productos_vendidos']= productos_vendidos 
        
        vars_sistema = settings

        return context

class EmpresaView(VariablesMixin,ListView):
    model = gral_empresa
    template_name = 'general/empresas/empresas_listado.html'
    context_object_name = 'empresas'
    queryset = gral_empresa.objects.filter().order_by('id')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(EmpresaView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EmpresaView, self).get_context_data(**kwargs)
        return context

class EmpresaEditView(VariablesMixin,UpdateView):
    form_class = EmpresaForm
    model = gral_empresa
    pk_url_kwarg = 'id'
    template_name = 'general/empresas/empresa_form.html'
    success_url = '/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(EmpresaEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(EmpresaEditView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(EmpresaEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):         
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):    
        initial = super(EmpresaEditView, self).get_initial()
        initial['request'] = self.request                      
        return initial 

#************* TAREAS **************

class TareasView(VariablesMixin,ListView):
    model = gral_tareas
    template_name = 'general/tareas/tareas_listado.html'
    context_object_name = 'tareas'   

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)
        if not tiene_permiso(self.request,'gral_tareas'):
            return redirect(reverse('principal'))
        return super(TareasView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TareasView, self).get_context_data(**kwargs)        
        try:                         
            tareas = gral_tareas.objects.filter(empresa__id__in=empresas_habilitadas(self.request)).select_related('usuario_creador','usuario_asignado').order_by('-fecha','-fecha_creacion','-id')               
            context['tareas'] = tareas           
        except:
            context['tareas'] = None
        return context

class TareasCreateView(VariablesMixin,CreateView):
    form_class = TareasForm
    template_name = 'general/tareas/tareas_form.html'
    success_url = '/tareas/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_tareas'):
            return redirect(reverse('tareas_listado'))
        return super(TareasCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        # form.instance.empresa = self.request.user.userprofile.id_usuario.empresa        
        form.instance.usuario_creador = usuario_actual(self.request)
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(TareasCreateView, self).form_valid(form)

    def form_invalid(self, form):         
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):    
        initial = super(TareasCreateView, self).get_initial()               
        return initial    

class TareasEditView(VariablesMixin,UpdateView):
    form_class = TareasForm
    model = gral_tareas
    pk_url_kwarg = 'id'
    template_name = 'general/tareas/tareas_form.html'
    success_url = '/tareas/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_tareas'):
            return redirect(reverse('tareas_listado'))
        return super(TareasEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form): 
        messages.success(self.request, u'Los datos se guardaron con éxito!')       
        return super(TareasEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(TareasEditView, self).get_initial()                      
        return initial    

@login_required
def TareasDeleteView(request, id):
    t = get_object_or_404(gral_tareas, id=id)
    if not tiene_permiso(request,'gral_tareas'):
            return redirect(reverse('tareas_listado'))
    t.delete()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return redirect('tareas_listado')        

#***************************

@login_required 
def recargar_clientes(request):
    context={}
    clientes = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).distinct().order_by('apellido_y_nombre')
    context["clientes"]=[{'detalle':p.__unicode__(),'id':p.pk} for p in clientes]    
    return HttpResponse(json.dumps(context))

@login_required 
def recargar_vendedores(request):
    context={}
    vendedores = egr_entidad.objects.filter(tipo_entidad=3,baja=False,empresa__id__in=empresas_habilitadas(request)).distinct().order_by('apellido_y_nombre')      
    context["vendedores"]=[{'detalle':p.__unicode__(),'id':p.pk} for p in vendedores]
    return HttpResponse(json.dumps(context))

@login_required 
def recargar_proveedores(request):
    context={}
    proveedores = egr_entidad.objects.filter(tipo_entidad=2,baja=False,empresa__id__in=empresas_habilitadas(request)).distinct().order_by('apellido_y_nombre')  
    context["proveedores"]=[{'detalle':p.__unicode__(),'id':p.pk} for p in proveedores]
    return HttpResponse(json.dumps(context))

@login_required 
def recargar_productos(request,tipo):
    context={}
    productos = prod_productos.objects.filter(baja=False,mostrar_en__in=(tipo,3),empresa__id__in=empresas_habilitadas(request)).distinct().order_by('nombre','codigo')          
    prods = [{'detalle':p.get_prod_busqueda(),'id':p.pk} for p in productos]
    context["productos"]= prods
    return HttpResponse(json.dumps(context))

@login_required 
def entidad_baja_reactivar(request,id):
    entidad = egr_entidad.objects.get(pk=id) 
    entidad.baja = not entidad.baja
    entidad.save()               
    return HttpResponseRedirect(entidad.get_listado())


from django.http import HttpResponse
from PIL import Image

def chequear_email(request,id):
    try:
        cpb=cpb_comprobante.objects.get(pk=id)
        if cpb.fecha_envio_mail:
            cpb.fecha_recepcion_mail = date.today()
            cpb.save()
        red = Image.new('RGB', (1, 1))
        response = HttpResponse(content_type="image/png")
        red.save(response, "PNG")    
        return response
    except:
        HttpResponse('ERROR')


def codbar(request):
    cod = "272211991410600037040117046218920201016"
    dv1= str(digVerificador(cod))
    return HttpResponse(dv1)


def codqr(request):
    from general.qr_generator import QRCodeGenerator
    cod = "www.google.com"
    qrcode, qrdata = QRCodeGenerator(data=cod).get_qrcode()
    template = 'general/facturas/QR_test.html'
    # return render_to_pdf(template, locals())
    return render_to_pdf_response(request, template, locals())

