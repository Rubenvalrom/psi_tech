# Integration Testing with FastAPI + Pytest

## Database Integration Tests

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_expediente_full_flow(
    client: AsyncClient,
    auth_headers: dict,
    db_session
):
    """Test full expediente creation flow"""
    
    # Create expediente
    response = await client.post(
        "/api/expedientes",
        json={
            "numero": "EXP-2024-001",
            "solicitante": "Juan Pérez",
            "concepto": "Solicitud de licencia"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    expediente_id = data["id"]
    
    # Verify in database
    from app.models import Expediente
    from sqlalchemy.future import select
    
    result = await db_session.execute(
        select(Expediente).where(Expediente.id == expediente_id)
    )
    expediente = result.scalar_one()
    
    assert expediente.numero == "EXP-2024-001"
    assert expediente.estado == "iniciado"


@pytest.mark.asyncio
async def test_update_expediente_status(
    client: AsyncClient,
    auth_headers: dict,
    db_session
):
    """Test updating expediente status through API"""
    
    # Create initial expediente
    create_response = await client.post(
        "/api/expedientes",
        json={"numero": "EXP-TEST-001", "solicitante": "Test"},
        headers=auth_headers
    )
    expediente_id = create_response.json()["id"]
    
    # Update status
    response = await client.put(
        f"/api/expedientes/{expediente_id}",
        json={"estado": "en_revision"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["estado"] == "en_revision"


@pytest.mark.asyncio
async def test_transaction_rollback(
    client: AsyncClient,
    auth_headers: dict,
    db_session
):
    """Test transaction rollback on error"""
    
    # Attempt to create with invalid data
    response = await client.post(
        "/api/expedientes",
        json={"numero": None},  # Invalid
        headers=auth_headers
    )
    
    assert response.status_code == 422
    
    # Verify nothing was created
    from app.models import Expediente
    from sqlalchemy.future import select
    
    result = await db_session.execute(select(Expediente))
    assert result.scalars().all() == []
```

## API Chain Tests

```python
@pytest.mark.asyncio
async def test_workflow_chain(
    client: AsyncClient,
    auth_headers: dict
):
    """Test chained API calls (complete workflow)"""
    
    # Step 1: Create expediente
    exp_response = await client.post(
        "/api/expedientes",
        json={"numero": "CHAIN-001", "solicitante": "User"},
        headers=auth_headers
    )
    exp_id = exp_response.json()["id"]
    
    # Step 2: Add documento
    doc_response = await client.post(
        f"/api/expedientes/{exp_id}/documentos",
        json={"nombre": "documento.pdf", "tipo": "solicitud"},
        headers=auth_headers
    )
    doc_id = doc_response.json()["id"]
    
    # Step 3: Submit for review
    review_response = await client.put(
        f"/api/expedientes/{exp_id}",
        json={"estado": "en_revision"},
        headers=auth_headers
    )
    
    assert review_response.status_code == 200
    assert review_response.json()["estado"] == "en_revision"
```

## Concurrent Request Tests

```python
import asyncio


@pytest.mark.asyncio
async def test_concurrent_expediente_creation(
    client: AsyncClient,
    auth_headers: dict
):
    """Test handling multiple concurrent requests"""
    
    async def create_expediente(num):
        response = await client.post(
            "/api/expedientes",
            json={
                "numero": f"CONCURRENT-{num}",
                "solicitante": f"User {num}"
            },
            headers=auth_headers
        )
        return response
    
    # Create 10 expedientes concurrently
    tasks = [create_expediente(i) for i in range(10)]
    responses = await asyncio.gather(*tasks)
    
    # Verify all succeeded
    assert all(r.status_code == 201 for r in responses)
    assert len(set(r.json()["id"] for r in responses)) == 10


@pytest.mark.asyncio
async def test_concurrent_read_write(
    client: AsyncClient,
    auth_headers: dict
):
    """Test concurrent read and write operations"""
    
    # Create initial expediente
    create_response = await client.post(
        "/api/expedientes",
        json={"numero": "CONCURRENT-RW", "solicitante": "Test"},
        headers=auth_headers
    )
    exp_id = create_response.json()["id"]
    
    async def read_and_update(task_num):
        # Read
        read_response = await client.get(
            f"/api/expedientes/{exp_id}",
            headers=auth_headers
        )
        
        # Update
        update_response = await client.put(
            f"/api/expedientes/{exp_id}",
            json={"estado": f"estado-{task_num}"},
            headers=auth_headers
        )
        
        return read_response, update_response
    
    # Run concurrent operations
    tasks = [read_and_update(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    # Verify no errors
    for read_r, update_r in results:
        assert read_r.status_code == 200
        assert update_r.status_code == 200
```

## Error Scenario Tests

```python
@pytest.mark.asyncio
async def test_database_error_handling(
    client: AsyncClient,
    auth_headers: dict,
    mocker
):
    """Test API behavior when database errors occur"""
    
    # Mock database error
    mocker.patch(
        "app.crud.create_expediente",
        side_effect=Exception("Database connection failed")
    )
    
    response = await client.post(
        "/api/expedientes",
        json={"numero": "TEST", "solicitante": "User"},
        headers=auth_headers
    )
    
    # Should return 500 error
    assert response.status_code == 500
    assert "error" in response.json()
```

## Event Stream Testing

```python
@pytest.mark.asyncio
async def test_webhook_events(
    client: AsyncClient,
    auth_headers: dict,
    mocker
):
    """Test webhook triggers on state changes"""
    
    webhook_mock = mocker.patch("app.webhooks.send_webhook")
    
    # Create expediente (should trigger webhook)
    response = await client.post(
        "/api/expedientes",
        json={"numero": "WEBHOOK-TEST", "solicitante": "User"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    webhook_mock.assert_called_once()
    
    # Verify webhook call details
    call_kwargs = webhook_mock.call_args[1]
    assert call_kwargs["event"] == "expediente.created"
    assert call_kwargs["data"]["numero"] == "WEBHOOK-TEST"
```
