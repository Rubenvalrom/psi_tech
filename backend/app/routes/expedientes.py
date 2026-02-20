"""Expediente CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from ..core.database import get_db
from ..models.expediente import Expediente, EstadoExpediente, PasoTramitacion, EstadoPaso
from ..schemas.expediente import (
    ExpedienteCreate,
    ExpedienteUpdate,
    ExpedienteRead,
    ExpedientePaginatedResponse,
    PasoTramitacionCreate,
    PasoTramitacionRead,
)

router = APIRouter(prefix="/expedientes", tags=["expedientes"])


@router.post("", response_model=ExpedienteRead, status_code=201)
async def create_expediente(
    expediente: ExpedienteCreate,
    db: Session = Depends(get_db),
):
    """Create a new expediente (case file)."""
    # Check if numero is already used
    existing = db.query(Expediente).filter(Expediente.numero == expediente.numero).first()
    if existing:
        raise HTTPException(status_code=400, detail="Expediente numero already exists")

    db_expediente = Expediente(**expediente.dict())
    db.add(db_expediente)
    db.commit()
    db.refresh(db_expediente)
    return db_expediente


@router.get("", response_model=ExpedientePaginatedResponse)
async def list_expedientes(
    split: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: str = Query(None),
    db: Session = Depends(get_db),
):
    """List expedientes with pagination and optional filtering."""
    query = db.query(Expediente)

    # Filter by state if provided
    if estado:
        try:
            estado_enum = EstadoExpediente(estado)
            query = query.filter(Expediente.estado == estado_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid estado: {estado}")

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    items = query.order_by(desc(Expediente.fecha_creacion)).offset(split).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "skip": split,
        "limit": limit,
    }


@router.get("/{expediente_id}", response_model=ExpedienteRead)
async def get_expediente(
    expediente_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific expediente by ID."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")
    return expediente


@router.put("/{expediente_id}", response_model=ExpedienteRead)
async def update_expediente(
    expediente_id: int,
    expediente_update: ExpedienteUpdate,
    db: Session = Depends(get_db),
):
    """Update an expediente."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")

    # Update fields provided
    update_data = expediente_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(expediente, key, value)

    db.add(expediente)
    db.commit()
    db.refresh(expediente)
    return expediente


@router.post("/{expediente_id}/pasos", response_model=PasoTramitacionRead, status_code=201)
async def create_paso(
    expediente_id: int,
    paso: PasoTramitacionCreate,
    db: Session = Depends(get_db),
):
    """Add a new step (paso) to the expediente workflow."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")

    db_paso = PasoTramitacion(expediente_id=expediente_id, **paso.dict())
    db.add(db_paso)
    db.commit()
    db.refresh(db_paso)
    return db_paso


@router.get("/{expediente_id}/pasos", response_model=List[PasoTramitacionRead])
async def list_pasos(
    expediente_id: int,
    db: Session = Depends(get_db),
):
    """List all steps (pasos) for an expediente."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")

    pasos = db.query(PasoTramitacion).filter(
        PasoTramitacion.expediente_id == expediente_id
    ).order_by(PasoTramitacion.numero_paso).all()

    return pasos
