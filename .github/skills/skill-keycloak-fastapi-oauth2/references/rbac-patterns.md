# Role-Based Access Control (RBAC)

## Role Hierarchy

**Olympus Roles** (server-side in Keycloak):

| Role | Permissions | Use Case |
|------|------------|----------|
| `ADMIN` | All endpoints, user management, system config | System administrators |
| `FUNCIONARIO` | Create/view expedientes, upload docs, comment | Government employees |
| `GESTOR_FINANCIERO` | Create facturas, approve payments, budgets | Finance department |
| `VIEWER` | Read-only access to expedientes | Audit, reporting |

**Scope** (optional): `expedientes:read`, `expedientes:write`, `facturas:approve`

## Decorator Pattern

### Simple Role Check

```python
from functools import wraps
from fastapi import HTTPException, status

def require_role(*allowed_roles):
    """Decorator to enforce role-based access."""
    async def role_checker(user = Depends(get_current_user)):
        user_roles = user.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {allowed_roles}"
            )
        return user
    
    return Depends(role_checker)

# Usage
@app.post("/api/v1/expedientes")
async def create_expediente(
    expediente: ExpedienteCreate,
    user = require_role("FUNCIONARIO", "ADMIN")
):
    return {"created_by": user["sub"]}
```

### Multi-Role Checks

```python
def require_any_role(*roles):
    """User must have at least ONE role."""
    async def checker(user = Depends(get_current_user)):
        if not any(r in user.get("roles", []) for r in roles):
            raise HTTPException(status_code=403)
        return user
    return Depends(checker)

def require_all_roles(*roles):
    """User must have ALL roles."""
    async def checker(user = Depends(get_current_user)):
        user_roles = user.get("roles", [])
        if not all(r in user_roles for r in roles):
            raise HTTPException(status_code=403)
        return user
    return Depends(checker)
```

## Resource-Level Access

Enforce permissions per resource instance:

```python
async def get_expediente_or_404(
    expediente_id: int,
    user = Depends(get_current_user)
) -> Expediente:
    exp = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not exp:
        raise HTTPException(status_code=404)
    
    # Only ADMIN or owner (responsable) can view
    is_admin = "ADMIN" in user.get("roles", [])
    is_owner = exp.responsable_id == user["sub"]
    
    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=403,
            detail="No permission to access this expediente"
        )
    return exp

@app.get("/api/v1/expedientes/{expediente_id}")
async def get_expediente(
    exp = Depends(get_expediente_or_404)
):
    return exp
```

## Audit Logging

Log all authorization decisions:

```python
import logging
from datetime import datetime

logger = logging.getLogger("auth_audit")

def log_access(user_id: str, action: str, resource: str, allowed: bool):
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "allowed": allowed
    })

# In role_checker or resource check
try:
    # ... permission check
    log_access(user["sub"], "read", f"expediente:{exp.id}", True)
except HTTPException:
    log_access(user["sub"], "read", f"expediente:{exp.id}", False)
    raise
```

## Testing RBAC

```python
def test_create_expediente_requires_funcionario():
    # Create token with VIEWER role only
    viewer_token = create_test_token(roles=["VIEWER"])
    
    response = client.post(
        "/api/v1/expedientes",
        json={"asunto": "Test"},
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert response.status_code == 403

def test_create_expediente_allowed_for_funcionario():
    funcionario_token = create_test_token(roles=["FUNCIONARIO"])
    
    response = client.post(
        "/api/v1/expedientes",
        json={"asunto": "Test"},
        headers={"Authorization": f"Bearer {funcionario_token}"}
    )
    assert response.status_code == 201

def test_admin_can_view_all_expedientes():
    admin_token = create_test_token(roles=["ADMIN"])
    funcionario_token = create_test_token(roles=["FUNCIONARIO"])
    
    # Funcionario creates expediente
    response = client.post(
        "/api/v1/expedientes",
        json={"asunto": "Test"},
        headers={"Authorization": f"Bearer {funcionario_token}"}
    )
    exp_id = response.json()["id"]
    
    # Admin views it (even if not owner)
    response = client.get(
        f"/api/v1/expedientes/{exp_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
```
