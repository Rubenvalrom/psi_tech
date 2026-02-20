"""Pydantic schemas for Financial models."""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class PartidaPresupuestariaBase(BaseModel):
    """Base schema for budget lines."""
    codigo_contable: str
    descripcion: str
    presupuestado: Decimal


class PartidaPresupuestariaCreate(PartidaPresupuestariaBase):
    """Schema for creating a budget line."""
    pass


class PartidaPresupuestariaRead(PartidaPresupuestariaBase):
    """Schema for reading a budget line."""
    id: int
    comprometido: Decimal
    pagado: Decimal
    saldo: Decimal
    disponible: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartidaPresupuestariaUpdate(BaseModel):
    """Schema for updating a budget line."""
    descripcion: Optional[str] = None
    presupuestado: Optional[Decimal] = None


class FacturaBase(BaseModel):
    """Base schema for invoices."""
    numero: str
    proveedor: str
    monto: Decimal
    fecha_emision: datetime


class FacturaCreate(FacturaBase):
    """Schema for creating an invoice."""
    expediente_id: Optional[int] = None
    partida_presupuestaria_id: Optional[int] = None
    contenido_xml: Optional[str] = None


class FacturaRead(FacturaBase):
    """Schema for reading an invoice."""
    id: int
    fecha_recepcion: Optional[datetime] = None
    estado: str
    expediente_id: Optional[int] = None
    partida_presupuestaria_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
