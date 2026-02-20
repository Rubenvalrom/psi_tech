"""Financial (budget & invoices) endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.financiero import PartidaPresupuestaria, Factura
from ..schemas.financiero import (
    PartidaPresupuestariaCreate,
    PartidaPresupuestariaRead,
    PartidaPresupuestariaUpdate,
    FacturaCreate,
    FacturaRead
)
from ..services.accounting import AccountingService

router = APIRouter(prefix="/finanzas", tags=["finanzas"])


@router.post("/presupuestos", response_model=PartidaPresupuestariaRead, status_code=201)
async def create_partida(
    partida: PartidaPresupuestariaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new budget line item."""
    service = AccountingService(db)
    # Check if exists
    existing = db.query(PartidaPresupuestaria).filter(
        PartidaPresupuestaria.codigo_contable == partida.codigo_contable
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Codigo contable already exists")
        
    return service.create_partida(
        partida.codigo_contable, 
        partida.descripcion, 
        partida.presupuestado
    )


@router.get("/presupuestos", response_model=List[PartidaPresupuestariaRead])
async def list_partidas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all budget lines."""
    return db.query(PartidaPresupuestaria).all()


@router.get("/presupuestos/{codigo}", response_model=PartidaPresupuestariaRead)
async def get_partida(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific budget line."""
    partida = db.query(PartidaPresupuestaria).filter(
        PartidaPresupuestaria.codigo_contable == codigo
    ).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida not found")
    return partida


@router.post("/presupuestos/{id}/comprometer")
async def comprometer_gasto(
    id: int,
    monto: Decimal = Query(..., gt=0),
    expediente_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Commit funds from a budget line to an expediente."""
    service = AccountingService(db)
    try:
        service.commit_budget(id, monto, expediente_id, current_user.id)
        return {"message": "Budget committed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/facturas", response_model=FacturaRead, status_code=201)
async def registrar_factura(
    factura: FacturaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a new invoice."""
    service = AccountingService(db)
    try:
        return service.register_invoice(factura.dict(), current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/facturas", response_model=List[FacturaRead])
async def list_facturas(
    expediente_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List invoices, optionally filtered by expediente, with pagination."""
    query = db.query(Factura)
    if expediente_id:
        query = query.filter(Factura.expediente_id == expediente_id)
    return query.offset(skip).limit(limit).all()
