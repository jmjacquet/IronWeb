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