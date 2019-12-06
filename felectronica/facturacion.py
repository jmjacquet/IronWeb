# coding: utf8
# try something like

import os
import datetime
import time
from django.conf import settings

CERTIFICADOS_PATH = settings.CERTIFICADOS_PATH


from comprobantes.models import *
from general.utilidades import *


def validarAFIP(idCpb):
    try:
        cpb=cpb_comprobante.objects.get(pk=idCpb)
    except:
        cpb = None
        return 'Comprobante Incorrecto'    

    if ((cpb.letra=='A')and(cpb.entidad.fact_categFiscal==1)and(cpb.entidad.tipo_doc!=80)):
        return u'Las facturas A solo pueden ser emitidas a Responsables Inscriptos, consignando el CUIT válido y registrado (tipo_doc=80)'

    if (cpb.importe_total!= (cpb.importe_no_gravado+cpb.importe_iva+cpb.importe_gravado+cpb.importe_exento+cpb.importe_perc_imp)):
        return 'La suma de importes del Comprobante es Incorrecta'        

    return ''


def _autenticar(request,crt,key,service="wsfe", ttl=60*60*10,cuit=None):
    "Obtener el TA"

    from pyafipws import wsaa

    CUIT = cuit
    CERTIFICATE = crt
    PRIVATE_KEY = key
    
    empresa = empresa_actual(request)
    HOMO = empresa.homologacion

    if HOMO:
        WSDL = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
        WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
    else:
        WSDL="https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"    
        WSAA_URL = "https://wsaa.afip.gov.ar/ws/services/LoginCms"    
    
    if service not in ("wsfe","wsfev1","wsmtxca","wsfex","wsbfe"):
        raise HTTP(500,"Servicio %s incorrecto" % service)
    
    # verifico archivo temporal con el ticket de acceso
    TA = os.path.join(CERTIFICADOS_PATH, "TA-%s-%s.xml" % (cuit,service))
    ttl = 60*60*5
    if not os.path.exists(TA) or os.path.getmtime(TA)+(ttl)<time.time():
        # solicito una nueva autenticación
        # wsaa = pyafipws.wsaa
        cert = os.path.join(CERTIFICADOS_PATH, CERTIFICATE)
        privatekey = os.path.join(CERTIFICADOS_PATH, PRIVATE_KEY)
        # creo un ticket de requerimiento de acceso
        # cambiando a wsfe si es wsfe(v_)
        if "wsfev" in service: service = "wsfe"
        tra = wsaa.create_tra(service=service,ttl=ttl)

        # firmo el ticket de requerimiento de acceso
        cms = wsaa.sign_tra(str(tra),str(cert),str(privatekey))


        # llamo al webservice para obtener el ticket de acceso
        ta_string = wsaa.call_wsaa(cms,WSAA_URL,trace=False)
        # guardo el ticket de acceso obtenido:
        open(TA,"w").write(ta_string)


    # procesar el ticket de acceso y extraer TOKEN y SIGN:
    # from gluon.contrib.pysimplesoap.simplexml import SimpleXMLElement
    
    # agregar librería modificada para aceptar etiquetas vacías
    from pysimplesoap.simplexml import SimpleXMLElement
        
    ta_string=open(TA).read()
    ta = SimpleXMLElement(ta_string)
    token = str(ta.credentials.token)
    sign = str(ta.credentials.sign)   
    return token, sign




from django.http import JsonResponse
from pyafipws.wsfev1 import WSFEv1

def consultar_cae(request,idcpb):               
    
    empresa = empresa_actual(request)
    HOMO = empresa.homologacion

    if HOMO:
        WSDL = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
        WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
    else:
        WSDL="https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"    
        WSAA_URL = "https://wsaa.afip.gov.ar/ws/services/LoginCms"    


    #Traigo el comprobante
    token = ''
    sign = ''
    cae = ''
    fecha_vencimiento = ''
    cpb_nro = ''
    resultado = ''
    motivo = ''
    reproceso = ''
    observaciones = ''
    concepto = ''
    tipo_cpb = ''
    pto_vta = ''
    fecha_cbte = ''
    imp_total = ''
    imp_tot_conc = ''
    imp_neto = ''
    imp_op_ex = ''
    imp_trib = ''
    imp_iva = ''
    moneda_id = ''
    moneda_ctz = ''
    detalle = ''
    ult_nro = ''
    errores = ''
        
    data = {            
        'token':token,
        'sign':sign,
        'cae': cae,
        'fecha_vencimiento': fecha_vencimiento,
        'cpb_nro':cpb_nro,
        'resultado':resultado,
        'motivo':motivo,
        'reproceso':reproceso,
        'observaciones' : observaciones,
        'concepto':concepto,
        'tipo_cbte': tipo_cpb,
        'punto_vta':pto_vta,   
        'fecha_cbte': fecha_cbte,
        'imp_total': imp_total,
        'imp_tot_conc': imp_tot_conc,
        'imp_neto': imp_neto,
        'imp_op_ex': imp_op_ex,
        'imp_trib': imp_trib,
        'imp_iva': imp_iva,    
        'moneda_id': moneda_id,
        'moneda_ctz': moneda_ctz,    
        'detalle':detalle,
        'ult_nro':ult_nro,
        'excepcion':'',     
        'traceback':'',
        'XmlRequest':'',
        'XmlResponse':'',
        'appserver_status':'',
        'dbserver_status':'',
        'authserver_status':'',
        'errores':errores,
        } 
    try:
        cpb=cpb_comprobante.objects.get(id=idcpb)       
    except:
        cpb = None
       
    if not cpb:        
        data['errores']=u'¡El comprobante no es válido!'
        return data

    try:
        cpb_nafip = cpb.get_nro_afip()
        
        tipo_cpb = cpb_nafip     
        pto_vta = int(cpb.pto_vta)
        nro_cpb = int(cpb.numero)
    except:
        data['errores']=u'¡El comprobante no es válido!'
        return data
    
    #Si el pto_vta no admite factura electrónica    
    if not cpb.get_pto_vta().fe_electronica:
        data['errores']=u'¡El comprobante no es válido!'
        return data
    
    appserver_status = ''
    dbserver_status = ''
    authserver_status = ''
    #try:
    fecha = datetime.now().strftime("%Y%m%d")
    wsfev1 = WSFEv1()
    
    wsfev1.Conectar(wsdl=WSDL)
    
    cuit = cpb.get_pto_vta().cuit
    # cuit = 30714843571
    wsfev1.Cuit = cuit

    if HOMO:
        crt = "COPYFAST_PRUEBA.crt"
        key= "COPYFAST_PRUEBA.key"
    else:
        try:
            #crt = "COPYFAST_PRUEBA.crt"
            crt = cpb.get_pto_vta().fe_crt
        except:
            data['errores']=u'¡fe_crt no es válido!'
            return data
        try:
            key= cpb.get_pto_vta().fe_key
            #key= "COPYFAST_PRUEBA.key"
        except:
            data['errores']=u'¡fe_key no es válido!'
            return data

    wsfev1.Token, wsfev1.Sign = _autenticar(request,crt=crt,key=key,cuit=cuit)        

    wsfev1.Dummy()
    appserver_status = wsfev1.AppServerStatus
    dbserver_status = wsfev1.DbServerStatus
    authserver_status = wsfev1.AuthServerStatus
    # except:
    #     data['excepcion']=wsfev1.Excepcion
    #     data['traceback']=wsfev1.Traceback
    #     data['XmlRequest']=wsfev1.XmlRequest
    #     data['XmlResponse']=wsfev1.XmlResponse
    #     data['appserver_status']=appserver_status
    #     data['dbserver_status']=dbserver_status
    #     data['authserver_status']=authserver_status
    #     data['errores']=u'¡Falló la comunicación con los servidores de AFIP!'
    #     return data      
        
    try:
        wsfev1.CompConsultar(tipo_cpb, pto_vta, nro_cpb) 
                
        cpb_nro = wsfev1.CbteNro
        fecha_vencimiento = wsfev1.Vencimiento    
        resultado = wsfev1.Resultado
        motivo = wsfev1.Motivo
        reproceso = wsfev1.Reproceso
        imp_total = wsfev1.ImpTotal
        cae = wsfev1.CAE       
        observaciones = wsfev1.Observaciones    
        fecha_cbte = wsfev1.FechaCbte
        concepto = wsfev1.ObtenerCampoFactura('concepto')    
        imp_tot_conc = wsfev1.ObtenerCampoFactura('imp_tot_conc')
        imp_neto = wsfev1.ImpNeto
        imp_op_ex = wsfev1.ImpOpEx
        imp_trib = wsfev1.ImpTrib
        imp_iva = wsfev1.ImpIVA      
        moneda_id = wsfev1.ObtenerCampoFactura('moneda_id')
        moneda_ctz = wsfev1.ObtenerCampoFactura('moneda_ctz')
        
        errores=wsfev1.ErrMsg


        detalle = ''
        
        if cae=='':        
            detalle= "La página esta caida o la respuesta es inválida"
        elif (wsfev1.Resultado!="A"):
            detalle= "No se asignó CAE (Rechazado). Motivos:%s" %wsfev1.Motivo
        elif wsfev1.Observaciones!="":
            detalle = "Se asignó CAE pero con advertencias. Motivos: %s" %wsfev1.Observaciones   

        fecha_vencimiento = None
        fecha_cbte = None
        EmisionTipo = ''
        if cae:
            fecha_vencimiento = datetime.strptime(wsfev1.Vencimiento,'%Y%m%d')
            EmisionTipo = wsfev1.EmisionTipo        
            fecha_cbte =datetime.strptime(wsfev1.FechaCbte,'%Y%m%d')              
        
        ult_nro = long(wsfev1.CompUltimoAutorizado(tipo_cpb, pto_vta) or 0)

        data = {            
            'token':token,
            'sign':sign,
            'cae': cae,
            'fecha_vencimiento': fecha_vencimiento,
            'cpb_nro':cpb_nro,
            'resultado':resultado,
            'motivo':motivo,
            'reproceso':reproceso,
            'observaciones' : observaciones,
            'concepto':concepto,
            'tipo_cbte': tipo_cpb,
            'punto_vta':pto_vta,   
            'fecha_cbte': fecha_cbte,
            'imp_total': imp_total,
            'imp_tot_conc': imp_tot_conc,
            'imp_neto': imp_neto,
            'imp_op_ex': imp_op_ex,
            'imp_trib': imp_trib,
            'imp_iva': imp_iva,    
            'moneda_id': moneda_id,
            'moneda_ctz': moneda_ctz,    
            'detalle':detalle,
            'ult_nro':ult_nro,
            'excepcion':wsfev1.Excepcion,     
            'traceback':wsfev1.Traceback,
            'XmlRequest':wsfev1.XmlRequest,
            'XmlResponse':wsfev1.XmlResponse,
            'appserver_status':appserver_status,
            'dbserver_status':dbserver_status,
            'authserver_status':authserver_status,
            'errores':errores,
            }
    except:
        if wsfev1:
            data = {
            'token':token,
            'sign':sign,
            'cae': cae,
            'fecha_vencimiento': fecha_vencimiento,
            'cpb_nro':cpb_nro,
            'resultado':resultado,
            'motivo':motivo,
            'reproceso':reproceso,
            'observaciones' : observaciones,
            'concepto':concepto,
            'tipo_cbte': tipo_cpb,
            'punto_vta':pto_vta,   
            'fecha_cbte': fecha_cbte,
            'imp_total': imp_total,
            'imp_tot_conc': imp_tot_conc,
            'imp_neto': imp_neto,
            'imp_op_ex': imp_op_ex,
            'imp_trib': imp_trib,
            'imp_iva': imp_iva,    
            'moneda_id': moneda_id,
            'moneda_ctz': moneda_ctz,    
            'detalle':detalle,
            'ult_nro':ult_nro,
            'excepcion':wsfev1.Excepcion,     
            'traceback':wsfev1.Traceback,
            'XmlRequest':wsfev1.XmlRequest,
            'XmlResponse':wsfev1.XmlResponse,
            'appserver_status':appserver_status,
            'dbserver_status':dbserver_status,
            'authserver_status':authserver_status,
            'errores':errores,
            }                   

    return data


def facturarAFIP(request,idCpb):        
    empresa = empresa_actual(request)
    HOMO = empresa.homologacion

    if HOMO:
        WSDL = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
        WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
    else:
        WSDL="https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"    
        WSAA_URL = "https://wsaa.afip.gov.ar/ws/services/LoginCms"    
    token = ''
    sign = ''
    cae = ''
    fecha_vencimiento = ''
    cpb_nro = ''
    resultado = ''
    motivo = ''
    reproceso = ''
    observaciones = ''
    concepto = ''
    tipo_cpb = ''
    pto_vta = ''
    fecha_cbte = ''
    imp_total = ''
    imp_tot_conc = ''
    imp_neto = ''
    imp_op_ex = ''
    imp_trib = ''
    imp_iva = ''
    moneda_id = ''
    moneda_ctz = ''
    detalle = ''
    ult_nro = ''
    errores = ''
        
    data = {            
        'token':token,
        'sign':sign,
        'cae': cae,
        'fecha_vencimiento': fecha_vencimiento,
        'cpb_nro':cpb_nro,
        'resultado':resultado,
        'motivo':motivo,
        'reproceso':reproceso,
        'observaciones' : observaciones,
        'concepto':concepto,
        'tipo_cbte': tipo_cpb,
        'punto_vta':pto_vta,   
        'fecha_cbte': fecha_cbte,
        'imp_total': imp_total,
        'imp_tot_conc': imp_tot_conc,
        'imp_neto': imp_neto,
        'imp_op_ex': imp_op_ex,
        'imp_trib': imp_trib,
        'imp_iva': imp_iva,    
        'moneda_id': moneda_id,
        'moneda_ctz': moneda_ctz,    
        'detalle':detalle,
        'ult_nro':ult_nro,
        'excepcion':'',     
        'traceback':'',
        'XmlRequest':'',
        'XmlResponse':'',
        'appserver_status':'',
        'dbserver_status':'',
        'authserver_status':'',
        'errores':errores,
        }                
    
    try:
        cpb=cpb_comprobante.objects.get(pk=idCpb)
    except:
        cpb = None

    if not cpb:
        data['errores']=u'¡El comprobante no es válido!'
        return data

    resultado=validarAFIP(idCpb)
    if resultado!='':
        data['errores']=resultado
        return data        
      
    cpb_nafip = cpb.get_nro_afip()
    #Traigo el comprobante
    try:
        cpb_nafip = cpb.get_nro_afip()    
        tipo_cpb = cpb_nafip     
        pto_vta = int(cpb.pto_vta)
        nro_cpb = int(cpb.numero)
    except:
        data['errores']=u'¡El comprobante no es válido!'
        return data
    
    #Si el pto_vta no admite factura electrónica
    if not cpb.get_pto_vta().fe_electronica:
        data['errores']=u'¡El Punto de Venta seleccionado no admite factura electrónica!'
        return data         

    appserver_status = ''
    dbserver_status = ''
    authserver_status = ''
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        wsfev1 = WSFEv1()
        wsfev1.Conectar(wsdl=WSDL)
        f = cpb
        cuit = cpb.get_pto_vta().cuit

        # cuit = 30714843571
        wsfev1.Cuit = cuit
        #wsfev1.Cuit = 30715026178
        
        if HOMO:
            crt = "COPYFAST_PRUEBA.crt"
            key= "COPYFAST_PRUEBA.key"
        else:
            try:
                #crt = "COPYFAST_PRUEBA.crt"
                crt = cpb.get_pto_vta().fe_crt
            except:
                data['errores']=u'¡fe_crt no es válido!'
                return data
            try:
                key= cpb.get_pto_vta().fe_key
                #key= "COPYFAST_PRUEBA.key"
            except:
                data['errores']=u'¡fe_key no es válido!'
                return data


        wsfev1.Token, wsfev1.Sign = _autenticar(request,crt=crt,key=key,cuit=cuit)            
        token=wsfev1.Token
        sign=wsfev1.Sign

        cbte_nro = long(wsfev1.CompUltimoAutorizado(tipo_cpb, pto_vta) or 0)      


        wsfev1.Dummy()
        appserver_status = wsfev1.AppServerStatus
        dbserver_status = wsfev1.DbServerStatus
        authserver_status = wsfev1.AuthServerStatus
        
    except:
        data['excepcion']=wsfev1.Excepcion
        data['traceback']=wsfev1.Traceback
        data['XmlRequest']=wsfev1.XmlRequest
        data['XmlResponse']=wsfev1.XmlResponse
        data['appserver_status']=appserver_status
        data['dbserver_status']=dbserver_status
        data['authserver_status']=authserver_status
        data['errores']=u'¡Falló la comunicación con los servidores de AFIP / Certificados NO VALIDOS!'
        return data         

    try:
        fecha = datetime.now().strftime("%Y%m%d")
        concepto = 3 #Productos y Servicios
        tipo_doc = f.entidad.tipo_doc


        if not tipo_doc:
            data['errores']=u'¡Debe cargar un tipo de Documento válido!'
            return data         
        
        if tipo_doc == 99:
            nro_doc = 0
        elif tipo_doc == 96:
            nro_doc = f.entidad.nro_doc
        elif tipo_doc == 80:    
            nro_doc = f.entidad.fact_cuit
        else:
            nro_doc = f.entidad.fact_cuit

        if nro_doc == '':
            data['errores']=u'¡Debe cargar un Nº de Documento válido!'
            data['excepcion']=wsfev1.Excepcion
            data['traceback']=wsfev1.Traceback
            data['XmlRequest']=wsfev1.XmlRequest
            data['XmlResponse']=wsfev1.XmlResponse
            data['appserver_status']=appserver_status
            data['dbserver_status']=dbserver_status
            data['authserver_status']=authserver_status
            return data        

        cbt_desde = cbte_nro + 1; cbt_hasta = cbte_nro + 1
        
        #Informar o no IVA
        #Datos de http://www.sistemasagiles.com.ar/trac/wiki/ManualPyAfipWs#FacturaCMonotributoExento
        if f.letra == 'C':
            imp_total = f.importe_total
            imp_tot_conc = 0
            imp_neto = f.importe_total
            imp_iva = 0
            imp_trib = 0
            imp_op_ex = 0
        else:
            imp_total = f.importe_total
            imp_tot_conc = f.importe_no_gravado
            imp_neto = f.importe_gravado
            imp_iva = f.importe_iva
            imp_trib = f.importe_perc_imp
            imp_op_ex = f.importe_exento
        
        fecha_cbte = f.fecha_cpb.strftime("%Y%m%d")
        fecha_venc_pago = f.fecha_cpb.strftime("%Y%m%d")
        
        # Fechas del período del servicio facturado (solo si concepto = 1?)
        fecha_serv_desde = f.fecha_cpb.strftime("%Y%m%d")
        fecha_serv_hasta = f.fecha_cpb.strftime("%Y%m%d")
        moneda_id = 'PES'; moneda_ctz = '1.000'

        # Inicializo la factura interna con los datos de la cabecera
        wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cpb, pto_vta,
            cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
            imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
            fecha_serv_desde, fecha_serv_hasta,moneda_id, moneda_ctz)
        
        if f.letra != 'C':
            #Traigo los coeficientes de IVA
                # iva_id: código Alícuota de IVA (según tabla de parámetros AFIP)
                # base_imp: base imponible (importe)
                # importe_iva: importe liquidado (base_imp por alicuota)        
            cpb_iva = cpb_comprobante_tot_iva.objects.filter(cpb_comprobante=f)
            for c in cpb_iva:            
                id = c.tasa_iva.id_afip # 21%
                base_imp = c.importe_base
                importe = c.importe_total
                wsfev1.AgregarIva(id, base_imp, importe) 

            
            #Traigo las percepciones de IVA
                # tributo_id: código tipo de impuesto (según tabla de parámetros AFIP)
                # desc: descripción del tributo (por ej. "Impuesto Municipal Matanza")
                # base_imp: base imponible (importe)
                # alic: alicuota (porcentaje)
                # importe: importe liquidado
            cpb_perc = cpb_comprobante_perc_imp.objects.filter(cpb_comprobante=f)
            for p in cpb_perc:            
                id = p.perc_imp.id 
                if (id==99)and(p.detalle):
                    desc=p.detalle
                else:
                    desc = p.perc_imp.nombre
                base_imp = p.importe_total
                alic = 100
                importe = p.importe_total
                wsfev1.AgregarTributo(id, desc, base_imp, alic, importe)  

         # Agrego los comprobantes asociados (solo para notas de crédito y débito):
        if (f.cpb_tipo.tipo in [2,3])and(f.id_cpb_padre):
            p = f.id_cpb_padre
            p_nafip = cpb_nro_afip.objects.get(cpb_tipo=p.cpb_tipo.tipo,letra=p.letra).numero_afip     
            p_tipo = p_nafip
            p_pv = int(p.pto_vta)
            p_nro = int(p.numero)
            wsfev1.AgregarCmpAsoc(p_tipo, p_pv, p_nro)                   
            
    except:        
        data['excepcion']=wsfev1.Excepcion
        data['traceback']=wsfev1.Traceback
        data['XmlRequest']=wsfev1.XmlRequest
        data['XmlResponse']=wsfev1.XmlResponse
        data['appserver_status']=appserver_status
        data['dbserver_status']=dbserver_status
        data['authserver_status']=authserver_status
        data['errores']=u'¡El comprobante no es válido!'  
        
        return data


    try:
        #http://www.sistemasagiles.com.ar/trac/wiki/ManualPyAfipWs#M%C3%A9todosprincipalesdeWSFEv1
        wsfev1.CAESolicitar()
        
        cae = wsfev1.CAE
        resultado = wsfev1.Resultado
        cpb_nro = wsfev1.CbteNro
        ult_nro = cpb_nro      
        
        detalle = ''
                
        motivo = wsfev1.Motivo
        observaciones = wsfev1.Observaciones   
        
        if cae=='':        
            detalle= u"La página esta caida o la respuesta es inválida"
        elif (wsfev1.Resultado!="A"):
            detalle= u"No se asignó CAE (Rechazado). Motivos:%s" %motivo
        elif observaciones!=[]:
                detalle = u"Se asignó CAE pero con advertencias. Motivos: %s" %observaciones          

        fecha_vencimiento = None
        fecha_cbte = None
        EmisionTipo = ''
        if cae!='':
            fecha_vencimiento = datetime.strptime(wsfev1.Vencimiento,'%Y%m%d')
            EmisionTipo = wsfev1.EmisionTipo        
            fecha_cbte =datetime.strptime(wsfev1.FechaCbte,'%Y%m%d')        

        reproceso = wsfev1.Reproceso
        imp_total = wsfev1.ImpTotal
        cae = wsfev1.CAE       
        concepto = wsfev1.ObtenerCampoFactura('concepto')    
        imp_tot_conc = wsfev1.ObtenerCampoFactura('imp_tot_conc')
        imp_neto = wsfev1.ImpNeto
        imp_op_ex = wsfev1.ImpOpEx
        imp_trib = wsfev1.ImpTrib
        imp_iva = wsfev1.ImpIVA      
        moneda_id = wsfev1.ObtenerCampoFactura('moneda_id')
        moneda_ctz = wsfev1.ObtenerCampoFactura('moneda_ctz')
        
        errores=wsfev1.ErrMsg

        data = {            
            'token':token,
            'sign':sign,
            'cae': cae,
            'fecha_vencimiento': fecha_vencimiento,
            'cpb_nro':cpb_nro,
            'resultado':resultado,
            'motivo':motivo,
            'reproceso':reproceso,
            'observaciones' : observaciones,
            'concepto':concepto,
            'tipo_cbte': tipo_cpb,
            'punto_vta':pto_vta,   
            'fecha_cbte': fecha_cbte,
            'imp_total': imp_total,
            'imp_tot_conc': imp_tot_conc,
            'imp_neto': imp_neto,
            'imp_op_ex': imp_op_ex,
            'imp_trib': imp_trib,
            'imp_iva': imp_iva,    
            'moneda_id': moneda_id,
            'moneda_ctz': moneda_ctz,    
            'detalle':detalle,
            'ult_nro':ult_nro,
            'excepcion':wsfev1.Excepcion,     
            'traceback':wsfev1.Traceback,
            'XmlRequest':wsfev1.XmlRequest,
            'XmlResponse':wsfev1.XmlResponse,
            'appserver_status':appserver_status,
            'dbserver_status':dbserver_status,
            'authserver_status':authserver_status,
            'errores':errores,
            }                

    except:
        if wsfev1:
            data = {
            'token':token,
            'sign':sign,
            'cae': cae,
            'fecha_vencimiento': fecha_vencimiento,
            'cpb_nro':cpb_nro,
            'resultado':resultado,
            'motivo':motivo,
            'reproceso':reproceso,
            'observaciones' : observaciones,
            'concepto':concepto,
            'tipo_cbte': tipo_cpb,
            'punto_vta':pto_vta,   
            'fecha_cbte': fecha_cbte,
            'imp_total': imp_total,
            'imp_tot_conc': imp_tot_conc,
            'imp_neto': imp_neto,
            'imp_op_ex': imp_op_ex,
            'imp_trib': imp_trib,
            'imp_iva': imp_iva,    
            'moneda_id': moneda_id,
            'moneda_ctz': moneda_ctz,    
            'detalle':detalle,
            'ult_nro':ult_nro,
            'excepcion':wsfev1.Excepcion,     
            'traceback':wsfev1.Traceback,
            'XmlRequest':wsfev1.XmlRequest,
            'XmlResponse':wsfev1.XmlResponse,
            'appserver_status':appserver_status,
            'dbserver_status':dbserver_status,
            'authserver_status':authserver_status,
            'errores':errores,
            }            
            
    return data


