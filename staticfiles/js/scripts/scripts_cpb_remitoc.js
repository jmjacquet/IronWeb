$(document).ready(function() {  


  if ($('#id_tipo_form').val()=='EDICION'){
       $('#id_entidad').trigger("chosen:updated");          
       $('#nuevoProveedores').hide();
  }else{      

  };

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

 $("#id_entidad").chosen({
          no_results_text: "Proveedor inexistente...",
          placeholder_text_single:"Seleccione un Proveedor",
          allow_single_deselect: true,
      }); 


function recalcular(){
      $('.form-detalles tr').each(function(j) {

        $("[name='formDetalle-"+j+"-producto']").chosen({
                no_results_text: "Producto inexistente...",
                placeholder_text_single:"Seleccione una Opcion",
                allow_single_deselect: true,
            });

      });
};

$('.formDetalle').formset({
          addText: 'Agregar Detalle',
          addCssClass: 'add-row btn blue-hoki ',       
          deleteCssClass: 'delete-row1',     
          deleteText: 'Eliminar',
          prefix: 'formDetalle',
          formCssClass: 'dynamic-form',
          keepFieldValues:'',
          added: function (row) {
            
            var i1 = $("#id_formDetalle-TOTAL_FORMS").val()-1;
            $("[name='formDetalle-"+i1+"-cantidad']").val(1);            
            $("[name='formDetalle-"+i1+"-unidad']").val('u.');
            
            $("[name='formDetalle-"+i1+"-producto']").chosen({
                no_results_text: "Producto inexistente...",
                placeholder_text_single:"Seleccione un Producto",
                allow_single_deselect: true,
            });
            $("[name='formDetalle-"+i1+"-producto']").focus();


            $("[name='formDetalle-"+i+"-producto']").change(function(){
              cargarProd(i);
             });
             $("[name='formDetalle-"+i1+"-producto']").trigger("change"); 
           },
          removed: function (row) {
            var i = $(row).index();
            $(row).attr("id", "formDetalle-"+i);             
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


    $( "#GuardarRemito" ).click(function() {        
       $("#form-alta:disabled").removeAttr('disabled');      
        $("#GuardarRemito").prop("disabled", true);    
        $( "#form-alta" ).submit();         
      });

$('#id_pto_vta').val(("00000" + $('#id_pto_vta').val()).slice(-5));      

$("#id_pto_vta").keyup(function(){
    h = ("00000" + $(this).val()).slice(-5);    
    $(this).val(h);
 });

$("#id_numero").keyup(function(){
    h = ("00000000" + $(this).val()).slice(-8);    
    $(this).val(h);
 });

$('#id_numero').val(("00000000" + $('#id_numero').val()).slice(-8));    

$("#recargarProductos").click(function () {      
      
        $.getJSON('/recargar_productos/1',{},
        function (c) {            
          $('.form-detalles tr').each(function(j) {
            $("[name='formDetalle-"+j+"-producto']").empty().append('<option value="">---</option>');            
            $.each(c["productos"], function (idx, item) {
                $("[name='formDetalle-"+j+"-producto']").append('<option name="' + item['id'] + '">' + item['codigo']+' - '+item['nombre'] + '</option>');                
            });
            $("[name='formDetalle-"+j+"-producto']").trigger("chosen:updated");                 
          });           
        });
  });



function ultimoNumCPB(cpb_tipo,letra,pto_vta,entidad){
   if ($('#id_tipo_form').val()=='ALTA')
    {
   $.ajax({
          data: {'cpb_tipo': cpb_tipo,'letra':letra,'pto_vta':pto_vta,'entidad':entidad},
          url: '/comprobantes/ultimp_nro_cpb_ajax/',
          type: 'get',
          cache: true,          
          success : function(data) {              
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
}

recalcular();

});
