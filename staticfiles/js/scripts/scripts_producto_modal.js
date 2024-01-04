$(document).ready(function() {  


//  $("#id_entidad").chosen({
//           no_results_text: "Cliente inexistente...",
//           placeholder_text_single:"Seleccione un Cliente",
//           allow_single_deselect: true,
//       }); 

$('[data-toggle=tooltip]').tooltip();

$("input[type=number]").click(function(){
            this.select()
          });


    $.datepicker.regional['es'] = {
     closeText: 'Cerrar',
     prevText: '',
     nextText: '',
     currentText: 'Hoy',
     monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
     monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
     dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
     dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
     dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
     weekHeader: 'Sm',
     dateFormat: 'dd/mm/yy',
     firstDay: 1,
     isRTL: false,
     showMonthAfterYear: false,
     yearSuffix: ''
     };
     $.datepicker.setDefaults($.datepicker.regional['es']);

    $('.datepicker').each(function(){
        $(this).datepicker();
    });


 
function recalcular(){
        $("#id_precio_costo").change(function(){
             var $precio_costo = parseFloat($("#id_precio_costo").val())|| 0.00;  
             var $coef_ganancia = parseFloat($("#id_coef_ganancia").val())|| 0.00;
             var coef = parseFloat($("#id_coef_iva").val())|| 0.00;  
             var $precio_cimp = $precio_costo * (coef+1);
             var monto_iva = $precio_cimp - $precio_costo;
             var $precio_venta = $precio_costo * ($coef_ganancia+1) + monto_iva;
             $("#id_precio_cimp").val($precio_cimp.toFixed(2));  
             $("#id_precio_venta").val($precio_venta.toFixed(2));
           });
        $("#id_precio_cimp").change(function(){            
            var $precio_costo = parseFloat($("#id_precio_costo").val())|| 0.00;  
            var $coef_ganancia = parseFloat($("#id_coef_ganancia").val())|| 0.00;
            var coef = parseFloat($("#id_coef_iva").val())|| 0.000;  
            var $precio_cimp = $precio_costo * (coef+1);
            var monto_iva = $precio_cimp - $precio_costo;
            var $precio_venta = $precio_costo * ($coef_ganancia+1) + monto_iva;
            $("#id_precio_venta").val($precio_venta.toFixed(2));
           });
        $("#id_coef_ganancia").change(function(){
            var $precio_costo = parseFloat($("#id_precio_costo").val())|| 0.00;  
            var $coef_ganancia = parseFloat($("#id_coef_ganancia").val())|| 0.00;
            var coef = parseFloat($("#id_coef_iva").val())|| 0.00;  
            var $precio_cimp = $precio_costo * (coef+1);
            var monto_iva = $precio_cimp - $precio_costo;
            var $precio_venta = $precio_costo * ($coef_ganancia+1) + monto_iva;
            $("#id_precio_venta").val($precio_venta.toFixed(2));
           });        

};

$("#id_tasa_iva").change(function(){
    var id = $("#id_tasa_iva").val();
           $.ajax({
            data: {'id': id},
            url: '/productos/coeficiente_iva/',
            type: 'get',            
            cache: true,          
            success : function(data) {                 
                if (data!='')
                    {
                      $("#id_coef_iva").val(parseFloat(data['tiva']))                                           
                    }
            },
            error : function(message) {                
                 console.log(message);
              }
          });
  });
      


recalcular(); 
$("#id_tasa_iva").trigger("change");


$("#generarCB").click(function(e){  
     codigo = $("#id_codigo").val();
     if (codigo=='')
     {
      alertify.alert("GENERAR CODIGO DE BARRAS","¡Debe cargar un Código de producto!"); 
     }
     else
      {
        $.ajax({
          data: {'codigo': codigo},
          url: '/productos/generarCB/',
          type: 'get',
          cache: true,          
          success : function(data) {               
               if (data!='')
                  {$("#id_codigo_barras").val(data);                    
                  }else
                  {alertify.alert("GENERAR CODIGO DE BARRAS","¡No se pudo generar el Código de Barras!"); }
          },
          error : function(message) {
               alertify.alert("GENERAR CODIGO DE BARRAS","¡No se pudo generar el Código de Barras!"); 
               console.log(message);
            }
        });     
      }
        
});


});
