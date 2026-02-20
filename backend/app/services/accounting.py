from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..models.financiero import PartidaPresupuestaria, Factura, EstadoFactura
from ..models.expediente import Expediente, Trazabilidad

class AccountingService:
    """Handles financial logic: budget checks, commitments, and invoicing."""

    def __init__(self, db: Session):
        self.db = db

    def create_partida(self, codigo: str, descripcion: str, monto: Decimal):
        """Creates a new budget line."""
        partida = PartidaPresupuestaria(
            codigo_contable=codigo,
            descripcion=descripcion,
            presupuestado=monto
        )
        self.db.add(partida)
        self.db.commit()
        self.db.refresh(partida)
        return partida

    def check_availability(self, partida_id: int, amount: Decimal) -> bool:
        """Checks if a budget line has enough available funds."""
        partida = self.db.query(PartidaPresupuestaria).filter(PartidaPresupuestaria.id == partida_id).first()
        if not partida:
            raise ValueError("Partida not found")
        return partida.disponible >= amount

    def commit_budget(self, partida_id: int, amount: Decimal, expediente_id: int, user_id: int):
        """Commits funds from a budget line to an expediente."""
        partida = self.db.query(PartidaPresupuestaria).filter(PartidaPresupuestaria.id == partida_id).first()
        if not partida:
            raise ValueError("Partida not found")

        if partida.disponible < amount:
            raise ValueError("Insufficient budget available")

        partida.comprometido += amount
        
        # Log logic
        self._log_financial_event(expediente_id, user_id, "COMPROMISO_GASTO", 
                                f"Comprometidos {amount}€ de la partida {partida.codigo_contable}")
        
        self.db.commit()
        self.db.refresh(partida)
        return partida

    def register_invoice(self, invoice_data: dict, user_id: int):
        """Registers a new invoice and updates budget execution if applicable."""
        # Check if invoice number exists
        existing = self.db.query(Factura).filter(Factura.numero == invoice_data['numero']).first()
        if existing:
            raise ValueError("Invoice number already exists")

        factura = Factura(**invoice_data)
        factura.fecha_recepcion = datetime.now()
        
        # Auto-update partida if linked
        if factura.partida_presupuestaria_id:
            partida = self.db.query(PartidaPresupuestaria).filter(
                PartidaPresupuestaria.id == factura.partida_presupuestaria_id
            ).first()
            
            if partida:
                # Assuming the committed amount is released and moved to 'pagado'
                # or just added to 'pagado' directly depending on the flow.
                # Simplified: Increase 'pagado', decrease 'comprometido' (if it was committed)
                # For now, just track 'pagado' accumulation.
                partida.pagado += factura.monto
                # If we assume it was previously committed, we should reduce committed. 
                # But typically commitment happens at an earlier stage (AD). 
                # Let's assume strict flow: A (Auth) -> D (Commit) -> O (Obligation) -> P (Payment)
                # Here we just increment 'pagado' for simplicity in Phase 4.

        self.db.add(factura)
        
        if factura.expediente_id:
             self._log_financial_event(factura.expediente_id, user_id, "FACTURA_RECIBIDA", 
                                f"Factura {factura.numero} recibida por {factura.monto}€")

        self.db.commit()
        self.db.refresh(factura)
        return factura

    def _log_financial_event(self, expediente_id: int, user_id: int, action: str, description: str):
        """Helper to log to Trazabilidad."""
        log = Trazabilidad(
            expediente_id=expediente_id,
            user_id=user_id,
            accion=action,
            descripcion=description
        )
        self.db.add(log)
