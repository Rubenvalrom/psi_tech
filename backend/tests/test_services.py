import pytest
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.workflow import WorkflowService
from app.services.accounting import AccountingService
from app.models.expediente import Expediente, EstadoExpediente, PasoTramitacion, EstadoPaso
from app.models.financiero import PartidaPresupuestaria

def test_workflow_start(db: Session):
    """Test starting a workflow logic."""
    # Setup
    exp = Expediente(numero="EXP-TEST-01", asunto="Test Workflow", estado=EstadoExpediente.ABIERTO)
    db.add(exp)
    db.commit()
    
    service = WorkflowService(db)
    service.start_workflow(exp.id, user_id=1)
    
    db.refresh(exp)
    assert exp.estado == EstadoExpediente.EN_PROCESO

def test_workflow_complete_step(db: Session):
    """Test completing a step in a workflow."""
    # Setup
    exp = Expediente(numero="EXP-TEST-02", asunto="Test Workflow Step", estado=EstadoExpediente.EN_PROCESO)
    db.add(exp)
    db.commit()
    
    paso = PasoTramitacion(expediente_id=exp.id, numero_paso=1, titulo="Paso 1", estado=EstadoPaso.PENDIENTE)
    db.add(paso)
    db.commit()
    
    service = WorkflowService(db)
    service.complete_step(exp.id, paso.id, user_id=1)
    
    db.refresh(paso)
    db.refresh(exp)
    assert paso.estado == EstadoPaso.COMPLETADO
    # In our simple logic, 0 pending steps closes the expediente
    assert exp.estado == EstadoExpediente.CERRADO

def test_accounting_budget_availability(db: Session):
    """Test budget availability checks."""
    partida = PartidaPresupuestaria(
        codigo_contable="PT-01", 
        descripcion="Test Partida", 
        presupuestado=Decimal("1000.00"),
        comprometido=Decimal("0.00"),
        pagado=Decimal("0.00")
    )
    db.add(partida)
    db.commit()
    
    service = AccountingService(db)
    assert service.check_availability(partida.id, Decimal("500.00")) is True
    assert service.check_availability(partida.id, Decimal("1500.00")) is False

def test_accounting_commit_budget(db: Session):
    """Test committing funds to an expediente."""
    partida = PartidaPresupuestaria(
        codigo_contable="PT-02", 
        descripcion="Test Partida Commit", 
        presupuestado=Decimal("1000.00")
    )
    db.add(partida)
    db.commit()
    
    exp = Expediente(numero="EXP-FIN-01", asunto="Test Finance", estado=EstadoExpediente.ABIERTO)
    db.add(exp)
    db.commit()
    
    service = AccountingService(db)
    service.commit_budget(partida.id, Decimal("200.00"), exp.id, user_id=1)
    
    db.refresh(partida)
    assert partida.comprometido == Decimal("200.00")
    assert partida.disponible == Decimal("800.00")
