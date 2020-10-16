# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import render, redirect, get_object_or_404,render_to_response,HttpResponseRedirect,HttpResponse
from django.template.loader import render_to_string,get_template
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView,DetailView
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from datetime import datetime,date,timedelta
from django.utils import timezone
from dateutil.relativedelta import *
from .forms import MovimCuentasForm,BancosForm,MovimCuentasFPForm,PercImpForm,FormaPagoForm,PtoVtaForm,DispoForm,SeguimientoForm,FormCheques,FormChequesCobro,PtoVtaEditForm,RetencForm
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from django.db.models import Q,Sum,Count,F,DecimalField
from .models import *
import json
import random
from decimal import *
from modal.views import AjaxCreateView,AjaxUpdateView,AjaxDeleteView
from django.contrib import messages
from general.utilidades import *
from general.models import gral_empresa
from general.views import VariablesMixin,getVariablesMixin
from usuarios.views import tiene_permiso
from django.forms.models import inlineformset_factory,BaseInlineFormSet,modelformset_factory
from productos.models import prod_productos,prod_producto_ubicac,prod_producto_lprecios
from django.contrib.messages.views import SuccessMessageMixin
from django.core.serializers.json import DjangoJSONEncoder
from general.forms import ConsultaCpbs,pto_vta_habilitados,pto_vta_habilitados_list,ConsultaCpbsCompras
from django.utils.functional import curry 
from django.forms.models import model_to_dict

@login_required 
def recalcular_precios(request):
    detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante__cpb_tipo__tipo__in=[1,2,3,9,14,21,22,23],cpb_comprobante__cpb_tipo__usa_stock=True)
    for c in detalles:
        lp = prod_producto_lprecios.objects.get(producto=c.producto,lista_precios=c.lista_precios)
        c.importe_costo = lp.precio_costo
        c.save()

    return HttpResponseRedirect(reverse('principal')) 

@login_required 
def recalcular_cpbs(request):
    comprobantes = cpb_comprobante.objects.all()
    for c in comprobantes:
        recalcular_saldo_cpb(c.id)

    return HttpResponseRedirect(reverse('principal')) 

@login_required 
def recalcular_cobranzas(request):

    comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in = [4,7,8])    
    for c in comprobantes:
        recalcular_saldos_cobranzas(c.id)

    return HttpResponseRedirect(reverse('principal')) 

@login_required 
def eliminar_detalles_fp_huerfanos(request):
    empresa = empresa_actual(request)
    ids = cpb_comprobante.objects.all().values_list('id',flat=True)
    ids = [int(x) for x in ids]
    
    detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante__empresa=empresa).exclude(cpb_comprobante__id__in=ids).values_list('cpb_comprobante',flat=True)

    # for c in detalles
    #     recalcular_saldo_cpb(c.id)

    return HttpResponse( json.dumps(list(detalles), cls=DjangoJSONEncoder), content_type='application/json' )     
  
@login_required 
def recalcular_compras(request):
    usr= request.user     
    try:
        usuario = usr                        
    except:
        usuario = None         
    try:
        tipo_usr = usr.userprofile.id_usuario.tipoUsr
    except:
        tipo_usr = 1
    try:
        empresa = usr.userprofile.id_usuario.empresa
    except gral_empresa.DoesNotExist:
        empresa = None           
    comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[1,2,3,9,21,22,23],cpb_tipo__compra_venta='C',empresa=empresa).order_by('-fecha_cpb','-id','-fecha_creacion')
    for c in comprobantes:
        recalcular_saldo_cpb(c.id)

    return HttpResponseRedirect(reverse('cpb_compra_listado'))    

@login_required 
def recalcular_presupuestos(request):
    usr= request.user     
    try:
        usuario = usr                        
    except:
        usuario = None         
    try:
        tipo_usr = usr.userprofile.id_usuario.tipoUsr
    except:
        tipo_usr = 1
    try:
        empresa = usr.userprofile.id_usuario.empresa
    except gral_empresa.DoesNotExist:
        empresa = None           
    comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo__in=[6],cpb_tipo__compra_venta='V',empresa=empresa).order_by('-fecha_cpb','-id','-fecha_creacion')
    for c in comprobantes:
        recalcular_saldo_cpb(c.id)

    return HttpResponseRedirect(reverse('cpb_presup_listado'))

def puedeEditarCPB(idCpb):
    cpb=cpb_comprobante.objects.get(pk=idCpb)
    #Si es factura NC ND o Recibo
    puede=(cpb.estado.id<3)
    if cpb.cpb_tipo.tipo not in [4,7]:     
        puede=(cpb.importe_total==cpb.saldo) and (puede)       
    if cpb.cpb_tipo.facturable:
        puede=not(cpb.cae) and (puede)    
    return puede

def puedeEliminarCPB(idCpb):
    cpb=cpb_comprobante.objects.get(pk=idCpb)
    #Si es factura NC ND o Recibo
    puede=(cpb.estado.id<=3)
    if cpb.cpb_tipo.tipo not in [4,7]:     
        puede=(cpb.importe_total==cpb.saldo) and (puede)       
    puede=(not(cpb.cae)) and (puede)    
    return puede

def comprobantes_con_saldo(tipo):    
    comprobantes = cpb_comprobante.objects.filter(cpb_tipo__tipo=tipo,saldo__gt=0).order_by('-fecha_cpb','-fecha_creacion')
    return comprobantes

def saldo_cpb(idCpb):
    cpb=cpb_comprobante.objects.get(pk=idCpb)    
    #los reciobs dde el cpb es el padre
    cobranzas = cpb_cobranza.objects.filter(cpb_factura=cpb,cpb_comprobante__estado__pk__lt=3).aggregate(sum=Sum('importe_total'))
    importes = cobranzas['sum']    
    if not importes:
      return cpb.importe_total
    else:
      return (cpb.importe_total - Decimal(importes))

def cobros_cpb(idCpb):
    cpb=cpb_comprobante.objects.get(pk=idCpb)    
    #los reciobs dde el cpb es el padre
    cobranzas = cpb_cobranza.objects.filter(cpb_factura=cpb).aggregate(sum=Sum('importe_total'))
    importes = cobranzas['sum']    
    return importes

def obtener_stock(prod_ubi):     
        total_stock = cpb_comprobante_detalle.objects.filter(cpb_comprobante__estado__in=[1,2],cpb_comprobante__cpb_tipo__usa_stock=True,cpb_comprobante__empresa__id=prod_ubi.ubicacion.empresa.id,producto__id=prod_ubi.producto.id,origen_destino__id=prod_ubi.ubicacion.id).prefetch_related('cpb_comprobante__empresa','producto','ubicacion').aggregate(total=Sum(F('cantidad') *F('cpb_comprobante__cpb_tipo__signo_stock'),output_field=DecimalField()))['total'] or 0               
        return total_stock

@login_required 
def buscarDatosProd(request):                                  
   try:                          
     prod= {}
     idProd = request.GET.get('idp', '')
     idubi = request.GET.get('idubi', None)       
     idlista = request.GET.get('idlista', None)
     p = None
     coeficiente = 0
     ppedido = 0
     stock = 1
     pventa = 0
     precio_siva = 0
     costo_siva = 0
     total_iva=0
     precio_tot = 0
     pcosto = 0       
     tasa_iva = 5 #Por defecto 0.21
     pitc = 0.00
     ptasa = 0.00
     unidad = 'u.'
     prod_lista = None
     if idProd:
      p = prod_productos.objects.get(id=idProd)
      if p:
          coeficiente = p.tasa_iva.coeficiente       
          tasa_iva = p.tasa_iva.id
          unidad = p.get_unidad_display()
          if idubi:
             
              try:
                  prod_ubi = prod_producto_ubicac.objects.get(producto=p,ubicacion__id=idubi)            
              except:
                  prod_ubi = None
              if prod_ubi:
                  stock = prod_ubi.get_stock_()
                  ppedido = prod_ubi.get_reposicion()
          if idlista:
             try:
                  prod_lista = prod_producto_lprecios.objects.get(producto=p,lista_precios__id=idlista) 
             except:
                  prod_lista = None
             if prod_lista:
                  pventa = prod_lista.precio_venta
                  pcosto = prod_lista.precio_cimp           
                  pitc = prod_lista.precio_itc
                  ptasa = prod_lista.precio_tasa

     precio_siva = pventa /(1+coeficiente)
     precio_siva = Decimal(round(precio_siva,2))
     if prod_lista:
      costo_siva = prod_lista.precio_costo
     total_iva = pventa - precio_siva
     total_iva = Decimal(round(total_iva, 2))
     precio_tot = pventa
     
     prod={'precio_venta':pventa,'precio_costo':pcosto,'stock':stock,'ppedido':ppedido,'tasa_iva__id':tasa_iva,'tasa_iva__coeficiente':coeficiente
          ,'unidad':unidad,'precio_siva':precio_siva,'total_iva':total_iva,'precio_tot':precio_tot,'costo_siva':costo_siva,'pitc':pitc,'ptasa':ptasa}  
             
   except:
     prod= {}
   return HttpResponse( json.dumps(prod, cls=DjangoJSONEncoder), content_type='application/json' )     
  
def buscarPrecioProd(prod,letra,cant,precio):                                  
                                       
       coeficiente = 0
       stock = 1
       tasa_iva = 5 #Por defecto 0.21
       unidad = 'u.'
       if prod:
            coeficiente = prod.tasa_iva.coeficiente       
            tasa_iva = prod.tasa_iva.id
            unidad = prod.get_unidad_display()                        

       precio_siva = precio /(1+coeficiente)
       
       if letra=='A':
        precio = precio_siva
        importe_subtotal = (precio * cant)
        importe_iva = round(importe_subtotal * coeficiente,2)
        importe_total = round(importe_subtotal,2) + importe_iva
       else:
        precio = precio
        importe_subtotal = (precio * cant)
        importe_iva = round(importe_subtotal-(importe_subtotal/(1+coeficiente)),2)
        importe_total = round(importe_subtotal,2) 
        importe_subtotal = importe_total - importe_iva;


       prod={'precio':round(precio,2),'importe_iva':round(importe_iva,2),'importe_subtotal':round(importe_subtotal,2),'importe_total':round(importe_total,2)}  
       
   
       return prod

def buscarPrecioListaProd(p,lista):                                      
  try:
    coeficiente = 0 
    pventa = 0
    precio_siva = 0
    costo_siva = 0
    total_iva=0
    precio_tot = 0
    pcosto = 0       
    tasa_iva = 5 #Por defecto 0.21
    pitc = 0.00
    ptasa = 0.00
    unidad = 'u.'
    coeficiente = p.tasa_iva.coeficiente       
    tasa_iva = p.tasa_iva.id
    unidad = p.get_unidad_display()
    try:
        prod_lista = prod_producto_lprecios.objects.get(producto=p,lista_precios=lista) 
    except:
        prod_lista = None
    if prod_lista:
            pventa = prod_lista.precio_venta
            pcosto = prod_lista.precio_cimp           
            pitc = prod_lista.precio_itc
            ptasa = prod_lista.precio_tasa

    precio_siva = pventa /(1+coeficiente)
    precio_siva = Decimal(round(precio_siva,2))
    if prod_lista:
      costo_siva = prod_lista.precio_costo
    total_iva = pventa - precio_siva
    total_iva = Decimal(round(total_iva, 2))
    precio_tot = pventa

    prod={'precio_venta':pventa,'precio_costo':pcosto,'tasa_iva__id':tasa_iva,'tasa_iva__coeficiente':coeficiente
        ,'unidad':unidad,'precio_siva':precio_siva,'total_iva':total_iva,'precio_tot':precio_tot,'costo_siva':costo_siva,'pitc':pitc,'ptasa':ptasa}  
  except:
    prod = {}

  return prod  
@login_required 
def buscarDatosEntidad(request):                     
   lista= {}  
   try:
      id = request.GET['id']
      entidad = egr_entidad.objects.get(id=id)   
      dcto=entidad.dcto_general or 0    
      tope_cta_cte = entidad.tope_cta_cte
      lista_precios = 1
      if entidad.lista_precios_defecto:
          lista_precios = entidad.lista_precios_defecto.id   
      if tope_cta_cte>0:
          saldo = entidad.get_saldo_pendiente()
      else:
          saldo = 0    
      if not tope_cta_cte:
        saldo_sobrepaso = 0
      else:
        saldo_sobrepaso = saldo - tope_cta_cte     
      lista = {'fact_categFiscal':entidad.fact_categFiscal,'dcto_general':dcto,'saldo_sobrepaso':saldo_sobrepaso,'lista_precios':lista_precios}
   except:
    lista= {}
   return HttpResponse( json.dumps(lista, cls=DjangoJSONEncoder), content_type='application/json' )  

@login_required 
def setearLetraCPB(request):
   try:                          
    id = request.GET['id']   
    tipo = int(request.GET['tipo'])
    entidad = egr_entidad.objects.get(id=id)
    empr=empresa_actual(request)        
    #Si el tipo es de Compra(2) paso los params a la inversa
    if tipo==2:
      letra = get_letra(empr.categ_fiscal,entidad.fact_categFiscal)    
    else:
      letra = get_letra(entidad.fact_categFiscal,empr.categ_fiscal)    
    letra=list({letra})  
   except:
    letra= []
   return HttpResponse( json.dumps(letra, cls=DjangoJSONEncoder), content_type='application/json' )   

@login_required 
def setearCta_FP(request):   
   try:                          
    fp = request.GET.get('fp', None)
    cta = request.GET.get('cta',None)   
    datos= []
    if fp and not cta:        
        tipo_fp = cpb_tipo_forma_pago.objects.get(id=fp)        
        cta = tipo_fp.cuenta.id        
        datos = [int(cta)]            
    elif cta and not fp:                
        try:
            tipo_fp = cpb_cuenta.objects.get(id=cta).tipo_forma_pago       
            banco = cpb_cuenta.objects.get(id=cta).banco       
            cbu = cpb_cuenta.objects.get(id=cta).nro_cuenta_bancaria       
            if tipo_fp:
                fp= tipo_fp.id
                datos.append(int(fp))
            if banco:
                banco = banco.id
                datos.append(int(banco))            
            datos.append(cbu)

        except:
            tipo_fp = None
   except:
    datos= []
   return HttpResponse( json.dumps(datos, cls=DjangoJSONEncoder), content_type='application/json' )   

@login_required 
def ultimp_nro_cpb_ajax(request):
    ttipo = request.GET.get('cpb_tipo',0)
    letra = request.GET.get('letra','X')
    pto_vta = request.GET.get('pto_vta',0)
    entidad = request.GET.get('entidad',None)
    if ttipo=='':
      ttipo=0
    if letra=='':
      letra='X'
    if pto_vta=='':
      pto_vta=0
    if entidad=='':
      entidad=None

    try:
        tipo=cpb_tipo.objects.get(id=ttipo)        
        nro = 1    
        if tipo.usa_pto_vta == True:            
            pv = cpb_pto_vta.objects.get(numero=int(pto_vta),empresa=empresa_actual(request))                        
            ult_nro = cpb_pto_vta_numero.objects.get(cpb_tipo=tipo,letra=letra,cpb_pto_vta=pv,empresa=empresa_actual(request)).ultimo_nro
            nro = ult_nro+1                
        else:
            nro = 1                
            if entidad:
                entidad = egr_entidad.objects.get(id=entidad)
                ult_cpb = cpb_comprobante.objects.filter(entidad=entidad,cpb_tipo=tipo,letra=letra,pto_vta=int(pto_vta),empresa=empresa_actual(request)).order_by('numero').last()        
                if ult_cpb:
                        nro = ult_cpb.numero + 1        
            else:
              tipo=cpb_tipo.objects.get(id=ttipo)
              nro = tipo.ultimo_nro + 1  
    except:                        
        nro = 1  

    nro=list({nro})     
    
    return HttpResponse( json.dumps(nro, cls=DjangoJSONEncoder), content_type='application/json' )   

@login_required 
def buscarDatosCPB(request):                     
   try:                          
    id = request.GET['id']   
    saldo=saldo_cpb(id)
    cpbs=list({'saldo':saldo})  
   except:
    cpbs= []
   return HttpResponse( json.dumps(cpbs, cls=DjangoJSONEncoder), content_type='application/json' )     

@login_required 
def verifCobranza(request):                     
    cpbs = request.GET.getlist('cpbs[]')            
    cant = 0
    if cpbs:                                
        entidades = list(cpb_comprobante.objects.filter(id__in=cpbs).values_list('entidad',flat=True))
        cant=len(set(entidades))        
    
    return HttpResponse(json.dumps(cant), content_type = "application/json")

@login_required 
def verifUnificacion(request):                     
    cpbs = request.GET.getlist('cpbs[]')            
    cant = 0
    data= {}
    if cpbs: 
        comprobantes = cpb_comprobante.objects.filter(id__in=cpbs,cae=None,estado__id__lte=2,cpb_tipo__tipo__in=[1,2,3,9,21,22,23])                                       
        cant_cpbs = len(set(list(comprobantes.values_list('id',flat=True))))        
        cant_entidades = len(set(list(comprobantes.values_list('entidad',flat=True))))
        cant_cpb_tipo = len(set(list(comprobantes.values_list('cpb_tipo',flat=True))))                    
        data = {'cant_cpbs':int(cant_cpbs),'cant_entidades':int(cant_entidades),'cant_cpb_tipo':int(cant_cpb_tipo)}        
    return HttpResponse(json.dumps(data,cls=DjangoJSONEncoder), content_type = "application/json")
    
@login_required 
def presup_aprobacion(request,id,estado):
    cpb = cpb_comprobante.objects.get(pk=id) 
    cpb.presup_aprobacion=cpb_estado.objects.get(id=estado)
    cpb.save()
    messages.success(request, u'Los datos se guardaron con éxito!')               
    return HttpResponseRedirect(reverse('cpb_presup_listado'))

@login_required 
def presup_anular_reactivar(request,id,estado):
    cpb = cpb_comprobante.objects.get(pk=id) 
    cpb.estado=cpb_estado.objects.get(id=estado)    
    if int(estado)==1:
      cpb.presup_aprobacion=cpb_estado.objects.get(id=estado)
    cpb.save()
    messages.success(request, u'Los datos se guardaron con éxito!')               
    return HttpResponseRedirect(reverse('cpb_presup_listado'))
       
@login_required 
def cpb_anular_reactivar(request,id,estado,descr=None):
    cpb = cpb_comprobante.objects.get(pk=id) 
    #Si es Factura de Venta/Compra y tiene pago/cobro asociado
    
    if ((cpb.cpb_tipo.tipo not in [4,7])and cpb.tiene_cobranzas()):       
        messages.error(request, u'¡El Comprobante posee movimientos de cobro/pago asociados!.Verifique')
        return HttpResponseRedirect(cpb.get_listado())
   
     #Para cada uno de los comprobantes de Movimientos/Traspaso anulo o reactivo sus CPBS(Cheques cobrados/diferidos/depositados)
    fps = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb,mdcp_salida__isnull=False).values_list('mdcp_salida',flat=True)
    
    if (len(fps)>0):
        messages.error(request, u'¡El Comprobante posee movimientos de cobranza/depósito de Cheques asociados!. Verifique')
        return HttpResponseRedirect(cpb.get_listado())    


    state = cpb_estado.objects.get(id=estado)
    cpb.estado=state
    
    if estado==3:
        cpb.anulacion_fecha=hoy()
    else:
        cpb.anulacion_fecha=None

    if descr:
        cpb.anulacion_motivo = descr 
    cpb.save()
    

    movs = cpb_comprobante_fp.objects.filter(pk__in=fps)
    for m in movs:
        m.cpb_comprobante.estado = state
        if estado==3:
            m.cpb_comprobante.anulacion_fecha=hoy()
        else:
            m.cpb_comprobante.anulacion_fecha=None

        if descr:
            m.cpb_comprobante.anulacion_motivo = descr 
        m.cpb_comprobante.save()   

    #Para cada uno de los comprobantes del Recibo/OP recalculo su saldo (Recibos/OP anulados no suman)
    if (cpb.cpb_tipo.tipo in [4,7]):
        cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=cpb)
        for c in cobranzas:
            recalcular_saldo_cpb(c.cpb_factura.pk)

    messages.success(request, u'¡Los datos se guardaron con éxito!')
    return HttpResponseRedirect(cpb.get_listado())

@login_required 
def cpb_facturar(request,id,nro):
    try:
        cpb = cpb_comprobante.objects.get(pk=id) 
    except:
        cpb=None
    #cpb.estado=cpb_estado.objects.get(id=4)
    if cpb:                
        if nro == None:
            nro = random.randrange(0, 99999999999999, 14) 
        nro = "{num:>014}".format(num=str(nro))
        cpb.cae = nro
        cpb.cae_vto = cpb.fecha_cpb+timedelta(days=30)        
        cpb.save()   
        messages.success(request, u'Los datos se guardaron con éxito!') 
        return HttpResponseRedirect(cpb.get_listado())
    return HttpResponseRedirect(reverse('cpb_venta_listado'))

from felectronica.facturacion import facturarAFIP,consultar_cae

@login_required 
def cpb_facturar_afip(request):
    respuesta = []    
    id = request.GET.get('id', None)     
    try:
        cpb = cpb_comprobante.objects.get(pk=id) 
    except:
        cpb=None
    if cpb:
        respuesta = facturarAFIP(request,id)
        estado = respuesta.get('resultado','')
        cae = respuesta.get('cae','')
        vto_cae = respuesta.get('fecha_vencimiento',None)
        detalle = respuesta.get('detalle','')        
        nro_cpb = respuesta.get('cpb_nro','')
        if (estado=='A')and(cae!=''):            
            #cpb.estado=cpb_estado.objects.get(id=4)
            cpb.cae = cae
            cpb.cae_vto = vto_cae
            cpb.cae_errores = None
            if detalle!='':
                cpb.cae_observaciones = cpb.cae_observaciones+' '+detalle
            cpb.numero = int(nro_cpb)
        else:
            cpb.cae = None
            cpb.cae_errores = respuesta.get('errores','')
            cpb.cae_excepcion = respuesta.get('excepcion','')
            cpb.cae_traceback = respuesta.get('traceback','')
        
        cpb.cae_xml_request = respuesta.get('XmlRequest','')   
        cpb.cae_xml_response = respuesta.get('XmlResponse','')   

        cpb.save()
        messages.success(request, u'Los datos se guardaron con éxito!')

    return HttpResponse(json.dumps(respuesta,cls=DjangoJSONEncoder), content_type = "application/json")

@login_required 
def respuesta(request):
    respuesta = ['holaaa']    
    print 'holaaa'
    import time
    time.sleep(5)
    print 'chau'
    return HttpResponse(json.dumps(respuesta,cls=DjangoJSONEncoder), content_type = "application/json")

@login_required 
def cpb_facturar_afip_id(request,id):
    respuesta = []
    try:
        cpb = cpb_comprobante.objects.get(pk=id) 
    except:
        cpb=None

    if cpb:
        #cpb.estado=cpb_estado.objects.get(id=4)
        respuesta = facturarAFIP(request,id)
        estado = respuesta.get('resultado','')
        cae = respuesta.get('cae','')
        vto_cae = respuesta.get('fecha_vencimiento',None)
        detalle = respuesta.get('detalle','')
        observaciones = respuesta.get('observaciones','')
        errores = respuesta.get('errores','')
        nro_cpb = respuesta.get('cpb_nro','')
        if (estado=='A')and(cae!=''):            
            cpb.cae = cae
            cpb.cae_vto = vto_cae
            if detalle!='':
                cpb.observacion = cpb.observacion+' '+detalle
            cpb.numero = int(nro_cpb)
            cpb.save()
            messages.success(request, u'Los datos se guardaron con éxito!')

    return HttpResponse(json.dumps(respuesta,cls=DjangoJSONEncoder), content_type = "application/json")

@login_required 
def cpbs_anular(request):        
    limpiar_sesion(request)        
    id_cpbs = request.GET.getlist('id_cpb')    
    id_cpbs = cpb_comprobante.objects.filter(id__in=id_cpbs,cae=None).values_list('id',flat=True)    
    for c in id_cpbs:        
        cpb_anular_reactivar(request,c,3)    

    return HttpResponse(json.dumps(len(id_cpbs)), content_type = "application/json")

class EditarSeguimientoView(VariablesMixin,AjaxUpdateView):
    form_class = SeguimientoForm
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    template_name = 'modal/general/form_seguimiento.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        return super(EditarSeguimientoView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(EditarSeguimientoView, self).form_valid(form)

    def form_invalid(self, form):         
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):    
        initial = super(EditarSeguimientoView, self).get_initial()                      
        return initial 

# def unique_field_formset(field_name):
#     from django.forms.models import BaseInlineFormSet
#     class UniqueFieldFormSet (BaseInlineFormSet):
#         def clean(self):
#             if any(self.errors):
#                 # Don't bother validating the formset unless each form is valid on its own
#                 return
#             values = set()
#             for form in self.forms:
#                 value = form.cleaned_data[field_name]
#                 if value in values:
#                     raise forms.ValidationError('No deben repetirse productos!')
#                 values.add(value)
#     return UniqueFieldFormSet

####################################################################################
from easy_pdf.rendering import render_to_pdf_response,render_to_pdf 
from reportlab.lib import units
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from general.generarI25 import GenerarImagen
from general.base64 import encodestring,b64encode
import StringIO

def armarCodBar(cod):
    barcode = GenerarImagen(codigo=cod)
    output = StringIO.StringIO()
    barcode.save(output,format="PNG")
    data = encodestring(output.getvalue())
    return format(data)

@login_required 
def imprimirFactura(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    #puedeVerPadron(request,c.id_unidad.pk)    
    
    if not cpb:
      raise Http404            

    detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)
    detalle_totales_iva = cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=cpb)    
    
    discrimina_iva = cpb.letra == 'A'

    if cpb.condic_pago == 2:
        cobranzas = cpb_comprobante_fp.objects.filter(cpb_comprobante__cpb_cobranza_cpb__cpb_factura=cpb,cpb_comprobante__estado__pk__lt=3)
        cantidad = cobranzas.count()    
    else:
        cobranzas = None
        cantidad = 0
    
    try:
        cod_cpb = cpb_nro_afip.objects.get(cpb_tipo=cpb.cpb_tipo.tipo,letra=cpb.letra).numero_afip    
        codigo_letra = '{0:0{width}}'.format(cod_cpb,width=2)
    except:
        codigo_letra = '000'

    if cpb.letra == 'X':
        codigo_letra = '000'        
        tipo_cpb =  'REMITO X'
        leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'
           
    facturado = (cpb.cae!=None)

    cantidad = detalle_comprobante.count() + cantidad
    total_exng = cpb.importe_exento + cpb.importe_no_gravado + cpb.importe_perc_imp
    if discrimina_iva:
        total_bruto = cpb.importe_subtotal        
    else:
        total_bruto = cpb.importe_total        
    
    renglones = 20 - cantidad
    if renglones < 0:
        renglones = 0
    renglones = range(renglones)
    context = Context()    
    fecha = hoy()

    try:
      total_imp1 = cpb.importe_tasa1
      total_imp2 = cpb.importe_tasa2
      total_imp = total_imp1 + total_imp2      
    except:
      total_imp1=0
      total_imp2=0
      total_imp=0
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        config = None 
    
    sujeto_retencion = None
    

    if cpb.cpb_tipo.usa_pto_vta == True:
        c = cpb.get_pto_vta()  
        if c.leyenda and discrimina_iva:
          sujeto_retencion = u"OPERACIÓN SUJETA A RETENCIÓN"      
    else:
        c = config
    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ
    
         
    if facturado:                
        cod = ""
        cod += str(cuit).rjust(11, "0") #CUIT
        cod += str(cod_cpb).rjust(2, "0") #TIPO_CPB
        cod += str(cpb.pto_vta).rjust(4, "0") #PTO_VTA 
        cod += str(cpb.cae).rjust(14, "0") #CAE
        cod += str(cpb.cae_vto.strftime("%Y%m%d")).rjust(8, "0") #VTO_CAE
        cod += str(digVerificador(cod))                       
        codbar = armarCodBar(cod)
        codigo = cod
  
    template = 'general/facturas/factura.html'                        
    if pdf:
        return render_to_pdf(template,locals())
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirFacturaHTML(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    #puedeVerPadron(request,c.id_unidad.pk)    
    if not cpb:
      raise Http404   

    detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)
    detalle_totales_iva = cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=cpb)    
    
    discrimina_iva = cpb.letra == 'A'

    if cpb.condic_pago == 2:
        cobranzas = cpb_comprobante_fp.objects.filter(cpb_comprobante__cpb_cobranza_cpb__cpb_factura=cpb,cpb_comprobante__estado__pk__lt=3)
        cantidad = cobranzas.count()    
    else:
        cobranzas = None
        cantidad = 0
    
    try:
        cod_cpb = cpb_nro_afip.objects.get(cpb_tipo=cpb.cpb_tipo.tipo,letra=cpb.letra).numero_afip    
        codigo_letra = '{0:0{width}}'.format(cod_cpb,width=2)
    except:
        codigo_letra = '000'

    if cpb.letra == 'X':
        codigo_letra = '000'        
        tipo_cpb =  'REMITO X'
        leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'
           
    facturado = (cpb.cae!=None)

    cantidad = detalle_comprobante.count() + cantidad
    total_exng = cpb.importe_exento + cpb.importe_no_gravado
    if discrimina_iva:
        total_bruto = cpb.importe_subtotal
    else:
        total_bruto = cpb.importe_total
    renglones = 20 - cantidad
    if renglones < 0:
        renglones = 0
    renglones = range(renglones)
    context = Context()    
    fecha = datetime.now()    
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        config = None 
    
    if cpb.cpb_tipo.usa_pto_vta == True:
        c = cpb.get_pto_vta()        
    else:
        c = config
    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ

    if facturado:        
        cod = ""
        cod += str(cuit).rjust(11, "0") #CUIT
        cod += str(cod_cpb).rjust(2, "0") #TIPO_CPB
        cod += str(cpb.pto_vta).rjust(4, "0") #PTO_VTA 
        cod += str(cpb.cae).rjust(14, "0") #CAE
        cod += str(cpb.cae_vto.strftime("%Y%m%d")).rjust(8, "0") #VTO_CAE
        cod += str(digVerificador(cod))       
                
        codbar = armarCodBar(cod)
        codigo = cod
  
    template = 'general/facturas/factura.html'                        
    return render(request, template, locals())    

@login_required 
def imprimirPresupuesto(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    if not cpb:
      raise Http404   
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        config = None 
    
    c = config    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ

    detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)    
    cantidad = detalle_comprobante.count()        
    
    renglones = 20 - cantidad
    if renglones < 0:
        renglones = 0
    renglones = range(renglones)
    context = Context()    
    fecha = datetime.now()    
    discrimina_iva = cpb.letra == 'A'
    factura_X = cpb.letra == 'X'
    if discrimina_iva:
        subtotal = cpb.importe_subtotal
    else:
        subtotal = cpb.importe_total
    codigo_letra = '000'    
    leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'

    template = 'general/facturas/presupuesto.html'                        
    if pdf:
        return render_to_pdf(template,locals())
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirRemito(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    if not cpb:
      raise Http404   
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        config = None 
    
    c = config    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ      

    detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb)    
    cantidad = detalle_comprobante.count()
    leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'
    codigo_letra = '000'
    renglones = 20 - cantidad
    if renglones < 0:
        renglones = 0
    renglones = range(renglones)
    context = Context()    
    fecha = hoy()   
    tipo = 'ORIGINAL'
    template = 'general/facturas/remito.html'                        
    if pdf:
        return render_to_pdf(template,locals())
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirCobranza(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    if not cpb:
      raise Http404   
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        config = None  
    
    c = config
    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ       
    
    cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=cpb)    
    retenciones = cpb_comprobante_retenciones.objects.filter(cpb_comprobante=cpb)    
    leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'
    pagos = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb)    
    codigo_letra = '000'
    
    context = Context()    
    fecha = hoy()    
        
    template = 'general/facturas/cobranza.html'                        
    if pdf:
        return render_to_pdf(template,locals())
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirCobranzaCtaCte(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    if not cpb:
      raise Http404   
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        raise Http404   
    
    c = config
    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ   
    
    leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'
    pagos = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb)    
    codigo_letra = '000'
    retenciones = cpb_comprobante_retenciones.objects.filter(cpb_comprobante=cpb) 
    context = Context()    
    fecha = hoy()    
    
    total_ctacte = cpb_comprobante.objects.filter(entidad=cpb.entidad,pto_vta__in=pto_vta_habilitados_list(request),cpb_tipo__usa_ctacte=True,cpb_tipo__compra_venta='V'\
        ,empresa=config,estado__in=[1,2],fecha_cpb__lte=cpb.fecha_cpb).aggregate(sum=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0    
    if total_ctacte<0:
        total_ctacte=0
    
    template = 'general/facturas/cobranza_ctacte.html'                        
    if pdf:
        return render_to_pdf(template,locals())
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirPagoCtaCte(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    if not cpb:
      raise Http404   
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        raise Http404   
    
    c = config
    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ   
    
    cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=cpb,cpb_comprobante__estado__pk__lt=3)    
    leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'
    pagos = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb,cpb_comprobante__estado__pk__lt=3)    
    codigo_letra = '000'
    
    context = Context()    
    fecha = datetime.now()    
    
    total_ctacte = cpb_comprobante.objects.filter(entidad=cpb.entidad,pto_vta__in=pto_vta_habilitados_list(request),cpb_tipo__usa_ctacte=True,cpb_tipo__compra_venta='C'\
        ,empresa=config,estado__in=[1,2],fecha_cpb__lte=cpb.fecha_cpb).aggregate(sum=Sum(F('importe_total')*F('cpb_tipo__signo_ctacte'), output_field=DecimalField()))['sum'] or 0    
    if total_ctacte<0:
        total_ctacte=0
    
    template = 'general/facturas/orden_pago_ctacte.html'                        
    if pdf:
        return render_to_pdf(template,locals())
    return render_to_pdf_response(request, template, locals())

@login_required 
def imprimirPago(request,id,pdf=None):   
    cpb = cpb_comprobante.objects.get(id=id)        
    if not cpb:
      raise Http404   
    #puedeVerPadron(request,c.id_unidad.pk)    
    try:
        config = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        config = None 
    
    c = config
    
    tipo_logo_factura = c.tipo_logo_factura
    cuit = c.cuit
    ruta_logo = c.ruta_logo
    nombre_fantasia = c.nombre_fantasia
    domicilio = c.domicilio
    email = c.email
    telefono = c.telefono
    celular = c.celular
    iibb = c.iibb
    categ_fiscal = c.categ_fiscal
    fecha_inicio_activ = c.fecha_inicio_activ

    cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=cpb,cpb_comprobante__estado__pk__lt=3)    
    leyenda = u'DOCUMENTO NO VÁLIDO COMO FACTURA'
    pagos = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb,cpb_comprobante__estado__pk__lt=3)    
    codigo_letra = '000'
    
    context = Context()    
    fecha = datetime.now()    
  
    template = 'general/facturas/orden_pago.html'                        
    if pdf:
        return render_to_pdf(template,locals())
    return render_to_pdf_response(request, template, locals())

#************* EMAIL **************
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend


def verifEmail(request):                     
    id = request.POST.get('id',None)            
    email = None
    try:
      email = cpb_comprobante.objects.filter(id=id).first().entidad.get_correo()    
      if not email:
        email=''
    except:
      email=''
    return HttpResponse(json.dumps(email), content_type = "application/json")

@login_required 
def mandarEmail(request,id):   
    try:
        email = str(request.GET.get('email',''))        
        cpb = cpb_comprobante.objects.get(id=id)            
        mail_destino = []
        if not email:
          email=str(cpb.entidad.email)
        direccion = email
        if not direccion:
            messages.error(request, 'El comprobante no pudo ser enviado! (verifique la dirección de correo del destinatario)')  
            return HttpResponseRedirect(cpb.get_listado())
        mail_destino.append(direccion)
        try:
          config = empresa_actual(request)    
        except gral_empresa.DoesNotExist:
             raise ValueError

        datos = config.get_datos_mail()      
        mail_cuerpo = datos['mail_cuerpo']
        mail_servidor = datos['mail_servidor']
        mail_puerto = int(datos['mail_puerto'])
        mail_usuario = datos['mail_usuario']
        mail_password = str(datos['mail_password'])
        mail_origen = datos['mail_origen']      
       
        if cpb.cpb_tipo.tipo == 4 or cpb.cpb_tipo.tipo == 7:
            post_pdf = imprimirCobranza(request,id,True)              
        elif cpb.cpb_tipo.tipo == 5:
            post_pdf = imprimirRemito(request,id,True)          
        elif cpb.cpb_tipo.tipo == 6:
            post_pdf = imprimirPresupuesto(request,id,True)  
        else:
            post_pdf = imprimirFactura(request,id,True)  
            
        fecha = datetime.now()              
        nombre = "%s" % cpb
        image_url = request.build_absolute_uri(reverse("chequear_email",kwargs={'id': cpb.id}))
        
        html_content = get_template('general/varios/email.html').render({'mensaje': mail_cuerpo,'image_url':image_url})
                
        backend = EmailBackend(host=mail_servidor, port=mail_puerto, username=mail_usuario,password=mail_password,fail_silently=False)        
        email = EmailMessage( subject=u'%s' % (cpb.get_cpb_tipo),body=html_content,from_email=mail_origen,to=mail_destino,connection=backend)                
        email.attach(u'%s.pdf' %nombre,post_pdf, "application/pdf")
        email.content_subtype = 'html'        
        email.send()        
        cpb.fecha_envio_mail=fecha
        cpb.save()
        messages.success(request, 'El comprobante fué enviado con éxito!')
        return HttpResponseRedirect(cpb.get_listado())
    except Exception as e:
        messages.error(request, 'El comprobante no pudo ser enviado! (verifique la dirección de correo del destinatario)')  
        return HttpResponseRedirect(cpb.get_listado())

#************* BANCOS **************
class BancosView(VariablesMixin,ListView):
    model = cpb_banco
    template_name = 'general/lista_bancos.html'
    context_object_name = 'bancos'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(BancosView, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        try:            
            queryset = cpb_banco.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = cpb_banco.objects.none()
        return queryset

class BancosCreateView(VariablesMixin,AjaxCreateView):
    form_class = BancosForm
    template_name = 'modal/general/form_banco.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(BancosCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(BancosCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(BancosCreateView, self).get_initial()               
        return initial    

class BancosEditView(VariablesMixin,AjaxUpdateView):
    form_class = BancosForm
    model = cpb_banco
    pk_url_kwarg = 'id'
    template_name = 'modal/general/form_banco.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(BancosEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, u'Los datos se guardaron con éxito!')        
        return super(BancosEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(BancosEditView, self).get_initial()                      
        return initial    


@login_required
def BancosDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_banco, id=id)
        if not tiene_permiso(request,'gral_configuracion'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('bancos_listado')        

#************* MOVIMIENTOS INTERNOS **************

class MovInternosViewList(VariablesMixin,ListView):
    model = cpb_comprobante
    template_name = 'general/movimientos/movimientos_listado.html'
    context_object_name = 'movimientos'    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):         
        limpiar_sesion(self.request)        
        if not tiene_permiso(self.request,'cpb_movimientos'):
            return redirect(reverse('principal'))
        return super(MovInternosViewList, self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(MovInternosViewList, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        form = ConsultaCpbsCompras(self.request.POST or None,empresa=config,request=self.request)   
        movimientos = cpb_comprobante_fp.objects.filter(cpb_comprobante__cpb_tipo__id=13,cpb_comprobante__empresa__id__in=empresas_habilitadas(self.request)).order_by('-cpb_comprobante__fecha_cpb','-cpb_comprobante__fecha_creacion').select_related('cpb_comprobante')                
        if form.is_valid():                                
            fdesde = form.cleaned_data['fdesde']   
            fhasta = form.cleaned_data['fhasta']                                                             
            
            if fdesde:
                movimientos= movimientos.filter(cpb_comprobante__fecha_cpb__gte=fdesde)
            if fhasta:
                movimientos= movimientos.filter(cpb_comprobante__fecha_cpb__lte=fhasta)              
        else:
            mvs= movimientos.filter(cpb_comprobante__fecha_cpb__gte=inicioMesAnt(),cpb_comprobante__fecha_cpb__lte=finMes())            
            if len(mvs)==0:
                mvs = movimientos[:20]                        
            movimientos=mvs

        context['form'] = form
        context['movimientos'] = movimientos
        return context

    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

class CPBMIFPFormSet(BaseInlineFormSet): 
    pass 

CPBFPFormSet = inlineformset_factory(cpb_comprobante, cpb_comprobante_fp,form=MovimCuentasFPForm,formset=CPBMIFPFormSet, can_delete=True,extra=0,min_num=1)

class MovInternosCreateView(VariablesMixin,CreateView):
    form_class = MovimCuentasForm
    template_name = 'general/movimientos/movimientos_form.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_mov_abm'):
            return redirect(reverse('principal'))
        return super(MovInternosCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(MovInternosCreateView, self).get_initial()        
        initial['tipo_form'] = 'ALTA'        
        return initial   

    def get_form_kwargs(self,**kwargs):
        kwargs = super(MovInternosCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request              
        
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBFPFormSet.form = staticmethod(curry(MovimCuentasFPForm,request=request))
        cpb_fp = CPBFPFormSet(prefix='formFP')        
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBFPFormSet.form = staticmethod(curry(MovimCuentasFPForm,request=request))
        cpb_fp = CPBFPFormSet(self.request.POST,prefix='formFP')
        if form.is_valid() and cpb_fp.is_valid():            
            return self.form_valid(form, cpb_fp)
        else:
            return self.form_invalid(form, cpb_fp)        

    def form_valid(self, form, cpb_fp):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=2)
        self.object.estado=estado   
        self.object.letra='X'
        self.object.pto_vta=0
        self.object.numero = ultimoNro(13,self.object.pto_vta,self.object.letra)
        tipo=cpb_tipo.objects.get(pk=13)
        self.object.cpb_tipo=tipo
        self.object.empresa = empresa_actual(self.request)
        self.object.usuario = usuario_actual(self.request)        
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id               
        cpb_fp.save()
        messages.success(self.request, u'Los datos se guardaron con éxito!') 
        return HttpResponseRedirect(reverse('movimientos_listado'))

    def form_invalid(self, form,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp))

class MovInternosEditView(VariablesMixin,UpdateView):
    form_class = MovimCuentasForm
    template_name = 'general/movimientos/movimientos_form.html'
    pk_url_kwarg = 'id'    
    model = cpb_comprobante    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):            
        if not tiene_permiso(self.request,'cpb_mov_abm'):
            return redirect(reverse('principal'))        
        return super(MovInternosEditView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(MovInternosEditView, self).get_initial()        
        initial['tipo_form'] = 'EDICION'
        return initial 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)                       
        # form.fields['numero'].widget.attrs['disabled'] = True        
        CPBFPFormSet.form = staticmethod(curry(MovimCuentasFPForm,request=request))
        cpb_fp = CPBFPFormSet(instance=self.object,prefix='formFP')
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)       
        CPBFPFormSet.form = staticmethod(curry(MovimCuentasFPForm,request=request))
        cpb_fp = CPBFPFormSet(self.request.POST,instance=self.object,prefix='formFP')
        if form.is_valid() and cpb_fp.is_valid():
            return self.form_valid(form, cpb_fp)
        else:
            return self.form_invalid(form, cpb_fp)        

    def form_valid(self, form, cpb_fp):
        self.object = form.save(commit=False)                
        self.object.fecha_imputacion=self.object.fecha_cpb
        self.object.save()
        cpb_fp.instance = self.object
        cpb_fp.cpb_comprobante = self.object.id        
        cpb_fp.save()                    
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('movimientos_listado'))

    def get_form_kwargs(self):
        kwargs = super(MovInternosEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form,cpb_fp):                                                       
        return self.render_to_response(self.get_context_data(form=form,cpb_fp = cpb_fp))
    
@login_required
def MovInternosDeleteView(request, id):
    cpb = get_object_or_404(cpb_comprobante, id=id)
    if not tiene_permiso(request,'cpb_mov_abm'):
            return redirect(reverse('principal'))
    try:        
        #Movim Traspaso
        if cpb.cpb_tipo.pk == 13: 
            #traigo los fps de los recibos asociados        
            cpbs = cpb_comprobante_fp.objects.filter(mdcp_salida__id=cpb.id)
            for c in cpbs:
                c.mdcp_salida = None
                c.save()            
        cpb.delete()
        messages.success(request, u'Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'No se pudo eliminar el Comprobante!')
    return redirect('movimientos_listado')

##########################################################################

class ComprobantesVerView(VariablesMixin,DetailView):
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    context_object_name = 'cpb'
    template_name = 'general/facturas/detalle_factura.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(ComprobantesVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(ComprobantesVerView, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        cpb = self.object
        context['config'] = config
        detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb).select_related('producto','tasa_iva')       
        context['detalle_comprobante'] = detalle_comprobante
        cobranzas = cpb_comprobante_fp.objects.filter(cpb_comprobante__cpb_cobranza_cpb__cpb_factura=cpb).select_related('tipo_forma_pago')  
        context['cobranzas'] = cobranzas 
        return context

class RecibosVerView(VariablesMixin,DetailView):
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    context_object_name = 'cpb'
    template_name = 'general/facturas/detalle_recibo.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(RecibosVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(RecibosVerView, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        cpb = self.object
        context['config'] = config
        detalle = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb).select_related('tipo_forma_pago','mdcp_banco','cta_ingreso','cta_egreso')       
        context['detalle'] = detalle        
        cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=cpb,cpb_comprobante__estado__pk__lt=3).select_related('cpb_comprobante')  
        context['cobranzas'] = cobranzas 
        return context

class OrdenPagoVerView(VariablesMixin,DetailView):
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    context_object_name = 'cpb'
    template_name = 'general/facturas/detalle_op.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(OrdenPagoVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(OrdenPagoVerView, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        cpb = self.object
        context['config'] = config
        detalle = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb).select_related('tipo_forma_pago','mdcp_banco','cta_ingreso','cta_egreso')       
        context['detalle'] = detalle        
        cobranzas = cpb_cobranza.objects.filter(cpb_comprobante=cpb,cpb_comprobante__estado__pk__lt=3).select_related('cpb_comprobante')  
        context['cobranzas'] = cobranzas 
        return context

class NCNDVerView(VariablesMixin,DetailView):
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    context_object_name = 'cpb'
    template_name = 'general/facturas/detalle_ncnd.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(NCNDVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(NCNDVerView, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        cpb = self.object
        context['config'] = config
        detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb).select_related('producto','tasa_iva')       
        context['detalle_comprobante'] = detalle_comprobante 
        return context

class RemitoVerView(VariablesMixin,DetailView):
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    context_object_name = 'cpb'
    template_name = 'general/facturas/detalle_remito.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(RemitoVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(RemitoVerView, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        cpb = self.object
        context['config'] = config
        detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb).select_related('producto','tasa_iva')       
        context['detalle_comprobante'] = detalle_comprobante             
        return context

class PresupVerView(VariablesMixin,DetailView):
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    context_object_name = 'cpb'
    template_name = 'general/facturas/detalle_presup.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(PresupVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(PresupVerView, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        cpb = self.object
        context['config'] = config
        detalle_comprobante = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb).select_related('producto','tasa_iva')       
        context['detalle_comprobante'] = detalle_comprobante    

        return context

class MovimVerView(VariablesMixin,DetailView):
    model = cpb_comprobante
    pk_url_kwarg = 'id'
    context_object_name = 'cpb'
    template_name = 'general/facturas/detalle_movimiento.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        return super(MovimVerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):        
        context = super(MovimVerView, self).get_context_data(**kwargs)
        try:
            config = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            config = None 
        cpb = self.object
        context['config'] = config
        detalle = cpb_comprobante_fp.objects.filter(cpb_comprobante=cpb).select_related('tipo_forma_pago','mdcp_banco','cta_ingreso','cta_egreso')       
        context['detalle'] = detalle               
        return context

#************* PercImp **************
class PercImpView(VariablesMixin,ListView):
    model = cpb_perc_imp
    template_name = 'general/lista_perc_imp.html'
    context_object_name = 'perc_imp'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(PercImpView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        try:            
            queryset = cpb_perc_imp.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = cpb_perc_imp.objects.none()
        return queryset

class PercImpCreateView(VariablesMixin,AjaxCreateView):
    form_class = PercImpForm
    template_name = 'modal/general/form_perc_imp.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(PercImpCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(PercImpCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(PercImpCreateView, self).get_initial()               
        return initial    

class PercImpEditView(VariablesMixin,AjaxUpdateView):
    form_class = PercImpForm
    model = cpb_perc_imp
    pk_url_kwarg = 'id'
    template_name = 'modal/general/form_perc_imp.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(PercImpEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(PercImpEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(PercImpEditView, self).get_initial()                      
        return initial    

@login_required
def PercImpDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_perc_imp, id=id)
        if not tiene_permiso(request,'gral_configuracion'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('percimp_listado')   

#************* Retenciones ****
class RetencView(VariablesMixin,ListView):
    model = cpb_retenciones
    template_name = 'general/lista_retenc.html'
    context_object_name = 'retenc'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(RetencView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        try:            
            queryset = cpb_retenciones.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = cpb_retenciones.objects.none()
        return queryset

class RetencCreateView(VariablesMixin,AjaxCreateView):
    form_class = RetencForm
    template_name = 'modal/general/form_retenc.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(RetencCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(RetencCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(RetencCreateView, self).get_initial()               
        return initial    

class RetencEditView(VariablesMixin,AjaxUpdateView):
    form_class = RetencForm
    model = cpb_retenciones
    pk_url_kwarg = 'id'
    template_name = 'modal/general/form_retenc.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(RetencEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(RetencEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(RetencEditView, self).get_initial()                      
        return initial    

@login_required
def RetencDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_retenciones, id=id)
        if not tiene_permiso(request,'gral_configuracion'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('retenc_listado')   

#************* FormaPago  **************
class FPView(VariablesMixin,ListView):
    model = cpb_tipo_forma_pago
    template_name = 'general/lista_formapago.html'
    context_object_name = 'formapago'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(FPView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        try:            
            queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = cpb_tipo_forma_pago.objects.none()
        return queryset

class FPCreateView(VariablesMixin,AjaxCreateView):
    form_class = FormaPagoForm
    template_name = 'modal/general/form_formapago.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(FPCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(FPCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(FPCreateView, self).get_initial()               
        return initial    

    def get_form_kwargs(self):
        kwargs = super(FPCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class FPEditView(VariablesMixin,AjaxUpdateView):
    form_class = FormaPagoForm
    model = cpb_tipo_forma_pago
    pk_url_kwarg = 'id'
    template_name = 'modal/general/form_formapago.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(FPEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(FPEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(FPEditView, self).get_initial()                      
        return initial    

    def get_form_kwargs(self):
        kwargs = super(FPEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

@login_required
def FPDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_tipo_forma_pago, id=id)
        if not tiene_permiso(request,'gral_configuracion'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('formapago_listado')           

#************* Pto de Venta y sus Nros **************
class PtoVtaView(VariablesMixin,ListView):
    model = cpb_pto_vta
    template_name = 'general/pto_vta/pto_vta_listado.html'
    context_object_name = 'pto_vta'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(PtoVtaView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PtoVtaView, self).get_context_data(**kwargs)        
        try:            
            context['numeros'] = cpb_pto_vta_numero.objects.filter(cpb_pto_vta__in=pto_vta_habilitados(self.request)).select_related('cpb_tipo','cpb_pto_vta').order_by('cpb_pto_vta__numero','cpb_tipo__nombre','letra')
        except:
            context['numeros'] = None
        return context

    def get_queryset(self):
        try:            
            empresa = empresa_actual(self.request)  
            usuario = usuario_actual(self.request) 
            queryset = cpb_pto_vta.objects.all().order_by('numero')
            if empresa:
                queryset = queryset.filter(empresa__id__in=empresas_habilitadas(self.request))        
            try:
                if usuario.cpb_pto_vta:
                    queryset = queryset.filter(id=usuario.cpb_pto_vta.id)        
            except:     
                return queryset
            return queryset            
        except:
            queryset = cpb_pto_vta.objects.none()

        return queryset

class PtoVtaCreateView(VariablesMixin,CreateView):
    form_class = PtoVtaForm
    model = cpb_pto_vta    
    template_name = 'general/pto_vta/pto_vta_form.html'
    success_url = '/comprobantes/pto_vta'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(PtoVtaCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(PtoVtaCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(PtoVtaCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):         
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):    
        initial = super(PtoVtaCreateView, self).get_initial()
        initial['request'] = self.request                      
        return initial        

class PtoVtaEditView(VariablesMixin,UpdateView):
    form_class = PtoVtaEditForm
    model = cpb_pto_vta
    pk_url_kwarg = 'id'
    template_name = 'general/pto_vta/pto_vta_form.html'
    success_url = '/comprobantes/pto_vta'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs): 
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(PtoVtaEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(PtoVtaEditView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(PtoVtaEditView, self).get_form_kwargs()
        # kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PtoVtaEditView, self).get_context_data(**kwargs)        
        try:            
            context['nro'] = self.get_object()
        except:
            context['nro'] = None
        return context

    def form_invalid(self, form):         
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):    
        initial = super(PtoVtaEditView, self).get_initial()
        # initial['request'] = self.request                      
        return initial



@login_required 
def pto_vta_baja_reactivar(request,id):
    pto_vta = cpb_pto_vta.objects.get(pk=id) 
    pto_vta.baja = not pto_vta.baja
    pto_vta.save()   
    messages.success(request, u'Los datos se guardaron con éxito!')            
    return HttpResponseRedirect(reverse("pto_vta_listado"))

@login_required 
def pto_vta_numero_cambiar(request,id,nro):        
    pto_vta_numero = cpb_pto_vta_numero.objects.get(id=id,cpb_pto_vta__empresa=empresa_actual(request))    
    if pto_vta_numero:
            pto_vta_numero.ultimo_nro = nro    
            pto_vta_numero.save()
            messages.success(request, u'Los datos se guardaron con éxito!')               
    return HttpResponseRedirect(reverse('pto_vta_listado'))

#************* Disponibilidades **************
class DispoView(VariablesMixin,ListView):
    model = cpb_cuenta
    template_name = 'general/lista_dispo.html'
    context_object_name = 'cuenta'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(DispoView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DispoView, self).get_context_data(**kwargs)                
        return context

    def get_queryset(self):
        try:            
            queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(self.request))
        except:
            queryset = cpb_cuenta.objects.none()
        return queryset

class DispoCreateView(VariablesMixin,AjaxCreateView):
    form_class = DispoForm
    template_name = 'modal/general/form_dispo.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(DispoCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(DispoCreateView, self).form_valid(form)

    def get_initial(self):    
        initial = super(DispoCreateView, self).get_initial()               
        return initial  
    
    def get_form_kwargs(self):
        kwargs = super(DispoCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs  

class DispoEditView(VariablesMixin,AjaxUpdateView):
    form_class = DispoForm
    model = cpb_cuenta
    pk_url_kwarg = 'id'
    template_name = 'modal/general/form_dispo.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))

        if not self.get_object().modificable:
            return redirect(reverse('disponibilidades_listado'))
        return super(DispoEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return super(DispoEditView, self).form_valid(form)

    def get_initial(self):    
        initial = super(DispoEditView, self).get_initial()                
        initial['request'] = self.request        
        return initial 

    def get_form_kwargs(self):
        kwargs = super(DispoEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs    

@login_required
def DispoDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_cuenta, id=id)
        if not tiene_permiso(request,'gral_configuracion'):
                return redirect(reverse('principal'))       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('disponibilidades_listado')     

@login_required 
def dispo_baja_reactivar(request,id):
    
    cuenta = cpb_cuenta.objects.get(pk=id)
    if not cuenta.modificable:
            return redirect(reverse('disponibilidades_listado')) 
    cuenta.baja = not cuenta.baja
    cuenta.save()               
    messages.success(self.request, u'Los datos se guardaron con éxito!')
    return HttpResponseRedirect(reverse("disponibilidades_listado"))

@login_required 
def SeleccionarChequesView(request):        
    if request.method == 'POST' and request.is_ajax():                                       
        cheque = request.POST.get('cheques', None)              
        response = []
        if cheque:
            cpb_fp = cpb_comprobante_fp.objects.filter(id=int(cheque))            
            response = list(cpb_fp.values('id','tipo_forma_pago__id','cta_ingreso__id','cta_egreso__id','mdcp_fecha','mdcp_banco__id','mdcp_cheque','importe','detalle'))            
        return HttpResponse(json.dumps(response,cls=DjangoJSONEncoder), content_type='application/json')
    else:
        id_cheques = request.GET.getlist('id_ch')
        try:
            id_cheques = [int(x) for x in request.GET.getlist('id_ch')]
        except:
            id_cheques = []
        formCheques = FormCheques(request=request,id_cheques=id_cheques)
        variables = RequestContext(request, {'formCheques':formCheques})        
        return render_to_response("general/varios/buscar_cheques.html", variables)

@login_required 
def CobrarDepositarChequesView(request):        
    if request.method == 'POST' and request.is_ajax():                                                             
        formCheques = FormChequesCobro(request.POST,request=request)                                    
        response = []
        if formCheques.is_valid():
            #HAGO LA MAGIA DE CREAR MOVIM Y DEMAS            
            try:
                id_cheques = [int(x) for x in request.POST.getlist('id_fp')]
                cheques = cpb_comprobante_fp.objects.filter(id__in=id_cheques)
                total_cheques = cheques.aggregate(sum=Sum('importe'))['sum'] or 0    
            except:
                id_cheques = []
                cheques = None
                total_cheques = 0
           
            estado=cpb_estado.objects.get(pk=2)            
            tipo=cpb_tipo.objects.get(pk=13)            
            letra='X'
            pto_vta=0
            numero = ultimoNro(13,pto_vta,letra)
            cuenta = formCheques.cleaned_data['cuenta']                                                 
            fecha_cpb = formCheques.cleaned_data['fecha_cpb']
            

            detalle=u"Detalle Cobranza cheques"
            for c in cheques:
                detalle = detalle+' '+str(c.mdcp_cheque)

            movimiento = cpb_comprobante(cpb_tipo=tipo,estado=estado,pto_vta=pto_vta,letra=letra,numero=numero,fecha_cpb=fecha_cpb,importe_total=total_cheques,
                     usuario=usuario_actual(request),empresa = empresa_actual(request),fecha_imputacion=fecha_cpb)            
            movimiento.save()
            
            tipo_fp=cpb_tipo_forma_pago.objects.get(pk=1)
            cta_egreso = cpb_cuenta.objects.get(pk=4)
            recibo_fp = cpb_comprobante_fp(cpb_comprobante=movimiento,tipo_forma_pago=tipo_fp,cta_egreso=cta_egreso,cta_ingreso=cuenta,mdcp_fecha=datetime.now(),importe=total_cheques,detalle=detalle)
            recibo_fp.save()            
            
            
            for c in cheques:
                c.mdcp_salida = recibo_fp
                c.save()
            response.append({'msj':u'¡Se registró el movimiento con éxito!','estado':0})
        else:
            
            response.append({'msj':u'¡No se pudieron procesar las cobranzas!','estado':1})            
        return HttpResponse(json.dumps(response,cls=DjangoJSONEncoder), content_type='application/json')
    else:        
        try:
            id_cheques = [int(x) for x in request.GET.getlist('id_fp')]
            cheques = cpb_comprobante_fp.objects.filter(id__in=id_cheques)
            total_cheques = cheques.aggregate(sum=Sum('importe'))['sum'] or 0    
        except:
            id_cheques = []
            cheques = None
            total_cheques = 0        

        formCheques = FormChequesCobro(request=request)
        variables = RequestContext(request, {'formCheques':formCheques,'total_cheques':total_cheques})        
        return render_to_response("general/varios/cobrar_cheques.html", variables)

@login_required 
def imprimir_detalles(request):        
    limpiar_sesion(request)        
    id_cpbs = [int(x) for x in request.GET.getlist('id_cpb')]        
    cpbs_detalles = cpb_comprobante_detalle.objects.filter(cpb_comprobante__id__in=id_cpbs,cpb_comprobante__empresa = empresa_actual(request)).order_by('cpb_comprobante__fecha_cpb','producto__nombre')
    context = {}
    context = getVariablesMixin(request)  
    context['cpbs_detalles'] = cpbs_detalles
    fecha = datetime.now()        
    context['fecha'] = fecha 
    template = 'reportes/varios/rep_detalle_cpbs.html'                        
    return render_to_pdf_response(request, template, context)


###############################################################
from .forms import SaldoInicialForm
class SaldoInicialCreateView(VariablesMixin,AjaxCreateView):
    form_class = SaldoInicialForm
    template_name = 'modal/general/form_saldo_inicial.html'
    model = cpb_tipo_forma_pago

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):                    
        return super(SaldoInicialCreateView, self).dispatch(*args, **kwargs)
    
    def get_initial(self):    
        initial = super(SaldoInicialCreateView, self).get_initial()        
        return initial   

    def get_form_kwargs(self,**kwargs):
        kwargs = super(SaldoInicialCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request                      
        return kwargs
     

    def form_valid(self, form):
        self.object = form.save(commit=False)        
        estado=cpb_estado.objects.get(pk=3)
        tipo=cpb_tipo.objects.get(pk=27)
        cpb = cpb_comprobante(cpb_tipo=tipo,pto_vta=0,letra="X",numero=0,fecha_cpb=self.object.mdcp_fecha,importe_iva=0,fecha_imputacion=self.object.mdcp_fecha,
                importe_total=self.object.importe,estado=estado,usuario=usuario_actual(self.request),fecha_vto=self.object.mdcp_fecha,empresa = empresa_actual(self.request))
        cpb.save()              
        self.object.cpb_comprobante = cpb        
        self.object.save()
        messages.success(self.request, u'Los datos se guardaron con éxito!') 
        return super(SaldoInicialCreateView, self).form_valid(form)

@login_required
def SaldoInicialDeleteView(request, id):
    try:
        objeto = get_object_or_404(cpb_comprobante, id=id)       
        objeto.delete()
        messages.success(request, u'¡Los datos se guardaron con éxito!')
    except:
        messages.error(request, u'¡Los datos no pudieron eliminarse!')
    return redirect('caja_diaria')       


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
def verificar_existencia_cae(request):               
    from .forms import ImportarCPBSForm
    context = {}
    context = getVariablesMixin(request) 
    resultado = []
    if request.method == 'POST':
        form = ImportarCPBSForm(request.POST,request.FILES,request=request)
        if form.is_valid(): 
            csv_file = form.cleaned_data['archivo']
            empresa = form.cleaned_data['empresa']
           
            if not csv_file.name.endswith('.csv'):
                messages.error(request,'¡El archivo debe tener extensión .CSV!')
                return HttpResponseRedirect(reverse("verificar_existencia_cae"))
            
            if csv_file.multiple_chunks():
                messages.error(request,"El archivo es demasiado grande (%.2f MB)." % (csv_file.size/(1000*1000),))
                return HttpResponseRedirect(reverse("verificar_existencia_cae"))

            decoded_file = csv_file.read().decode("latin1").replace(",", "").replace("'", "")
            io_string = io.StringIO(decoded_file)
            reader = unicode_csv_reader(io_string)                
            
            comprobantes = cpb_comprobante.objects.filter(cpb_tipo__compra_venta='V',empresa=empresa)

            listado_cae_sistema = [c.cae for c in comprobantes]
            listado_cae_faltantes = []
            cant=0
            #Fecha Tipo  Punto de Venta  Número Desde  Número Hasta  Cód. Autorización Tipo Doc. Receptor  Nro. Doc. Receptor  
            # Denominación Receptor Tipo Cambio Moneda  Imp. Neto Gravado Imp. Neto No Gravado  Imp. Op. Exentas  IVA Imp. Total

            next(reader) #Omito el Encabezado                            
            for index,line in enumerate(reader):                      
                campos = line[0].split(";")               
                pv = campos[2].strip()
                nro = campos[3].strip()
                cae = campos[5].strip()
                if nro=='':
                    continue #Salta al siguiente                    
                
                if cae not in listado_cae_sistema:
                  listado_cae_faltantes.append(dict(cae=cae,pv=pv,nro=nro))

                
                
                cant+=1                       
            print listado_cae_faltantes
            messages.success(request, u'Se importó el archivo con éxito!<br>(%s Comprobantes verificados)'% cant )            
            resultado = listado_cae_faltantes
    else:
        form = ImportarCPBSForm(None,None,request=request)
    context['form'] = form    
    context['resultado'] = resultado 
    return render(request, 'general/varios/importar_cpbs.html',context)                