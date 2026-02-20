# Unit Testing Patterns

```python
import pytest
from unittest.mock import patch, MagicMock
from app.services.expediente_service import ExpedienteService
from app.models import Expediente

@pytest.fixture
def expediente_service():
    mock_db = MagicMock()
    return ExpedienteService(db=mock_db)

def test_create_expediente(expediente_service):
    """Test service create logic."""
    service = expediente_service
    
    result = service.create(
        numero="EXP-001",
        asunto="Test",
        user_id="user-123"
    )
    
    assert result.numero == "EXP-001"
    assert result.responsable_id == "user-123"

@patch('app.services.ollama_service.call_ollama')
def test_extract_metadata_with_mock(mock_ollama):
    """Mock external Ollama service."""
    mock_ollama.return_value = '{"solicitante": "Test"}'
    
    from app.services.ocr_service import OCRService
    service = OCRService()
    
    result = service.extract_metadata("Some OCR text")
    assert result["solicitante"] == "Test"

def test_validation_error():
    """Test error handling."""
    from pydantic import ValidationError
    from app.schemas import ExpedienteCreate
    
    with pytest.raises(ValidationError):
        ExpedienteCreate(numero="", asunto="")  # Invalid
```

# Endpoint Testing

```python
def test_create_expediente_endpoint(client, mocker):
    """Test POST /expedientes with auth."""
    mock_token = {"sub": "user-1", "roles": ["FUNCIONARIO"]}
    
    with patch('app.core.security.verify_token', return_value=mock_token):
        response = client.post(
            "/api/v1/expedientes",
            headers={"Authorization": "Bearer mock_token"},
            json={"numero": "EXP-001", "asunto": "Test"}
        )
    
    assert response.status_code == 201
    assert response.json()["numero"] == "EXP-001"
```
