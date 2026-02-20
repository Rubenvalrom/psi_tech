"""Presupuestos (budget) endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from ..core.database import get_db
from ..models.financiero import PartidaPresupuestaria
from ..schemas.financiero import (
    PartidaPresupuestariaCreate,
    PartidaPresupuestariaRead,
    PartidaPresupuestariaUpdate,
)

router = APIRouter(prefix="/presupuestos", tags=["presupuestos"])


@router.post("", response_model=PartidaPresupuestariaRead, status_code=201)
async def create_partida(
    partida: PartidaPresupuestariaCreate,
    db: Session = Depends(get_db),
):
    """Create a new budget line item (partida presupuestaria)."""
    # Check if codigo already exists
    existing = db.query(PartidaPresupuestaria).filter(
        PartidaPresupuestaria.codigo_contable == partida.codigo_contable
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Codigo contable already exists")

    db_partida = PartidaPresupuestaria(**partida.dict())
    db.add(db_partida)
    db.commit()
    db.refresh(db_partida)
    return db_partida


@router.get("", response_model=List[PartidaPresupuestariaRead])
async def list_partidas(
    db: Session = Depends(get_db),
):
    """List all budget line items."""
    partidas = db.query(PartidaPresupuestaria).all()
    return partidas


@router.get("/{codigo}", response_model=PartidaPresupuestariaRead)
async def get_partida(
    codigo: str,
    db: Session = Depends(get_db),
):
    """Get a specific budget line item by codigo contable."""
    partida = db.query(PartidaPresupuestaria).filter(
        PartidaPresupuestaria.codigo_contable == codigo
    ).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida not found")
    return partida


@router.put("/{codigo}", response_model=PartidaPresupuestariaRead)
async def update_partida(
    codigo: str,
    partida_update: PartidaPresupuestariaUpdate,
    db: Session = Depends(get_db),
):
    """Update a budget line item."""
    partida = db.query(PartidaPresupuestaria).filter(
        PartidaPresupuestaria.codigo_contable == codigo
    ).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida not found")

    update_data = partida_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(partida, key, value)

    db.add(partida)
    db.commit()
    db.refresh(partida)
    return partida


@router.post("/{codigo}/comprometer")
async def comprometer_presupuesto(
    codigo: str,
    monto: Decimal = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    """Register a committed amount (compromiso) on a budget line."""
    partida = db.query(PartidaPresupuestaria).filter(
        PartidaPresupuestaria.codigo_contable == codigo
    ).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida not found")

    # Validate: cannot commit more than budgeted
    nuevo_comprometido = partida.comprometido + monto
    if nuevo_comprometido > partida.presupuestado:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot commit {monto}: exceeds available budget",
        )

    partida.comprometido = nuevo_comprometido
    db.add(partida)
    db.commit()
    db.refresh(partida)

    return {
        "codigo": partida.codigo_contable,
        "presupuestado": float(partida.presupuestado),
        "comprometido": float(partida.comprometido),
        "pagado": float(partida.pagado),
        "saldo": float(partida.saldo),
    }


@router.post("/{codigo}/pagar")
async def pagar_presupuesto(
    codigo: str,
    monto: Decimal = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    """Register a paid amount (pago) on a budget line."""
    partida = db.query(PartidaPresupuestaria).filter(
        PartidaPresupuestaria.codigo_contable == codigo
    ).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida not found")

    # Validate: cannot pay more than committed
    nuevo_pagado = partida.pagado + monto
    if nuevo_pagado > partida.comprometido:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pay {monto}: exceeds committed amount",
        )

    partida.pagado = nuevo_pagado
    db.add(partida)
    db.commit()
    db.refresh(partida)

    return {
        "codigo": partida.codigo_contable,
        "presupuestado": float(partida.presupuestado),
        "comprometido": float(partida.comprometido),
        "pagado": float(partida.pagado),
        "disponible": float(partida.disponible),
    }
