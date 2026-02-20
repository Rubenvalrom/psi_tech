# RAG (Retrieval-Augmented Generation) Patterns

## Architecture Overview

**RAG Pipeline for Olympus**:

```
User Question
    ↓
Retrieve Similar Docs (pgvector + BM25)
    ↓
Rerank Top 3 by relevance
    ↓
Build Context-Aware Prompt
    ↓
Call Ollama with context
    ↓
Format & Return Response
```

## Retrieval Strategy

### Option 1: Vector Similarity (pgvector)

**When to use**: Semantic questions ("What's the next step for construction permits?")

```python
from sqlalchemy import text

def retrieve_similar_documents(query_text: str, model: str = "nomic-embed-text", limit: int = 3):
    # Generate embedding for query
    query_vector = get_embedding(query_text, model)
    
    # Search for similar documents
    sql = text("""
        SELECT 
            d.id, d.nombre, d.contenido, 
            1 - (de.embedding <=> :query_vec) as similarity
        FROM documento d
        JOIN document_embedding de ON d.id = de.documento_id
        WHERE 1 - (de.embedding <=> :query_vec) > 0.7
        ORDER BY similarity DESC
        LIMIT :limit
    """)
    
    result = db.execute(sql, {"query_vec": query_vector, "limit": limit})
    return [
        {
            "id": row[0],
            "nombre": row[1],
            "contenido": row[2],
            "similarity": float(row[3])
        }
        for row in result
    ]
```

### Option 2: Full-Text Search (BM25)

**When to use**: Keyword-based queries ("Find all expedientes about construction")

```python
from sqlalchemy import func, or_

def retrieve_by_keyword(keyword: str, limit: int = 3):
    # BM25 equivalent in PostgreSQL using tsvector
    sql = text("""
        SELECT 
            d.id, d.nombre, d.contenido,
            ts_rank_cd(to_tsvector('spanish', d.contenido), 
                       plainto_tsquery('spanish', :keyword)) as rank
        FROM documento d
        WHERE to_tsvector('spanish', d.contenido) @@ 
              plainto_tsquery('spanish', :keyword)
        ORDER BY rank DESC
        LIMIT :limit
    """)
    
    result = db.execute(sql, {"keyword": keyword, "limit": limit})
    return [
        {
            "id": row[0],
            "nombre": row[1],
            "contenido": row[2],
            "rank": float(row[3])
        }
        for row in result
    ]
```

### Option 3: Hybrid (Vector + Keyword)

**When to use**: Balance between semantic and keyword relevance

```python
def retrieve_hybrid(query: str, vector_weight: float = 0.6, keyword_weight: float = 0.4):
    # Get vector results
    vector_docs = retrieve_similar_documents(query, limit=5)
    
    # Get keyword results
    keyword_docs = retrieve_by_keyword(query, limit=5)
    
    # Normalize scores (0-1) and merge
    merged = {}
    for doc in vector_docs:
        merged[doc["id"]] = {**doc, "score": vector_weight * doc.get("similarity", 0.5)}
    
    for doc in keyword_docs:
        if doc["id"] in merged:
            merged[doc["id"]]["score"] += keyword_weight * (doc.get("rank", 0.5) / 100)
        else:
            merged[doc["id"]] = {**doc, "score": keyword_weight * (doc.get("rank", 0.5) / 100)}
    
    # Return top 3 by combined score
    return sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:3]
```

## Context Augmentation

### 1. Document Context

```python
def build_document_context(retrieved_docs: list) -> str:
    """Format retrieved documents for prompt."""
    context = "## Documentos Similares:\n\n"
    for i, doc in enumerate(retrieved_docs, 1):
        context += f"{i}. **{doc['nombre']}**\n"
        # Truncate to avoid token explosion
        contenido = doc['contenido'][:500] + "..." if len(doc['contenido']) > 500 else doc['contenido']
        context += f"{contenido}\n\n"
    return context
```

### 2. Expediente History Context

```python
def build_expediente_context(expediente_id: int) -> str:
    """Include expediente history for decision-making."""
    exp = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    
    context = f"""
## Contexto del Expediente:

**Numero**: {exp.numero}
**Asunto**: {exp.asunto}
**Estado Actual**: {exp.estado}
**Responsable**: {exp.responsable.nombre}

## Historial de Pasos:
"""
    for paso in exp.pasos:
        context += f"- {paso.fecha_inicio} → {paso.titulo} [{paso.estado}]\n"
    
    return context
```

### 3. Regulatory Context

```python
def build_regulatory_context(tipo_tramite: str) -> str:
    """Include relevant regulations for the procedure type."""
    regulations = {
        "licencia_construccion": """
Normativa Aplicable:
- Ley 38/1988 de Ordenación de la Edificación
- Código Técnico de la Edificación (CTE)
- Decreto 73/2011 de Régimen de Suelo (Madrid)
""",
        "autorización_ambiental": """
Normativa Aplicable:
- Ley 21/2013 de Evaluación Ambiental
- Directiva 2014/52/UE
""",
        # Add more as needed
    }
    return regulations.get(tipo_tramite, "")
```

## Prompt Construction

```python
def build_rag_prompt(user_question: str, expediente_id: int, retrieved_docs: list) -> str:
    doc_context = build_document_context(retrieved_docs)
    exp_context = build_expediente_context(expediente_id)
    reg_context = build_regulatory_context(?)  # Would need tipo_tramite
    
    prompt = f"""
You are a legal assistant for Spanish administrative processes.

{reg_context}

{exp_context}

{doc_context}

User Question: {user_question}

Provide a clear, actionable response in Spanish.
"""
    return prompt
```

## Generation with Context

```python
async def generate_with_rag(
    user_question: str,
    expediente_id: int,
    model: str = "mistral"
) -> dict:
    # Retrieve
    retrieved = retrieve_hybrid(user_question)
    
    # Augment
    prompt = build_rag_prompt(user_question, expediente_id, retrieved)
    
    # Generate
    response_text = await call_ollama(prompt, model)
    
    return {
        "response": response_text,
        "retrieved_documents": [
            {"id": d["id"], "nombre": d["nombre"], "similarity": d.get("score", 0)}
            for d in retrieved
        ]
    }
```

## Fallback Strategy

When no relevant documents found (similarity < 0.7):

```python
async def generate_with_fallback(user_question: str, expediente_id: int) -> dict:
    retrieved = retrieve_similar_documents(user_question)
    
    if not retrieved or max(d.get("similarity", 0) for d in retrieved) < 0.7:
        # No good matches: use generic prompt
        prompt = f"""
You are a legal assistant for Spanish administrative processes.

Question: {user_question}

Provide a general response based on standard administrative law.
"""
        confidence = "low"
    else:
        # Good matches: use RAG
        prompt = build_rag_prompt(user_question, expediente_id, retrieved)
        confidence = "high"
    
    response_text = await call_ollama(prompt)
    
    return {
        "response": response_text,
        "confidence": confidence,
        "retrieval_count": len(retrieved)
    }
```

## Performance Tuning

| Parameter | Value | Trade-off |
|-----------|-------|-----------|
| Vector similarity threshold | 0.7 | Higher = stricter relevance, fewer false positives |
| Top-k documents | 3 | More = richer context but longer prompts |
| Document content max | 500 chars | Smaller = shorter prompts, less context |
| Reranking | Top 5 → 3 | Expensive but improves quality |

## Testing

```python
def test_rag_retrieval():
    question = "How to get building permit?"
    docs = retrieve_hybrid(question)
    
    assert len(docs) > 0, "Should retrieve at least one document"
    assert docs[0]["score"] > docs[-1]["score"], "Should be sorted by score"

def test_rag_with_no_matches():
    question = "Irrelevant question xyz"
    docs = retrieve_hybrid(question)
    
    # Fallback should be triggered
    assert len(docs) == 0 or max(d["score"] for d in docs) < 0.5
```
