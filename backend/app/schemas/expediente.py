"""Pydantic schemas for Expediente models."""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class DocumentoBase(BaseModel):
    """Base documento schema."""
    nombre: str
    tipo: str = "ADJUNTO"


class DocumentoCreate(DocumentoBase):
    """Schema for creating a documento."""
    pass


class DocumentoRead(DocumentoBase):
    """Schema for reading a documento."""
    id: int
    expediente_id: int
    fecha_carga: datetime
    metadatos_extraidos: Optional[str] = None

    class Config:
        from_attributes = True


class PasoTramitacionBase(BaseModel):
    """Base paso tramitacion schema."""
    titulo: str
    descripcion: Optional[str] = None
    numero_paso: int


class PasoTramitacionCreate(PasoTramitacionBase):
    """Schema for creating a paso tramitacion."""
    pass


class PasoTramitacionRead(PasoTramitacionBase):
    """Schema for reading a paso tramitacion."""
    id: int
    expediente_id: int
    estado: str
    datetime_inicio: Optional[datetime] = None
    datetime_fin: Optional[datetime] = None
    responsable_id: Optional[int] = None
    comentarios: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpedienteBase(BaseModel):
    """Base expediente schema."""
    numero: str
    asunto: str
    descripcion: Optional[str] = None


class ExpedienteCreate(ExpedienteBase):
    """Schema for creating an expediente."""
    responsable_id: Optional[int] = None


class ExpedienteUpdate(BaseModel):
    """Schema for updating an expediente."""
    asunto: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    responsable_id: Optional[int] = None


class ExpedienteRead(ExpedienteBase):
    """Schema for reading an expediente."""
    id: int
    estado: str
    responsable_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_cierre: Optional[datetime] = None
    documentos: List[DocumentoRead] = []
    pasos: List[PasoTramitacionRead] = []

    class Config:
        from_attributes = True


class ExpedientePaginatedResponse(BaseModel):
    """Paginated expedientes response."""
    items: List[ExpedienteRead]
    total: int
    skip: int
    limit: int
