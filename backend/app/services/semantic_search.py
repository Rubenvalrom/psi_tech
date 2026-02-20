from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List, Dict, Any, Optional
import json
import logging

from ..models.expediente import Documento, Expediente
from .ollama_service import OllamaService

logger = logging.getLogger(__name__)

class SemanticSearchService:
    """Handles semantic search and RAG (Retrieval-Augmented Generation)."""

    def __init__(self, db: Session):
        self.db = db
        self.ollama = OllamaService()

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic search in pgvector.
        Returns the top results with similarity scores.
        """
        query_embedding = self.ollama.generate_embedding(query)
        if not query_embedding:
            logger.error("Failed to generate query embedding.")
            return []

        # pgvector cosine distance: embedding <=> query_embedding
        # Sorting by distance (ascending) gives most similar results.
        results = (
            self.db.query(Documento)
            .order_by(Documento.embedding.cosine_distance(query_embedding))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": doc.id,
                "nombre": doc.nombre,
                "expediente_id": doc.expediente_id,
                "tipo": doc.tipo,
                "metadatos": json.loads(doc.metadatos_extraidos) if doc.metadatos_extraidos else {}
            }
            for doc in results
        ]

    def ask_assistant(self, question: str) -> Dict[str, Any]:
        """
        RAG workflow:
        1. Search semantically for relevant fragments.
        2. Build prompt with context.
        3. Get response from LLM.
        """
        # 1. Retrieve relevant context
        docs = self.search_documents(question, limit=3)
        context_str = "\n".join([
            f"Documento: {doc['nombre']} (Expediente ID: {doc['expediente_id']})\n"
            f"Tipo: {doc['tipo']}\n"
            f"Resumen Extraído: {doc['metadatos'].get('resumen', 'N/A')}"
            for doc in docs
        ])

        # 2. Construct RAG prompt
        prompt = f"""
        Eres un asistente inteligente para la administración pública (Olympus Smart Gov).
        Utiliza el siguiente contexto para responder a la pregunta de forma precisa y servicial.
        Si la información no está en el contexto, indícalo educadamente.

        CONTEXTO:
        ---
        {context_str}
        ---

        PREGUNTA: {question}

        Respuesta detallada:
        """

        # 3. Generate response with Ollama
        try:
            import requests
            import os
            OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
            OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=90
            )
            
            if response.status_code != 200:
                logger.error(f"RAG LLM error: {response.status_code}")
                return {"answer": "Lo siento, hubo un error al consultar el asistente.", "sources": docs}

            result = response.json()
            return {
                "answer": result.get("response", ""),
                "sources": docs
            }

        except Exception as e:
            logger.error(f"Error in RAG Assistant: {e}")
            return {"answer": "Error al procesar la solicitud con el asistente.", "sources": docs}
