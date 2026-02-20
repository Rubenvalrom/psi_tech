# Embedding Schema Design

## Core Tables

```sql
-- Main embedding storage
CREATE TABLE document_embedding (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL,
    embedding vector(1536) NOT NULL,  -- Dimension from nomic-embed-text
    embedding_model VARCHAR(50) DEFAULT 'nomic-embed-text',
    embedding_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (documento_id) REFERENCES documento(id) ON DELETE CASCADE,
    UNIQUE(documento_id, embedding_model)
);

-- Index for fast similarity search
CREATE INDEX idx_document_embedding_hnsw 
ON document_embedding USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- Additional index for timestamp queries
CREATE INDEX idx_document_embedding_created 
ON document_embedding(created_at DESC);

-- Expediente-level embedding cache (optional)
CREATE TABLE expediente_context_embedding (
    id SERIAL PRIMARY KEY,
    expediente_id INTEGER NOT NULL,
    context_text TEXT,
    embedding vector(1536),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (expediente_id) REFERENCES expediente(id) ON DELETE CASCADE,
    UNIQUE(expediente_id)
);
```

## Embedding Strategies

### Document-Level Embeddings

**When**: Each document = one embedding (PDF abstract, OCR text, etc.)

```sql
INSERT INTO document_embedding (documento_id, embedding, embedding_model)
VALUES (123, :'embedding_vector'::vector, 'nomic-embed-text');
```

### Chunked Embeddings

For long documents, split into chunks:

```sql
CREATE TABLE document_chunk (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL,
    chunk_index INTEGER,
    chunk_text TEXT,
    chunk_length INTEGER,
    
    FOREIGN KEY (documento_id) REFERENCES documento(id)
);

CREATE TABLE chunk_embedding (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL,
    embedding vector(1536),
    
    FOREIGN KEY (chunk_id) REFERENCES document_chunk(id) ON DELETE CASCADE
);

-- Create index on chunk embeddings
CREATE INDEX idx_chunk_embedding_hnsw 
ON chunk_embedding USING hnsw (embedding vector_cosine_ops);
```

## Index Configuration

### HNSW Index (Recommended for MVP)

Fast approximate nearest neighbor search:

```sql
CREATE INDEX idx_fast_search 
ON document_embedding USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,              -- Number of connections per node
    ef_construction = 200 -- Construction parameter (higher = better quality, slower)
);
```

**Parameters**:
- `m = 16`: Good balance (8-32 typical)
- `ef_construction = 200`: Quality (100-500)
- Trade-off: Higher = slower index creation, faster queries

### IVFFlat Index (Alternative)

If HNSW becomes too slow to build:

```sql
CREATE INDEX idx_ivf_search 
ON document_embedding USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- Number of clusters
```

## Query Performance

Typical query times (10M vectors, 1536-dim):

| Index Type | Build Time | Query Time | Memory |
|-----------|-----------|-----------|--------|
| HNSW (m=16) | ~5 min | 10-50ms | 8-10x vector size |
| IVFFlat | ~1 min | 50-200ms | 1.5x vector size |
| Exact (IVFFLAT 1) | N/A | 1-5s | 1x vector size |

For Olympus (estimated 10K-100K documents):
- HNSW: ~1-2 min build, ~10-20ms query → **Choose this**
- IVFFlat: ~30s build, ~50-100ms query
- Exact: unacceptable for UX

## Maintenance

```sql
-- Analyze table for query planner
ANALYZE document_embedding;

-- Reindex if queries slow down (every 3-6 months)
REINDEX INDEX idx_document_embedding_hnsw;

-- Check index size
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'document_embedding';
```
