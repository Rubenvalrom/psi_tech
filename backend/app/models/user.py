"""User model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ..core.database import Base


class User(Base):
    """User model for system users (funcionarios, gestores, admins)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    roles = Column(JSON, default=["FUNCIONARIO"], nullable=False)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"
