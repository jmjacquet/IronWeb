$(document).ready(function() {  

$("input[type=number]").click(function(){
            this.select()
          });

function calcularTotales(){                
      var tot2=0;      
      $('.formFP').each(function(j) {
            var $importe = parseFloat($("input[name='formFP-"+j+"-importe']").val())|| 0;               
            if ($importe == '') $importe=0;       
            tot2 = tot2 + $importe;                  
       });
       console.log(tot2);
      $("#id_importe_total").val(tot2);
  };

  
$('.formFP').formset({
          addText: 'Agregar',
          addCssClass: 'add-row btn blue-hoki',       
          deleteCssClass: 'delete-row btn btn-danger',   
          deleteText: 'Eliminar',
          prefix: 'formFP',
          formCssClass: 'dynamic-form',
          keepFieldValues:'',
          added: function (row) {           
            var i = $(row).index();            
            $("[name='formFP-"+i+"-importe']").val('0');                        
            $("[name='formFP-"+i+"-tipo_forma_pago']").focus();                       
            $('.datepicker').each(function(){
                  $(this).datepicker({
                      format: "dd/mm/yyyy",
                      language: "es",
                      autoclose: true,
                      todayHighlight: true
                });
              });
            recalcular(); 
           },
          removed: function (row) {      
            recalcular();               
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


function recalcular(){
      $('.formFP').each(function(j) {
       
        $("input[name='formFP-"+j+"-importe']").change(function(){
            calcularTotales();      
         });
      });
     calcularTotales();   
    };

  //Se ejecuta al crearse el form
  recalcular();



$( "#Guardar" ).click(function() {    
      total = parseFloat($("#id_importe_total").val());
      
      if (total<=0){
        alertify.errorAlert("¡El importe total debe ser mayor a cero!");
         $("#Guardar").prop("disabled", false);
         return false;
      };       

      $("#form-alta:disabled").removeAttr('disabled');
        $("#Guardar").prop("disabled", true);    
        $( "#form-alta" ).submit();              
    

  });


  });
