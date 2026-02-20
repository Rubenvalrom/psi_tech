# APIRouter & Routing Patterns

## Basic Router Setup

```python
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List
from app.schemas.expediente import ExpedienteRead, ExpedienteCreate
from app.services.expediente_service import ExpedienteService
from app.core.dependencies import get_current_user
from app.core.security import require_role

router = APIRouter(
    prefix="/api/v1/expedientes",
    tags=["Expedientes"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=List[ExpedienteRead])
async def list_expedientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    estado: str = Query(None),
    service: ExpedienteService = Depends()
):
    return service.list(skip=skip, limit=limit, estado=estado)

@router.get("/{expediente_id}", response_model=ExpedienteRead)
async def get_expediente(
    expediente_id: int = Path(..., ge=1),
    service: ExpedienteService = Depends()
):
    exp = service.get(expediente_id)
    if not exp:
        raise HTTPException(status_code=404)
    return exp

@router.post("/", response_model=ExpedienteRead, status_code=201)
async def create_expediente(
    exp: ExpedienteCreate,
    user = Depends(require_role("FUNCIONARIO")),
    service: ExpedienteService = Depends()
):
    return service.create(exp, user_id=user["sub"])
```

## Router Versioning

```python
# routes/v1/expedientes.py
router_v1 = APIRouter(prefix="/api/v1/expedientes")

# routes/v2/expedientes.py
router_v2 = APIRouter(prefix="/api/v2/expedientes")

# main.py
app.include_router(router_v1)
app.include_router(router_v2)
```

## Include Routers in Main

```python
from fastapi import FastAPI
from app.routes import expedientes, documentos, facturas, auth

app = FastAPI(
    title="Olympus Smart Gov API",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(expedientes.router)
app.include_router(documentos.router)
app.include_router(facturas.router)
```
