# coding: utf8
# try something like

import os
import datetime
import time

def _autenticar(service="wsfe", ttl=60*60*5):
    "Obtener el TA"

    from pyafipws import wsaa    
    
    CUIT = 20267565393
    CERTIFICATE = "reingart.crt"
    PRIVATE_KEY = "reingart.key"
    WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
    
    # wsfev1 => wsfe!
    # service = {'wsfev1': 'wsfe'}.get(service, service)
    
    if service not in ("wsfe","wsfev1","wsmtxca","wsfex","wsbfe"):
        raise HTTP(500,"Servicio %s incorrecto" % service)
    
    # verifico archivo temporal con el ticket de acceso
    TA = os.path.join(PRIVATE_PATH, "TA-%s.xml" % service)
    ttl = 60*60*5
    if not os.path.exists(TA) or os.path.getmtime(TA)+(ttl)<time.time():
        # solicito una nueva autenticación
        # wsaa = pyafipws.wsaa
        cert = os.path.join(PRIVATE_PATH, CERTIFICATE)
        privatekey = os.path.join(PRIVATE_PATH, PRIVATE_KEY)
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



def index(): 
    pagos = db(db.pagos.id>0).select()

    return dict(pagos=pagos)
    
def cae():   
    from pyafipws.wsfev1 import WSFEv1
    wsfev1 = WSFEv1()
    wsfev1.Conectar()
    wsfev1.Cuit = 20267565393
    wsfev1.Token, wsfev1.Sign = _autenticar()

    id = request.args[0]
    f = db(db.pagos.id == id).select().first()
    
    if f.resultado == "A":
        raise HTTP(500, "La factura ya tiene CAE: %s" % f.cae)
    
    tipo_cbte = f.tipo_cbte
    punto_vta = f.pto_vta
    cbte_nro = long(wsfev1.CompUltimoAutorizado(tipo_cbte, punto_vta) or 0)
    fecha = datetime.datetime.now().strftime("%Y%m%d")
    concepto = 2
    tipo_doc = f.tipo_doc
    nro_doc = f.nro_doc
    cbt_desde = cbte_nro + 1; cbt_hasta = cbte_nro + 1
    imp_total = f.imp_total; imp_tot_conc = "0.00"; imp_neto = "0.00"
    imp_iva = "0.00"; imp_trib = "0.00"; imp_op_ex = f.imp_total
    fecha_cbte = fecha; fecha_venc_pago = fecha
    # Fechas del período del servicio facturado (solo si concepto = 1?)
    fecha_serv_desde = fecha; fecha_serv_hasta = fecha
    moneda_id = 'PES'; moneda_ctz = '1.000'

    wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
        cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
        imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
        fecha_serv_desde, fecha_serv_hasta, #--
        moneda_id, moneda_ctz)
    
    if False:
        tipo = 19
        pto_vta = 2
        nro = 1234
        wsfev1.AgregarCmpAsoc(tipo, pto_vta, nro)
    
    #id = 99
    #desc = 'Impuesto Municipal Matanza'
    #base_imp = 100
    #alic = 1
    #importe = 1
    #wsfev1.AgregarTributo(id, desc, base_imp, alic, importe)

    #id = 5 # 21%
    #base_imp = 100
    #importe = 21
    #wsfev1.AgregarIva(id, base_imp, importe)
    
    wsfev1.CAESolicitar()

    db(db.pagos.id == int(request.args[0])).update(cae=wsfev1.CAE, 
                                                   cbte_nro=cbt_desde, 
                                                   fecha_vto=wsfev1.Vencimiento, 
                                                   fecha=request.now.date(), 
                                                   motivo=wsfev1.Obs,
                                                   resultado=wsfev1.Resultado)
    response.view = "generic.html"
    return {'CAE': wsfev1.CAE, "Resultado": wsfev1.Resultado,
            "Reproceso": wsfev1.Reproceso,
            "Vencimiento": wsfev1.Vencimiento,
            "ErrMsg": wsfev1.ErrMsg,
            "Obs": wsfev1.Obs,
            "Token": wsfev1.Token,
            "Sign": wsfev1.Sign,
           }

def pdf():
    id = request.args[0]
    
    from pyafipws.pyfepdf import FEPDF
    fepdf = FEPDF()
    fepdf.CUIT = 20267565393
        
    # cargo el formato CSV por defecto (factura.csv)
    t = os.path.join(request.env.web2py_path,'applications',request.application,'modules', 'pyafipws', 'factura.csv')
    fepdf.CargarFormato(t)
    
    f = db(db.pagos.id == id).select().first()
    
    if not f.cae:
        raise HTTP(500, "Debe soliticar CAE a AFIP antes de generar el PDF!")
    
    # creo una factura de ejemplo
    tipo_cbte = int(f.tipo_cbte)
    punto_vta = int(f.pto_vta)
    fecha = f.fecha.strftime("%Y%m%d")
    concepto = 3
    tipo_doc = int(f.tipo_doc); nro_doc = int(f.nro_doc)
    cbte_nro = int(f.cbte_nro)
    imp_total = f.imp_total
    imp_tot_conc = "0.00"
    imp_neto = "0.00"
    imp_iva = "0.00"
    imp_trib = "0.00"
    imp_op_ex = "0.00"
    imp_subtotal = "0.00"
    fecha_cbte = fecha
    fecha_venc_pago = fecha
    # Fechas del período del servicio facturado (solo si concepto = 1?)
    fecha_serv_desde = fecha; fecha_serv_hasta = fecha
    moneda_id = 'PES'; moneda_ctz = '1.000'
    obs_generales = u"EMAIL: %s" % f.email
    obs_comerciales = u"En tu resumen verás el cargo como WWW.MERCADOPAGO.COM"

    nombre_cliente = "%s, %s" % (f.last_name, f.first_name)
    domicilio_cliente = ""
    pais_dst_cmp = 16
    id_impositivo = ""
    moneda_id = 'PES'
    moneda_ctz = 1
    forma_pago = f.forma_pago
    incoterms = 'FOB'
    idioma_cbte = 1
    motivo = f.motivo

    cae = f.cae
    fch_venc_cae = f.fecha_vto
           
    fepdf.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
        cbte_nro, imp_total, imp_tot_conc, imp_neto,
        imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
        fecha_serv_desde, fecha_serv_hasta, 
        moneda_id, moneda_ctz, cae, fch_venc_cae, id_impositivo,
        nombre_cliente, domicilio_cliente, pais_dst_cmp, 
        obs_comerciales, obs_generales, forma_pago, incoterms, 
        idioma_cbte, motivo)
    
    #tipo = 91
    #pto_vta = 2
    #nro = 1234
    #fepdf.AgregarCmpAsoc(tipo, pto_vta, nro)
    
    #tributo_id = 99
    #desc = 'Impuesto Municipal Matanza'
    #base_imp = "100.00"
    #alic = "1.00"
    #importe = "1.00"
    #fepdf.AgregarTributo(tributo_id, desc, base_imp, alic, importe)

    #iva_id = 5 # 21%
    #base_imp = 100
    #importe = 21
    #fepdf.AgregarIva(iva_id, base_imp, importe)
    
    u_mtx = 123456
    cod_mtx = 1234567890123
    codigo = "P0001"
    ds = f.ds
    qty = 1.00
    umed = 7
    precio = f.imp_total
    bonif = 0.00
    iva_id = 1
    imp_iva = 0
    importe = f.imp_total
    despacho = ""
    fepdf.AgregarDetalleItem(u_mtx, cod_mtx, codigo, ds, qty, umed, 
            precio, bonif, iva_id, imp_iva, importe, despacho)

    #fepdf.AgregarDato("pedido", "1234")
    
    fepdf.CrearPlantilla(papel="A4", orientacion="portrait")
    fepdf.ProcesarPlantilla(num_copias=3, lineas_max=24, qty_pos='izq')
    salida = t = os.path.join(request.env.web2py_path,'applications',request.application, 'private', 'factura%s.pdf' % id)
    fepdf.GenerarPDF(archivo=salida)
    
    response.headers['Content-Type']='application/pdf'
    return open(salida).read()
