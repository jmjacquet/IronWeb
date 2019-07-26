$(document).ready(function() {  

$("input[type=number]").click(function(){
            this.select()
          });
$.fm({        
        custom_callbacks: {
            "recargarP": function(data, options) {
               recargarProveedores();
               },            
            }
  });

  if ($('#id_tipo_form').val()=='EDICION'){
       $('#id_pto_vta').attr('disabled', 'disabled');               
       $('#id_entidad').trigger("chosen:updated");          
       $('#nuevoProveedores').hide();
       $('#id_pto_vta').val(("00000" + $('#id_pto_vta').val()).slice(-5));
  }else{      
      $('#id_pto_vta').val(("00000" + $('#id_pto_vta').val()).slice(-5));
      setear_CTA($("[name='formFP-0-cta_egreso']"),$("[name='formFP-0-tipo_forma_pago']"));
  };



  $("#id_entidad").chosen({
            no_results_text: "Cliente inexistente...",
            placeholder_text_single:"Seleccione un Cliente",
            allow_single_deselect: true,
        }); 

  function calcularTotales(){                
        var tot=0;
        var tot2=0;
        $('.form-detalles tr').each(function(j) {
            if ($(this).is(':visible'))
            {
              var $importe_parcial = parseFloat($("input[name='formFP-"+j+"-importe']").val())|| 0;               
              if ($importe_parcial == '') $importe_parcial=0;       
              tot = tot + $importe_parcial;                  
            }
         });
        $("#id_importe_subtotal").val(tot.toFixed(2));
        var tot=0;
         $('.form-detallesRet tr').each(function(j) {
              if ($(this).is(':visible'))
                  {
                    var $importe_tot = parseFloat($("input[name='formRet-"+j+"-importe_total']").val())|| 0;                
                    if ($importe_tot == '') $importe_tot=0;                    
                    tot = tot + $importe_tot;  
                  }
              });       
        var $importe_ret = tot;
        $("#id_importe_ret").val($importe_ret.toFixed(2));
        
        if($("#id_importe_cpbs").val()){
          $('.form-cpbs tr').each(function(j) {
             if ($(this).is(':visible'))
            {
             var $importe = parseFloat($("input[name='formCPB-"+j+"-importe_total']").val())|| 0;               
              if ($importe == '') $importe=0;       
              tot2 = tot2 + $importe;                  
            }
          }); 
          $("#id_importe_cpbs").val(tot2.toFixed(2));
          };
             
        
         
        var $importe_subtot = parseFloat($("#id_importe_subtotal").val())|| 0;
        var $importe_ret = parseFloat($("#id_importe_ret").val())|| 0;
        var $importe_total = 0;        
        $importe_total = $importe_ret + $importe_subtot;  
        $importe_total = parseFloat($importe_total).toFixed(2); 
        $("#id_importe_total").val($importe_total);
    };

  function setear_CTA(cta,fp)
  {   
      var id_fp =  fp.val();      
      $.ajax({
            data: {'fp': id_fp},
            url: '/comprobantes/setearCta_FP/',
            type: 'get',
            cache: true,          
            success : function(data) {
                 //console.log(data);
                 if (data!='')
                    {
                      cta.val(data[0]);                     
                    }          
            },
            error : function(message) {
                 /*alertify.alert('Búsqueda por CUIT','No se encontró el Proveedor.');*/
                 //console.log(message);
              }
          });
  };
function setear_FP(cta,fp,banco)
{
    var id_cta =  cta.val();      
    $.ajax({
          data: {'cta':id_cta},
          url: '/comprobantes/setearCta_FP/',
          type: 'get',
          cache: true,          
          success : function(data) {
               console.log(data);
               if (data!='')
                  {                    
                    fp.val(data[0]);
                    banco.val(data[1]);                     
                  }
                 
          },
          error : function(message) {
               /*alertify.alert('Búsqueda por CUIT','No se encontró el Proveedor.');*/
               console.log(message);
            }
        });
};

  function cargarTipoP(i){
    //Traigo todos los datos del producto
    if ($("input[name='formFP-"+i+"-importe']").val()==0)
    {
      var tot_pagos = 0;
      if($("#id_importe_cpbs").val()){
      tot_pagos = $("#id_importe_cpbs").val();}
      var tot_fps =  $("#id_importe_subtotal").val();
      var dif = tot_pagos - tot_fps;
      if (dif < 0) {dif=0;};

      $("input[name='formFP-"+i+"-importe']").val(dif) 
    };
  };
    

  function recalcular(){        
        $('.form-detalles tr').each(function(j) {
         
         $("input[name='formFP-"+j+"-importe']").change(function(){
              calcularTotales();      
           });
             
         $("[name='formFP-"+j+"-tipo_forma_pago']").change(function(){
              //setear_CTA($("[name='formFP-"+j+"-cta_egreso']"),$("[name='formFP-"+j+"-tipo_forma_pago']"));
              cargarTipoP(j);            
              calcularTotales();    
           });

         $("[name='formFP-"+j+"-cta_egreso']").change(function(){            
              setear_FP($("[name='formFP-"+j+"-cta_egreso']"),$("[name='formFP-"+j+"-tipo_forma_pago']"),$("[name='formFP-"+j+"-mdcp_banco']"));
              cargarTipoP(j);
              calcularTotales();    
           });

         
        });
       $('.form-detallesRet tr').each(function(j) {
          $("input[name='formRet-"+j+"-importe_total']").change(function(){
             calcularTotales();     
           });      
        });
       calcularTotales();
      
      };

    //Se ejecuta al crearse el form
    recalcular();


  $('.formFP').formset({
            addText: 'Agregar Detalle',
            addCssClass: 'add-row btn blue-hoki ',       
            deleteCssClass: 'delete-row1',   
            deleteText: 'Eliminar',
            prefix: 'formFP',
            formCssClass: 'dynamic-form',
            keepFieldValues:'',
            added: function (row) {                             
              $("[name='formFP-"+i+"-tipo_forma_pago']").focus();           
              var i = $(row).index();
              var tot = parseFloat(0.00);
              tot =  parseFloat(tot).toFixed(2);             
              $("[name='formFP-"+i+"-importe']").val(tot);
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

  $('.formRet').formset({
          addText: 'Agregar Retención',
          addCssClass: 'add-row btn blue-hoki ',
          deleteCssClass: 'delete-row2',       
          deleteText: 'Eliminar',
          prefix: 'formRet',
          formCssClass: 'dynamic-form2',
          keepFieldValues:'',
          added: function (row) {
            var i = $(row).index();
            $("[name='formRet-"+i+"-importe_total']").val('0.00');
            recalcular();
            $("[name='formRet-"+i+"-retencion']").focus();
           },
          removed: function (row) {
            calcularTotales();             
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


  $( "#GuardarRec" ).click(function() {
              
        total = parseFloat($("#id_importe_total").val());
        
        var total_cpbs = 0;
        if($("#id_importe_cpbs").val()){
        total_cpbs = parseFloat($("#id_importe_cpbs").val())};

        if (total<=0){
          alertify.errorAlert("¡El importe total debe ser mayor a cero!");
           $("#GuardarRec").prop("disabled", false);
           return false;
        };
        if (total_cpbs>0){
          if (total!=total_cpbs){
            alertify.errorAlert("¡El importe total no coincide con los comprobantes seleccionados!");
            $("#GuardarRec").prop("disabled", false);
            return false;
          }
        };   
           

         $("#form-alta:disabled").removeAttr('disabled');
          $('#id_pto_vta').removeAttr('disabled');                                    
          $("#id_entidad").removeAttr('disabled'); 
         

          $("#GuardarRec").prop("disabled", true);
      

          $( "#form-alta" ).submit();         
        
      

    });



  $("#id_pto_vta").keyup(function(){
      h = ("00000" + $(this).val()).slice(-5);    
      $(this).val(h);
   });
 


});
