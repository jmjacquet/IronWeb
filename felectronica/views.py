# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import *
from .models import *
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView
from django.conf import settings
from django.db.models import Q,Sum,Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,redirect
from django.contrib import messages
import json
import urllib
from general.views import VariablesMixin
from .facturacion import facturarAFIP,consultar_cae,recuperar_cpb_afip,ultimo_cpb_afip,facturarAFIP_simulac
from comprobantes.models import *
from django.core.serializers.json import DjangoJSONEncoder
from .forms import RecuperarCPBS,ConsultaCPB


class CPBDatosView(VariablesMixin,TemplateView):
    template_name = 'general/cpb_afip_consulta.html'
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CPBDatosView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CPBDatosView, self).get_context_data(**kwargs)        
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCPB(self.request.POST or None,empresa=empresa,request=self.request)           
        datos_cpb=None
        cpb = None  
        if form.is_valid():                                
            cpb_tipo = form.cleaned_data['cpb_tipo']            
            pto_vta = form.cleaned_data['pto_vta']            
            numero = form.cleaned_data['numero']            
            datos_cpb=recuperar_cpb_afip(self.request,cpb_tipo.numero_afip,pto_vta,numero)                    
                        
        context['datos_cpb'] =   datos_cpb        
        context['form'] = form
        return context

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

def felectronica_json(request,id):      
   facturacion=consultar_cae(id)
   return HttpResponse( json.dumps(facturacion,cls=DjangoJSONEncoder), content_type='application/json' ) 

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
    from copy import deepcopy

    context = {}
    context = VariablesMixin().get_context_data(request=request)
    resultado = []
    if request.method == 'POST':
        form = ImportarCPBSForm(request.POST,request.FILES,request=request)
        if form.is_valid():      

            csv_file = form.cleaned_data['archivo']
            empresa = form.cleaned_data['empresa']
            migra = form.cleaned_data['migra']
           
            if not csv_file.name.endswith('.csv'):
                messages.error(request,'¡El archivo debe tener extensión .CSV!')
                return HttpResponseRedirect(reverse("verificar_existencia_cae"))
            
            if csv_file.multiple_chunks():
                messages.error(request,"El archivo es demasiado grande (%.2f MB)." % (csv_file.size/(1000*1000),))
                return HttpResponseRedirect(reverse("verificar_existencia_cae"))

            decoded_file = csv_file.read().decode("latin1").replace(",", ".").replace("'", "")
            io_string = io.StringIO(decoded_file)
            reader = unicode_csv_reader(io_string)                
            
            comprobantes = cpb_comprobante.objects.filter(cpb_tipo__compra_venta='V',empresa=empresa,cae__isnull=False)

            listado_cae_sistema = [c.cae.strip() for c in comprobantes]
            listado_cae_faltantes = []
            cant=0
            #Fecha Tipo  Punto de Venta  Número Desde  Número Hasta  Cód. Autorización Tipo Doc. Receptor  Nro. Doc. Receptor  
            # Denominación Receptor Tipo Cambio Moneda  Imp. Neto Gravado Imp. Neto No Gravado  Imp. Op. Exentas  IVA Imp. Total

            next(reader) #Omito el Encabezado Gral                            
            next(reader) #Omito el Encabezado de las columnas                           
            for index,line in enumerate(reader):                      
                campos = line[0].split(";")               
                fecha=campos[0].strip()
                if fecha=='':
                    fecha=None
                else:
                    fecha = datetime.strptime(fecha, "%d/%m/%Y").date()   #fecha_nacim             
                tipo = campos[1].strip()
                pv = int(campos[2].strip())
                nro = int(campos[3].strip())
                cae = campos[5].strip()                

                if nro=='':
                    continue #Salta al siguiente                    
                
                if cae not in listado_cae_sistema:
                  tdoc = campos[6].strip()
                  nrodoc = campos[7].strip()
                  receptor = campos[8].strip()

                  imp_neto_g = campos[11].strip()
                  imp_neto_nograv = campos[12].strip()
                  imp_exento = campos[13].strip()
                  imp_iva = campos[14].strip()
                  imp_total = campos[15].strip()
                  listado_cae_faltantes.append(dict(fecha=fecha,tipo=tipo,cae=cae,pv=pv,nro=nro,tdoc=tdoc,nrodoc=nrodoc,receptor=receptor,imp_neto_g=imp_neto_g,\
                                                    imp_neto_nograv=imp_neto_nograv,imp_exento=imp_exento,imp_iva=imp_iva,imp_total=imp_total))
                
                cant+=1                       

            if migra=='S':
              for l in listado_cae_faltantes:
                try:                  
                  nro = l['nro']
                  nro_sig=nro+1
                  cae = l['cae']
                  pv=l['pv']
                  imp_total = l['imp_total']
                  tipo_afip = int(l['tipo'].split('-')[0])
                  tipo_cpb_afip = cpb_nro_afip.objects.filter(numero_afip=tipo_afip).first()
                  letra,t = tipo_cpb_afip.letra,tipo_cpb_afip.cpb_tipo                  
                  cpb_sig = cpb_comprobante.objects.filter(numero=nro_sig,pto_vta=pv,importe_total=imp_total,letra=letra,cpb_tipo__tipo=t).first()
                  cpb_sig_det = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb_sig)
                  #import pdb; pdb.set_trace()
                  datos=recuperar_cpb_afip(request,tipo_afip,pv,nro)
                  if cpb_sig:
                    cpb_creado = deepcopy(cpb_sig)
                    cpb_creado.id = None                  
                    cpb_creado.numero = nro                  
                    cpb_creado.cae = cae
                    cpb_creado.cae_vto = datos['fecha_vencimiento']
                    cpb_creado.saldo = 0
                    cpb_creado.estado = cpb_estado.objects.get(pk=2)
                    cpb_creado.save()
                    
                    for d in cpb_sig_det:
                      d_new = deepcopy(d)
                      d_new.id = None
                      d_new.cantidad = 0
                      d_new.cpb_comprobante = cpb_creado
                      d_new.save()
                    
                    coeficientes=cpb_sig_det.filter(tasa_iva__id__gt=2).values('tasa_iva').annotate(importe_total=Sum('importe_iva'),importe_base=Sum('importe_subtotal'))
                    for cc in coeficientes:
                      tasa = gral_tipo_iva.objects.get(pk=cc['tasa_iva'])       
                      cpb_ti = cpb_comprobante_tot_iva(cpb_comprobante=cpb_creado,tasa_iva=tasa,importe_total=cc['importe_total'],importe_base=cc['importe_base'])
                      cpb_ti.save()
                    
                except Exception as e:
                  pass

                  #if cpb_sig:
              tot=len(listado_cae_faltantes)
              messages.success(request, u'Se regeneraron %s CPBs faltantes con éxito! (%s Comprobantes verificados)'%(tot,cant))            
            else:
              messages.success(request, u'Se importó el archivo con éxito! (%s Comprobantes verificados)'% cant )            
            resultado = listado_cae_faltantes
    else:
        form = ImportarCPBSForm(None,None,request=request)
    context['form'] = form    
    context['resultado'] = resultado 
    return render(request, 'general/varios/importar_cpbs.html',context)                

def listar_cpbs_afip_faltantes(request):    
    pv = request.GET.get('pv', None)     
    letra = request.GET.get('letra', '')
    inicio = int(request.GET.get('inicio', 1))
    fin = request.GET.get('fin', None)
    lista_sistema = []
    if pv:
        try:
            cpbs = cpb_comprobante.objects.filter(cpb_tipo__compra_venta='V',letra=letra,pto_vta=pv,cae__isnull=False).order_by('-numero')
            if not fin:
              fin = int(cpbs.first().numero)
            else:
              fin = int(fin)
            cpbs = list(set([int(x.numero) for x in cpbs]))
            lista_optima = range(inicio,fin+1)        
            lista_sistema = [int(x) for x in lista_optima if int(x) not in cpbs]
            lista_facturas = [recuperar_cpb_afip]
        except:
            cpbs=None
        
        # print lista_optima,lista_sistema
        return HttpResponse(json.dumps(lista_sistema,cls=DjangoJSONEncoder), content_type='application/json' )  
        
    else:
        return HttpResponse('No existe el PV!')      


class recuperar_cpbs_afip(VariablesMixin,TemplateView):
    template_name = 'general/varios/recuperar_cpbs_afip.html'
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(recuperar_cpbs_afip, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(recuperar_cpbs_afip, self).get_context_data(**kwargs)        
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = RecuperarCPBS(self.request.POST or None,empresa=empresa,request=self.request)           
        resultado,lista_faltantes = [],[]
        cpbs = None          
        if form.is_valid():                                
            from copy import deepcopy
            cpb_tipo = form.cleaned_data['cpb_tipo']            
            pto_vta = form.cleaned_data['pto_vta']                        
            generar = form.cleaned_data['generar']            
            if generar=='':
              generar=2
            letra = cpb_tipo.letra
            tipo = cpb_tipo.cpb_tipo
            tipo_afip = cpb_tipo.numero_afip
            cpbs = cpb_comprobante.objects.filter(cpb_tipo=tipo,letra=letra,pto_vta=pto_vta,cae__isnull=False)
            id_cpbs = sorted(list(set([int(x.numero) for x in cpbs])))            
            if id_cpbs:
              utimo_cpb=int(ultimo_cpb_afip(self.request,tipo_afip,pto_vta))
              lista_optima = range(id_cpbs[0],utimo_cpb)        
              lista_faltantes = [x for x in lista_optima if x not in id_cpbs]
            # data = {                        
            # 'cae': cae,
            # 'fecha_vencimiento': fecha_vencimiento,
            # 'cpb_nro':cpb_nro,
            # 'resultado':resultado,
            # 'motivo':motivo,
            # 'reproceso':reproceso,
            # 'observaciones' : observaciones,
            # 'concepto':concepto,
            # 'tipo_cbte': tipo_cpb,
            # 'punto_vta':pto_vta,   
            # 'fecha_cbte': fecha_cbte,
            # 'imp_total': imp_total,
            # 'imp_tot_conc': imp_tot_conc,
            # 'imp_neto': imp_neto,
            # 'imp_op_ex': imp_op_ex,
            # 'imp_trib': imp_trib,
            # 'imp_iva': imp_iva,    
            # 'moneda_id': moneda_id,
            # 'moneda_ctz': moneda_ctz,    
            # 'detalle':detalle,
            # 'ult_nro':ult_nro,
            # 'errores':errores,
            # 'factura':factura,
            # }
            if lista_faltantes:
              for l in lista_faltantes:
                datos=recuperar_cpb_afip(self.request,tipo_afip,pto_vta,l)
                if datos:
                  #busco el cpb relacionado superior
                  cpb = cpbs.filter(numero=l+1).first()
                  datos.update(cpb_sistema=cpb)
                  resultado.append(datos)
                  if int(generar)==1:
                    try:
                      cpb_sig = cpb
                      cpb_sig_det = cpb_comprobante_detalle.objects.filter(cpb_comprobante=cpb_sig)
                      #import pdb; pdb.set_trace()
                      if cpb_sig:
                        cpb_creado = deepcopy(cpb_sig)
                        cpb_creado.id = None                  
                        cpb_creado.numero = l                  
                        cpb_creado.cae = datos['cae']
                        cpb_creado.cae_vto = datos['fecha_vencimiento']
                        cpb_creado.saldo = 0
                        cpb_creado.estado = cpb_estado.objects.get(pk=2)
                        cpb_creado.save()
                        
                        for d in cpb_sig_det:
                          d_new = deepcopy(d)
                          d_new.id = None
                          d_new.cantidad = 0
                          d_new.cpb_comprobante = cpb_creado
                          d_new.save()
                        
                        coeficientes=cpb_sig_det.filter(tasa_iva__id__gt=2).values('tasa_iva').annotate(importe_total=Sum('importe_iva'),importe_base=Sum('importe_subtotal'))
                        for cc in coeficientes:
                          tasa = gral_tipo_iva.objects.get(pk=cc['tasa_iva'])       
                          cpb_ti = cpb_comprobante_tot_iva(cpb_comprobante=cpb_creado,tasa_iva=tasa,importe_total=cc['importe_total'],importe_base=cc['importe_base'])
                          cpb_ti.save()
                      else:
                        #tengo que generarlo con los datos que trago de la factura de afip

                        # cpb_creado = cpb_comprobante()
                        # cpb_creado.numero = l                  
                        # cpb_creado.cae = datos['cae']
                        # cpb_creado.cae_vto = datos['fecha_vencimiento']
                        # cpb_creado.saldo = 0
                        # cpb_creado.estado = cpb_estado.objects.get(pk=2)
                        # cpb_creado.save()

                        # for d in cpb_sig_det:
                        #   d_new = cpb_comprobante_detalle(d)
                        #   d_new.id = None
                        #   d_new.cantidad = 0
                        #   d_new.cpb_comprobante = cpb_creado
                        #   d_new.save()
                        
                        
                        pass
                    except Exception as e:
                      resultado.append(e)
                        
        context['resultado'] =   resultado        
        context['form'] = form
        return context

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)




@login_required 
def cpb_facturar_simulacion(request):
    respuesta = []    
    id = request.GET.get('id', None)     
    try:
      cpb = cpb_comprobante.objects.get(pk=id) 
    except:
      cpb=None
    if cpb:
      respuesta = facturarAFIP_simulac(request,id)      
          
    return HttpResponse(json.dumps(respuesta,cls=DjangoJSONEncoder), content_type = "application/json")

@login_required 
def datos_afip(request):
    from .facturacion import datos_afip
    respuesta = []    
    cuit = request.GET.get('cuit', None)     
    data = datos_afip(request,cuit) 
    # try:
    #   data = datos_afip(request,cuit) 
    # except:
    #   data=None    
          
    return HttpResponse(json.dumps(data,cls=DjangoJSONEncoder), content_type = "application/json")    