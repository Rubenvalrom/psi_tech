# Embedding Service (Generation & Batch Processing)

## Single Document Embedding

```python
import asyncio
import httpx
from typing import List

async def get_embedding(text: str, model: str = "nomic-embed-text") -> List[float]:
    """Generate embedding vector from Ollama."""
    
    url = "http://ollama:11434/api/embed"
    payload = {
        "model": model,
        "input": text
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        # Returns {"embeddings": [[...]]}
        embeddings = response.json()["embeddings"]
        return embeddings[0]  # First (and usually only) embedding


async def embed_document(documento_id: int, text: str, db):
    """Embed a document and store in pgvector."""
    
    embedding = await get_embedding(text)
    
    # Store in database
    query = """
    INSERT INTO document_embedding (documento_id, embedding, embedding_model)
    VALUES (:doc_id, :emb::vector, :model)
    ON CONFLICT (documento_id, embedding_model) 
    DO UPDATE SET embedding = EXCLUDED.embedding, updated_at = NOW()
    """
    
    db.execute(query, {
        "doc_id": documento_id,
        "emb": embedding,
        "model": "nomic-embed-text"
    })
    db.commit()
```

## Batch Embedding

```python
from typing import List, Tuple
import asyncio

async def embed_documents_batch(
    docs: List[Tuple[int, str]],  # [(id, text), ...]
    batch_size: int = 50,
    db = None
) -> int:
    """Embed multiple documents efficiently."""
    
    total_embedded = 0
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        
        tasks = [
            get_embedding(text) for _, text in batch
        ]
        
        embeddings = await asyncio.gather(*tasks)
        
        # Store all embeddings
        for (doc_id, text), embedding in zip(batch, embeddings):
            query = """
            INSERT INTO document_embedding (documento_id, embedding)
            VALUES (:doc_id, :emb::vector)
            ON CONFLICT (documento_id, embedding_model) 
            DO UPDATE SET embedding = EXCLUDED.embedding
            """
            
            db.execute(query, {
                "doc_id": doc_id,
                "emb": embedding
            })
        
        db.commit()
        total_embedded += len(batch)
        print(f"Embedded {total_embedded}/{len(docs)} documents")
    
    return total_embedded
```

## Incremental Update Strategy

```python
from datetime import datetime

async def embed_new_documents(db, model: str = "nomic-embed-text"):
    """Find and embed new documents."""
    
    # Find documents without embeddings
    query = """
    SELECT d.id, d.contenido_blob
    FROM documento d
    LEFT JOIN document_embedding de ON d.id = de.documento_id 
        AND de.embedding_model = :model
    WHERE de.id IS NULL
    AND d.contenido_blob IS NOT NULL
    ORDER BY d.fecha_carga DESC
    LIMIT 100
    """
    
    rows = db.execute(query, {"model": model}).fetchall()
    
    if not rows:
        print("No new documents to embed")
        return
    
    docs = [(row[0], row[1]) for row in rows]
    await embed_documents_batch(docs, db=db)
    print(f"Embedded {len(docs)} new documents")
```

## Scheduled Embedding

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def scheduled_embedding_job(db):
    """Background job to embed new documents every hour."""
    asyncio.run(embed_new_documents(db))

# Register job
scheduler.add_job(
    func=scheduled_embedding_job,
    args=(db,),
    trigger="interval",
    hours=1,
    id="embed_new_docs"
)

scheduler.start()
```

## Quality Control

```python
from sqlalchemy import func

def check_embedding_coverage(db) -> dict:
    """Check % of documents with embeddings."""
    
    total = db.query(func.count(Documento.id)).scalar()
    embedded = db.query(func.count(DocumentEmbedding.id)).scalar()
    
    coverage = (embedded / total * 100) if total > 0 else 0
    
    return {
        "total_documents": total,
        "embedded_documents": embedded,
        "coverage_percent": f"{coverage:.1f}",
        "pending": total - embedded
    }

# Usage
coverage = check_embedding_coverage(db)
print(f"Embedding coverage: {coverage['coverage_percent']}%")
```

## Error Handling

```python
import logging

logger = logging.getLogger(__name__)

async def embed_with_fallback(documento_id: int, text: str, db):
    """Embed with fallback on failure."""
    
    try:
        embedding = await get_embedding(text)
        # Store...
    except asyncio.TimeoutError:
        logger.warning(f"Embedding timeout for doc {documento_id}")
        # Skip this document, will retry next cycle
    except Exception as e:
        logger.error(f"Embedding failed for doc {documento_id}: {e}")
        # Mark as failed for manual review
        db.execute("""
            UPDATE documento SET embedding_status = 'failed'
            WHERE id = :id
        """, {"id": documento_id})
        db.commit()
```

## Performance Monitoring

```python
import time

async def embed_with_metrics(documents: List[Tuple[int, str]], db) -> dict:
    """Track embedding performance."""
    
    start_time = time.time()
    total_tokens = sum(len(text.split()) for _, text in documents)
    
    embedded = await embed_documents_batch(documents, db=db)
    
    elapsed = time.time() - start_time
    
    return {
        "documents_embedded": embedded,
        "total_tokens": total_tokens,
        "elapsed_seconds": f"{elapsed:.2f}",
        "tokens_per_second": f"{total_tokens / elapsed:.0f}"
    }
```
