"""Pydantic schemas for Expediente models."""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentoBase(BaseModel):
    """Base documento schema."""
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del documento")
    tipo: str = Field(default="ADJUNTO", max_length=50)


class DocumentoCreate(DocumentoBase):
    """Schema for creating a documento."""
    pass


class DocumentoRead(DocumentoBase):
    """Schema for reading a documento."""
    id: int
    expediente_id: int
    fecha_carga: datetime
    metadatos_extraidos: Optional[str] = None
    
    # Phase 3: Digital signing
    hash_firma: Optional[str] = None
    firmado_por: Optional[str] = None
    fecha_firma: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentoSign(BaseModel):
    """Schema for signing a documento."""
    firmado_por: str = Field(..., min_length=1, max_length=255, description="Nombre de quien firma")


class TrazabilidadRead(BaseModel):
    """Schema for reading audit trail."""
    id: int
    expediente_id: int
    usuario_id: Optional[int] = None
    accion: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    datos_anteriores: Optional[dict] = None
    datos_nuevos: Optional[dict] = None
    timestamp: datetime

    class Config:
        from_attributes = True



class PasoTramitacionBase(BaseModel):
    """Base paso tramitacion schema."""
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=2000)
    numero_paso: int = Field(..., gt=0)


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
    numero: str = Field(..., min_length=3, max_length=50, description="Número único del expediente")
    asunto: str = Field(..., min_length=5, max_length=500, description="Asunto del expediente")
    descripcion: Optional[str] = Field(None, max_length=2000)


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
