-- Accounting Schema for Spanish Public Administration (Contabilidad Pública)
-- Supports: Presupuestado, Comprometido, Pagado tracking

-- Partidas Presupuestarias (Budget Components)
CREATE TABLE partida_presupuestaria (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "48011"
    descripcion VARCHAR(255) NOT NULL,
    capítulo INT NOT NULL,  -- 1-9 (personal, goods, services, etc)
    articulo INT NOT NULL,  -- Details within chapter
    concepto INT NOT NULL,  -- Specific concept
    importe_presupuestado NUMERIC(15, 2) NOT NULL DEFAULT 0,
    importe_comprometido NUMERIC(15, 2) NOT NULL DEFAULT 0,
    importe_obligado NUMERIC(15, 2) NOT NULL DEFAULT 0,
    importe_pagado NUMERIC(15, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Compromisos (Budget Commitments / Obligations)
CREATE TABLE compromiso (
    id SERIAL PRIMARY KEY,
    numero_compromiso VARCHAR(50) UNIQUE NOT NULL,
    partida_presupuestaria_id INT NOT NULL,
    descripcion VARCHAR(255),
    importe NUMERIC(15, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente',  -- pendiente, aprobado, modificado, anulado
    fecha_compromiso DATE NOT NULL,
    fecha_vencimiento DATE,
    beneficiario VARCHAR(255),
    nif_beneficiario VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (partida_presupuestaria_id) REFERENCES partida_presupuestaria(id)
);

-- Facturas (Invoices / Bills)
CREATE TABLE factura (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) NOT NULL,
    serie_factura VARCHAR(10),
    compromiso_id INT,
    proveedor VARCHAR(255) NOT NULL,
    nif_proveedor VARCHAR(15) NOT NULL,
    descripcion VARCHAR(255),
    base_imponible NUMERIC(15, 2) NOT NULL,
    iva_porcentaje NUMERIC(5, 2) DEFAULT 21,
    iva_importe NUMERIC(15, 2) GENERATED ALWAYS AS (base_imponible * iva_porcentaje / 100) STORED,
    importe_total NUMERIC(15, 2) GENERATED ALWAYS AS (base_imponible + iva_importe) STORED,
    estado VARCHAR(20) DEFAULT 'registrada',  -- registrada, aprobada, pagada, rechazada
    fecha_factura DATE NOT NULL,
    fecha_recepcion DATE,
    fecha_pago DATE,
    forma_pago VARCHAR(20),  -- transferencia, cheque, efectivo, etc
    referencia_pago VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compromiso_id) REFERENCES compromiso(id)
);

-- Asientos Contables (Accounting Entries)
CREATE TABLE asiento_contable (
    id SERIAL PRIMARY KEY,
    numero_asiento VARCHAR(50) UNIQUE NOT NULL,
    fecha_asiento DATE NOT NULL,
    concepto VARCHAR(255),
    debe NUMERIC(15, 2) DEFAULT 0,
    haber NUMERIC(15, 2) DEFAULT 0,
    naturaleza VARCHAR(20),  -- gasto, ingreso, transferencia
    referencia_documento VARCHAR(50),  -- compromiso_id or factura_id
    tipo_documento VARCHAR(20),  -- compromiso, factura, transferencia
    usuario_id INT,
    estado VARCHAR(20) DEFAULT 'registrado',  -- registrado, contabilizado, anulado
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ejecución Presupuestaria (Budget Execution)
CREATE TABLE ejecucion_presupuestaria (
    id SERIAL PRIMARY KEY,
    partida_presupuestaria_id INT NOT NULL,
    ejercicio_presupuestario INT NOT NULL,  -- 2024, 2025, etc
    presupuestado NUMERIC(15, 2) NOT NULL DEFAULT 0,
    comprometido NUMERIC(15, 2) NOT NULL DEFAULT 0,
    obligado NUMERIC(15, 2) NOT NULL DEFAULT 0,
    pagado NUMERIC(15, 2) NOT NULL DEFAULT 0,
    libre NUMERIC(15, 2) GENERATED ALWAYS AS (presupuestado - comprometido) STORED,
    tasa_ejecucion NUMERIC(5, 2) GENERATED ALWAYS AS (
        CASE WHEN presupuestado = 0 THEN 0
             ELSE (pagado * 100.0 / presupuestado)
        END
    ) STORED,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (partida_presupuestaria_id) REFERENCES partida_presupuestaria(id),
    UNIQUE(partida_presupuestaria_id, ejercicio_presupuestario)
);

-- Indexes for performance
CREATE INDEX idx_compromiso_partida ON compromiso(partida_presupuestaria_id);
CREATE INDEX idx_compromiso_estado ON compromiso(estado);
CREATE INDEX idx_compromiso_fecha ON compromiso(fecha_compromiso);
CREATE INDEX idx_factura_compromiso ON factura(compromiso_id);
CREATE INDEX idx_factura_proveedor ON factura(nif_proveedor);
CREATE INDEX idx_factura_estado ON factura(estado);
CREATE INDEX idx_factura_fecha ON factura(fecha_factura);
CREATE INDEX idx_asiento_fecha ON asiento_contable(fecha_asiento);
CREATE INDEX idx_asiento_naturaleza ON asiento_contable(naturaleza);
CREATE INDEX idx_ejecucion_partida ON ejecucion_presupuestaria(partida_presupuestaria_id);
CREATE INDEX idx_ejecucion_ejercicio ON ejecucion_presupuestaria(ejercicio_presupuestario);

-- Views for Budget Analysis
CREATE VIEW v_ejecucion_presupuestaria AS
SELECT 
    pp.codigo,
    pp.descripcion,
    ep.ejercicio_presupuestario,
    ep.presupuestado,
    ep.comprometido,
    ep.obligado,
    ep.pagado,
    ep.libre,
    ep.tasa_ejecucion,
    COUNT(DISTINCT f.id) as num_facturas
FROM partida_presupuestaria pp
LEFT JOIN ejecucion_presupuestaria ep ON pp.id = ep.partida_presupuestaria_id
LEFT JOIN compromiso c ON pp.id = c.partida_presupuestaria_id
LEFT JOIN factura f ON c.id = f.compromiso_id
GROUP BY pp.id, ep.id, ep.ejercicio_presupuestario;

CREATE VIEW v_compromisos_pendientes AS
SELECT 
    c.id,
    c.numero_compromiso,
    pp.codigo as partida_codigo,
    pp.descripcion as partida_descripcion,
    c.descripcion,
    c.importe,
    c.estado,
    c.beneficiario,
    c.fecha_compromiso,
    CURRENT_DATE - c.fecha_vencimiento as dias_vencimiento
FROM compromiso c
JOIN partida_presupuestaria pp ON c.partida_presupuestaria_id = pp.id
WHERE c.estado IN ('pendiente', 'aprobado')
    AND c.fecha_vencimiento < CURRENT_DATE;

CREATE VIEW v_facturas_por_pagar AS
SELECT 
    f.id,
    f.numero_factura,
    f.proveedor,
    f.importe_total,
    f.estado,
    f.fecha_factura,
    CURRENT_DATE - f.fecha_vencimiento as dias_vencimiento
FROM factura f
WHERE f.estado IN ('registrada', 'aprobada')
    AND f.fecha_pago IS NULL
ORDER BY f.fecha_factura DESC;
