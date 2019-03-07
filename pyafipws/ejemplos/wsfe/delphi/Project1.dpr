{ Ejemplo de Uso de Interface COM con Web Services AFIP (PyAfipWs)
  2009 (C) Mariano Reingart <reingart@gmail.com> }

program Project1;

{$APPTYPE CONSOLE}

uses
  ActiveX, ComObj, Dialogs, SysUtils;

var
  WSAA, WSFE: Variant;
  tra, path, Certificado, ClavePrivada, cms, ta: String;
  qty, LastId, LastCBTE, cae, ok : Variant;
  tipo_cbte, punto_vta, tipo_doc, presta_serv, id,
    cbt_desde, cbt_hasta : Integer;
  fecha, nro_doc, imp_total, imp_tot_conc, imp_neto, impto_liq,
    impto_liq_rni, imp_op_ex, fecha_cbte, fecha_venc_pago,
    fecha_serv_desde, fecha_serv_hasta, venc : String;

begin
  CoInitialize(nil);
  // Crear objeto interface Web Service Autenticaci�n y Autorizaci�n
  WSAA := CreateOleObject('WSAA') ;

  // Generar un Ticket de Requerimiento de Acceso (TRA)
  tra := WSAA.CreateTRA;
  WriteLn(tra);

  // Especificar la ubicacion de los archivos certificado y clave privada
  path := GetCurrentDir + '\';
  // Certificado: certificado es el firmado por la AFIP
  // ClavePrivada: la clave privada usada para crear el certificado
  Certificado := 'ghf.crt'; // certificado de prueba
  ClavePrivada := 'ghf.key'; // clave privada de prueba' +
  // Generar el mensaje firmado (CMS)
  cms := WSAA.SignTRA(tra, Path + Certificado, Path + ClavePrivada);
  WriteLn(cms);

  // Llamar al web service para autenticar:
  ta := WSAA.CallWSAA(cms, 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms'); // Hologaci�n
  //ta = WSAA.CallWSAA(cms, 'https://wsaa.afip.gov.ar/ws/services/LoginCms'); // Producci�n

  // Imprimir el ticket de acceso, ToKen y Sign de autorizaci�n
  WriteLn(ta);
  WriteLn('Token:' + WSAA.Token);
  WriteLn('Sign:' + WSAA.Sign);

  // Una vez obtenido, se puede usar el mismo token y sign por 6 horas
  // (este per�odo se puede cambiar)

  // Crear objeto interface Web Service de Factura Electr�nica
  WSFE := CreateOleObject('WSFE');
  // Setear tocken y sing de autorizaci�n (pasos previos)
  WSFE.Token := WSAA.Token;
  WSFE.Sign := WSAA.Sign;

  // CUIT del emisor (debe estar registrado en la AFIP)
  WSFE.Cuit := '23111111114';
    
  // Conectar al Servicio Web de Facturaci�n
  ok := WSFE.Conectar('https://wswhomo.afip.gov.ar/wsfe/service.asmx'); // homologaci�n
  //ok := WSFE.Conectar('https://wsw.afip.gov.ar/wsfe/service.asmx'); // producci�n
   
  // Llamo a un servicio nulo, para obtener el estado del servidor (opcional)
  WSFE.Dummy;
  WriteLn('appserver status ' + WSFE.AppServerStatus);
  WriteLn('dbserver status ' + WSFE.DbServerStatus);
  WriteLn('authserver status ' + WSFE.AuthServerStatus);

  // Recupera cantidad m�xima de registros (opcional)
  //qty := WSFE.RecuperarQty;

  // Recupera �ltimo n�mero de secuencia ID
  LastId := WSFE.UltNro;

  // Recupero �ltimo n�mero de comprobante para un punto de venta y tipo (opcional)
  tipo_cbte := 1; punto_vta := 1;
  LastCBTE := WSFE.RecuperaLastCMP(punto_vta, tipo_cbte);

  // Establezco los valores de la factura o lote a autorizar:
  DateTimeToString(Fecha, 'yyyymmdd', Date);
  id := LastId + 1; presta_serv := 1;
  tipo_doc := 80; nro_doc := '23111111114';
  cbt_desde := LastCBTE + 1; cbt_hasta := LastCBTE + 1;
  imp_total := '121.00'; imp_tot_conc := '0.00'; imp_neto := '100.00';
  impto_liq := '21.00'; impto_liq_rni := '0.00'; imp_op_ex := '0.00';
  fecha_cbte := Fecha; fecha_venc_pago := Fecha;
  // Fechas del per�odo del servicio facturado (solo si presta_serv = 1)
  fecha_serv_desde := Fecha; fecha_serv_hasta := Fecha;

  // Llamo al WebService de Autorizaci�n para obtener el CAE
  cae := WSFE.Aut(id, presta_serv,
        tipo_doc, nro_doc, tipo_cbte, punto_vta,
        cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
        impto_liq, impto_liq_rni, imp_op_ex, fecha_cbte, fecha_venc_pago,
        fecha_serv_desde, fecha_serv_hasta); // si presta_serv = 0 no pasar estas fechas

  WriteLn('Vencimiento ' +  WSFE.Vencimiento); // Fecha de vencimiento o vencimiento de la autorizaci�n 
  WriteLn('Resultado: ' + WSFE.Resultado); // A=Aceptado, R=Rechazado
  WriteLn('Motivo de rechazo o advertencia ' + WSFE.Motivo); // 00= No hay error
  WriteLn('Reprocesado? ' +  WSFE.Reproceso); // S=Si, N=No

  // Verifico que no haya rechazo o advertencia al generar el CAE
  If cae = '' then
    ShowMessage('La p�gina esta caida o la respuesta es inv�lida')
  Else
    If (cae = 'NULL') or not (WSFE.Resultado = 'A') Then
      ShowMessage('No se asign� CAE (Rechazado). Motivos: ' + WSFE.Motivo)
    Else
      If (WSFE.Motivo <> 'NULL') and (WSFE.Motivo <> '00') Then
         ShowMessage('Se asign� CAE pero con advertencias. Motivos: ' + WSFE.Motivo);

  // Imprimo respuesta XML para depuraci�n (errores de formato)
  //WriteLn(WSFE.XmlResponse);

  ShowMessage('CAE: ' + cae);

  WriteLn('Presione Enter para terminar');
  ReadLn;

  CoUninitialize;
end.
