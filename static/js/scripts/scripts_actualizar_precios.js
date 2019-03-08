$(document).ready(function() { 

  $("input[type=number]").click(function(){
            this.select()
          });


  $( "#AceptarSeleccion" ).click(function() {
      datos = [];
      formData = $('#selecc_prods').serialize()+'&'+$("#btnActualizar").val();
      $.ajax({
      url : "/productos/prod_precios_actualizar/" ,
      data : formData,
      type: "POST",            
      dataType : "json",
       success: function(data) {            
          console.log(data);
          if (data['cant']<=0){
                  alertify.errorAlert(data["message"]);     
                }
                else{                       
                 alertify.successAlert("¡Los precios fueron actualizados exitosamente!",function(){ location.reload(); }); 
                  setTimeout(function(){
                    location.reload();}, 5000);
                   };
      },
      error: function(data) {            
          console.log(data);}
    });           
  });

  $("#id_tipo_operacion").change(function(){
           id = $(this).val();          
           if (id==3){
            $('#campo').hide();
            $('#valor').hide();
            $('#porc').hide();
            $('#coef').show();
           }else if (id<=1) {
            $('#campo').show();
            $('#valor').show();
            $('#porc').hide();
            $('#coef').hide();            
           }else{
            $('#campo').show();
            $('#valor').hide();
            $('#porc').show();
            $('#coef').hide();
           }
         });   

  $("#id_tipo_operacion").trigger("change");
});