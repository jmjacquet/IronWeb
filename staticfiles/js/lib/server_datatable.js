/*
 * Generic helper to wire a DataTable to server-side pagination/sorting/search.
 * Pages keep their own columns/ajax/order/sumColumns; this only supplies the
 * defaults every listing repeats (language, loading indicator, export buttons,
 * numeric-sum footer).
 */
var ServerDataTable = (function() {

    var ES_LANG = {
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
        "sInfoThousands": ".",
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
        }
    };

    function floatVal(i) {
        if (typeof i === "number") {
            return i;
        } else if (typeof i === "string") {
            i = i.replace(/[^0-9\-,]/g, "");
            i = i.replace(/\,/g, "");
            i = i.replace(/\./g, "");
            var result = parseFloat(i) / 100;
            if (isNaN(result)) {
                try {
                    result = parseFloat($jq(i).text());
                    return isNaN(result) ? 0 : result;
                } catch (error) {
                    return 0;
                }
            }
            return result;
        }
        return 0;
    }

    function excelBodyFormatter(data, row, column, node) {
        data = $('<p>' + data + '</p>').text();
        return (node.className === 'importe') ? floatVal(data) : data;
    }

    function defaultButtons(exportFilename) {
        return [
            {
                extend: 'colvis',
                text: '<i class="fa fa-list"></i>',
                titleAttr: 'Ver/Ocultar',
                className: 'btnToolbar',
            },
            {
                extend: 'copyHtml5',
                text: '<i class="fa fa-files-o"></i>',
                titleAttr: 'Copiar',
                exportOptions: { columns: ':visible' },
                className: 'btnToolbar',
            },
            {
                extend: 'excel',
                text: '<i class="fa fa-file-excel-o"></i>',
                titleAttr: 'Excel',
                filename: exportFilename || 'REPORTE',
                exportOptions: {
                    modifier: { page: 'current' },
                    columns: '.imprimir',
                    format: { body: excelBodyFormatter }
                },
                className: 'btnToolbar',
            },
            {
                extend: 'pdfHtml5',
                text: '<i class="fa fa-file-pdf-o"></i>',
                titleAttr: 'PDF',
                footer: true,
                exportOptions: { columns: '.imprimir' },
                orientation: 'landscape',
                className: 'btnToolbar',
            },
            {
                extend: 'print',
                text: '<i class="fa fa-print"></i>',
                titleAttr: 'Imprimir',
                exportOptions: { columns: '.imprimir' },
                className: 'btnToolbar',
            },
        ];
    }

    // opts.sumColumns: column indexes to sum in the footer, using only the current page's data.
    function sumFooterCallback(sumColumns) {
        return function() {
            var api = this.api();
            sumColumns.forEach(function(colIndex) {
                var pageTotal = api.column(colIndex, { page: 'current' }).data().reduce(function(a, b) {
                    return floatVal(a) + floatVal(b);
                }, 0);
                $(api.column(colIndex).footer()).html(pageTotal.toLocaleString(undefined, { minimumFractionDigits: 2 }));
            });
        };
    }

    // opts: { loadingSelector, exportFilename, sumColumns, dtOptions }
    // dtOptions carries the page-specific bits (ajax, columns, order, ...) and
    // overrides any default below it shares a key with.
    function init(tableSelector, opts) {
        opts = opts || {};
        var loadingSelector = opts.loadingSelector || '#cargando';

        var defaults = {
            language: ES_LANG,
            processing: true,
            serverSide: true,
            autoWidth: false,
            colReorder: true,
            searching: false,
            fixedHeader: { header: false, footer: false },
            responsive: true,
            dom: "Bf<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-3'l><'col-sm-9'ip>>",
            columnDefs: [{ targets: 'no-sort', orderable: false }],
            buttons: defaultButtons(opts.exportFilename),
            preDrawCallback: function() {
                $(loadingSelector).show();
            },
            drawCallback: function() {
                $(tableSelector).show();
                $(loadingSelector).hide();
            },
        };

        if (opts.sumColumns) {
            defaults.footerCallback = sumFooterCallback(opts.sumColumns);
        }

        var config = $.extend({}, defaults, opts.dtOptions);
        return $(tableSelector).DataTable(config);
    }

    return { init: init, floatVal: floatVal };

})();
