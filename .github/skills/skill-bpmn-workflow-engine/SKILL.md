---
name: skill-bpmn-workflow-engine
description: Implement lightweight BPMN workflow orchestration for government procedures (tramitaciones). Includes state machine patterns, step execution logic, event handling, and persistence. Use when building process automation that requires sequential steps, conditional branching, and state tracking without heavy frameworks like Camunda.
---

# BPMN Workflow Engine (Lightweight)

## Quick Start

```python
from app.bpmn.engine import WorkflowEngine

# Define workflow
workflow_def = {
    "id": "licencia_construccion",
    "name": "Licencia de Construcción",
    "pasos": [
        {
            "id": "paso_1",
            "nombre": "Validación Inicial",
            "tipo": "validacion",
            "siguiente": "paso_2"
        },
        {
            "id": "paso_2",
            "nombre": "Evaluación Técnica",
            "tipo": "evaluacion",
            "siguiente": "paso_3"
        },
        {
            "id": "paso_3",
            "nombre": "Aprobación",
            "tipo": "aprobacion",
            "siguiente": None
        }
    ]
}

# Execute
engine = WorkflowEngine(db)
engine.start_workflow(expediente_id=123, workflow_def=workflow_def)
engine.move_to_next_step(expediente_id=123)
```

## Architecture

See [references/workflow-definition.md](references/workflow-definition.md):
- JSON-based workflow definitions
- Step types: validacion, evaluacion, aprobacion, notificacion
- Conditional logic (if/then branches)

See [references/step-execution.md](references/step-execution.md):
- Execute step handlers (validation, approval)
- Event hooks (on_enter, on_exit)
- Persistence to database

See [references/state-transitions.md](references/state-transitions.md):
- Validate state transitions
- Prevent invalid step sequences
- Rollback on error

## Scripts

**Run workflow simulation**:
```bash
python scripts/workflow_engine.py --workflow licencia_construccion --simulate
```

**Test workflows**:
```bash
pytest scripts/test_workflows.py -v
```
