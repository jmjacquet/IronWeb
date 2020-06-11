ALTER TABLE `cpb_comprobante_detalle`
        ADD COLUMN `importe_tasa1` numeric(15, 2);
ALTER TABLE `cpb_comprobante_detalle`
        ADD COLUMN `importe_tasa2` numeric(15, 2);

ALTER TABLE `cpb_comprobante`
        ADD COLUMN `importe_tasa2` numeric(15, 2);
ALTER TABLE `cpb_comprobante`
        ADD COLUMN `importe_tasa1` numeric(15, 2);

ALTER TABLE `prod_producto_lprecios`
        ADD COLUMN `precio_tasa` numeric(15, 3);
ALTER TABLE `prod_producto_lprecios`
        ADD COLUMN `precio_itc` numeric(15, 3);                

ALTER TABLE `gral_empresa`
        ADD COLUMN `usa_impuestos` bool NOT NULL;        


ALTER TABLE `gral_empresa`
        ADD COLUMN `firma_facturas` bool NOT NULL;        


INSERT INTO `cpb_tipo` (`id`, `tipo`, `nombre`, `codigo`, `detalle`, `ultimo_nro`, `usa_forma_pago`, `signo_forma_pago`, `usa_ctacte`, `signo_ctacte`, `usa_stock`, `signo_stock`, `compra_venta`, `libro_iva`, `signo_libro_iva`, `baja`, `fecha_creacion`, `fecha_modif`, `usa_pto_vta`, `facturable`) VALUES (24, 21, 'FACTURA CRED.ELECTR.', 'FE', 'FACTURA CREDITO ELECTRONICO', 0, 1, 1, 1, 1, 1, -1, 'V', 1, 1, 0, '0000-00-00 00:00:00.000000', '2018-02-16 16:47:15.238030', 1, 1), (25, 22, 'NOTA DEBITO ELECTR.', 'NDE', NULL, 0, 1, 1, 1, 1, 1, 1, 'V', 1, -1, 0, '2017-07-31 16:22:24.184000', '2017-12-13 11:36:22.965000', 1, 1), (26, 23, 'NOTA CREDITO ELECTR.', 'NCE', NULL, 0, 1, -1, 1, -1, 1, 1, 'V', 1, -1, 0, '0000-00-00 00:00:00.000000', '2017-12-20 07:54:29.312000', 1, 1)        