"""Pydantic schemas for financial models."""
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class PartidaPresupuestariaBase(BaseModel):
    """Base partida presupuestaria schema."""
    codigo_contable: str
    descripcion: str
    presupuestado: Decimal


class PartidaPresupuestariaCreate(PartidaPresupuestariaBase):
    """Schema for creating a partida presupuestaria."""
    pass


class PartidaPresupuestariaUpdate(BaseModel):
    """Schema for updating a partida presupuestaria."""
    descripcion: Optional[str] = None
    presupuestado: Optional[Decimal] = None


class PartidaPresupuestariaRead(PartidaPresupuestariaBase):
    """Schema for reading a partida presupuestaria."""
    id: int
    comprometido: Decimal
    pagado: Decimal
    saldo: Decimal
    disponible: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacturaBase(BaseModel):
    """Base factura schema."""
    numero: str
    proveedor: str
    monto: Decimal
    fecha_emision: datetime


class FacturaCreate(FacturaBase):
    """Schema for creating a factura."""
    expediente_id: Optional[int] = None
    partida_presupuestaria_id: Optional[int] = None


class FacturaUpdate(BaseModel):
    """Schema for updating a factura."""
    estado: Optional[str] = None


class FacturaRead(FacturaBase):
    """Schema for reading a factura."""
    id: int
    estado: str
    expediente_id: Optional[int] = None
    partida_presupuestaria_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
