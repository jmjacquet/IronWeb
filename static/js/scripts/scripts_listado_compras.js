function abrir_modal(url) {
        $('#popup').load(url, function() {
            $(this).modal('show');
        });
        return false;
    }
    function cerrar_modal() {
        $('#popup').modal('hide');
        return false;
    }
$(document).ready(function() {

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
        
moment.locale('es');
$.fn.dataTable.moment('DD/MM/YYYY'); 
var tabla = $('#dataTables-cpb_compra').DataTable({
           "language": {
                "decimal": ",",
                "thousands": ".", 
                "sProcessing": "Procesando...",
                "sLengthMenu": "Mostrar _MENU_ registros",
                "sZeroRecords": "No se encontraron resultados",
                "sEmptyTable": "No hay registros en esta tabla",
                "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
                "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
                "sInfoPostFix": "",
                "sSearch": "Buscar:",
                "sUrl": "",
                "sInfoThousands": ",",
                "sLoadingRecords": "Cargando...",
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "oAria": {
                    "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
                    "sSortDescending": ": Activar para ordenar la columna de manera descendente"
                },
                      
            },                      
            "columnDefs": [ {
                  "targets"  : 'no-sort',
                  "orderable": false,
                }],          
           "paging":   true,
           "lengthMenu": [[20, 50, -1], [20, 50, "Todos"]],
           "autoWidth": false,
           "order": [],
           "colReorder": true,
           "searching": true,
            responsive: true,
            //dom: 'Bfrtlip',
            dom: "Bf<'row'<'col-sm-12'tr>>"+"<'row'<'col-sm-3'l><'col-sm-9'ip>>",
            buttons: [
                {
                    extend:    'colvis',
                    text:      '<i class="fa fa-list"></i>',
                    titleAttr: 'Ver/Ocultar',
                    className: 'btnToolbar',                    
                },
                {
                    extend:    'copyHtml5',
                    text:      '<i class="fa fa-files-o"></i>',
                    titleAttr: 'Copiar',
                    exportOptions: { columns: ':visible' },
                    className: 'btnToolbar',                    
                },
                {
                    extend:    'excel',
                    text:      '<i class="fa fa-file-excel-o"></i>',
                    titleAttr: 'Excel',
                    filename: 'COMPRAS',                    
                    exportOptions: {  modifier: {
                                        page: 'current'
                                    }, 
                                      columns: '.imprimir',
                                      format: {
                                      body: function(data, row, column, node) {
                                        var floatVal = function (i) {
                                            if (typeof i === "number") {
                                                return i;
                                            } else if (typeof i === "string") {
                                                i = i.replace(/\$/g, "");
                    i = i.replace(/\,/g ,"");                    
                    i = i.replace(/\./g, "");
                                                var result = parseFloat(i)/100;
                                                // console.log(result);
                                                if (isNaN(result)) {
                                                    try {
                                                        var result = $jq(i).text();
                                                        result = parseFloat(result);
                                                        if (isNaN(result)) { result = 0 };
                                                        return result * 1;
                                                    } catch (error) {
                                                        return 0;
                                                    }
                                                } else {
                                                    return result * 1;
                                                }
                                            } else {
                                                alert("Unhandled type for totals [" + (typeof i) + "]");
                                                return 0
                                            }
                                        };
                                          data = $('<p>' + data + '</p>').text();
                                          return (node.className=='importe') ? floatVal(data)  : data;
                                      }
                                    }},
                    className: 'btnToolbar',     
                },
               
                {
                    extend:    'pdfHtml5',
                    text:      '<i class="fa fa-file-pdf-o"></i>',
                    titleAttr: 'PDF',footer: true,
                    exportOptions: { columns: '.imprimir'},
                    orientation: 'landscape',
                    className: 'btnToolbar',                    
                },
                {
                    extend: 'print',
                    text:      '<i class="fa fa-print"></i>',
                    titleAttr: 'Imprimir',
                    exportOptions: { columns: '.imprimir' },
                    className: 'btnToolbar',                    
                },
            ],
              PreDrawCallback:function(){
            $("#cargando").show();
            },
            initComplete: function () {
               // this.api().columns().every( function () {[0, 1, 9]
                this.api().columns([3,5]).every( function () {
                    var column = this;
                    var select = $('<select class="form-control"><option value="">Todos</option></select>')
                        .appendTo( $(column.footer()).empty() )
                        .on( 'change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );
     
                            column
                                .search( val ? '^'+val+'$' : '', true, false )
                                .draw();
                        } );
     
                     column.data().unique().sort().each( function ( d, j ) {
                    //column.cells('', column[0]).render('display').sort().unique().each( function ( d, j ){
                        select.append( '<option value="'+d+'">'+d+'</option>' )
                    } );
                } );
                 $("#dataTables-cpb_compra").show();
                  this.fnAdjustColumnSizing();
                $("#cargando").hide();

            },
            "footerCallback": function ( row, data, start, end, display ) {
            var api = this.api(), data;
            var floatVal = function (i) {
                if (typeof i === "number") {
                    return i;
                } else if (typeof i === "string") {
                    i = i.replace(/\$/g, "");
                    i = i.replace(/\,/g ,"");                    
                    i = i.replace(/\./g, "");
                    var result = parseFloat(i)/100;
                    // console.log(result);
                    if (isNaN(result)) {
                        try {
                            var result = $jq(i).text();
                            result = parseFloat(result);
                            if (isNaN(result)) { result = 0 };
                            return result * 1;
                        } catch (error) {
                            return 0;
                        }
                    } else {
                        return result * 1;
                    }
                } else {
                    alert("Unhandled type for totals [" + (typeof i) + "]");
                    return 0
                }
            };
            let col_tot_sum =[8, 9, 10, 11, 12]
            col_tot_sum.forEach(function (col_number) {
                pageTotal = api.column(col_number, { page: 'current'} ).data().reduce( function (a, b) {return floatVal(a) + floatVal(b);}, 0 );
                $( api.column(col_number).footer() ).html('$'+pageTotal.toLocaleString(undefined,{minimumFractionDigits:2}));
            });


            }
        });



 function abrir_modal(url) {
        $('#popup').load(url, function() {
            $(this).modal('show');
        });
        return false;
    }
    function cerrar_modal() {
        $('#popup').modal('hide');
        return false;
    }
    var cpbs = [];
   
    

    $("input[class='tildado']" ,tabla.rows().nodes()).change(function() {                
        str1 = '/egresos/pagos/comprobantes/?';
        str2 = '';
        checkbox=this;
        id_cpb = checkbox.value;
        if (checkbox.checked) {               
                //Agrego al array de cpbs seleccionados
                cpbs.push(id_cpb);                
                $(checkbox).closest('tr').toggleClass('selected', checkbox.checked);                                
        } else {
            if ($(checkbox).closest('tr').hasClass('selected')) {
                $(checkbox).closest('tr').removeClass('selected');
            };
            var cpbs2=[];
            //Regenero el array de cpbs selecionados sin el que acabo de quitar
            for( var i = 0; i < cpbs.length; i++){
                if ( cpbs[i] != id_cpb) cpbs2.push(cpbs[i]);                    
                };
            cpbs=cpbs2;     
        };
        //Armo el String para los botones
        for (var i = 0; i < cpbs.length; i++) {                
                if (str2 == '') {
                    str2 = str2 + 'id_cpb=' + cpbs[i];
                } else {
                    str2 = str2 + '&id_cpb=' + cpbs[i];
                };
        };
        $('#btnPago').val(str1 + str2)
        $('#btnAnular').val(str2);
               
    });
       
    // function checkBoxClick2() {
    //     cpbs = [];
    //     cant = 0;
    //     str1 = '/egresos/pagos/comprobantes/?'
    //     str2 = ''
    //     $("input[class='tildado']", tabla.rows().nodes()).each(function(index, checkbox) {
    //         if (checkbox.checked) {                
    //             chk = document.getElementById(checkbox.id);
    //             if (chk!=null){
    //                 id_cpb = chk.value;
    //                 cpbs.push(id_cpb);
    //                 cant += 1;
    //                 $(checkbox).closest('tr').toggleClass('selected', checkbox.checked);
    //                 if (str2 == '') {
    //                     str2 = str2 + 'id_cpb=' + id_cpb;
    //                 } else {
    //                     str2 = str2 + '&id_cpb=' + id_cpb;
    //                 };
    //             }
    //         } else {
    //             if ($(checkbox).closest('tr').hasClass('selected')) {
    //                 $(checkbox).closest('tr').removeClass('selected');
    //             }
    //         };
    //         $('#btnPago').val(str1 + str2)
    //         $('#btnAnular').val(str2);
    //     });
    // };

    $('#btnAnular').click(function() {
        if (cpbs.length == 0) {
            alertify.errorAlert("¡Debe seleccionar algún comprobante!");
        } else {
            alerta = alertify.dialog('confirm').set({
                'labels': {
                    ok: 'Aceptar',
                    cancel: 'Cancelar'
                },
                'message': '¿Desea Anular los Comprobantes seleccionados?',
                transition: 'fade',
                'onok': function() {
                    $.ajax({
                        url: "/comprobantes/cpbs_anular?" + $('#btnAnular').val(),
                        type: "get",
                        dataType: 'json',
                        success: function(data) {
                            window.location.href = window.location.href
                        }
                    });
                },
                'oncancel': function() {
                    return true;
                }
            });
            alerta.setting('modal', true);
            alerta.setHeader('ANULAR COMPROBANTES');
            alerta.show();
            return true;
        }
    });
    $('#btnPago').click(function() {
        if (cpbs.length == 0) {
            alertify.errorAlert("¡Debe seleccionar algún comprobante!");
        } else {
            datos = []
            $.ajax({
                url: "/comprobantes/verifCobranza/",
                type: "get",
                dataType: 'json',
                data: {
                    'cpbs[]': cpbs
                },
                success: function(data) {
                    if (data > 1) {
                        alertify.errorAlert("¡No debe seleccionar comprobantes de más de un Proveedor!");
                    } else {
                        return abrir_modal($('#btnPago').val());
                    }
                }
            });
        }
    });

    $('#btnImprimirDetalles').click(function() {
        if (cpbs.length == 0) {
            alertify.errorAlert("¡Debe seleccionar algún comprobante!");
        } else {
            alerta = alertify.dialog('confirm').set({
                'labels': {
                    ok: 'Aceptar',
                    cancel: 'Cancelar'
                },
                'message': '¿Desea Imprimir el Detalle de los Comprobantes seleccionados?',
                transition: 'fade',
                'onok': function() {
                    window.open("/comprobantes/imprimir_detalles?" + $('#btnAnular').val())                   
                },
                'oncancel': function() {
                    return true;
                }
            });
            alerta.setting('modal', true);
            alerta.setHeader('IMPRIMIR COMPROBANTES');
            alerta.show();
            return true;
        }
    });

$("a[name='mandarEmail']", tabla.rows().nodes()).click(function() {
        var id = $(this).attr('value');
        datos = []
        $.ajax({
            url: "/comprobantes/verifEmail/",
            type: "post",
            dataType: 'json',
            data: {
                'id': id
            },
            success: function(data) {
                if (data!='') {
                    window.location.href = '/comprobantes/mandarEmail/'+id;
                } else {
                    alertify.prompt('ENVIAR COMPROBANTE x EMAIL','Ingrese la dirección de Email:','',
                        function(evt, value) 
                        {
                            var email = value;
                            window.location.href = '/comprobantes/mandarEmail/'+id+'/?email='+email;
                        },
                        function(){} ).set('labels', {ok:'Aceptar', cancel:'Cancelar'}).set('type', 'email');
                }
            }
        });
        });   
    

});