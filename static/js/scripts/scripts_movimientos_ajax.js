$(document).ready(function() {  


function calcularTotales(){                
      var tot2=0;      
            var $importe = parseFloat($("input[name='importe']").val())|| 0;               
            if ($importe == '') $importe=0;       
            tot2 = tot2 + $importe;                  
      $("#id_importe_total").val(tot2);
  };


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
      $("input[name='importe']").change(function(){
          calcularTotales();      
       });     
    };

  //Se ejecuta al crearse el form
  recalcular();



function ultimoNumCPB(cpb_tipo,letra,pto_vta){
   $.ajax({
          data: {'cpb_tipo': cpb_tipo,'letra':letra,'pto_vta':pto_vta},
          url: '/comprobantes/ultimp_nro_cpb_ajax/',
          type: 'get',
          cache: true,          
          success : function(data) {
               console.log(data);
               if (data!='')
                  {
                    $("#id_numero").val(("00000000" + data[0]).slice(-8));                    
                  }
          },
          error : function(message) {
               /*alertify.alert('Búsqueda por CUIT','No se encontró el Proveedor.');*/
               console.log(message);
            }
        });     
}

$("#id_numero").keyup(function(){
    h = ("00000000" + $(this).val()).slice(-8);    
    $(this).val(h);
 });


$("#id_pto_vta").change(function(){
     letra = 'X';
     pto_vta = $("#id_pto_vta").val();
     cpb_tipo = 13;     
     
     ultimoNumCPB(cpb_tipo,letra,pto_vta);
 });  



  });
