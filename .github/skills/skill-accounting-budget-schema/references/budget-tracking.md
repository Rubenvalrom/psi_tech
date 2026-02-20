# Budget Execution Tracking

```python
def registrar_compromiso(partida_id: int, monto: float, expediente_id: int, db):
    """Register budget commitment (gasto comprometido)."""
    partida = db.query(PartidaPresupuestaria).get(partida_id)
    
    # Validate no over-commitment
    if partida.comprometido + monto > partida.presupuestado:
        raise ValueError("Budget exceeded")
    
    partida.comprometido += monto
    db.commit()
    
    # Log to audit trail
    audit = AsientoContable(
        fecha=datetime.now().date(),
        concepto=f"Compromiso exp {expediente_id}",
        partida_id=partida_id,
        expediente_id=expediente_id,
        debe=monto,
        haber=0
    )
    db.add(audit)
    db.commit()

def registrar_pago(partida_id: int, monto: float, factura_id: int, db):
    """Register budget payment (gasto pagado)."""
    partida = db.query(PartidaPresupuestaria).get(partida_id)
    
    # Payment liquidates commitment + adds to paid
    partida.comprometido -= monto
    partida.pagado += monto
    db.commit()

def obtener_ejecucion(partida_id: int, db) -> dict:
    """Get budget execution status."""
    p = db.query(PartidaPresupuestaria).get(partida_id)
    return {
        "presupuestado": float(p.presupuestado),
        "comprometido": float(p.comprometido),
        "pagado": float(p.pagado),
        "saldo": float(p.saldo),
        "ejecucion_pct": (float(p.pagado) / float(p.presupuestado) * 100) if p.presupuestado > 0 else 0
    }
```
