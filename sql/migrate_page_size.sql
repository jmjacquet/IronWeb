ALTER TABLE gral_empresa
    ADD COLUMN etiq_cb_pdf_page_size   VARCHAR(10) NOT NULL DEFAULT 'A4',
    ADD COLUMN etiq_cb_pdf_page_width  DECIMAL(6,2) NULL,
    ADD COLUMN etiq_cb_pdf_page_height DECIMAL(6,2) NULL;
