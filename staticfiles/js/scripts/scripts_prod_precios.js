


$(document).ready(function() { 


function abrir_modal(url)
{        $('#popup').load(url, function()
        {        $(this).modal('show');
        });
        return false;}

function cerrar_modal()
{        $('#popup').modal('hide');
        return false;}


var lista = [];

$("#checkall").click (function () {
     var checkedStatus = this.checked;
    $("input[class='tildado precios']").each(function () {
        $(this).prop("checked", checkedStatus);
        $(this).find('span').addClass('checked');
        $(this).change();
     });
  });


$("input[class='tildado precios']").change(function() {      
      chk_precio();                     
  });

function chk_precio() {
    lista = [];
    cant = 0; 
    str1 = '/productos/prod_precios/actualizar?'
    str2 = ''
    $("input[class='tildado precios']").each(function(index,checkbox){
        if(checkbox.checked){               
         id = document.getElementById(checkbox.id+"_id").value.replace('.', '');                        
         lista.push(id);             
         cant += 1;          
         $(checkbox).closest('tr').toggleClass('selected', checkbox.checked);
         if (str2==''){
          str2= str2+'id='+id;
         }else{
          str2= str2+'&id='+id;
         };
      }
      else {  
          if($(checkbox).closest('tr').hasClass('selected')){
            $(checkbox).closest('tr').removeClass('selected');}
          };
      $('#btnActualizar').val(str2)
          
    });
   //console.log('CPBs:'+cpbs);
};


$('#btnActualizar').click(function(){
    //console.log(cpbs)
    if (lista.length==0)
      { 
           alertify.errorAlert("¡Debe seleccionar algún Producto!");
           return true;
      }
    else
    {
      return abrir_modal('/productos/prod_precios_actualizar?'+$('#btnActualizar').val());
    }

});

$('#btnImprimirCBS').click(function(){
    //console.log(cpbs)
    if (lista.length==0)
      {          
           alertify.errorAlert("¡Debe seleccionar algún Producto!");
           return true;
      }
    else {
        return abrir_modal('/productos/prod_precios_imprimirCBS?'+$('#btnActualizar').val());        
    }

});

      
});