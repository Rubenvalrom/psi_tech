"""Expediente CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.expediente import Expediente, EstadoExpediente, PasoTramitacion, EstadoPaso, Trazabilidad, Documento
from ..models.user import User
from ..schemas.expediente import (
    ExpedienteCreate,
    ExpedienteUpdate,
    ExpedienteRead,
    ExpedientePaginatedResponse,
    PasoTramitacionCreate,
    PasoTramitacionRead,
    TrazabilidadRead,
    DocumentoSign,
    DocumentoRead,
)
from ..services.workflow import WorkflowService
from ..services.signing import SigningService
from ..services.document_processing import DocumentProcessingService


router = APIRouter(prefix="/expedientes", tags=["expedientes"])

# Constants for file validation
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_CONTENT_TYPES = ["application/pdf", "image/jpeg", "image/png", "application/msword",
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]


@router.post("/{expediente_id}/documentos", response_model=DocumentoRead)
async def upload_documento(
    expediente_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document to an expediente and trigger IA analysis."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")

    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Read file content with size validation
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Create document record
    db_documento = Documento(
        expediente_id=expediente_id,
        nombre=file.filename,
        contenido_blob=file_content,
        tipo="ADJUNTO" # Default type, IA can override this
    )
    db.add(db_documento)
    db.commit()
    db.refresh(db_documento)

    # Trigger background analysis
    doc_service = DocumentProcessingService(db)
    background_tasks.add_task(
        doc_service.process_pdf_content, db_documento.id, current_user.id
    )

    return db_documento


@router.post("", response_model=ExpedienteRead, status_code=201)
async def create_expediente(
    expediente: ExpedienteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new expediente (case file)."""
    # Check if numero is already used
    existing = db.query(Expediente).filter(Expediente.numero == expediente.numero).first()
    if existing:
        raise HTTPException(status_code=400, detail="Expediente numero already exists")

    exp_data = expediente.dict()
    if not exp_data.get("responsable_id"):
        exp_data["responsable_id"] = current_user.id

    db_expediente = Expediente(**exp_data)
    db.add(db_expediente)
    db.commit()
    db.refresh(db_expediente)
    return db_expediente


@router.get("", response_model=ExpedientePaginatedResponse)
async def list_expedientes(
    split: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List expedientes with pagination and optional filtering."""
    query = db.query(Expediente)

    # Filter by state if provided
    if estado:
        try:
            estado_enum = EstadoExpediente(estado)
            query = query.filter(Expediente.estado == estado_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid estado: {estado}")

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    items = query.order_by(desc(Expediente.fecha_creacion)).offset(split).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "skip": split,
        "limit": limit,
    }


@router.get("/{expediente_id}", response_model=ExpedienteRead)
async def get_expediente(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific expediente by ID."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")
    return expediente


@router.put("/{expediente_id}", response_model=ExpedienteRead)
async def update_expediente(
    expediente_id: int,
    expediente_update: ExpedienteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an expediente."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")

    # Update fields provided
    update_data = expediente_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(expediente, key, value)

    db.add(expediente)
    db.commit()
    db.refresh(expediente)
    return expediente


@router.post("/{expediente_id}/pasos", response_model=PasoTramitacionRead, status_code=201)
async def create_paso(
    expediente_id: int,
    paso: PasoTramitacionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new step (paso) to the expediente workflow."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")

    db_paso = PasoTramitacion(expediente_id=expediente_id, **paso.dict())
    db.add(db_paso)
    db.commit()
    db.refresh(db_paso)
    return db_paso


@router.get("/{expediente_id}/pasos", response_model=List[PasoTramitacionRead])
async def list_pasos(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all steps (pasos) for an expediente."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente not found")

    pasos = db.query(PasoTramitacion).filter(
        PasoTramitacion.expediente_id == expediente_id
    ).order_by(PasoTramitacion.numero_paso).all()

    return pasos


@router.post("/{expediente_id}/start", response_model=ExpedienteRead)
async def start_workflow(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start the workflow for an expediente."""
    service = WorkflowService(db)
    service.start_workflow(expediente_id, current_user.id)
    
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    return expediente


@router.post("/{expediente_id}/pasos/{paso_id}/complete", response_model=PasoTramitacionRead)
async def complete_paso(
    expediente_id: int,
    paso_id: int,
    comentarios: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a workflow step."""
    service = WorkflowService(db)
    try:
        return service.complete_step(expediente_id, paso_id, current_user.id, comentarios)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/documentos/{documento_id}/sign", response_model=DocumentoRead)
async def sign_documento(
    documento_id: int,
    firma: DocumentoSign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sign a document digitaly."""
    service = SigningService(db)
    try:
        # Use signed_by from payload if present, else fallback to current_user.nombre_completo
        signer_name = firma.firmado_por if firma.firmado_por else current_user.nombre_completo
        return service.sign_document(documento_id, signer_name, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{expediente_id}/trazabilidad", response_model=List[TrazabilidadRead])
async def list_trazabilidad(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit trail for an expediente."""
    return db.query(Trazabilidad).filter(
        Trazabilidad.expediente_id == expediente_id
    ).order_by(desc(Trazabilidad.timestamp)).all()
