---
name: skill-ollama-llm-prompts
description: Integrate Ollama local LLMs (Llama 2, Mistral) with FastAPI for automated document analysis, virtual assistant, and predictive analytics. Includes prompt templates for key Olympus use cases (extract metadata from expedientes, generate legal recommendations, predict bottlenecks), strategies for reliable inference (retry logic, timeouts, fallbacks), and guidance on model selection and fine-tuning. Use when implementing AI features requiring text generation, document understanding, or recommendation engines without external APIs.
---

# Ollama LLM & Prompt Engineering

## Architecture Decision

**Why Ollama?**
- Local inference: No API dependencies, full data privacy, no token costs
- Model flexibility: Pull/swap models (Llama 2, Mistral, Neural Chat) without code changes
- Integration: Simple HTTP API, easy to containerize, Kubernetes-ready
- Development: Instant feedback loop, no rate limits

**Supported Models** (balance accuracy vs. speed):
- `llama2` (7B): General purpose, good UX recommendations. ~6GB VRAM
- `mistral` (7B): Best quality-to-speed ratio. ~7GB VRAM
- `neural-chat` (7B): Conversational, good for assistant. ~6GB VRAM
- `nomic-embed-text`: For embeddings (pgvector), ~500MB

**Model Selection Criteria**:

| Use Case | Model | Reason |
|----------|-------|--------|
| Extract expediente metadata | Mistral 7B | Accurate JSON output, fast |
| Virtual assistant chat | Llama 2 Chat | Conversational, 60 token/sec |
| Budget forecasting | Llama 2 | Mathematical reasoning OK |
| Embebddings (semantic search) | nomic-embed-text | Fast, 1536-dim vectors |

## Quick Start

```bash
# Pull model (one-time, auto on first request)
ollama pull mistral

# Verify Ollama running
curl http://localhost:11434/api/tags
```

```python
import requests
import json

def call_ollama(prompt: str, model: str = "mistral") -> str:
    url = "http://ollama:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    
    response = requests.post(url, json=payload, timeout=30)
    return response.json()["response"]

# Example: Extract metadata
ocr_text = "Solicitud de licencia de construcción..."
prompt = f"Extract: solicitante, tipo trámite, monto\n\nDocumento:\n{ocr_text}"
result = call_ollama(prompt, "mistral")
print(result)
```

## Prompt Templates

See [references/prompt-templates.md](references/prompt-templates.md):
- Auto-rellenado de expedientes (OCR → JSON metadata)
- Asistente virtual (context-aware recommendations)
- Predicción de tendencias (time-series forecasting)
- Extracción de cláusulas legales

## RAG Strategy

See [references/rag-patterns.md](references/rag-patterns.md):
- Retrieval: pgvector for semantic search + simple text BM25
- Augmentation: Precedent documents + regulatory references
- Generation: Context-aware prompts with retrieved examples
- Fallback: When no relevant docs found, use generic prompt

## Reliability Patterns

See [references/reliability-patterns.md](references/reliability-patterns.md):
- Retry logic with exponential backoff
- Request timeouts (30s default)
- Graceful degradation (return cached/default on failure)
- Structured output validation (JSON schema check)

## Scripts

**Client library**:
```bash
python scripts/ollama_client.py --model mistral --prompt "What is machine learning?"
```

**Prompt evaluation framework**:
```bash
pytest scripts/test_prompts.py -v
# Runs test cases with different models, measures accuracy
```

**Model benchmarking**:
```bash
python scripts/benchmark_models.py --models mistral llama2 neural-chat
# Outputs: latency, accuracy, VRAM usage
```

## Decisions

- **MVP models**: Mistral (text) + nomic-embed (vectors), both 7B to fit on single GPU
- **Streaming vs. Complete**: Use complete (stream=False) for MVP, simpler handling
- **Structured output**: Prompt for JSON, validate with Pydantic, fallback to named entities
- **Caching**: Cache embeddings in pgvector, NOT raw LLM outputs (too large)
- **Cost estimation**: Ollama local = no API costs, but infra/compute cost (single GPU ~$500/year)
