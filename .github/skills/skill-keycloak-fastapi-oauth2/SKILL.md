---
name: skill-keycloak-fastapi-oauth2
description: Integrate Keycloak with FastAPI for OAuth2/OIDC authentication, JWT validation, and role-based access control (RBAC). Includes patterns for securing endpoints, implementing login/logout flows, and enforcing role-based permissions (ADMIN, FUNCIONARIO, GESTOR_FINANCIERO). Use when building authentication/authorization in FastAPI applications with Keycloak as the identity provider.
---

# Keycloak + FastAPI OAuth2 Integration

## Architecture Decision

**Why Keycloak + FastAPI?**
- Keycloak: Enterprise-grade identity management, OpenID Connect compliant, role/attribute mapping
- FastAPI: Native async support, built-in dependency injection, automatic OpenAPI docs
- JWT tokens: Stateless, distributed auth, delegated to Keycloak (no session management in app)
- RBAC: Roles embedded in JWT claims, enforced via decorators on endpoints

**Flow**: Client → Keycloak login → JWT token → FastAPI validates JWT on each request → role checks via decorators

## Quick Start

1. **Environment Setup**
   ```
   KEYCLOAK_URL=http://keycloak:8080
   KEYCLOAK_REALM=olympus
   KEYCLOAK_CLIENT_ID=olympus-backend
   KEYCLOAK_CLIENT_SECRET=<secret>
   ```

2. **Core Module Structure**
   ```
   backend/app/core/
   ├── security.py       # JWT validation, decorators
   ├── config.py         # Keycloak connection config
   └── dependencies.py   # FastAPI dependency injection
   ```

3. **Minimal Example**
   ```python
   from fastapi import FastAPI, Depends
   from app.core.security import verify_token, require_role
   
   app = FastAPI()
   
   @app.get("/api/v1/expedientes")
   async def list_expedientes(
       current_user = Depends(verify_token),
       _ = Depends(require_role("FUNCIONARIO"))
   ):
       return {"user": current_user}
   ```

## Key Patterns

### JWT Token Validation
See [references/jwt-validation.md](references/jwt-validation.md):
- Token introspection (validate signature + expiry)
- Extract claims (user_id, roles, permissions)
- Handle invalid/expired tokens gracefully
- Caching strategy for public key refresh

### Role-Based Access Control
See [references/rbac-patterns.md](references/rbac-patterns.md):
- Map Keycloak roles to app roles (ADMIN, FUNCIONARIO, GESTOR_FINANCIERO)
- Decorator pattern for endpoint protection: `@require_role("ADMIN")`
- Fine-grained permissions: role + resource scope checking
- Audit logging of authorization decisions

### Keycloak Client Setup
See [references/client-setup.md](references/client-setup.md):
- Realm creation ("olympus")
- Client configuration (credentials flow, JWT settings)
- Role and scope definitions
- User/role mapping for testing

## Scripts

**Initialize Keycloak** (auto-setup):
```bash
python scripts/keycloak_init.py
```
Creates realm, roles (ADMIN, FUNCIONARIO, GESTOR_FINANCIERO), test users.

**Test Integration**:
```bash
pytest scripts/test_keycloak.py -v
```
Validates login flow, JWT parsing, role-based access.

**Generate Test Token** (debugging):
```bash
python scripts/keycloak_init.py --get-token --user admin --password admin
```

## Decisions

- **JWT over OAuth2 implicit**: JWT is stateless, better for distributed backends
- **Role-based over attribute-based**: Simpler PoC, can upgrade to ABAC later
- **Keycloak public key caching**: Refresh every 24h or on signature failure
- **Frontend redirect**: Browser redirects to Keycloak for login (not backend handling)
