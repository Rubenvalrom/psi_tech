"""Expediente (case management) models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class EstadoExpediente(str, enum.Enum):
    """Estados posibles de un expediente."""
    ABIERTO = "ABIERTO"
    EN_PROCESO = "EN_PROCESO"
    CERRADO = "CERRADO"
    ANULADO = "ANULADO"


class TipoDocumento(str, enum.Enum):
    """Tipos de documentos en un expediente."""
    SOLICITUD = "SOLICITUD"
    INFORME = "INFORME"
    RESOLUCIÓN = "RESOLUCIÓN"
    ADJUNTO = "ADJUNTO"
    OTRO = "OTRO"


class EstadoPaso(str, enum.Enum):
    """Estados posibles de un paso de tramitación."""
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADO = "COMPLETADO"
    RECHAZADO = "RECHAZADO"


class Expediente(Base):
    """Main case file (expediente) model."""

    __tablename__ = "expedientes"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, index=True, nullable=False)
    asunto = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(Enum(EstadoExpediente), default=EstadoExpediente.ABIERTO, index=True)
    responsable_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    fecha_creacion = Column(DateTime, server_default=func.now(), index=True)
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())
    fecha_cierre = Column(DateTime, nullable=True)

    # Relationships
    documentos = relationship("Documento", back_populates="expediente", cascade="all, delete-orphan")
    pasos = relationship("PasoTramitacion", back_populates="expediente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Expediente {self.numero}>"


class Documento(Base):
    """Document attached to an expediente."""

    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id"), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    contenido_blob = Column(LargeBinary, nullable=True)  # For small files; use S3 for large files
    tipo = Column(Enum(TipoDocumento), default=TipoDocumento.ADJUNTO)
    ruta_archivo = Column(String(500), nullable=True)  # Path to file if stored externally
    metadatos_extraidos = Column(String(2000), nullable=True)  # JSON string with OCR/IA metadata
    fecha_carga = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    expediente = relationship("Expediente", back_populates="documentos")

    def __repr__(self):
        return f"<Documento {self.nombre}>"


class PasoTramitacion(Base):
    """Step in the case workflow (BPMN)."""

    __tablename__ = "pasos_tramitacion"

    id = Column(Integer, primary_key=True, index=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id"), nullable=False, index=True)
    numero_paso = Column(Integer, nullable=False)  # Sequential step number
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(Enum(EstadoPaso), default=EstadoPaso.PENDIENTE, index=True)
    datetime_inicio = Column(DateTime, nullable=True)
    datetime_fin = Column(DateTime, nullable=True)
    responsable_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    comentarios = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    expediente = relationship("Expediente", back_populates="pasos")

    def __repr__(self):
        return f"<PasoTramitacion {self.expediente_id}-{self.numero_paso}>"
