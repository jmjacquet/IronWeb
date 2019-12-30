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
var tabla = $('#dataTables-cpb_venta').DataTable({
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
                    "sLast": "Ãšltimo",
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
            fixedHeader: {
              header: false,
              footer: false
              },
            responsive: true,
            dom: 'Bfrtlip',
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
                    filename: 'COMPROBANTES',                    
                    exportOptions: {  modifier: {
                                        page: 'current'
                                    }, 
                                      columns: ':visible',
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
                    exportOptions: { columns: ':visible'},
                    orientation: 'landscape',
                    className: 'btnToolbar',                    
                },
                {
                    extend: 'print',
                    text:      '<i class="fa fa-print"></i>',
                    titleAttr: 'Imprimir',
                    exportOptions: { columns: ':visible' },
                    className: 'btnToolbar',                    
                },
            ],
            PreDrawCallback:function(){
            $("#cargando").show();
            },
    
           
            initComplete: function () {
               // this.api().columns().every( function () {[0, 1, 9]
                this.api().columns([3,6]).every( function () {
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
                $("#dataTables-cpb_venta").show();
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
                        
            
            pageTotal1 = api.column(8, { page: 'current'} ).data().reduce( function (a, b) {return floatVal(a) + floatVal(b);}, 0 );            
            $( api.column(8).footer() ).html('$'+pageTotal1.toLocaleString(undefined,{minimumFractionDigits:2}));            
            },
                                  
        });

  var cpbs = [];
    $("#checkall").click(function() {
        var checkedStatus = this.checked;
        $("input[class='tildado']", tabla.rows().nodes()).each(function() {
            $(this).prop("checked", checkedStatus);
            $(this).find('span').addClass('checked');
            $(this).change();
        });
    });
    $("input[class='tildado']" ,tabla.rows().nodes()).change(function() {        
        checkBoxClick1();
    });
   
      function checkBoxClick1() {
        cpbs = [];
        cant = 0;
        str2 = ''
        $("input[class='tildado']",tabla.rows().nodes()).each(function(index, checkbox) {
            if (checkbox.checked) {
                id_cpb = document.getElementById(checkbox.id + "_id_cpb").value.replace('.', '');
                cpbs.push(id_cpb);
                cant += 1;
                $(checkbox).closest('tr').toggleClass('selected', checkbox.checked);
                if (str2 == '') {
                    str2 = str2 + 'id_cpb=' + id_cpb;
                } else {
                    str2 = str2 + '&id_cpb=' + id_cpb;
                }
                ;
            } else {
                if ($(checkbox).closest('tr').hasClass('selected')) {
                    $(checkbox).closest('tr').removeClass('selected');
                }
            };
            
            $('#btnImprimirDetalles').val(str2);
        });
    };

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
                    window.open("/comprobantes/imprimir_detalles?" + $('#btnImprimirDetalles').val())                   
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


 


});

      


