#!/usr/bin/env python3
"""
test_workflows.py - Test BPMN workflow engine
"""

import pytest
import asyncio
from workflow_engine import WorkflowEngine, StepType


@pytest.fixture
def engine():
    """Create workflow engine instance"""
    return WorkflowEngine()


@pytest.fixture
def simple_workflow_def():
    """Simple linear workflow definition"""
    return {
        "id": "simple",
        "name": "Simple Workflow",
        "steps": [
            {
                "id": "step1",
                "type": StepType.VALIDACION.value,
                "config": {"required_fields": ["name"]},
                "next": 1
            },
            {
                "id": "step2",
                "type": StepType.NOTIFICACION.value,
                "config": {"recipients": ["user@email.com"]},
                "next": 2
            }
        ]
    }


@pytest.fixture
def conditional_workflow_def():
    """Workflow with conditional transitions"""
    return {
        "id": "conditional",
        "name": "Conditional Workflow",
        "steps": [
            {
                "id": "validate",
                "type": StepType.VALIDACION.value,
                "config": {"required_fields": ["amount"]},
                "next": {
                    "condition": "context.get('amount', 0) > 5000",
                    "then": 2,
                    "else": 1
                }
            },
            {
                "id": "simple_approval",
                "type": StepType.APROBACION.value,
                "config": {"required_role": "manager"},
                "next": 3
            },
            {
                "id": "director_approval",
                "type": StepType.APROBACION.value,
                "config": {"required_role": "director"},
                "next": 3
            },
            {
                "id": "complete",
                "type": StepType.NOTIFICACION.value,
                "config": {"recipients": ["admin@email.com"]},
                "next": 4
            }
        ]
    }


@pytest.mark.asyncio
async def test_workflow_registration(engine, simple_workflow_def):
    """Test workflow definition registration"""
    engine.register_definition("test", simple_workflow_def)
    
    assert "test" in engine.definitions
    assert engine.definitions["test"]["name"] == "Simple Workflow"


@pytest.mark.asyncio
async def test_simple_workflow_execution(engine, simple_workflow_def):
    """Test simple linear workflow execution"""
    engine.register_definition("simple", simple_workflow_def)
    
    instance = await engine.start_workflow(
        "simple",
        "wf-001",
        {"name": "John"}
    )
    
    assert instance.status == "completed"
    assert len(instance.steps_executed) == 2
    assert instance.steps_executed[0].status == "success"
    assert instance.steps_executed[1].status == "success"


@pytest.mark.asyncio
async def test_validation_step_success(engine, simple_workflow_def):
    """Test validation step with valid data"""
    engine.register_definition("simple", simple_workflow_def)
    
    instance = await engine.start_workflow(
        "simple",
        "wf-002",
        {"name": "Jane", "age": 30}
    )
    
    validation_result = instance.steps_executed[0]
    assert validation_result.status == "success"
    assert validation_result.output["valid"] is True


@pytest.mark.asyncio
async def test_validation_step_failure(engine, simple_workflow_def):
    """Test validation step with missing required fields"""
    engine.register_definition("simple", simple_workflow_def)
    
    instance = await engine.start_workflow(
        "simple",
        "wf-003",
        {"age": 30}  # Missing "name"
    )
    
    validation_result = instance.steps_executed[0]
    assert validation_result.status == "failed"
    assert "name" in validation_result.output["missing_fields"]


@pytest.mark.asyncio
async def test_context_propagation(engine):
    """Test context data propagation through steps"""
    workflow_def = {
        "id": "context-test",
        "name": "Context Test",
        "steps": [
            {
                "id": "eval",
                "type": StepType.EVALUACION.value,
                "config": {"criteria": [{"name": "score", "field": "score", "value": 85}]},
                "next": 1
            },
            {
                "id": "notify",
                "type": StepType.NOTIFICACION.value,
                "config": {"recipients": ["user@email.com"]},
                "next": 2
            }
        ]
    }
    
    engine.register_definition("context-test", workflow_def)
    
    instance = await engine.start_workflow(
        "context-test",
        "wf-004",
        {"score": 85, "user": "John"}
    )
    
    assert instance.context["score"] == 85
    assert instance.context["user"] == "John"


@pytest.mark.asyncio
async def test_conditional_transition_high_amount(engine, conditional_workflow_def):
    """Test conditional transition with high amount (> 5000)"""
    engine.register_definition("conditional", conditional_workflow_def)
    
    instance = await engine.start_workflow(
        "conditional",
        "wf-005",
        {"amount": 10000}
    )
    
    assert instance.status == "completed"
    # Should execute: validate -> director_approval -> notify
    step_ids = [s.step_id for s in instance.steps_executed]
    assert "director_approval" in step_ids


@pytest.mark.asyncio
async def test_conditional_transition_low_amount(engine, conditional_workflow_def):
    """Test conditional transition with low amount (<= 5000)"""
    engine.register_definition("conditional", conditional_workflow_def)
    
    instance = await engine.start_workflow(
        "conditional",
        "wf-006",
        {"amount": 2000}
    )
    
    assert instance.status == "completed"
    # Should execute: validate -> simple_approval -> notify
    step_ids = [s.step_id for s in instance.steps_executed]
    assert "simple_approval" in step_ids
    assert "director_approval" not in step_ids


@pytest.mark.asyncio
async def test_workflow_status_tracking(engine, simple_workflow_def):
    """Test workflow instance status tracking"""
    engine.register_definition("simple", simple_workflow_def)
    
    instance = await engine.start_workflow(
        "simple",
        "wf-007",
        {"name": "Test"}
    )
    
    status = engine.get_status("wf-007")
    
    assert status["status"] == "completed"
    assert status["steps_executed"] == 2
    assert "progress" in status


@pytest.mark.asyncio
async def test_workflow_not_found(engine):
    """Test error handling for non-existent workflow"""
    with pytest.raises(ValueError, match="Definition not found"):
        await engine.start_workflow(
            "non-existent",
            "wf-008",
            {}
        )


@pytest.mark.asyncio
async def test_custom_step_handler(engine):
    """Test custom step handler registration"""
    from workflow_engine import StepResult
    
    async def custom_handler(step, context):
        return StepResult(
            step_id="",
            status="success",
            output={"custom": True}
        )
    
    engine.register_handler(StepType.DECISION, custom_handler)
    
    workflow_def = {
        "id": "custom",
        "name": "Custom",
        "steps": [
            {
                "id": "decide",
                "type": StepType.DECISION.value,
                "next": 1
            }
        ]
    }
    
    engine.register_definition("custom", workflow_def)
    instance = await engine.start_workflow("custom", "wf-009", {})
    
    assert instance.steps_executed[0].output["custom"] is True


@pytest.mark.asyncio
async def test_evaluation_step():
    """Test evaluation step scoring"""
    engine = WorkflowEngine()
    
    workflow_def = {
        "id": "eval-test",
        "name": "Eval Test",
        "steps": [
            {
                "id": "score",
                "type": StepType.EVALUACION.value,
                "config": {
                    "criteria": [
                        {"name": "age", "field": "age", "value": 25},
                        {"name": "income", "field": "income", "value": 50000}
                    ]
                },
                "next": 1
            }
        ]
    }
    
    engine.register_definition("eval-test", workflow_def)
    instance = await engine.start_workflow(
        "eval-test",
        "wf-010",
        {"age": 25, "income": 50000}
    )
    
    result = instance.steps_executed[0]
    assert result.output["criteria_met"] == 2
    assert result.output["total_criteria"] == 2


async def main():
    """Run tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
