-- IronWeb Multi-Currency Migration Script
-- Execute this BEFORE running Django (the app models reference these tables)
-- IMPORTANT: Run STEP 0 first (create gral_moneda table), then run Django so
-- models.ForeignKey references resolve. Steps 1-5 can run anytime after.

-- ============================================
-- STEP 0: Create gral_moneda table (if not exists)
-- This table is referenced by Django models via ForeignKey,
-- so it MUST exist before the app is first used.
-- ============================================
CREATE TABLE IF NOT EXISTS gral_moneda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    simbolo VARCHAR(5) NOT NULL,
    decimales INT NOT NULL DEFAULT 2,
    baja TINYINT(1) NOT NULL DEFAULT 0,
    INDEX idx_gral_moneda_codigo (codigo)
);

INSERT INTO gral_moneda (codigo, nombre, simbolo, decimales, baja) VALUES
('ARS', 'Peso Argentino', '$', 2, 0),
('USD', 'Dólar Estadounidense', 'U$S', 2, 0),
('EUR', 'Euro', '€', 2, 0),
('GBP', 'Libra Esterlina', '£', 2, 0),
('BRL', 'Real Brasileño', 'R$', 2, 0),
('CLP', 'Peso Chileno', '$', 0, 0),
('UYU', 'Peso Uruguayo', '$', 2, 0);


-- ============================================
-- STEP 1: Exchange rate table
-- ============================================
CREATE TABLE IF NOT EXISTS gral_cotizacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    moneda_origen_id INT NOT NULL,
    moneda_destino_id INT NOT NULL,
    cotizacion DECIMAL(15, 6) NOT NULL DEFAULT 1.000000,
    fecha DATE NOT NULL,
    baja TINYINT(1) NOT NULL DEFAULT 0,
    INDEX idx_cotizacion_moneda_origen (moneda_origen_id),
    INDEX idx_cotizacion_moneda_destino (moneda_destino_id),
    INDEX idx_cotizacion_fecha (fecha),
    FOREIGN KEY (moneda_origen_id) REFERENCES gral_moneda(id),
    FOREIGN KEY (moneda_destino_id) REFERENCES gral_moneda(id)
);


-- ============================================
-- STEP 2: Add cotizacion and importe_sistema fields
-- ============================================

-- ============================================
-- Helper: add column if not exists (compatible with MySQL < 8.0)
-- ============================================
DROP PROCEDURE IF EXISTS add_column_if_not_exists;
DELIMITER //
CREATE PROCEDURE add_column_if_not_exists(
    IN p_table_name VARCHAR(64),
    IN p_column_name VARCHAR(64),
    IN p_column_def VARCHAR(512)
)
BEGIN
    DECLARE col_count INT;
    SELECT COUNT(*) INTO col_count
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = p_table_name
      AND COLUMN_NAME = p_column_name;
    IF col_count = 0 THEN
        SET @sql = CONCAT('ALTER TABLE ', p_table_name, ' ADD COLUMN ', p_column_name, ' ', p_column_def);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;


-- ============================================
-- STEP 2a: Ensure moneda FK columns exist on all referencing tables
-- (these should already exist from the model schema, but may be missing
--  on databases created from older SQL dumps)
-- ============================================
CALL add_column_if_not_exists('gral_empresa', 'moneda_default', 'INT NULL');
CALL add_column_if_not_exists('egr_entidad', 'moneda_default', 'INT NULL');
CALL add_column_if_not_exists('prod_lista_precios', 'moneda', 'INT NULL');
CALL add_column_if_not_exists('cpb_comprobante', 'moneda', 'INT NULL');
CALL add_column_if_not_exists('cpb_cobranza', 'moneda', 'INT NULL');


-- ============================================
-- STEP 2b: Add cotizacion and importe_sistema fields
-- ============================================

-- cpb_comprobante: exchange rate at document time + total in system base currency
CALL add_column_if_not_exists('cpb_comprobante', 'cotizacion', 'DECIMAL(15, 6) NOT NULL DEFAULT 1.000000');
CALL add_column_if_not_exists('cpb_comprobante', 'importe_total_sistema', 'DECIMAL(15, 2) NULL DEFAULT NULL');

-- cpb_comprobante_detalle: unit prices and totals in system base currency
CALL add_column_if_not_exists('cpb_comprobante_detalle', 'importe_unitario_sistema', 'DECIMAL(15, 2) NULL DEFAULT NULL');
CALL add_column_if_not_exists('cpb_comprobante_detalle', 'importe_total_sistema', 'DECIMAL(15, 2) NULL DEFAULT NULL');

-- cpb_cobranza: exchange rate at payment time + total in system base currency
CALL add_column_if_not_exists('cpb_cobranza', 'cotizacion', 'DECIMAL(15, 6) NOT NULL DEFAULT 1.000000');
CALL add_column_if_not_exists('cpb_cobranza', 'importe_total_sistema', 'DECIMAL(15, 2) NULL DEFAULT NULL');

-- cpb_comprobante_fp: exchange rate + import in system base currency per payment method
CALL add_column_if_not_exists('cpb_comprobante_fp', 'cotizacion', 'DECIMAL(15, 6) NOT NULL DEFAULT 1.000000');
CALL add_column_if_not_exists('cpb_comprobante_fp', 'importe_sistema', 'DECIMAL(15, 2) NULL DEFAULT NULL');

DROP PROCEDURE IF EXISTS add_column_if_not_exists;


-- ============================================
-- STEP 3: Update existing records to ARS
-- (commented by default; uncomment after currencies exist)
-- ============================================
-- UPDATE gral_empresa SET moneda_default_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE egr_entidad SET moneda_default_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE prod_lista_precios SET moneda_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE cpb_comprobante SET moneda_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE cpb_cobranza SET moneda_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');


-- ============================================
-- STEP 4: Seed default cotizacion (ARS=1 for all currencies)
-- (uncomment and adjust rates as needed)
-- ============================================
-- INSERT INTO gral_cotizacion (moneda_origen_id, moneda_destino_id, cotizacion, fecha)
-- SELECT mo.id, md.id, 1.000000, CURDATE()
-- FROM gral_moneda mo, gral_moneda md
-- WHERE md.codigo = 'ARS' AND mo.codigo != 'ARS'
-- ON DUPLICATE KEY UPDATE cotizacion = VALUES(cotizacion);