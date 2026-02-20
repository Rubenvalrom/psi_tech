---
name: skill-pgvector-semantic-search
description: Implement vector semantic search using PostgreSQL pgvector extension. Includes schemas for storing embeddings (Ollama-generated), similarity queries (cosine distance), indexing strategies (HNSW), and RAG integration patterns. Use when building semantic search, document retrieval, or recommendation systems that require fast approximate nearest neighbor queries on high-dimensional vectors.
---

# PostgreSQL pgvector Semantic Search

## Quick Start

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for embeddings
CREATE TABLE document_embedding (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documento(id),
    embedding vector(1536),
    similarity_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for fast search
CREATE INDEX ON document_embedding USING hnsw (embedding vector_cosine_ops);
```

## Core Patterns

See [references/schema-vectors.md](references/schema-vectors.md):
- Table design for embeddings (1536-dim vectors from nomic-embed-text)
- Index strategies (HNSW for approximate search, slower but memory-efficient)

See [references/embedding-service.md](references/embedding-service.md):
- Generate embeddings via Ollama's nomic-embed-text model
- Batch processing for bulk document embedding
- Update strategy (incremental on new docs)

See [references/similarity-queries.md](references/similarity-queries.md):
- Cosine similarity search: `1 - (vec1 <=> vec2)`
- Top-K retrieval: `ORDER BY similarity DESC LIMIT k`
- Threshold filtering: `WHERE similarity > 0.7`

## Scripts

**Setup schema**:
```bash
psql -U postgres -h localhost -f scripts/pgvector_setup.sql
```

**Embed documents**:
```bash
python scripts/embedding_service.py --batch-size 50
```

**Test queries**:
```bash
pytest scripts/test_vectors.py -v
```

## Decisions

- **Vector dimension**: 1536 (nomic-embed-text output)
- **Similarity metric**: Cosine distance (best for text embeddings)
- **Index type**: HNSW (faster queries, ~90% recall at 10x speed vs. exact)
- **Batch size**: 50 documents (balance memory vs. throughput)
