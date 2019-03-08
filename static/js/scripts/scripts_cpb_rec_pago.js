$(document).ready(function() {  

  if ($('#id_tipo_form').val()=='EDICION'){
       $('#id_pto_vta').attr('disabled', 'disabled');               
       $('#id_entidad').trigger("chosen:updated");          
       $('#recargarProveedores').hide();
       $('#id_pto_vta').val(("0000" + $(this).val()).slice(-4));
  }else{
      $('#id_pto_vta').val(("0000" + $(this).val()).slice(-4));
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
             
        
        var tot=0;
        $("#id_importe_imp_perc").val(0.00);
        var $importe_subtot = parseFloat($("#id_importe_subtotal").val())|| 0;
        var $importe_imp_perc = parseFloat($("#id_importe_imp_perc").val())|| 0;
        var $importe_total = 0;        
        $importe_total = $importe_imp_perc + $importe_subtot;  
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
              var tot = parseFloat($("#id_importe_total").val()) - parseFloat($("#id_total_fp").val());
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


  $("#recargarProveedores").click(function () {
    $.getJSON('/recargar_proveedores/',{},
          function (c) {
              $("#id_entidad").empty().append('<option value="">---</option>');
              $.each(c["proveedores"], function (idx, item) {
                  jQuery("<option/>").text(item['codigo']+' - '+item['apellido_y_nombre']+' - '+item['fact_cuit']).attr("value", item['id']).appendTo("#id_entidad");
              })
              $('#id_entidad').trigger("chosen:updated");
          }); 
       });

  $( "#GuardarRec" ).click(function() {
              
        total = parseFloat($("#id_importe_total").val());
        total_pagos = parseFloat($("#id_importe_subtotal").val());        
        var total_cpbs = 0;
        if($("#id_importe_cpbs").val()){
        total_cpbs = parseFloat($("#id_importe_cpbs").val())};

        if (total<=0){
          alertify.errorAlert("¡El importe total debe ser mayor a cero!");
           $("#GuardarRec").prop("disabled", false);
           return false;
        };
        if (total_cpbs>0){
          if (total_pagos!=total_cpbs){
            alertify.errorAlert("¡El importe total no coincide con los comprobantes seleccionados!");
            $("#GuardarRec").prop("disabled", false);
            return false;
          }
        };   
        if ((total != total_pagos))
        {                
            alertify.errorAlert("¡El importe total ($"+total+") no coincide con los pagos cargados ($"+total_pagos+")!");
            $("#GuardarRec").prop("disabled", false);     
            return false;
        }       
        //El solicitante debe cargar un EMAil
      

         $("#form-alta:disabled").removeAttr('disabled');
          $('#id_pto_vta').removeAttr('disabled');                                    
          $("#id_entidad").removeAttr('disabled'); 
         

          $("#GuardarRec").prop("disabled", true);
      

          $( "#form-alta" ).submit();         
        
      

    });



  $("#id_pto_vta").keyup(function(){
      h = ("0000" + $(this).val()).slice(-4);    
      $(this).val(h);
   });
 


});