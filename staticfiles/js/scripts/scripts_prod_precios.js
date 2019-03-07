


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

$("#lp_checkall").click (function () {
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
          alerta = alertify.dialog('confirm').set({
                'labels': {
                    ok: 'Aceptar',
                    cancel: 'Cancelar'
                },
                'message': '¿Desea actualizar el precio de todos los productos?',
                transition: 'fade',
                'onok': function() {
                    alerta.close();
                    return abrir_modal('/productos/prod_precios_actualizar/');                    
                },
                'oncancel': function() {                   
                    return true;                    
                }
            });
            alerta.setting('modal', true);
            alerta.setHeader('ACTUALIZAR PRECIOS');
            alerta.show();
      }
    else
    {
      return abrir_modal('/productos/prod_precios_actualizar?'+$('#btnActualizar').val());
    }

});

      
});