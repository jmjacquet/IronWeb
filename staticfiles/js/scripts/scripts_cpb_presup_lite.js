$(document).ready(function() {  


$("input[type=number]").click(function(){
            this.select()
          });

$("#id_entidad").chosen({
          no_results_text: "Cliente inexistente...",
          placeholder_text_single:"Seleccione un Cliente",
          allow_single_deselect: true,
      }); 

$("#id_vendedor").chosen({
          no_results_text: "Vendedor inexistente...",
          placeholder_text_single:"Seleccione un Vendedor",
          allow_single_deselect: true,
      }); 



$("#id_entidad").change(function(){
    var id =  $("#id_entidad").val();
          $.ajax({
                data: {'id': id},
                url: '/comprobantes/buscarDatosEntidad/',
                type: 'get',
                cache: true,          
                success : function(data) {
                     
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
    if ($('#id_tipo_form').val()=='ALTA')
    {
      $.ajax({
                data: {'id': id},
                url: '/comprobantes/setearLetraCPB/',
                type: 'get',
                cache: true,          
                success : function(data) {
                    
                     if (data!='')
                        {
                          $("#id_letra").val(data[0]); 
                          $("#id_letra").trigger("change");
                        }
                       
                },
                error : function(message) {
                     /*alertify.alert('Búsqueda por CUIT','No se encontró el Proveedor.');*/
                     console.log(message);
                  }
              });
    };

  }); 


function calcularProd(i){
  var cant = parseFloat($("input[name='formDetalle-"+i+"-cantidad']").val())|| 0;
  var porcDcto = parseFloat($("input[name='formDetalle-"+i+"-porc_dcto']").val())|| 0;
  var importe_subtotal = 0;
  var importe_iva = 0;
  var importe_total = 0;
  var coef_iva = parseFloat($("input[name='formDetalle-"+i+"-coef_iva']").val())|| 0;            
  var importe_unitario = parseFloat($("input[name='formDetalle-"+i+"-importe_unitario']").val())|| 0;    
  var importe_parcial = (importe_unitario * cant)*(1-porcDcto/100)
  
  letra = $("#id_letra").val();                      
  if (letra=='A'){ 
    importe_iva = importe_parcial * coef_iva;
    importe_subtotal = importe_parcial;
    importe_total = importe_subtotal + importe_iva;    
   }else
  {if  (letra=='X') {    
    importe_iva = 0
    importe_total = importe_parcial; 
    importe_subtotal = importe_total - importe_iva;
  }  
  else{    
    importe_iva = importe_parcial-(importe_parcial/(1+coef_iva))
    importe_total = importe_parcial; 
    importe_subtotal = importe_total - importe_iva;
  }}  
  $("input[name='formDetalle-"+i+"-importe_subtotal']").val(importe_subtotal.toFixed(2));  
  $("input[name='formDetalle-"+i+"-importe_total']").val(importe_total.toFixed(2)); 
  $("input[name='formDetalle-"+i+"-importe_iva']").val(importe_iva.toFixed(2));
};


function calcularTotales(){                
      var totParcial=0;
      var tot_prod = 0;
      var totIVA=0;
      $('.form-detalles tr').each(function(j) {
             if ($(this).is(':visible'))
          {            
            var $importe_tot_prod = parseFloat($("input[name='formDetalle-"+j+"-importe_total']").val())|| 0;               
            var $iva_parcial = parseFloat($("input[name='formDetalle-"+j+"-importe_iva']").val())|| 0; 
            var $importe_parcial = parseFloat($("input[name='formDetalle-"+j+"-importe_subtotal']").val())|| 0;               
            if ($importe_parcial == '') $importe_parcial=0;       
            totParcial = totParcial + $importe_parcial;
            tot_prod = tot_prod + $importe_tot_prod;
            totIVA = totIVA + $iva_parcial; 
          }
       });
      $("#id_importe_subtotal").val((totParcial).toFixed(2));
      $("#id_importe_iva").val(totIVA.toFixed(2));
           
     
      var $importe_total = 0;        
      var $importe_subtot = parseFloat($("#id_importe_subtotal").val())|| 0;      
      $importe_total = $importe_subtot + totIVA;
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
                 
                 if (data!='')
                    {
                      
                      $("[name='formDetalle-"+i+"-importe_costo']").val(data['costo_siva']); 
                      $("[name='formDetalle-"+i+"-coef_iva']").val(data['tasa_iva__coeficiente']); 
                      $("[name='formDetalle-"+i+"-tasa_iva']").val(data['tasa_iva__id']); 
                      $("[name='formDetalle-"+i+"-unidad']").val(data['unidad']);                     
                      $("[name='formDetalle-"+i+"-porc_dcto']").val(dcto); 
                      $("[name='formDetalle-"+i+"-cantidad']").val('1');                  
                      var $porcDcto = dcto;
                      var $importe_unitario = data['precio_venta'];
                      var $importe_iva = data['total_iva'];
                      var $importe_tot = data['precio_tot'];                              
                      var $importe_siva = data['precio_siva'];                   
                      var $coef_iva = data['tasa_iva__coeficiente'];
                      letra = $("#id_letra").val();                      
                      if (letra=='A'){ 
                        $("[name='formDetalle-"+i+"-importe_unitario']").val(parseFloat($importe_siva).toFixed(2));
                      }else
                      {
                        $("[name='formDetalle-"+i+"-importe_unitario']").val(parseFloat($importe_unitario).toFixed(2));
                      };
                      
                      $("[name='formDetalle-"+i+"-importe_total']").val(parseFloat($importe_tot).toFixed(2));                      
                      $("[name='formDetalle-"+i+"-importe_iva']").val(parseFloat($importe_iva).toFixed(2));
                    }
                    else{                 
                      $("[name='formDetalle-"+i+"-importe_unitario']").val('0');
                      $("[name='formDetalle-"+i+"-coef_iva']").val('0'); 
                      $("[name='formDetalle-"+i+"-importe_costo']").val('0');
                      $("[name='formDetalle-"+i+"-tasa_iva']").val('0');  
                      $("[name='formDetalle-"+i+"-unidad']").val('u.');
                      $("[name='formDetalle-"+i+"-porc_dcto']").val(dcto); 
                      $("[name='formDetalle-"+i+"-cantidad']").val('0'); 
                      $("[name='formDetalle-"+i+"-importe_total']").val('0');
                      $("[name='formDetalle-"+i+"-importe_iva']").val('0');
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

function recargarProd(i){
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
                 
                 if (data!='')
                    {                      
                      $("[name='formDetalle-"+i+"-importe_costo']").val(data['costo_siva']); 
                      $("[name='formDetalle-"+i+"-coef_iva']").val(data['tasa_iva__coeficiente']); 
                      $("[name='formDetalle-"+i+"-tasa_iva']").val(data['tasa_iva__id']); 
                      $("[name='formDetalle-"+i+"-unidad']").val(data['unidad']);                                           
                    }
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
          $("input[name='formDetalle-"+j+"-porc_dcto']").change(function(){
              calcularProd(j);
              calcularTotales();      
           });

          $("[name='formDetalle-"+j+"-producto']").change(function(){           
              cargarProd(j);
           });

           $("input[name='formDetalle-"+j+"-importe_iva']").change(function(){            
              calcularTotales();      
           });
          $("input[name='formDetalle-"+j+"-importe_subtotal']").change(function(){            
              calcularTotales();      
           });
          $("input[name='formDetalle-"+j+"-importe_total']").change(function(){            
              calcularTotales();      
           }); 

      });
      calcularTotales();
      $("#id_letra").trigger("change");
};


$('.formDetalle').formset({
          addText: 'Agregar Detalle',
          addCssClass: 'add-row btn blue-hoki ',       
          deleteCssClass: 'delete-row btn red-flamingo',   
          deleteText: 'Quitar',
          prefix: 'formDetalle',
          formCssClass: 'dynamic-form',
          keepFieldValues:'',
          added: function (row) {
            var i1 = $("#id_formDetalle-TOTAL_FORMS").val()-1;
            $("[name='formDetalle-"+i1+"-cantidad']").val(1);
            $("[name='formDetalle-"+i1+"-importe_unitario']").val('0');
            $("[name='formDetalle-"+i1+"-porc_dcto']").val('0');
            $("[name='formDetalle-"+i1+"-unidad']").val('u.');
            
            $("[name='formDetalle-"+i1+"-producto']").chosen({
                no_results_text: "Producto inexistente...",
                placeholder_text_single:"Seleccione un Producto",
                allow_single_deselect: true,
            });
            $("[name='formDetalle-"+i1+"-producto']").focus();
            cargarProd(i1);
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



$( "#Guardar" ).click(function() {
    total = parseFloat($("#id_importe_total").val());
    if (total<=0){
        alertify.errorAlert("¡El importe total debe ser mayor a cero!");
         $("#GuardarVenta").prop("disabled", false);
         return false;
      };         
        $("#form-alta:disabled").removeAttr('disabled');
        $('#id_pto_vta').removeAttr('disabled');          
        $("#id_letra").removeAttr('disabled');        
        $("#id_numero").removeAttr('disabled'); 
        $("#id_entidad").removeAttr('disabled', 'disabled');
        $("#id_vendedor").removeAttr('disabled', 'disabled');        
        $( "#form-alta" ).submit();         
  });
 


function ultimoNumCPB(cpb_tipo,letra,pto_vta){
    if ($('#id_tipo_form').val()=='ALTA')
    {
      $.ajax({
          data: {'cpb_tipo': cpb_tipo,'letra':letra,'pto_vta':pto_vta},
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

$("#id_letra").change(function(){
     letra = $("#id_letra").val();
     pto_vta = $("#id_pto_vta").val();
     cpb_tipo = 11; 
     $('.segunLetra').each(function() {
        if (letra != 'A'){
          $(this).hide();          
          $("#tit_precio").attr('data-original-title', "Precio Venta con impuestos");
          $("#tit_total").attr('data-original-title', "Importe Total");
        }
        else{
          $(this).show();
          $("#tit_precio").attr('data-original-title', "Precio Venta sin impuestos");
          $("#tit_total").attr('data-original-title', "Importe Subtotal + IVA");
        };
       });
     ultimoNumCPB(cpb_tipo,letra,pto_vta);
 });  

$("#id_numero").keyup(function(){
    h = ("00000000" + $(this).val()).slice(-8);    
    $(this).val(h);
 });

 
$("#id_pto_vta").change(function(){
     letra = $("#id_letra").val();
     pto_vta = $("#id_pto_vta").val();
     cpb_tipo = 11;          
     ultimoNumCPB(cpb_tipo,letra,pto_vta);
 });  


$('.form-detalles tr').each(function(j) {
  $("[name='formDetalle-"+j+"-producto']").chosen({
                no_results_text: "Producto inexistente...",
                placeholder_text_single:"Seleccione una Opcion",
                allow_single_deselect: true,
            });
});

$("#id_formDetalle-0-producto").focus();



recalcular(); 
$("#id_entidad").trigger("change");
$("#id_letra").trigger("change"); 

 });