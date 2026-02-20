from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from typing import Optional

from ..models.expediente import Documento, Trazabilidad, Expediente

class SigningService:
    """Handles digital signatures for documents."""

    def __init__(self, db: Session):
        self.db = db

    def sign_document(self, document_id: int, signed_by: str, user_id: Optional[int] = None):
        """Generates a digital signature hash for the document and updates its status."""
        doc = self.db.query(Documento).filter(Documento.id == document_id).first()
        if not doc:
            raise ValueError("Document not found")

        # Simulate digital signature by hashing the document content (if exists) or metadata
        if doc.contenido_blob:
            content_to_hash = doc.contenido_blob
        else:
            # Fallback if no content exists yet (Phase 1 placeholder)
            content_to_hash = f"{doc.nombre}-{doc.expediente_id}-{datetime.now()}".encode()

        hash_obj = hashlib.sha256(content_to_hash)
        signature_hash = hash_obj.hexdigest()

        # Update document
        doc.hash_firma = signature_hash
        doc.firmado_por = signed_by
        doc.fecha_firma = datetime.now()

        # Log action in Audit Trail
        log = Trazabilidad(
            expediente_id=doc.expediente_id,
            user_id=user_id,
            accion="FIRMA_DOCUMENTO",
            descripcion=f"Documento '{doc.nombre}' firmado digitalmente por {signed_by}.",
            metadata_json=f'{{"hash": "{signature_hash}"}}'
        )
        self.db.add(log)
        
        self.db.commit()
        self.db.refresh(doc)
        return doc
