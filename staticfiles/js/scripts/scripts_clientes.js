$(document).ready(function() {  


$("input[type=number]").click(function(){
            this.select()
          });

$( "#Buscar" ).click(function() {
      var e = $.Event( "keyup", { which: 13 } );
      $('#id_fact_cuit').trigger(e);
 });


$("#id_fact_cuit").keyup(function(e){  
  if(e.which === 13) {
     consulta = $("#id_fact_cuit").val();
     if (consulta.length<6)
     {
      alertify.alert('Búsqueda por CUIT','Debe ingresar un CUIT válido!.');
      $("#id_fact_cuit").focus();
     }
     else{
        $.ajax({
        data: {'cuit': consulta},
        url: '/buscarDatosAPICUIT/',
        type: 'get',
        cache: true,
        beforeSend: function(){
            $('#cargando').show();
        },
        complete: function(){
            $('#cargando').hide();
        },
        success : function(data) {
             console.log(data);
             if (data!='')
                {
                    if (data['tipoPersona']=='JURIDICA'){
                      $("#id_apellido_y_nombre").val(data['razonSocial']);
                      $("#id_nro_doc").val(data['idPersona']);
                      $("#id_tipo_doc").find('option[value="80"]').attr("selected",true);
                    }else{
                      $("#id_apellido_y_nombre").val(data['apellido']+' '+data['nombre']);
                      $("#id_nro_doc").val(data['numeroDocumento']);
                      $("#id_tipo_doc").find('option[value="99"]').attr("selected",true);
                    };
                    $("#id_fact_razon_social").val( $("#id_apellido_y_nombre").val());
                    if (data['categoria']!=''){
                       $("#id_fact_categFiscal").find('option[value="'+data['categoria']+'"]').attr("selected",true);
                    };
                    
                    if (data['telefono']!= undefined ){ 
                      $("#id_telefono").val(data['telefono']['numero']);
                      $("#id_fact_telefono").val(data['telefono']['numero']);
                    };

                    if (data['email']!= undefined ){ 
                      $("#id_email").val(data['email']['direccion']);
                    };

                    if (data['domicilio']!= undefined ){ 
                      $("#id_domicilio").val(data['domicilio'][0]['direccion']);
                      $("#id_fact_direccion").val(data['domicilio'][0]['direccion']);
                      $("#id_localidad").val(data['domicilio'][0]['localidad']);                                
                      idProv = data['domicilio'][0]['idProvincia']                       
                      $("#id_provincia").find('option[value="'+idProv+'"]').attr("selected",true);
                      $("#id_cod_postal").val(data['domicilio'][0]['codPostal']);}

                    else{
                       $("#id_domicilio").val('');
                       $("#id_fact_direccion").val('');          
                       $("#id_localidad").val('');
                       $("#id_cod_postal").val('');
                    };                   
                }else
                {                 
                  $("#id_fact_cuit").val('');
                  $("#id_apellido_y_nombre").val('');
                  $("#id_fact_nro_doc").val('');
                  $("#id_fact_tipo_doc").val('');
                  $("#id_domicilio").val('');
                  $("#id_fact_direccion").val('');          
                  $("#id_localidad").val('');
                  $("#id_cod_postal").val('');   
                  $("#id_fact_cuit").focus();
                  alertify.alert('Búsqueda por CUIT','No se encontraron contribuyentes con el CUIT '+consulta+'. <br>El servicio de consulta de CUIT ONline (AFIP) puede estar momentáneamente interrumpido. Vuelva a intentarlo mas tarde.');
                }
        },
        error : function(message) {
             $('#cargando').hide();
             alertify.alert('Búsqueda por CUIT','No se encontraron contribuyentes. <br>El servicio de consulta de CUIT ONline (AFIP) puede estar momentáneamente interrumpido. Vuelva a intentarlo mas tarde.');
             console.log(message);
          }
      });
      
      }
      
      
    }
  });

});