$(document).ready(function() {  


function cambiar_nro(i,nro){
	
	alertify.prompt('Modificar Último  Número', 
	'Se generará el siguiente número para la combinación de TipoCPB/Pto.Venta/Letra.<br>Ingrese el último Número generado:',nro,function(evt, value) {
	 	var nro = value;window.location.href = '{% url "pto_vta_numero_cambiar" pk=i nro=nro %}';
	 },
	 function(){} ).set('labels', {ok:'Aceptar', cancel:'Cancelar'});
};

});

