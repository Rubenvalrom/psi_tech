from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..services.semantic_search import SemanticSearchService

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/search/semantic")
async def semantic_search(
    query: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for documents/expedientes semantically based on meanings.
    """
    service = SemanticSearchService(db)
    results = service.search_documents(query)
    return results

@router.post("/ask")
async def ask_assistant(
    question: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ask the Olympus Smart Gov assistant about documents using RAG.
    """
    service = SemanticSearchService(db)
    response = service.ask_assistant(question)
    return response
