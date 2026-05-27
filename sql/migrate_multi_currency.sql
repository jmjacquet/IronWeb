-- IronWeb Multi-Currency Migration Script
-- Execute this after running Django migrations

-- ============================================
-- STEP 1: Create currencies (run first)
-- ============================================
INSERT INTO gral_moneda (codigo, nombre, simbolo, decimales, baja) VALUES
('ARS', 'Peso Argentino', '$', 2, 0),
('USD', 'Dólar Estadounidense', 'U$S', 2, 0),
('EUR', 'Euro', '€', 2, 0),
('GBP', 'Libra Esterlina', '£', 2, 0),
('BRL', 'Real Brasileño', 'R$', 2, 0),
('CLP', 'Peso Chileno', '$', 0, 0),
('UYU', 'Peso Uruguayo', '$', 2, 0);

-- ============================================
-- STEP 2: Update existing records to ARS
-- (These are handled by migration, but included for reference)
-- ============================================
-- UPDATE gral_empresa SET moneda_default_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE egr_entidad SET moneda_default_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE prod_lista_precios SET moneda_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE cpb_comprobante SET moneda_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');
-- UPDATE cpb_cobranza SET moneda_id = (SELECT id FROM gral_moneda WHERE codigo = 'ARS');