-- ============================================================
-- IronWeb - Borrar comprobantes (y todos sus registros relacionados)
-- ============================================================
-- Elimina por completo los comprobantes creados entre dos fechas junto
-- con TODAS sus filas relacionadas: detalles, totales de IVA, percepciones,
-- retenciones, cobranzas/pagos (cpb_comprobante_fp) y cobranzas (cpb_cobranza).
--
-- Filtro: cpb_comprobante.fecha_creacion  (timestamp de creación, columna
--         the type datetime(6)). Se pasan fecha de inicio y fin (inclusive).
--
-- ADVERTENCIA: operación DESTRUCTIVA e IRREVERSIBLE. Hacer backup antes.
-- Ejecutar una vez por cada base de tenant (cada tenant tiene su propia DB).
--
-- USO:
--   CALL borrar_comprobantes_por_fecha('2026-01-01 00:00:00', '2026-01-31 23:59:59');
--
-- Comportamiento (importante, schema legacy):
--   Las FKs de las tablas hijas son ON DELETE RESTRICT (no CASCADE), así que se
--   borran primero las filas hijas en orden de dependencia y luego el padre.
--   trab_orden_pedido referencias cpb_comprobante sin FK en DB: se ponen en NULL.
-- ============================================================

DROP PROCEDURE IF EXISTS borrar_comprobantes_por_fecha;

DELIMITER //

CREATE PROCEDURE borrar_comprobantes_por_fecha(
    IN p_fecha_desde DATETIME,
    IN p_fecha_hasta DATETIME
)
BEGIN
    DECLARE v_cant INT DEFAULT 0;

    -- Tabla temporal con los IDs de los comprobantes a borrar
    DROP TEMPORARY TABLE IF EXISTS tmp_cpbs_a_borrar;
    CREATE TEMPORARY TABLE tmp_cpbs_a_borrar (
        id INT PRIMARY KEY
    ) ENGINE=MEMORY;

    INSERT INTO tmp_cpbs_a_borrar (id)
    SELECT id
    FROM cpb_comprobante
    WHERE fecha_creacion >= p_fecha_desde
      AND fecha_creacion <= p_fecha_hasta;

    SELECT COUNT(*) INTO v_cant FROM tmp_cpbs_a_borrar;
    IF v_cant = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No hay comprobantes en el rango de fechas indicado.';
    END IF;

    -- 1) Percepciones y retenciones del comprobante
    DELETE FROM cpb_comprobante_perc_imp
    WHERE cpb_comprobante IN (SELECT id FROM tmp_cpbs_a_borrar);

    DELETE FROM cpb_comprobante_retenciones
    WHERE cpb_comprobante IN (SELECT id FROM tmp_cpbs_a_borrar);

    -- 2) Totales de IVA por comprobante
    DELETE FROM cpb_comprobante_tot_iva
    WHERE cpb_comprobante IN (SELECT id FROM tmp_cpbs_a_borrar);

    -- 3) Detalles del comprobante
    DELETE FROM cpb_comprobante_detalle
    WHERE cpb_comprobante IN (SELECT id FROM tmp_cpbs_a_borrar);

    -- 4) Formas de pago / cheques (cpb_comprobante_fp)
    --    La columna mdcp_salida es autorreferente (RESTRICT): se desvincula
    --    en las filas que apunten a un fp a borrar antes de eliminarlas.
    UPDATE cpb_comprobante_fp f
    SET f.mdcp_salida = NULL
    WHERE f.mdcp_salida IS NOT NULL
      AND f.mdcp_salida IN (
          SELECT id FROM cpb_comprobante_fp
          WHERE cpb_comprobante IN (SELECT id FROM tmp_cpbs_a_borrar)
      );

    DELETE FROM cpb_comprobante_fp
    WHERE cpb_comprobante IN (SELECT id FROM tmp_cpbs_a_borrar);

    -- 5) Cobranzas / Ordenes de pago (cpb_cobranza)
    --    Tiene dos FKs a cpb_comprobante (recibo -> factura). Se borran las
    --    filas en las que cualquiera de los dos comprobantes está en el rango.
    DELETE FROM cpb_cobranza
    WHERE cpb_comprobante IN (SELECT id FROM tmp_cpbs_a_borrar)
       OR cpb_factura     IN (SELECT id FROM tmp_cpbs_a_borrar);

    -- 6) Referencias en cpb_comprobante a otros comprobantes (id_cpb_padre)
    --    Se desvinculan los que apunten a un comprobante a borrar, tanto dentro
    --    como fuera del rango, para evitar RESTRICT al borrar el padre.
    UPDATE cpb_comprobante
    SET id_cpb_padre = NULL
    WHERE id_cpb_padre IN (SELECT id FROM tmp_cpbs_a_borrar);

    -- 7) Ordenes de pedido que referencian presupuestos/ventas a borrar
    UPDATE trab_orden_pedido
    SET id_presupuesto = NULL
    WHERE id_presupuesto IN (SELECT id FROM tmp_cpbs_a_borrar);

    UPDATE trab_orden_pedido
    SET id_venta = NULL
    WHERE id_venta IN (SELECT id FROM tmp_cpbs_a_borrar);

    -- 8) Borrar los comprobantes
    DELETE FROM cpb_comprobante
    WHERE id IN (SELECT id FROM tmp_cpbs_a_borrar);

    SELECT v_cant AS comprobantes_borrados;

    DROP TEMPORARY TABLE IF EXISTS tmp_cpbs_a_borrar;
END //

DELIMITER ;
