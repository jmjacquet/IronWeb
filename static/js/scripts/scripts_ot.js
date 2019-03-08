$(document).ready(function() {  

if ($('#id_tipo_form').val()=='EDICION'){
 
     $("#id_responsable").trigger("change");         
     $('#id_responsable').trigger("chosen:updated");


}else{
  $("#id_responsable").chosen({
          no_results_text: "Responsable inexistente...",
          placeholder_text_single:"Seleccione un Responsable",
          allow_single_deselect: true,
      });   
}


$("#id_responsable").chosen({
          no_results_text: "Responsable inexistente...",
          placeholder_text_single:"Seleccione un Responsable",
          allow_single_deselect: true,
      });




  //Se ejecuta al crearse el form
  
$('.form-detalles tr').each(function(j) {
        $("[name='formDetalle-"+j+"-producto']").change(function(){
            cargarProd(j);
         }); 
      });

$('.formDetalle').formset({
          addText: 'Agregar Detalle',
          addCssClass: 'add-row btn agregarItem ',       
          deleteCssClass: 'delete-row1',   
          deleteText: 'Eliminar',
          prefix: 'formDetalle',
          formCssClass: 'dynamic-form',
          keepFieldValues:'',
          added: function (row) {
            var i = $(row).index();                       
            var i1 = $("#id_formDetalle-TOTAL_FORMS").val()-1;
            $("[name='formDetalle-"+i1+"-cantidad']").val(1);
            $("[name='formDetalle-"+i1+"-importe_unitario']").val('0');            
            $("[name='formDetalle-"+i1+"-unidad']").val('u.');            
            $("[name='formDetalle-"+i1+"-producto']").chosen({
                no_results_text: "Producto inexistente...",
                placeholder_text_single:"Seleccione un Producto",
                allow_single_deselect: true,
            });
            $("[name='formDetalle-"+i1+"-producto']").focus();
            $("[name='formDetalle-"+i1+"-producto']").change(function(){              
            cargarProd(i1);
         }); 
           },
          removed: function (row) {      
          }
      });



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

   $('.datepicker').each(function(){
        $(this).datepicker();
    });


$("#id_numero").keyup(function(){
    h = ("00000000" + $(this).val()).slice(-8);    
    $(this).val(h);
});
      

function cargarProd(i){
    //Traigo todos los datos del producto
    var idp =  $("[name='formDetalle-"+i+"-producto']").val();
    var idubi =  $("#id_origen_destino").val();
    var idlista =  $("#id_lista_precios").val();
    $.ajax({
            data: {'idp': idp,'idubi':idubi,'idlista':idlista},
            url: '/comprobantes/buscarDatosProd/',
            type: 'get',
            cache: true,          
            success : function(data) {
                 console.log(data);
                 if (data!='')
                    {
                       $("[name='formDetalle-"+i+"-unidad']").val(data['unidad']);           
                      $("[name='formDetalle-"+i+"-cantidad']").val('1');                                   
                    }
                    else{                                        
                      $("[name='formDetalle-"+i+"-cantidad']").val('0');
                      $("[name='formDetalle-"+i+"-unidad']").val('u.'); 
                    };
            },
            error : function(message) {
                 /*alertify.alert('Búsqueda por CUIT','No se encontró el Proveedor.');*/
                 console.log(message);
              }
          });  
    };



$( "#Guardar" ).click(function() {    
      total = parseFloat($("#id_importe_total").val());     
     
      $("#form-alta:disabled").removeAttr('disabled');      
        $("#id_numero").removeAttr('disabled');         
        $("#id_responsable").removeAttr('disabled', 'disabled');
        $("#Guardar").prop("disabled", true);    
        $( "#form-alta" ).submit();         
  });
$("[name='formDetalle-0-producto']").chosen({
                no_results_text: "Producto inexistente...",
                placeholder_text_single:"Seleccione una Opcion",
                allow_single_deselect: true,
            });
$("#id_formDetalle-0-producto").focus();


 });