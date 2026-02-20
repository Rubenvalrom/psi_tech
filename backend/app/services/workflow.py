from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import json

from ..models.expediente import Expediente, PasoTramitacion, EstadoPaso, EstadoExpediente, Trazabilidad

class WorkflowService:
    """Orchestrates the state transitions and step execution of an expediente."""

    def __init__(self, db: Session):
        self.db = db

    def log_action(self, expediente_id: int, action: str, description: str, user_id: Optional[int] = None, metadata_dict: Optional[dict] = None):
        """Creates an audit trail entry."""
        log = Trazabilidad(
            expediente_id=expediente_id,
            user_id=user_id,
            accion=action,
            descripcion=description,
            metadata_json=json.dumps(metadata_dict) if metadata_dict else None
        )
        self.db.add(log)
        self.db.commit()

    def complete_step(self, expediente_id: int, paso_id: int, user_id: int, comments: Optional[str] = None):
        """Completes the current step and determines the next step in the workflow."""
        paso = self.db.query(PasoTramitacion).filter(
            PasoTramitacion.id == paso_id,
            PasoTramitacion.expediente_id == expediente_id
        ).first()

        if not paso:
            raise ValueError("Paso not found")

        if paso.estado == EstadoPaso.COMPLETADO:
            return paso

        # Update current step
        paso.estado = EstadoPaso.COMPLETADO
        paso.datetime_fin = datetime.now()
        paso.responsable_id = user_id
        paso.comentarios = comments
        
        # Log action
        self.log_action(
            expediente_id=expediente_id,
            user_id=user_id,
            action="PASO_COMPLETADO",
            description=f"Paso '{paso.titulo}' marcado como completado.",
            metadata_dict={"paso_id": paso_id, "numero_paso": paso.numero_paso}
        )

        # Check for next step or close expediente
        self._progress_workflow(expediente_id, user_id)
        
        self.db.commit()
        self.db.refresh(paso)
        return paso

    def _progress_workflow(self, expediente_id: int, user_id: int):
        """Logic to advance to the next step or close the expediente."""
        expediente = self.db.query(Expediente).filter(Expediente.id == expediente_id).first()
        
        # Current logic: Simple sequential steps
        # In a real BPMN this would check the next definition
        
        # Check if all steps are completed
        pending_steps = self.db.query(PasoTramitacion).filter(
            PasoTramitacion.expediente_id == expediente_id,
            PasoTramitacion.estado != EstadoPaso.COMPLETADO
        ).count()

        if pending_steps == 0:
            expediente.estado = EstadoExpediente.CERRADO
            expediente.fecha_cierre = datetime.now()
            self.log_action(
                expediente_id=expediente_id,
                user_id=user_id,
                action="EXPEDIENTE_CERRADO",
                description="Todos los pasos completados. Expediente cerrado automáticamente."
            )
        else:
            expediente.estado = EstadoExpediente.EN_PROCESO
            
    def start_workflow(self, expediente_id: int, user_id: int):
        """Initialize the first step of an expediente."""
        expediente = self.db.query(Expediente).filter(Expediente.id == expediente_id).first()
        expediente.estado = EstadoExpediente.EN_PROCESO
        
        self.log_action(
            expediente_id=expediente_id,
            user_id=user_id,
            action="WORKFLOW_INICIADO",
            description="Tramitación iniciada."
        )
        self.db.commit()
