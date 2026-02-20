# Spanish Public Accounting (Contabilidad Pública)

## Budget States Framework

### Presupuestado (Budgeted)
Amount approved in the annual budget (PGE - Presupuestos Generales del Estado)

```python
class BudgetState(BaseModel):
    presupuestado: Decimal  # Initial approved budget
    creditos_inicial: Decimal = Field(default=0)
    modificaciones: Decimal = Field(default=0)
    creditos_vigente: Decimal = Field(default=0)
```

### Comprometido (Committed/Obligated)
Amount committed through contracts, orders, or commitments that will generate payment

```python
class CommitmentState(BaseModel):
    compromiso_id: str  # Reference to commitment
    fecha_compromiso: date
    importe: Decimal
    beneficiario: str  # Service provider
    estado: str  # "pendiente", "aprobado", "modificado", "anulado"
```

### Obligado (Accrued/Invoiced)
Amount resulting from received invoices (recognition of the obligation)

```python
class AccrualState(BaseModel):
    factura_id: str
    fecha_factura: date
    proveedor: str
    importe_total: Decimal
    iva: Decimal = Field(default=0)
    estado: str  # "registrada", "aprobada", "pagada"
```

### Pagado (Paid)
Amount actually paid out

```python
class PaymentState(BaseModel):
    factura_id: str
    fecha_pago: date
    importe_pagado: Decimal
    forma_pago: str  # transferencia, cheque, etc
    referencia_pago: str
```

## Budget Execution Formula

```
Presupuestado - Comprometido = Crédito Disponible
Comprometido - Obligado = Comprometido Pendiente
Obligado - Pagado = Obligaciones Pendientes de Pago
```

## Accounting Entries (Asientos Contables)

### Entry Types

```python
class AsientoContable(Base):
    __tablename__ = "asientos_contables"
    
    numero = Column(String(50), unique=True)
    fecha = Column(Date)
    concepto = Column(String(255))
    
    # T-account structure
    debe = Column(Numeric(15, 2))  # Debit
    haber = Column(Numeric(15, 2))  # Credit
    
    # Accounting equation: Assets = Liabilities + Equity
    # debe always = haber
```

### Common Entries

1. **Budget Recognition** (Presupuestado)
```
DEBE: Crédito Presupuestario
HABER: Presupuesto Aprobado
```

2. **Commitment** (Compromiso)
```
DEBE: Compromiso Presupuestario
HABER: Crédito Disponible
```

3. **Accrual** (Obligación)
```
DEBE: Gasto (Expense Account)
HABER: Proveedores (Payable Account)
```

4. **Payment** (Pago)
```
DEBE: Proveedores Pagados
HABER: Caja/Banco (Cash Account)
```

## Key Accounting Codes (Spain)

### Income Codes (Ingresos)
- 1: Impuestos Directos
- 2: Impuestos Indirectos
- 3: Tasas y otros Ingresos
- 4: Transferencias Corrientes
- 5: Ingresos Patrimoniales
- 6: Ingresos por Enajenación
- 7: Transferencias de Capital
- 8: Activos Financieros
- 9: Pasivos Financieros

### Expense Codes (Gastos)
- 1: Personal
- 2: Bienes y Servicios
- 3: Transferencias Corrientes
- 4: Bienes de Inversión
- 5: Transferencias de Capital
- 6: Inversiones Financieras
- 7: Transferencias Financieras
- 8: Activos Financieros
- 9: Pasivos Financieros

## Budget Execution Reports

```python
# Sample budget execution report
{
    "periodo": "2024-Q1",
    "partida": "48011",  # Personnel expenses
    "presupuestado": 500000.00,
    "comprometido": 150000.00,
    "obligado": 125000.00,
    "pagado": 100000.00,
    "disponible": 350000.00,
    "tasa_ejecucion": 20,  # (100000 / 500000) * 100
    "tasa_compromiso": 30,  # (150000 / 500000) * 100
}
```

## Compliance & Audit Trail

```python
class AuditoriaContable(Base):
    __tablename__ = "auditoria_contable"
    
    # Full audit trail of all changes
    timestamp = Column(DateTime, server_default=func.now())
    usuario_id = Column(Integer)
    accion = Column(String(50))  # create, modify, delete
    tabla_afectada = Column(String(50))
    registro_id = Column(Integer)
    valores_anteriores = Column(JSON)
    valores_nuevos = Column(JSON)
    motivo = Column(String(255))
    
    # Required by Spanish LAC (Ley de Acceso a Cargos Públicos)
    # Must maintain for 6 years minimum
```

## VAT Management (IVA)

```python
class IVAGestion:
    """VAT calculation and management"""
    
    @staticmethod
    def calcular_iva(base: Decimal, porcentaje: Decimal) -> Decimal:
        """Calculate VAT amount"""
        return base * (porcentaje / 100)
    
    @staticmethod
    def calcular_total(base: Decimal, iva: Decimal) -> Decimal:
        """Calculate total with VAT"""
        return base + iva

    # Standard rates in Spain
    IVA_GENERAL = Decimal("21.0")  # 21%
    IVA_REDUCIDO = Decimal("10.0")  # 10% (food, medicine)
    IVA_SUPER_REDUCIDO = Decimal("4.0")  # 4% (basic food, books)
    IVA_EXENTO = Decimal("0.0")  # Exempt (education, healthcare)
```

## Chart of Accounts (Plan Contable)

```
1000-1999: ASSETS (Activo)
  1000-1299: Fixed Assets
  1300-1499: Current Assets
  1500-1599: Cash and Banks

2000-2999: LIABILITIES (Pasivo)
  2000-2499: Long-term Liabilities
  2500-2999: Current Liabilities (Payables)

3000-3999: EQUITY (Patrimonio)

4000-4999: INCOME (Ingresos)

5000-5999: EXPENSES (Gastos)
  5100-5199: Personnel
  5200-5299: Supplies & Services
  5300-5399: Utilities
```
