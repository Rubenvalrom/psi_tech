---
name: skill-fastapi-modular-arch
description: Design modular FastAPI applications with clean separation of concerns. Includes directory structure, routing patterns (APIRouter), dependency injection, schema validation (Pydantic), error handling, and middleware. Use when building enterprise backends requiring maintainability, testing, and scalability.
---

# Modular FastAPI Architecture

## Structure Template

```
backend/app/
├── core/
│   ├── config.py         # Settings, env vars
│   ├── security.py       # Auth, JWT validation
│   └── dependencies.py   # Shared dependencies
├── db/
│   ├── base.py           # SQLAlchemy base
│   ├── session.py        # DB session management
│   └── migrations/       # Alembic migrations
├── models/
│   ├── __init__.py
│   ├── expediente.py     # ORM models
│   ├── documento.py
│   └── factura.py
├── schemas/
│   ├── __init__.py
│   ├── expediente.py     # Pydantic request/response
│   ├── documento.py
│   └── factura.py
├── routes/
│   ├── __init__.py
│   ├── expedientes.py    # FastAPI APIRouter
│   ├── documentos.py
│   ├── facturas.py
│   └── auth.py
├── services/
│   ├── __init__.py
│   ├── expediente_service.py   # Business logic
│   ├── ollama_service.py       # LLM integration
│   └── email_service.py        # Notifications
├── utils/
│   ├── __init__.py
│   ├── exceptions.py     # Custom exceptions
│   └── validators.py     # Custom validators
└── main.py              # FastAPI app entry point
```

## Key Patterns

### 1. APIRouter (Modular Routes)
See [references/routing-patterns.md](references/routing-patterns.md):
- Group endpoints by resource (expedientes, facturas)
- Use router prefix and tags
- Centralize error handling per route

### 2. Pydantic Schemas
See [references/pydantic-validation.md](references/pydantic-validation.md):
- Separate Create, Read, Update schemas
- Validators for business rules
- Response models for API contracts

### 3. Dependency Injection
See [references/dependencies.md](references/dependencies.md):
- Database session as dependency
- Authentication via Depends()
- Reusable validation logic

## Scripts

**Scaffold new module**:
```bash
python scripts/scaffold_module.py --name expedientes
```

**Validate structure**:
```bash
python scripts/validate_structure.py
```
