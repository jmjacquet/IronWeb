$(document).ready(function() { 

$("input[type=number]").click(function(){
            this.select()
          });

  $( "#AceptarSeleccion" ).click(function() {
    datos = [];
    formData = $('#selecc_prods').serialize()+'&'+$("#btnActualizar").val();
    $.ajax({
    url : "/productos/prod_stock_nuevo/" ,
    data : formData,
    type: "POST",            
    dataType : "json",
     success: function(data) {            
        console.log(data);
        if (data['cant']<=0){
                alertify.errorAlert(data["message"]);     
              }
              else{                       
               alertify.successAlert("¡El stock fue creado exitosamente!",function(){ location.reload(); }); 
                setTimeout(function(){
                  location.reload();}, 5000);
                 };
    },
    error: function(data) {            
        console.log(data);}
  });           
});


});