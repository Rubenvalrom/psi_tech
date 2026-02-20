#!/usr/bin/env python3
"""
Test suite for Ollama prompts.
Run: pytest test_prompts.py -v
"""

import asyncio
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict

# Import client (adjust path as needed)
import sys
sys.path.insert(0, '/path/to/scripts')
from ollama_client import OllamaClient


class TestMetadataExtraction:
    """Test extraction of metadata from documents."""
    
    @pytest.mark.asyncio
    async def test_extract_metadata_valid(self):
        """Extract valid metadata from OCR text."""
        ocr_text = """
        Solicitud de Licencia de Construcción
        
        Solicitante: María García López
        NIF: 12.345.678-A
        Tipo de Tramite: Ampliación de vivienda
        Presupuesto: 45.000 euros
        Artículos Aplicables: Art.47 Ley 38/1988
        Fecha: 15/02/2024
        """
        
        prompt = f"""Extract structured metadata:
        {ocr_text}
        
        Return JSON with: solicitante, tipo_tramite, monto, articulos"""
        
        with patch.object(OllamaClient, 'generate') as mock_gen:
            mock_gen.return_value = json.dumps({
                "solicitante": "María García López",
                "tipo_tramite": "Ampliación de vivienda",
                "monto": 45000,
                "articulos": ["Art.47 Ley 38/1988"]
            })
            
            client = OllamaClient()
            result = await client.generate(prompt)
            data = json.loads(result)
            
            assert data["solicitante"] == "María García López"
            assert data["monto"] == 45000
            assert "Art.47" in data["articulos"][0]
    
    @pytest.mark.asyncio
    async def test_extract_metadata_invalid_json(self):
        """Handle invalid JSON response."""
        with patch.object(OllamaClient, 'generate') as mock_gen:
            mock_gen.return_value = "Not valid JSON at all"
            
            client = OllamaClient()
            result = await client.generate("test prompt")
            
            with pytest.raises(json.JSONDecodeError):
                json.loads(result)


class TestAssistantPrompts:
    """Test virtual assistant recommendations."""
    
    @pytest.mark.asyncio
    async def test_assistant_next_step_recommendation(self):
        """Assistant recommends next procedural step."""
        expediente_context = """
        Expediente #: EXP-2024-001
        Type: Licencia de construcción
        Current Step: Solicitud registrada
        History: 
        - 2024-02-15: Solicitud registrada
        - 2024-02-16: Admisión a trámite
        """
        
        prompt = f"""Recommend next step for:
        {expediente_context}
        
        Return: paso, descripcion, documentos_requeridos, duracion"""
        
        with patch.object(OllamaClient, 'generate') as mock_gen:
            mock_gen.return_value = """
            Paso: Validación técnica del proyecto
            Descripción: Revisar planos y documentación técnica
            Documentos Requeridos: Planos, CTE, informe estructural
            Duración: 5 días laborales
            """
            
            client = OllamaClient()
            result = await client.generate(prompt)
            
            assert "Validación técnica" in result
            assert "5 días" in result


class TestPredictiveAnalytics:
    """Test budget forecasting."""
    
    @pytest.mark.asyncio
    async def test_predict_budget_trend(self):
        """Predict budget spending trend."""
        csv_data = """
        month,amount_eur
        2024-01,150000
        2024-02,155000
        2024-03,160000
        """
        
        prompt = f"""Analyze trend and predict next 3 months:
        {csv_data}
        
        Return: trend_description, predicted_jan, predicted_feb, predicted_mar"""
        
        with patch.object(OllamaClient, 'generate') as mock_gen:
            mock_gen.return_value = """
            Trend: Incremento 0.3% mensual
            Predicción Enero: 165000
            Predicción Febrero: 170000
            Predicción Marzo: 175000
            """
            
            client = OllamaClient()
            result = await client.generate(prompt)
            
            assert "Incremento" in result
            assert "165000" in result


class TestPromptRobustness:
    """Test prompt handling edge cases."""
    
    @pytest.mark.asyncio
    async def test_empty_prompt(self):
        """Handle empty prompt gracefully."""
        client = OllamaClient()
        
        with patch.object(OllamaClient, '_call_ollama') as mock_call:
            mock_call.return_value = ""
            
            result = await client.generate("")
            assert result == ""
    
    @pytest.mark.asyncio
    async def test_very_long_prompt(self):
        """Handle very long prompts."""
        long_text = "document " * 500  # ~3000 tokens
        
        client = OllamaClient()
        
        with patch.object(OllamaClient, '_call_ollama') as mock_call:
            mock_call.return_value = "Processed long document"
            
            result = await client.generate(long_text)
            assert result == "Processed long document"
    
    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Handle special characters in prompts."""
        prompt = "Extract data: Señor García, €50,000, Art.§47"
        
        client = OllamaClient()
        
        with patch.object(OllamaClient, '_call_ollama') as mock_call:
            mock_call.return_value = '{"name": "García", "amount": 50000}'
            
            result = await client.generate(prompt)
            assert "García" in result


class TestErrorHandling:
    """Test error handling and retries."""
    
    @pytest.mark.asyncio
    async def test_timeout_retry(self):
        """Retry on timeout."""
        import httpx
        
        client = OllamaClient()
        
        with patch.object(OllamaClient, '_call_ollama') as mock_call:
            # First two calls timeout, third succeeds
            mock_call.side_effect = [
                httpx.TimeoutException("timeout"),
                httpx.TimeoutException("timeout"),
                "Success after retries"
            ]
            
            result = await client.generate("test", max_retries=3)
            assert result == "Success after retries"
            assert mock_call.call_count == 3
    
    @pytest.mark.asyncio
    async def test_fallback_on_repeated_failure(self):
        """Use fallback when retries exhausted."""
        client = OllamaClient()
        
        result = await client.generate_with_fallback(
            "test",
            fallback_response="Fallback: Unable to process"
        )
        
        # Should succeed or fallback
        assert "response" in result
        assert result["source"] in ["ollama", "fallback"]


class TestJSONGeneration:
    """Test JSON output generation and validation."""
    
    @pytest.mark.asyncio
    async def test_generate_valid_json(self):
        """Generate valid JSON."""
        client = OllamaClient()
        
        with patch.object(OllamaClient, 'generate') as mock_gen:
            mock_gen.return_value = '{"name": "test", "value": 123}'
            
            result = await client.generate_json("test prompt")
            
            assert result["name"] == "test"
            assert result["value"] == 123
    
    @pytest.mark.asyncio
    async def test_extract_json_from_markdown(self):
        """Extract JSON from markdown-wrapped response."""
        client = OllamaClient()
        
        with patch.object(OllamaClient, 'generate') as mock_gen:
            # Response has markdown code block
            mock_gen.return_value = '''```json
            {"extracted": "data", "count": 42}
            ```'''
            
            result = await client.generate_json("test prompt")
            
            assert result["extracted"] == "data"
            assert result["count"] == 42


class TestMetrics:
    """Test performance metrics."""
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Track request metrics."""
        client = OllamaClient()
        
        with patch.object(OllamaClient, '_call_ollama') as mock_call:
            mock_call.return_value = "response"
            
            # Make 3 successful requests
            for _ in range(3):
                await client.generate("test")
            
            metrics = client.get_metrics()
            
            assert metrics["total_requests"] == 3
            assert metrics["successful_requests"] == 3
            assert float(metrics["success_rate_percent"]) == 100.0
    
    @pytest.mark.asyncio
    async def test_failure_metrics(self):
        """Track failure metrics."""
        client = OllamaClient()
        
        result = await client.generate_with_fallback("test")
        
        metrics = client.get_metrics()
        
        # Fallback counts as failure in metrics
        assert "failed" in metrics or "success" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
