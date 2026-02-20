# Similarity Queries & Semantic Search

## Basic Similarity Search

```python
from sqlalchemy import text, func
from typing import List, Dict

def search_similar_documents(
    query_embedding: List[float],
    limit: int = 5,
    similarity_threshold: float = 0.7,
    db = None
) -> List[Dict]:
    """Find documents similar to query embedding."""
    
    sql = text("""
    SELECT 
        de.id,
        de.documento_id,
        d.nombre,
        d.tipo,
        1 - (de.embedding <=> :query_vec::vector) as similarity,
        d.fecha_carga
    FROM document_embedding de
    JOIN documento d ON de.documento_id = d.id
    WHERE 1 - (de.embedding <=> :query_vec::vector) > :threshold
    ORDER BY similarity DESC
    LIMIT :limit
    """)
    
    results = db.execute(sql, {
        "query_vec": query_embedding,
        "threshold": similarity_threshold,
        "limit": limit
    }).fetchall()
    
    return [
        {
            "id": row[0],
            "documento_id": row[1],
            "nombre": row[2],
            "tipo": row[3],
            "similarity": float(row[4]),
            "fecha_carga": row[5]
        }
        for row in results
    ]
```

## Vector Distance Metrics

PostgreSQL pgvector supports multiple distance operators:

```sql
-- Cosine distance (recommended for text embeddings)
SELECT 1 - (embedding <=> query_vec) as cosine_similarity
FROM document_embedding;

-- L2 (Euclidean) distance
SELECT embedding <-> query_vec as l2_distance
FROM document_embedding
ORDER BY embedding <-> query_vec
LIMIT 5;

-- Inner product (dot product)
-- Rarely used for similarity; used for ranking
SELECT - (embedding <#> query_vec) as inner_product
FROM document_embedding
ORDER BY embedding <#> query_vec DESC
LIMIT 5;
```

**For Olympus**: Use cosine similarity (`<=>`) for text documents.

## Context-Aware Retrieval

```python
def search_by_expediente_type(
    query_embedding: List[float],
    tipo_tramite: str,
    limit: int = 5,
    db = None
) -> List[Dict]:
    """Find similar documents within specific procedure type."""
    
    sql = text("""
    SELECT 
        d.id,
        d.nombre,
        1 - (de.embedding <=> :query_vec::vector) as similarity
    FROM document_embedding de
    JOIN documento d ON de.documento_id = d.id
    JOIN expediente exp ON d.expediente_id = exp.id
    WHERE exp.tipo_tramite = :tipo
    AND 1 - (de.embedding <=> :query_vec::vector) > 0.6
    ORDER BY similarity DESC, d.fecha_carga DESC
    LIMIT :limit
    """)
    
    return db.execute(sql, {
        "query_vec": query_embedding,
        "tipo": tipo_tramite,
        "limit": limit
    }).fetchall()
```

## Hybrid Search (Vector + Keyword)

```python
def search_hybrid(
    query_text: str,
    query_embedding: List[float],
    limit: int = 5,
    db = None
) -> List[Dict]:
    """Combine semantic (vector) and keyword (BM25) search."""
    
    sql = text("""
    WITH vector_search AS (
        SELECT 
            d.id,
            d.nombre,
            1 - (de.embedding <=> :query_vec::vector) as vector_sim
        FROM document_embedding de
        JOIN documento d ON de.documento_id = d.id
        WHERE 1 - (de.embedding <=> :query_vec::vector) > 0.6
    ),
    keyword_search AS (
        SELECT 
            d.id,
            d.nombre,
            ts_rank_cd(
                to_tsvector('spanish', d.contenido), 
                plainto_tsquery('spanish', :keyword)
            ) / 32.0 as keyword_rank  -- Normalize to 0-1
        FROM documento d
        WHERE to_tsvector('spanish', d.contenido) @@ 
              plainto_tsquery('spanish', :keyword)
    )
    SELECT 
        COALESCE(vs.id, ks.id) as id,
        COALESCE(vs.nombre, ks.nombre) as nombre,
        COALESCE(vs.vector_sim, 0) as vector_sim,
        COALESCE(ks.keyword_rank, 0) as keyword_rank,
        0.7 * COALESCE(vs.vector_sim, 0) + 
        0.3 * COALESCE(ks.keyword_rank, 0) as combined_score
    FROM vector_search vs
    FULL OUTER JOIN keyword_search ks ON vs.id = ks.id
    ORDER BY combined_score DESC
    LIMIT :limit
    """)
    
    return db.execute(sql, {
        "query_vec": query_embedding,
        "keyword": query_text,
        "limit": limit
    }).fetchall()
```

## Clustering Similar Documents

```python
def cluster_similar_documents(
    documento_id: int,
    similarity_threshold: float = 0.8,
    db = None
) -> Dict:
    """Find all documents in same cluster (highly similar)."""
    
    sql = text("""
    WITH target as (
        SELECT embedding FROM document_embedding
        WHERE documento_id = :doc_id
    )
    SELECT 
        d.id,
        d.nombre,
        1 - (de.embedding <=> target.embedding) as similarity
    FROM document_embedding de
    JOIN documento d ON de.documento_id = d.id
    CROSS JOIN target
    WHERE 1 - (de.embedding <=> target.embedding) > :threshold
    AND d.id != :doc_id
    ORDER BY similarity DESC
    """)
    
    return db.execute(sql, {
        "doc_id": documento_id,
        "threshold": similarity_threshold
    }).fetchall()
```

## Performance Optimization

```python
def search_with_explain(
    query_embedding: List[float],
    db = None
):
    """Analyze query execution plan."""
    
    sql = text("""
    EXPLAIN ANALYZE
    SELECT 1 - (embedding <=> :query_vec::vector) as sim
    FROM document_embedding
    ORDER BY embedding <=> :query_vec::vector
    LIMIT 10
    """)
    
    plan = db.execute(sql, {"query_vec": query_embedding}).fetchall()
    
    # Should show HNSW index scan
    for line in plan:
        print(line)
```

Expect output like:
```
Index Scan using idx_document_embedding_hnsw on document_embedding (cost=...)
  Index Cond: (embedding <=> ...)
  -> Limit  (cost=0.27..27.75 rows=10)
```

Good sign: Uses HNSW index, fast cost.

## Common Patterns

### "More Like This"

```python
def find_similar_to_expediente(
    expediente_id: int,
    limit: int = 5,
    db = None
) -> List[Dict]:
    """Find other expedientes similar to this one."""
    
    # Get average embedding of all docs in expediente
    sql = text("""
    WITH target_embedding AS (
        SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY embedding) as median_emb
        FROM document_embedding de
        JOIN documento d ON de.documento_id = d.id
        WHERE d.expediente_id = :exp_id
    ),
    similar as (
        SELECT 
            DISTINCT e.id,
            e.numero,
            e.asunto,
            1 - (de.embedding <=> te.median_emb) as similarity
        FROM document_embedding de
        JOIN documento d ON de.documento_id = d.id
        JOIN expediente e ON d.expediente_id = e.id
        CROSS JOIN target_embedding te
        WHERE e.id != :exp_id
        AND 1 - (de.embedding <=> te.median_emb) > 0.7
    )
    SELECT * FROM similar
    ORDER BY similarity DESC
    LIMIT :limit
    """)
    
    return db.execute(sql, {"exp_id": expediente_id, "limit": limit}).fetchall()
```
