$(document).ready(function() {  

if ($('#id_tipo_form').val()=='EDICION'){
  console.log($('#id_tipo_form').val());
     $("#id_cliente").trigger("change");         
     $('#id_cliente').trigger("chosen:updated");
     $('#recargarClientes').hide();

}else{
  $("#id_cliente").chosen({
          no_results_text: "Cliente inexistente...",
          placeholder_text_single:"Seleccione un Cliente",
          allow_single_deselect: true,
      });   
}


$("#id_vendedor").chosen({
          no_results_text: "Vendedor inexistente...",
          placeholder_text_single:"Seleccione un Vendedor",
          allow_single_deselect: true,
      });

$("#id_muestra_enviada").chosen({
          no_results_text: "Contacto inexistente...",
          placeholder_text_single:"Seleccione un Contacto",
          allow_single_deselect: true,
      });

$("#id_cliente").change(function(){
    var id =  $("#id_cliente").val();
    $.ajax({
                data: {'id': id},
                url: '/comprobantes/buscarDatosEntidad/',
                type: 'get',
                cache: true,          
                success : function(data) {
                     console.log(data);
                     if (data!='')
                        {
                          $("#id_cliente_categ_fiscal").val(data['fact_categFiscal']); 
                          if (data['dcto_general']==''){
                            $("#id_cliente_descuento").val(data['dcto_general'])
                          }else {$("#id_cliente_descuento").val(0);};
                          
                        }
                        else{                 
                         $("#id_cliente_categ_fiscal").val(5); 
                          $("#id_cliente_descuento").val(0); 
                        };
                                                
                        calcularTotales();
                },
                error : function(message) {
                     /*alertify.alert('Búsqueda por CUIT','No se encontró el Proveedor.');*/
                     console.log(message);
                  }
              });        
  }); 


function calcularProd(i){
  var $importe_unitario = parseFloat($("input[name='formDetalle-"+i+"-importe_unitario']").val())|| 0;
  var $cant = parseFloat($("input[name='formDetalle-"+i+"-cantidad']").val())|| 0;
  var $porcDcto = parseFloat($("input[name='formDetalle-"+i+"-porc_dcto']").val())|| 0;
  var $importe_subtotal = 0;
  var $importe_iva = 0;
  var $importe_tot_prod = 0;
  if ($importe_unitario == '') $importe_unitario=0;             

  $importe_subtotal = ($importe_unitario * $cant)*(1-$porcDcto/100);  
  $importe_subtotal = $importe_subtotal; 
  
  var $iva = parseFloat($("input[name='formDetalle-"+i+"-coef_iva']").val())|| 0;
  $importe_iva = $importe_subtotal * $iva;  
  $importe_tot_prod = $importe_subtotal + $importe_iva;      
  $("input[name='formDetalle-"+i+"-importe_total']").val($importe_tot_prod.toFixed(2)); };

function calcularTotales(){                      
      var tot_prod = 0;      
      $('.form-detalles tr').each(function(j) {
          if ($(this).is(':visible'))
          {
            var $importe_tot_prod = parseFloat($("input[name='formDetalle-"+j+"-importe_total']").val())|| 0;               
            tot_prod = tot_prod + $importe_tot_prod;
          }
       });
           
      var $importe_total = 0;        
      $importe_total = tot_prod       
      $("#id_importe_total").val($importe_total.toFixed(2));
  };

function cargarProd(i){
    //Traigo todos los datos del producto
    var idp =  $("[name='formDetalle-"+i+"-producto']").val();
    var idubi =  $("#id_origen_destino").val();
    var idlista =  $("#id_lista_precios").val();
    var dcto = $("#id_cliente_descuento").val();
    if (dcto == undefined) {dcto=0;};
    $.ajax({
            data: {'idp': idp,'idubi':idubi,'idlista':idlista},
            url: '/comprobantes/buscarDatosProd/',
            type: 'get',
            cache: true,          
            success : function(data) {
                 console.log(data);
                 if (data!='')
                    {
                      $("[name='formDetalle-"+i+"-importe_unitario']").val(data['precio_venta']); 
                      $("[name='formDetalle-"+i+"-coef_iva']").val(data['tasa_iva__coeficiente']); 
                      $("[name='formDetalle-"+i+"-tasa_iva']").val(data['tasa_iva__id']); 
                      $("[name='formDetalle-"+i+"-unidad']").val(data['unidad']);                     
                      $("[name='formDetalle-"+i+"-porc_dcto']").val(dcto); 
                      $("[name='formDetalle-"+i+"-cantidad']").val('1');                                        
                    }
                    else{                 
                      $("[name='formDetalle-"+i+"-importe_unitario']").val('0');
                      $("[name='formDetalle-"+i+"-coef_iva']").val('0');                       
                      $("[name='formDetalle-"+i+"-tasa_iva']").val('0');                        
                      $("[name='formDetalle-"+i+"-cantidad']").val('0');
                      $("[name='formDetalle-"+i+"-porc_dcto']").val('0'); 
                      $("[name='formDetalle-"+i+"-unidad']").val('u.'); 
                    };
                    $("[name='formDetalle-"+i+"-lista_precios']").val(idlista); 
                    $("[name='formDetalle-"+i+"-origen_destino']").val(idubi);
                    calcularProd(i);                        
                    calcularTotales();
            },
            error : function(message) {
                 /*alertify.alert('Búsqueda por CUIT','No se encontró el Proveedor.');*/
                 console.log(message);
              }
          });  
    };


function recalcular(){
      $('.form-detalles tr').each(function(j) {
        $("input[name='formDetalle-"+j+"-importe_unitario']").change(function(){
            calcularProd(j);
            calcularTotales();      
         });
        $("input[name='formDetalle-"+j+"-cantidad']").change(function(){
            calcularProd(j);
            calcularTotales();      
         });
       

        $("[name='formDetalle-"+j+"-producto']").change(function(){
            cargarProd(j);
         }); 

        

      });
  

      calcularTotales();
    };

  //Se ejecuta al crearse el form
  


$('.formDetalle').formset({
          addText: 'Agregar Detalle',
          addCssClass: 'add-row btn agregarItem ',       
          deleteCssClass: 'delete-row1',   
          deleteText: 'Eliminar',
          prefix: 'formDetalle',
          formCssClass: 'dynamic-form',
          keepFieldValues:'',
          added: function (row) {
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

            recalcular(); 
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


$("#recargarClientes").click(function () {
  $.getJSON('/recargar_clientes/',{},
        function (c) {
            $("#id_cliente").empty().append('<option value="">---</option>');
            $.each(c["clientes"], function (idx, item) {
                jQuery("<option/>").text(item['codigo']+' - '+item['apellido_y_nombre']+' - '+item['fact_cuit']).attr("value", item['id']).appendTo("#id_entidad");
            })
            $('#id_cliente').trigger("chosen:updated");
        }); 
     });

$("#recargarVendedores").click(function () {
        $.getJSON('/recargar_vendedores/',{},
        function (c) {
            $("#id_vendedor").empty().append('<option value="">---</option>');
            $.each(c["vendedores"], function (idx, item) {
                jQuery("<option/>").text(item['codigo']+' - '+item['apellido_y_nombre']+' - '+item['fact_cuit']).attr("value", item['id']).appendTo("#id_vendedor");
            })
            $('#id_vendedor').trigger("chosen:updated");
        });
  });

$("#recargarProductos").click(function () {      
      
        $.getJSON('/recargar_productos/1',{},
        function (c) {            
          $('.form-detalles tr').each(function(j) {
            $("[name='formDetalle-"+j+"-producto']").empty().append('<option value="">---</option>');            
            $.each(c["productos"], function (idx, item) {
                $("[name='formDetalle-"+j+"-producto']").append('<option value="' + item['id'] + '">' + item['codigo']+' - '+item['nombre'] + '</option>');                
            }); 
            $("[name='formDetalle-"+j+"-producto']").trigger("chosen:updated");           
          });           
        });
  });

$("#id_numero").keyup(function(){
    h = ("00000000" + $(this).val()).slice(-8);    
    $(this).val(h);
});
      
$( "#Guardar" ).click(function() {    
      total = parseFloat($("#id_importe_total").val());     
      
      if (total<=0){
        alertify.errorAlert("¡El importe total debe ser mayor a cero!");
         $("#Guardar").prop("disabled", false);
         return false;
      };       
      $("#form-alta:disabled").removeAttr('disabled');      
        $("#id_numero").removeAttr('disabled'); 
        $("#id_cliente").removeAttr('disabled', 'disabled');
        $("#id_vendedor").removeAttr('disabled', 'disabled');
        $("#Guardar").prop("disabled", true);    
        $( "#form-alta" ).submit();         
        
    

  });



recalcular();

$('.form-detalles tr').each(function(j) {
  $("[name='formDetalle-"+j+"-producto']").chosen({
                no_results_text: "Producto inexistente...",
                placeholder_text_single:"Seleccione una Opcion",
                allow_single_deselect: true,
            });
});



 });