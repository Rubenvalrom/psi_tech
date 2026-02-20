# Pydantic Validation & Schemas

## Separate Schemas Per Operation

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# Request/Create Schema
class ExpedienteCreate(BaseModel):
    numero: str = Field(..., min_length=3, max_length=50)
    asunto: str = Field(..., min_length=10, max_length=500)
    descripcion: Optional[str] = None
    
    @validator('numero')
    def numero_format(cls, v):
        if not v.isalnum():
            raise ValueError("Must be alphanumeric")
        return v.upper()

# Update Schema (fewer required fields)
class ExpedienteUpdate(BaseModel):
    asunto: Optional[str] = None
    descripcion: Optional[str] = None

# Database/Internal Schema
class ExpedienteDB(ExpedienteCreate):
    id: int
    responsable_id: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True  # Works with ORM objects

# Response Schema (excludes sensitive fields)
class ExpedienteRead(BaseModel):
    id: int
    numero: str
    asunto: str
    estado: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True
```

## Custom Validators

```python
from pydantic import validator, root_validator
from typing import Dict, Any

class FacturaCreate(BaseModel):
    numero: str
    monto: float
    fecha_emision: datetime
    
    @validator('monto')
    def monto_positive(cls, v):
        if v <= 0:
            raise ValueError("Monto must be positive")
        return v
    
    @root_validator
    def validate_fechas(cls, values):
        fecha = values.get('fecha_emision')
        if fecha and fecha > datetime.now():
            raise ValueError("fecha_emision cannot be future")
        return values
```

## Nested Schemas

```python
class DocumentoSchema(BaseModel):
    id: int
    nombre: str
    tipo: str

class ExpedienteWith Documents(ExpedienteRead):
    documentos: List[DocumentoSchema]
```
