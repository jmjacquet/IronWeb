$(document).ready(function() {  


//  $("#id_entidad").chosen({
//           no_results_text: "Cliente inexistente...",
//           placeholder_text_single:"Seleccione un Cliente",
//           allow_single_deselect: true,
//       }); 

$("input[type=number]").click(function(){
            this.select()
          });

$('.formStock').formset({
          addText: 'Agregar Ubicación',
          addCssClass: 'add-row btn blue-hoki ',       
          deleteCssClass: 'delete-row1',     
          deleteText: 'Eliminar',
          prefix: 'formStock',
          formCssClass: 'dynamic-form',
          keepFieldValues:'',
          added: function (row) {
            var i = $(row).index();
            $(row).attr("id", "formStock-"+i);
            $("[name='formStock-"+i+"-stock']").val(1);           
           },
          removed: function (row) {
            var i = $(row).index();
            $(row).attr("id", "formStock-"+i);             
          }
      });

$('.formPrecios').formset({
          addText: 'Agregar Precio',
          addCssClass: 'add-row btn blue-hoki ',       
          deleteCssClass: 'delete-row2',     
          deleteText: 'Eliminar',
          prefix: 'formPrecios',
          formCssClass: 'dynamic-form2',
          keepFieldValues:'',
          added: function (row) {
            var i = $(row).index();
            $(row).attr("id", "formPrecios-"+i);            
            $("[name='formPrecios-"+i+"-precio_costo']").val(0);           
            $("[name='formPrecios-"+i+"-precio_cimp']").val(0);           
            $("[name='formPrecios-"+i+"-precio_venta']").val(0);           
            $("[name='formPrecios-"+i+"-coef_ganancia']").val(0);           
            recalcular();
          },
          removed: function (row) {
            var i = $(row).index();
            $(row).attr("id", "formPrecios-"+i);             
          }
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


    $( "#Guardar" ).click(function() {        
       $("#form-alta:disabled").removeAttr('disabled');      
        $("#Guardar").prop("disabled", true);    
        $( "#form-alta" ).submit();         
      });

function recalcular(){
  $('.form-detallesPrecios tr').each(function(j) {
        $("input[name='formPrecios-"+j+"-precio_costo']").change(function(){
             var $precio_costo = parseFloat($("input[name='formPrecios-"+j+"-precio_costo']").val())|| 0;  
             var $coef_ganancia = parseFloat($("input[name='formPrecios-"+j+"-coef_ganancia']").val())|| 0;
             var coef = parseFloat($("#id_coef_iva").val())|| 0;  
             var $precio_cimp = $precio_costo * (coef+1);  
             var $precio_venta = $precio_cimp * ($coef_ganancia+1);   
             $("input[name='formPrecios-"+j+"-precio_cimp']").val($precio_cimp.toFixed(2));  
             $("input[name='formPrecios-"+j+"-precio_venta']").val($precio_venta.toFixed(2));
           });
        $("input[name='formPrecios-"+j+"-precio_cimp']").change(function(){            
            var $precio_costo = parseFloat($("input[name='formPrecios-"+j+"-precio_costo']").val())|| 0;  
            var $coef_ganancia = parseFloat($("input[name='formPrecios-"+j+"-coef_ganancia']").val())|| 0;
            var coef = parseFloat($("#id_coef_iva").val())|| 0;  
            var $precio_venta = $precio_cimp * ($coef_ganancia+1); 
            $("input[name='formPrecios-"+j+"-precio_venta']").val($precio_venta.toFixed(2));
           });
        $("input[name='formPrecios-"+j+"-coef_ganancia']").change(function(){
            var $precio_costo = parseFloat($("input[name='formPrecios-"+j+"-precio_costo']").val())|| 0;  
            var $coef_ganancia = parseFloat($("input[name='formPrecios-"+j+"-coef_ganancia']").val())|| 0;
            var coef = parseFloat($("#id_coef_iva").val())|| 0;  
            var $precio_venta = $precio_cimp * ($coef_ganancia+1); 
            $("input[name='formPrecios-"+j+"-precio_venta']").val($precio_venta.toFixed(2));
           });        
        
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

});
