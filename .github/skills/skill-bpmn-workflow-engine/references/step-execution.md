# Step Execution Logic

## Execute Single Step

```python
from typing import Dict, Any

class StepExecutor:
    def __init__(self, db, handlers: Dict[str, callable]):
        self.db = db
        self.handlers = handlers
    
    async def execute_step(self, expediente_id: int, step: Dict[str, Any]):
        # On enter hook
        await self._emit_event("on_enter", expediente_id, step["id"])
        
        try:
            # Execute handler if exists
            if step["tipo"] in self.handlers:
                handler = self.handlers[step["tipo"]]
                result = await handler(expediente_id, step)
                
                # Save result
                self.db.query(PasoTramitacion).filter(
                    PasoTramitacion.expediente_id == expediente_id,
                    PasoTramitacion.numero_paso == step["numero"]
                ).update({"resultado": result})
            
            # On exit hook
            await self._emit_event("on_exit", expediente_id, step["id"])
            
            return True
        
        except Exception as e:
            await self._emit_event("on_error", expediente_id, step["id"], str(e))
            raise

# Register handlers
handlers = {
    "validacion": validate_documentos,
    "sistema": sistema_handler,
    "notificacion": send_notification
}
executor = StepExecutor(db, handlers)
```

## Event Hooks

```python
async def _emit_event(self, event_type: str, expediente_id: int, step_id: str, data: str = None):
    audit_log = AuditLog(
        expediente_id=expediente_id,
        step_id=step_id,
        event_type=event_type,
        data=data,
        timestamp=datetime.utcnow()
    )
    self.db.add(audit_log)
    self.db.commit()
```
