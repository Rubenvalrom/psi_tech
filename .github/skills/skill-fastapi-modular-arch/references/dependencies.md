# Dependency Injection

## Database Session

```python
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoints
@router.get("/")
async def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## Service Pattern

```python
from app.db.session import SessionLocal

class ExpedienteService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    def get(self, id: int):
        return self.db.query(Expediente).filter(Expediente.id == id).first()

# Usage
@router.get("/{id}")
async def get_exp(id: int, service: ExpedienteService = Depends()):
    return service.get(id)
```

## Current User Dependency

```python
async def get_current_user(token: str = Depends(HTTPBearer())) -> dict:
    user = await verify_token(token.credentials)
    return user

@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return user
```

## Composite Dependencies

```python
async def check_expediente_access(
    exp_id: int = Path(...),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exp = db.query(Expediente).filter(Expediente.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404)
    
    # Check ownership or admin
    if exp.responsable_id != user["sub"] and "ADMIN" not in user.get("roles", []):
        raise HTTPException(status_code=403)
    
    return exp

@router.get("/{exp_id}/detail")
async def get_detail(exp = Depends(check_expediente_access)):
    return exp
```
