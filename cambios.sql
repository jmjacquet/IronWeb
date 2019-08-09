ALTER TABLE `egr_entidad`
        ADD COLUMN `lista_precios_defecto` integer REFERENCES `prod_lista_precios` (`id`);
ALTER TABLE `egr_entidad`
        ADD COLUMN `tope_cta_cte` numeric(15, 3);
CREATE INDEX `egr_entidad_lista_precios_defecto`
        ON `egr_entidad` (`lista_precios_defecto`);