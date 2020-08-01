    alertify.defaults.transition = "slide";
    alertify.defaults.theme.ok = "btn btn-primary";
    alertify.defaults.theme.cancel = "btn btn-default";
    alertify.defaults.theme.input = "form-control";              
   
  
    

    toastr.options = {
      "closeButton": true,
      "debug": false,
      "positionClass": "toast-top-center",
      "onclick": null,
      "showDuration": "1000",
      "hideDuration": "1000",
      "timeOut": "5000",
      "extendedTimeOut": "1000",
      "showEasing": "swing",
      "hideEasing": "linear",
      "showMethod": "fadeIn",
      "hideMethod": "fadeOut",          
    };
    
    if(!alertify.errorAlert){
      alertify.dialog('errorAlert',function factory(){
    return{
            build:function(){
                var errorHeader = '<span class="fa fa-times-circle fa-2x" '
                +    'style="vertical-align:middle;margin-right:10px;color:#e10000;text-align:left;">'
                + '</span> ¡ATENCIÓN!';
                this.setHeader(errorHeader);
            }
        };
    },true,'alert'); 
    };

    if(!alertify.successAlert){
      alertify.dialog('successAlert',function factory(){
    return{
            build:function(){
                var successHeader = '<span class="fa fa-check-circle fa-2x" '
                +    'style="vertical-align:middle;margin-right:10px;color:#6aca5f;text-align:left;">'
                + '</span> ¡ATENCIÓN!';
                this.setHeader(successHeader);
            }
        };
    },true,'alert'); 
    };

    if(!alertify.warningAlert){
      alertify.dialog('warningAlert',function factory(){
    return{
            build:function(){
                var warningHeader = '<span class="fa fa-check-circle fa-2x" '
                +    'style="vertical-align:middle;color:#FFFF00;margin-right:10px;text-align:left;">'
                + '</span> ¡ATENCIÓN!';
                this.setHeader(warningHeader);
            }
        };
    },true,'alert'); 
    };

    $("input[type=number]").click(function() {
        this.select()
    });

     function recargarClientes(){
        $.getJSON('/recargar_clientes/',{},
        function (c) {
            $("#id_entidad").empty().append('<option value="">---</option>');
            $.each(c["clientes"], function (idx, item) {
                 $("#id_entidad").append('<option value="' + item['id'] + '">' + item['detalle'] + '</option>');      
            })
            $('#id_entidad').trigger("chosen:updated");
            $("#recargarClientes").trigger("click");
        });      
		};

	function recargarVendedores(){
	        $.getJSON('/recargar_vendedores/',{},
	        function (c) {
	            $("#id_vendedor").empty().append('<option value="">---</option>');
	            $.each(c["vendedores"], function (idx, item) {
	                 $("#id_vendedor").append('<option value="' + item['id'] + '">' + item['detalle'] + '</option>');      
	            })
	            $('#id_vendedor').trigger("chosen:updated");
	        });
	  };

	function recargarProveedores(){
        $.getJSON('/recargar_proveedores/',{},
        function (c) {
            $("#id_entidad").empty().append('<option value="">---</option>');
            $.each(c["proveedores"], function (idx, item) {
                $("#id_entidad").append('<option value="' + item['id'] + '">' + item['detalle'] + '</option>');                     
            })
            $('#id_entidad').trigger("chosen:updated");
            $("#recargarProductos").trigger("click");
        }); 
     };     

  function recargarProds(){
        $.getJSON('/recargar_productos/1',{},
        function (c) {            
          $('.form-detalles tr').each(function(j) {
            var idp =  $("[name='formDetalle-"+j+"-producto']").val(); 
            $("[name='formDetalle-"+j+"-producto']").empty().append('<option value="">---</option>');            
            $.each(c["productos"], function (idx, item) {
                $("[name='formDetalle-"+j+"-producto']").append('<option value="' + item['id'] + '">' + item['detalle'] + '</option>');                                
            });                         
            if ((idp == '')||(idp == undefined)){
              $("[name='formDetalle-"+j+"-producto']").trigger("chosen:updated");
            }else{
            $("[name='formDetalle-"+j+"-producto']").val(idp).trigger("chosen:updated");
            }
          });           
        });
     };     



	   