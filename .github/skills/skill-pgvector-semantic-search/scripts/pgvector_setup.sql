-- PostgreSQL pgvector setup script
-- Run: psql -U postgres -h localhost -f pgvector_setup.sql

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable tsvector for full-text search (hybrid search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Main embedding table
CREATE TABLE IF NOT EXISTS document_embedding (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL,
    embedding vector(1536) NOT NULL,
    embedding_model VARCHAR(50) DEFAULT 'nomic-embed-text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (documento_id) REFERENCES documento(id) ON DELETE CASCADE,
    UNIQUE(documento_id, embedding_model)
);

-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_document_embedding_hnsw 
ON document_embedding USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- Timestamp index for incremental updates
CREATE INDEX IF NOT EXISTS idx_document_embedding_created 
ON document_embedding(created_at DESC);

-- Optional: expediente context embedding cache
CREATE TABLE IF NOT EXISTS expediente_context_embedding (
    id SERIAL PRIMARY KEY,
    expediente_id INTEGER NOT NULL,
    context_type VARCHAR(50) DEFAULT 'full_context',
    embedding vector(1536),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (expediente_id) REFERENCES expediente(id) ON DELETE CASCADE,
    UNIQUE(expediente_id, context_type)
);

CREATE INDEX IF NOT EXISTS idx_expediente_context_hnsw 
ON expediente_context_embedding USING hnsw (embedding vector_cosine_ops);

-- Metadata for embeddings (optional, for monitoring)
CREATE TABLE IF NOT EXISTS embedding_metadata (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL,
    text_length INTEGER,
    text_preview VARCHAR(200),
    embedding_timestamp TIMESTAMP,
    embedding_latency_ms FLOAT,
    
    FOREIGN KEY (documento_id) REFERENCES documento(id) ON DELETE CASCADE
);

-- Grant permissions
-- (Adjust user as needed)
-- GRANT SELECT, INSERT, UPDATE ON document_embedding TO app_user;
-- GRANT SELECT ON expediente_context_embedding TO app_user;

-- Verify setup
SELECT 
    'pgvector enabled' as status
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'document_embedding');

-- Show table structure
-- \d document_embedding
-- \d expediente_context_embedding
