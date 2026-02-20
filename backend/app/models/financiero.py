"""Financial and budget models (Fase 4)."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class EstadoFactura(str, enum.Enum):
    """Estados posibles de una factura."""
    PENDIENTE = "PENDIENTE"
    PAGADA = "PAGADA"
    ANULADA = "ANULADA"
    RECHAZADA = "RECHAZADA"


class PartidaPresupuestaria(Base):
    """Budget line item (partida presupuestaria)."""

    __tablename__ = "partidas_presupuestarias"

    id = Column(Integer, primary_key=True, index=True)
    codigo_contable = Column(String(50), unique=True, index=True, nullable=False)
    descripcion = Column(String(500), nullable=False)
    presupuestado = Column(Numeric(15, 2), default=0, nullable=False)
    comprometido = Column(Numeric(15, 2), default=0, nullable=False)
    pagado = Column(Numeric(15, 2), default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    facturas = relationship("Factura", back_populates="partida")

    def __repr__(self):
        return f"<PartidaPresupuestaria {self.codigo_contable}>"

    @property
    def saldo(self):
        """Calculate remaining budget."""
        return self.presupuestado - self.comprometido

    @property
    def disponible(self):
        """Calculate available budget (presupuestado - comprometido - pagado)."""
        return self.presupuestado - self.comprometido - self.pagado


class Factura(Base):
    """Invoice (factura) model."""

    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, index=True, nullable=False)
    proveedor = Column(String(255), nullable=False)
    monto = Column(Numeric(15, 2), nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    fecha_recepcion = Column(DateTime, nullable=True)
    estado = Column(Enum(EstadoFactura), default=EstadoFactura.PENDIENTE, index=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id"), nullable=True)
    partida_presupuestaria_id = Column(Integer, ForeignKey("partidas_presupuestarias.id"), nullable=True)
    contenido_xml = Column(String(5000), nullable=True)  # UBL 2.1 XML content
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    expediente = relationship("Expediente", back_populates="facturas")
    partida = relationship("PartidaPresupuestaria", back_populates="facturas")

    def __repr__(self):
        return f"<Factura {self.numero}>"
