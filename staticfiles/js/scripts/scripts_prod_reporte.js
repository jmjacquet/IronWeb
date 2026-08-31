$(document).ready(function() {

    var tabla = ServerDataTable.init('#dataTables-reporte', {
        exportFilename: 'REPORTE_PRODUCTOS',
        sumColumns: [5, 6, 8, 9],
        dtOptions: {
            order: [[1, 'asc']],
            ajax: {
                url: prodReporteDataUrl,
                type: 'GET',
                data: function(d) {
                    d.lista_precios = $('#id_lista_precios').val();
                    d.ubicacion = $('#id_ubicacion').val();
                    d.producto = $('#id_producto').val();
                    d.categoria = $('#id_categoria').val();
                    d.tipo_prod = $('#id_tipo_prod').val();
                    d.mostrar_en = $('#id_mostrar_en').val();
                    d.baja = $('#id_baja').val();
                }
            },
            columns: [
                { data: 0, orderable: false, searchable: false, className: 'no-sort text-center' },
                { data: 1, className: 'imprimir' },
                { data: 2, className: 'imprimir' },
                { data: 3, className: 'imprimir' },
                { data: 4, className: 'imprimir' },
                { data: 5, className: 'importe' },
                { data: 6, className: 'importe' },
                { data: 7, className: 'importe' },
                { data: 8, className: 'importe_total' },
                { data: 9, className: 'importe_total' },
                { data: 10, className: 'text-left' },
            ],
        }
    });

    $('#btnBuscar').on('click', function() {
        tabla.ajax.reload();
    });

});
