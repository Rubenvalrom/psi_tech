"""Health check endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import requests

from ..core.database import get_db
from ..core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Check API health and dependencies."""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "ollama": "unknown",
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Ollama
    try:
        response = requests.get(
            f"{settings.OLLAMA_HOST}/api/tags",
            timeout=5.0,
        )
        if response.status_code == 200:
            health_status["ollama"] = "connected"
        else:
            health_status["ollama"] = f"error: status {response.status_code}"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["ollama"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
