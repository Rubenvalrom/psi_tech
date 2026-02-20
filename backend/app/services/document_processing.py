import io
import logging
from typing import Optional, Dict, Any
from pypdf import PdfReader
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..models.expediente import Documento, Trazabilidad, Expediente
from .ollama_service import OllamaService

logger = logging.getLogger(__name__)

class DocumentProcessingService:
    """Handles text extraction and automated metadata extraction via LLM."""

    def __init__(self, db: Session):
        self.db = db
        self.ollama = OllamaService()

    def process_pdf_content(self, document_id: int, user_id: int) -> Dict[str, Any]:
        """
        Extracts text from a PDF document and runs LLM analysis.
        Updates the document record with metadata.
        """
        doc = self.db.query(Documento).filter(Documento.id == document_id).first()
        if not doc:
            raise ValueError("Document not found")

        if not doc.contenido_blob:
            logger.warning(f"Document {document_id} has no content blob.")
            return {"error": "No content to process"}

        try:
            # 1. Extract text from PDF
            logger.info(f"Extracting text from document {document_id} ({doc.nombre})...")
            text = self._extract_text_from_pdf(doc.contenido_blob)
            
            if not text:
                logger.warning(f"No text extracted from document {document_id}.")
                return {"error": "Failed to extract text"}

            # 2. Analyze text via Ollama
            logger.info(f"Analyzing text with LLM for document {document_id}...")
            metadata = self.ollama.analyze_document_text(text)
            
            # 2b. Generate Embedding for Phase 5
            logger.info(f"Generating embedding for document {document_id}...")
            embedding = self.ollama.generate_embedding(text)
            if embedding:
                doc.embedding = embedding

            # 3. Update document metadata
            doc.metadatos_extraidos = json.dumps(metadata)
            
            # Log action in Audit Trail
            self._log_action(doc.expediente_id, user_id, "IA_ANALYSIS_COMPLETED", 
                            f"Análisis IA completado para '{doc.nombre}'.", 
                            {"metadata": metadata})

            self.db.commit()
            return metadata

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            return {"error": str(e)}

    def _extract_text_from_pdf(self, content_blob: bytes) -> str:
        """Helper to extract text from PDF using pypdf."""
        try:
            reader = PdfReader(io.BytesIO(content_blob))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""

    def _log_action(self, expediente_id: int, user_id: int, action: str, description: str, metadata: dict):
        """Log event to audit trail."""
        log = Trazabilidad(
            expediente_id=expediente_id,
            user_id=user_id,
            accion=action,
            descripcion=description,
            metadata_json=json.dumps(metadata)
        )
        self.db.add(log)
