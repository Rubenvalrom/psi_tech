# BPMN State Transitions

## State Machine Model

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Dict, List

class ExpedienteState(str, Enum):
    """Workflow states for expedientes (requests)"""
    INICIADO = "iniciado"
    VALIDADO = "validado"
    EVALUADO = "evaluado"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    NOTIFICADO = "notificado"
    ARCHIVADO = "archivado"


@dataclass
class Transition:
    """State transition definition"""
    from_state: ExpedienteState
    to_state: ExpedienteState
    condition: Callable[[Dict], bool] = None
    action: Callable = None
    
    async def can_transition(self, context: Dict) -> bool:
        """Check if transition is allowed"""
        if self.condition:
            return self.condition(context)
        return True


class StateMachine:
    """BPMN-like state machine"""
    
    def __init__(self):
        self.transitions: Dict[ExpedienteState, List[Transition]] = {}
        self._define_transitions()
    
    def _define_transitions(self):
        """Define valid state transitions"""
        
        self.transitions[ExpedienteState.INICIADO] = [
            Transition(
                from_state=ExpedienteState.INICIADO,
                to_state=ExpedienteState.VALIDADO,
                condition=lambda ctx: ctx.get("documentos_completos", False),
                action=self._on_validar
            )
        ]
        
        self.transitions[ExpedienteState.VALIDADO] = [
            Transition(
                from_state=ExpedienteState.VALIDADO,
                to_state=ExpedienteState.EVALUADO,
                action=self._on_evaluar
            )
        ]
        
        self.transitions[ExpedienteState.EVALUADO] = [
            Transition(
                from_state=ExpedienteState.EVALUADO,
                to_state=ExpedienteState.APROBADO,
                condition=lambda ctx: ctx.get("score", 0) >= 70,
                action=self._on_aprobar
            ),
            Transition(
                from_state=ExpedienteState.EVALUADO,
                to_state=ExpedienteState.RECHAZADO,
                condition=lambda ctx: ctx.get("score", 0) < 70,
                action=self._on_rechazar
            )
        ]
        
        self.transitions[ExpedienteState.APROBADO] = [
            Transition(
                from_state=ExpedienteState.APROBADO,
                to_state=ExpedienteState.NOTIFICADO,
                action=self._on_notificar
            )
        ]
        
        self.transitions[ExpedienteState.RECHAZADO] = [
            Transition(
                from_state=ExpedienteState.RECHAZADO,
                to_state=ExpedienteState.INICIADO,
                action=self._on_reiniciar
            ),
            Transition(
                from_state=ExpedienteState.RECHAZADO,
                to_state=ExpedienteState.ARCHIVADO,
                action=self._on_archivar
            )
        ]
        
        self.transitions[ExpedienteState.NOTIFICADO] = [
            Transition(
                from_state=ExpedienteState.NOTIFICADO,
                to_state=ExpedienteState.ARCHIVADO,
                action=self._on_archivar
            )
        ]
    
    async def transition(
        self,
        from_state: ExpedienteState,
        to_state: ExpedienteState,
        context: Dict
    ) -> bool:
        """Execute state transition"""
        
        valid_transitions = self.transitions.get(from_state, [])
        target_transition = None
        
        for t in valid_transitions:
            if t.to_state == to_state:
                if await t.can_transition(context):
                    target_transition = t
                    break
        
        if not target_transition:
            return False
        
        # Execute action
        if target_transition.action:
            await target_transition.action(context)
        
        return True
    
    async def _on_validar(self, context: Dict):
        """Action on validation"""
        print(f"Validating expediente {context.get('id')}")
    
    async def _on_evaluar(self, context: Dict):
        """Action on evaluation"""
        print(f"Evaluating expediente {context.get('id')}")
    
    async def _on_aprobar(self, context: Dict):
        """Action on approval"""
        print(f"Approving expediente {context.get('id')}")
    
    async def _on_rechazar(self, context: Dict):
        """Action on rejection"""
        print(f"Rejecting expediente {context.get('id')}")
    
    async def _on_notificar(self, context: Dict):
        """Action on notification"""
        print(f"Notifying user for expediente {context.get('id')}")
    
    async def _on_reiniciar(self, context: Dict):
        """Action on restart"""
        print(f"Restarting expediente {context.get('id')}")
    
    async def _on_archivar(self, context: Dict):
        """Action on archiving"""
        print(f"Archiving expediente {context.get('id')}")
```

## Workflow Definition as JSON

```json
{
  "id": "tramite-solicitud",
  "name": "Trámite de Solicitud",
  "version": "1.0",
  "states": [
    {
      "id": "iniciado",
      "type": "start",
      "label": "Iniciado"
    },
    {
      "id": "validado",
      "type": "process",
      "label": "Validado",
      "action": "validar_documentos"
    },
    {
      "id": "evaluado",
      "type": "process",
      "label": "Evaluado",
      "action": "evaluar_solicitud"
    },
    {
      "id": "aprobado",
      "type": "decision",
      "label": "Aprobado"
    },
    {
      "id": "rechazado",
      "type": "decision",
      "label": "Rechazado"
    },
    {
      "id": "notificado",
      "type": "process",
      "label": "Notificado",
      "action": "enviar_notificacion"
    },
    {
      "id": "archivado",
      "type": "end",
      "label": "Archivado"
    }
  ],
  "transitions": [
    {
      "from": "iniciado",
      "to": "validado",
      "condition": "documentos_completos == true"
    },
    {
      "from": "validado",
      "to": "evaluado"
    },
    {
      "from": "evaluado",
      "to": "aprobado",
      "condition": "score >= 70"
    },
    {
      "from": "evaluado",
      "to": "rechazado",
      "condition": "score < 70"
    },
    {
      "from": "aprobado",
      "to": "notificado"
    },
    {
      "from": "rechazado",
      "to": "iniciado"
    },
    {
      "from": "notificado",
      "to": "archivado"
    }
  ]
}
```

## Using State Transitions in FastAPI

```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()
state_machine = StateMachine()


@router.post("/expedientes/{id}/transition")
async def transition_state(
    id: int,
    new_state: str,
    db: AsyncSession = Depends(get_db)
):
    """Transition expediente to new state"""
    
    expediente = await get_expediente(db, id)
    if not expediente:
        raise HTTPException(status_code=404, detail="Not found")
    
    current_state = ExpedienteState(expediente.estado)
    target_state = ExpedienteState(new_state)
    
    context = {
        "id": id,
        "documentos_completos": expediente.documentos_completos,
        "score": expediente.evaluation_score
    }
    
    success = await state_machine.transition(
        current_state,
        target_state,
        context
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current_state} to {target_state}"
        )
    
    expediente.estado = new_state
    await db.commit()
    
    return {"status": "success", "new_state": new_state}
```
