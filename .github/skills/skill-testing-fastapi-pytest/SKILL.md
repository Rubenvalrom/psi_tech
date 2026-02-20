---
name: skill-testing-fastapi-pytest
description: Comprehensive testing strategy for FastAPI backends using pytest, pytest-asyncio, mocking, and fixtures. Includes unit tests, integration tests, endpoint testing, and coverage validation. Use when ensuring API reliability, preventing regressions, and achieving code coverage targets (60%+ minimum).
---

# FastAPI Testing (pytest)

## Quick Start

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_list_expedientes(client):
    response = client.get("/api/v1/expedientes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unauthorized_access(client):
    response = client.get("/api/v1/expedientes", headers={})
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_async_create_expediente(client):
    payload = {"numero": "EXP-001", "asunto": "Test"}
    response = client.post("/api/v1/expedientes", json=payload)
    assert response.status_code == 201
```

See [references/unit-testing.md](references/unit-testing.md):
- Mock external services (Keycloak, Ollama, pgvector)
- Test models, validators, utilities

See [references/endpoint-testing.md](references/endpoint-testing.md):
- Test each endpoint (GET, POST, PUT)
- Validate status codes, response schema
- Test authorization/permissions

See [references/integration-testing.md](references/integration-testing.md):
- E2E flows: login → create → list → update
- Test with real database (using fixtures)
- Async/await patterns

See [references/coverage-strategy.md](references/coverage-strategy.md):
- Run: `pytest --cov=app --cov-report=html`
- Target: 60%+ coverage
- Exclude test files, __init__.py
