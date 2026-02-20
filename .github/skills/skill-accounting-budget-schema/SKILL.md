---
name: skill-accounting-budget-schema
description: Design accounting database schema for Spanish public administration. Includes chart of accounts, budget execution tracking (presupuestado/comprometido/pagado), journal entries, and statutory reporting. Use when implementing financial management systems compliant with contabilidad pública rules.
---

# Accounting & Budget Schema (Contabilidad Pública)

## Database Schema

```sql
CREATE TABLE partida_presupuestaria (
    id SERIAL PRIMARY KEY,
    codigo_contable VARCHAR(20) UNIQUE,  -- e.g., "6140.200"
    descripcion TEXT,
    presupuestado DECIMAL(15,2),
    comprometido DECIMAL(15,2) DEFAULT 0,
    pagado DECIMAL(15,2) DEFAULT 0,
    saldo DECIMAL(15,2) GENERATED ALWAYS AS (presupuestado - ( comprometido + pagado)) STORED
);

CREATE TABLE asiento_contable (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    concepto TEXT,
    debe DECIMAL(15,2),
    haber DECIMAL(15,2),
    partida_id INTEGER REFERENCES partida_presupuestaria(id),
    expediente_id INTEGER REFERENCES expediente(id),
    creado_por VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE factura (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) UNIQUE,
    proveedor VARCHAR(100),
    monto DECIMAL(15,2),
    fecha_emision DATE,
    estado VARCHAR(20),  -- PENDIENTE,PAGADA,ANULADA
    partida_id INTEGER REFERENCES partida_presupuestaria(id),
    expediente_id INTEGER REFERENCES expediente(id)
);
```

See [references/budget-tracking.md](references/budget-tracking.md):
- Presupuestado (budgeted): Original allocation
- Comprometido (committed): Reserved/obligated
- Pagado (paid): Actual cash out

See [references/spanish-accounting.md](references/spanish-accounting.md):
- Plan Contable Público (chart of accounts)
- Balance sheet, profit/loss reporting
- Audit compliance (eIDAS, LRJPAC)
