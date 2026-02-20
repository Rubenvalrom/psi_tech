# Reliability Patterns for Ollama Integration

## Timeout Strategy

Set appropriate timeouts for different use cases:

```python
import asyncio
import httpx

TIMEOUTS = {
    "metadata_extraction": 30,  # Single inference
    "assistant_response": 60,   # With RAG + retrieval
    "batch_processing": 120,    # Multiple inferences
}

async def call_ollama_with_timeout(
    prompt: str,
    model: str = "mistral",
    use_case: str = "assistant_response"
) -> str:
    timeout = httpx.Timeout(TIMEOUTS[use_case])
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                "http://ollama:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            return response.json()["response"]
        except asyncio.TimeoutError:
            return "Response timeout - Ollama service may be overloaded"
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise
```

## Retry Logic with Exponential Backoff

```python
import random
from functools import wraps

def retry_on_ollama_failure(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """Decorator for automatic retry on Ollama failures."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        jitter = random.uniform(0, 0.1 * delay)
                        wait_time = delay + jitter
                        logger.warning(f"Ollama call failed (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time:.2f}s")
                        await asyncio.sleep(wait_time)
                        delay *= backoff_factor
                    else:
                        logger.error(f"Ollama call failed after {max_retries} retries")
            
            raise last_exception
        return wrapper
    return decorator

@retry_on_ollama_failure(max_retries=3)
async def call_ollama_reliable(prompt: str, model: str = "mistral") -> str:
    return await call_ollama_with_timeout(prompt, model)
```

## Graceful Degradation

Provide fallback responses when Ollama unavailable:

```python
import asyncio

class OllamaClient:
    def __init__(self, default_responses: dict = None):
        self.default_responses = default_responses or {}
        self.ollama_available = True
    
    async def generate_with_fallback(
        self,
        prompt: str,
        use_case: str = "assistant",
        model: str = "mistral"
    ) -> dict:
        try:
            # Try Ollama first
            response = await call_ollama_reliable(prompt, model)
            self.ollama_available = True
            return {
                "response": response,
                "source": "ollama",
                "reliability": "high"
            }
        
        except asyncio.TimeoutError:
            logger.warning("Ollama timeout, using fallback")
            return {
                "response": self._get_fallback(use_case),
                "source": "fallback",
                "reliability": "low"
            }
        
        except Exception as e:
            logger.error(f"Ollama error: {e}, using fallback")
            self.ollama_available = False
            return {
                "response": self._get_fallback(use_case),
                "source": "fallback",
                "reliability": "low",
                "error": str(e)
            }
    
    def _get_fallback(self, use_case: str) -> str:
        fallbacks = {
            "metadata_extraction": "Unable to extract metadata. Please fill in manually.",
            "assistant": "The AI assistant is temporarily unavailable. Please try again later.",
            "prediction": "Unable to generate forecast. Using historical average instead.",
        }
        return fallbacks.get(use_case, "Service temporarily unavailable")
```

## Structured Output Validation

Validate LLM outputs to ensure correct format:

```python
from pydantic import BaseModel, ValidationError, validator
import json

class MetadataExtraction(BaseModel):
    solicitante: str
    tipo_tramite: str
    monto: float = None
    articulos: list[str]
    
    @validator('monto')
    def monto_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Monto must be positive")
        return v

async def extract_metadata_validated(
    ocr_text: str,
    model: str = "mistral"
) -> MetadataExtraction or dict:
    prompt = f"""
Extract structural metadata from this document:
{ocr_text}

Return ONLY valid JSON with fields: solicitante, tipo_tramite, monto, articulos
"""
    
    try:
        response = await call_ollama_reliable(prompt, model)
        
        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from Ollama: {response}")
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                return {"error": "Could not parse JSON", "raw_response": response}
        
        # Validate with Pydantic
        validated = MetadataExtraction(**data)
        return validated
    
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        return {"error": "Validation failed", "details": e.errors()}
```

## Circuit Breaker Pattern

Stop calling Ollama if it's persistently failing:

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, skip calls
    HALF_OPEN = "half_open"  # Testing recovery

class OllamaCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout_seconds
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: attempting recovery")
            else:
                raise Exception("Ollama service unavailable (circuit breaker OPEN)")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_recovery(self) -> bool:
        return (
            self.last_failure_time and
            datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout)
        )
    
    def _on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker: recovered to CLOSED state")
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.utcnow()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker OPEN after {self.failures} failures")

# Usage
breaker = OllamaCircuitBreaker()

async def safe_ollama_call(prompt: str):
    return await breaker.call(call_ollama_reliable, prompt)
```

## Monitoring & Logging

```python
import logging
from typing import Dict
import time

logger = logging.getLogger("ollama_metrics")

class OllamaMetrics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0
    
    async def timed_call(self, prompt: str, model: str = "mistral") -> tuple[str, float]:
        start = time.time()
        
        try:
            result = await call_ollama_reliable(prompt, model)
            latency = time.time() - start
            
            self.total_requests += 1
            self.successful_requests += 1
            self.total_latency += latency
            
            logger.info(f"Ollama success | latency={latency:.2f}s | model={model}")
            return result, latency
        
        except Exception as e:
            latency = time.time() - start
            self.total_requests += 1
            self.failed_requests += 1
            
            logger.error(f"Ollama failed | latency={latency:.2f}s | error={e}")
            raise
    
    def get_stats(self) -> Dict:
        success_rate = (self.successful_requests / self.total_requests * 100
                       if self.total_requests > 0 else 0)
        avg_latency = (self.total_latency / self.successful_requests
                      if self.successful_requests > 0 else 0)
        
        return {
            "total_requests": self.total_requests,
            "success_rate": f"{success_rate:.1f}%",
            "avg_latency_ms": f"{avg_latency * 1000:.0f}",
            "failed_requests": self.failed_requests
        }
```
