


$(document).ready(function() { 

$("input[type=number]").click(function(){
            this.select()
          });
function abrir_modal(url)
{        $('#popup').load(url, function()
        {        $(this).modal('show');
        });
        return false;};

function cerrar_modal()
{        $('#popup').modal('hide');
        return false;};

var cheques = [];


$("input[class='selecc']").change(function() {      
      chequearFP();                   
  });

function chequearFP() {
    cheques = [];
    cant = 0; 
    str1 = '/comprobantes/cobrar_depositar_cheques?'    
    str2 = ''
    $("input[class='selecc']").each(function(index,checkbox){
     if(checkbox.checked){               
         id_fp = document.getElementById(checkbox.id+"_id_fp").value.replace('.', '');                        
         cheques.push(id_fp);             
         cant += 1;          
         $(checkbox).closest('tr').toggleClass('selected', checkbox.checked);
         if (str2==''){
          str2= str2+'id_fp='+id_fp;
         }else{
          str2= str2+'&id_fp='+id_fp;
         };
      }
      else {  
          if($(checkbox).closest('tr').hasClass('selected')){
            $(checkbox).closest('tr').removeClass('selected');}
      };
      $('#btnCobro').val(str2);      
    });   
};


$('#btnCobro').click(function(){
   
    if (cheques.length==0)
      { alertify.errorAlert("¡Debe seleccionar algún cheque!");}
    else
    {  return abrir_modal('/comprobantes/cobrar_depositar_cheques?'+$('#btnCobro').val());}
});


                              



});