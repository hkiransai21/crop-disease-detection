"""Knowledge base disease encyclopedia endpoints."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from backend.app.knowledge_base.schema import DiseaseEntry
from backend.app.services.risk import load_knowledge_base

router = APIRouter(prefix="/diseases", tags=["Agronomic Knowledge Base"])


@router.get("", response_model=List[DiseaseEntry])
async def list_all_diseases(
    crop: Optional[str] = Query(None, description="Filter by crop name"),
    causal_agent: Optional[str] = Query(None, description="Filter by pathogen type: fungal, bacterial, viral, pest, none")
):
    """List all 38 verified crop diseases and healthy conditions in the agronomic knowledge base."""
    kb = load_knowledge_base()
    entries = list(kb.values())

    if crop:
        entries = [e for e in entries if crop.lower() in e.crop.lower()]
    if causal_agent:
        entries = [e for e in entries if causal_agent.lower() in e.causal_agent_type.lower()]

    return entries


@router.get("/{disease_id}", response_model=DiseaseEntry)
async def get_disease_by_id(disease_id: str):
    """Fetch complete agronomic monograph, symptoms, favorable weather, organic/chemical controls, and cited sources."""
    kb = load_knowledge_base()
    entry = kb.get(disease_id)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease entry '{disease_id}' not found in knowledge base."
        )

    return entry
