$(document).ready(function() {  

$.fn.datepicker.dates['es'] = {
    days: ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
    daysShort: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
    daysMin: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"],
    months: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    monthsShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    today: "Hoy"
  };
  
   $('.datepicker').datepicker({
          format: "dd/mm/yyyy",
          language: "es",
          autoclose: true,
          todayHighlight: true
    });
   
$( "#Buscar" ).click(function() {
      var e = $.Event( "keyup", { which: 13 } );
      $('#id_cuit').trigger(e);
 });


$("input[type=number]").click(function(){
            this.select()
          });

$("#id_cuit").keyup(function(e){  
  if(e.which === 13) {
     consulta = $("#id_cuit").val();
     if (consulta.length<6)
     {
      alertify.alert('Búsqueda por CUIT','Debe ingresar un CUIT válido!.');
      $("#id_cuit").focus();
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
             console.log(data['success']);
              if (data!='')
                {
                    
                    if (data['tipoPersona']=='JURIDICA'){
                      $("#id_nombre").val(data['razonSocial']);                                            
                    }else{
                      $("#id_nombre").val(data['apellido']+' '+data['nombre']);                      
                    };
                    $("#id_fact_razon_social").val( $("#id_apellido_y_nombre").val());
                    if (data['categoria']!=''){
                       $("#id_categ_fiscal").find('option[value="'+data['categoria']+'"]').attr("selected",true);
                    };
                    
                    if (data['telefono']!= undefined ){ 
                      $("#id_telefono").val(data['telefono']['numero']);
                      $("#id_celular").val(data['telefono']['numero']);
                    };

                    if (data['email']!= undefined ){ 
                      $("#id_email").val(data['email']['direccion']);
                    };

                    if (data['fechaInscripcion']!= undefined ){ 
                      $("#id_fecha_inicio_activ").val(moment(data['fechaInscripcion']).format("DD/MM/YYYY"));                      
                    };

                    if (data['domicilio']!= undefined ){ 
                      $("#id_domicilio").val(data['domicilio'][0]['direccion']);                      
                      $("#id_localidad").val(data['domicilio'][0]['localidad']);                                
                      idProv = data['domicilio'][0]['idProvincia']                       
                      $("#id_provincia").find('option[value="'+idProv+'"]').attr("selected",true);
                      $("#id_cod_postal").val(data['domicilio'][0]['codPostal']);}

                    else{
                       $("#id_domicilio").val('');                       
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
             alertify.alert('Búsqueda por CUIT','No se encontraron datos. <br>El servicio de consulta de CUIT ONline (AFIP) puede estar momentáneamente interrumpido. Vuelva a intentarlo mas tarde.');
             console.log(message);
          }
      });
      
      }
      
      
    }
  });

});