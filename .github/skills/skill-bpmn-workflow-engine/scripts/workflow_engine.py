#!/usr/bin/env python3
"""
workflow_engine.py - Lightweight BPMN workflow orchestration
"""

import json
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Callable, Coroutine
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


class StepType(str, Enum):
    """Step execution types"""
    VALIDACION = "validacion"
    EVALUACION = "evaluacion"
    APROBACION = "aprobacion"
    NOTIFICACION = "notificacion"
    DECISION = "decision"
    ESPERA = "espera"


@dataclass
class StepResult:
    """Result of step execution"""
    step_id: str
    status: str  # "success", "failed", "waiting"
    output: Dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    executed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowInstance:
    """Active workflow instance"""
    id: str
    definition_id: str
    context: Dict[str, Any]
    current_step: int = 0
    status: str = "running"  # running, completed, failed
    steps_executed: List[StepResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class WorkflowEngine:
    """Lightweight BPMN workflow engine"""
    
    def __init__(self):
        self.definitions: Dict[str, dict] = {}
        self.handlers: Dict[StepType, Callable] = {
            StepType.VALIDACION: self._handle_validation,
            StepType.EVALUACION: self._handle_evaluation,
            StepType.APROBACION: self._handle_approval,
            StepType.NOTIFICACION: self._handle_notification,
            StepType.DECISION: self._handle_decision,
            StepType.ESPERA: self._handle_wait,
        }
        self.instances: Dict[str, WorkflowInstance] = {}
    
    def register_definition(self, definition_id: str, definition: dict):
        """Register workflow definition"""
        self.definitions[definition_id] = definition
        logger.info(f"Registered workflow definition: {definition_id}")
    
    def register_handler(self, step_type: StepType, handler: Callable):
        """Register custom step handler"""
        self.handlers[step_type] = handler
    
    async def start_workflow(
        self,
        definition_id: str,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> WorkflowInstance:
        """Start workflow execution"""
        
        if definition_id not in self.definitions:
            raise ValueError(f"Definition not found: {definition_id}")
        
        instance = WorkflowInstance(
            id=workflow_id,
            definition_id=definition_id,
            context=context
        )
        
        self.instances[workflow_id] = instance
        logger.info(f"Started workflow {workflow_id}")
        
        # Execute first step
        await self._execute_step(instance)
        
        return instance
    
    async def _execute_step(self, instance: WorkflowInstance):
        """Execute current step"""
        
        definition = self.definitions[instance.definition_id]
        steps = definition["steps"]
        
        if instance.current_step >= len(steps):
            instance.status = "completed"
            instance.completed_at = datetime.utcnow()
            logger.info(f"Workflow {instance.id} completed")
            return
        
        step = steps[instance.current_step]
        step_type = StepType(step["type"])
        
        logger.info(f"Executing step {instance.current_step}: {step['id']}")
        
        try:
            handler = self.handlers.get(step_type)
            if not handler:
                raise ValueError(f"No handler for step type: {step_type}")
            
            result = await handler(step, instance.context)
            result.step_id = step["id"]
            result.status = "success"
            
            instance.steps_executed.append(result)
            instance.context.update(result.output)
            
            # Check transitions
            next_step = step.get("next", instance.current_step + 1)
            
            if isinstance(next_step, dict):  # Conditional transition
                condition = next_step.get("condition", "")
                if self._evaluate_condition(condition, instance.context):
                    instance.current_step = next_step["then"]
                else:
                    instance.current_step = next_step.get("else", instance.current_step + 1)
            else:
                instance.current_step = next_step
            
            # Execute next step recursively
            await self._execute_step(instance)
        
        except Exception as e:
            logger.error(f"Error in step {step['id']}: {e}")
            result = StepResult(
                step_id=step["id"],
                status="failed",
                error=str(e)
            )
            instance.steps_executed.append(result)
            instance.status = "failed"
    
    async def _handle_validation(self, step: dict, context: Dict) -> StepResult:
        """Validate input data"""
        required_fields = step.get("config", {}).get("required_fields", [])
        
        missing = [f for f in required_fields if f not in context]
        
        return StepResult(
            step_id="",
            status="success" if not missing else "failed",
            output={"valid": len(missing) == 0, "missing_fields": missing},
            error=None if not missing else f"Missing: {', '.join(missing)}"
        )
    
    async def _handle_evaluation(self, step: dict, context: Dict) -> StepResult:
        """Evaluate request against criteria"""
        criteria = step.get("config", {}).get("criteria", [])
        
        results = {
            "criteria_met": 0,
            "total_criteria": len(criteria),
            "details": []
        }
        
        for criterion in criteria:
            met = context.get(criterion.get("field")) == criterion.get("value")
            results["criteria_met"] += int(met)
            results["details"].append({
                "criterion": criterion.get("name"),
                "met": met
            })
        
        return StepResult(
            step_id="",
            status="success",
            output=results
        )
    
    async def _handle_approval(self, step: dict, context: Dict) -> StepResult:
        """Approval step"""
        required_role = step.get("config", {}).get("required_role", "admin")
        
        return StepResult(
            step_id="",
            status="success",
            output={"approved": True, "role": required_role}
        )
    
    async def _handle_notification(self, step: dict, context: Dict) -> StepResult:
        """Send notification"""
        recipients = step.get("config", {}).get("recipients", [])
        message = step.get("config", {}).get("message", "")
        
        logger.info(f"Sending notification to {recipients}: {message}")
        
        return StepResult(
            step_id="",
            status="success",
            output={"notified": len(recipients)}
        )
    
    async def _handle_decision(self, step: dict, context: Dict) -> StepResult:
        """Decision step (just passes context)"""
        return StepResult(step_id="", status="success", output={})
    
    async def _handle_wait(self, step: dict, context: Dict) -> StepResult:
        """Wait step"""
        duration = step.get("config", {}).get("duration_seconds", 1)
        await asyncio.sleep(duration)
        
        return StepResult(
            step_id="",
            status="success",
            output={"waited_seconds": duration}
        )
    
    @staticmethod
    def _evaluate_condition(condition: str, context: Dict) -> bool:
        """Evaluate conditional expression"""
        if not condition:
            return True
        
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def get_instance(self, workflow_id: str) -> WorkflowInstance | None:
        """Get workflow instance"""
        return self.instances.get(workflow_id)
    
    def get_status(self, workflow_id: str) -> dict:
        """Get workflow status"""
        instance = self.get_instance(workflow_id)
        if not instance:
            return {"error": "Workflow not found"}
        
        return {
            "id": instance.id,
            "status": instance.status,
            "current_step": instance.current_step,
            "steps_executed": len(instance.steps_executed),
            "progress": f"{instance.current_step}/{len(self.definitions[instance.definition_id]['steps'])}"
        }


# Example usage
if __name__ == "__main__":
    async def main():
        engine = WorkflowEngine()
        
        # Define workflow
        workflow_def = {
            "id": "tramite-solicitud",
            "name": "Proceso de Solicitud",
            "steps": [
                {
                    "id": "validar",
                    "type": StepType.VALIDACION.value,
                    "config": {"required_fields": ["solicitante", "documento"]},
                    "next": 1
                },
                {
                    "id": "evaluar",
                    "type": StepType.EVALUACION.value,
                    "config": {"criteria": [{"name": "edad", "field": "edad", "value": 18}]},
                    "next": 2
                },
                {
                    "id": "aprobar",
                    "type": StepType.APROBACION.value,
                    "config": {"required_role": "funcionario"},
                    "next": 3
                },
                {
                    "id": "notificar",
                    "type": StepType.NOTIFICACION.value,
                    "config": {"recipients": ["solicitante@email.com"], "message": "Su solicitud fue aprobada"},
                    "next": 4
                }
            ]
        }
        
        engine.register_definition("tramite", workflow_def)
        
        # Execute workflow
        instance = await engine.start_workflow(
            "tramite",
            "tramite-001",
            {"solicitante": "Juan", "documento": "123456", "edad": 25}
        )
        
        print(f"Workflow status: {instance.status}")
        print(f"Steps executed: {len(instance.steps_executed)}")
        for step_result in instance.steps_executed:
            print(f"  - {step_result.step_id}: {step_result.status}")
    
    asyncio.run(main())
