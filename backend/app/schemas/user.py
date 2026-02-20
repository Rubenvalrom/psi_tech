"""Pydantic schemas for User model."""
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    nombre_completo: str
    roles: List[str] = ["FUNCIONARIO"]


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    nombre_completo: Optional[str] = None
    activo: Optional[bool] = None
    roles: Optional[List[str]] = None


class UserRead(UserBase):
    """Schema for reading a user (response)."""
    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
