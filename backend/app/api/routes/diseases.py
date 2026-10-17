"""Knowledge base disease encyclopedia endpoints."""
from typing import List, Optional
from backend.app.schemas.analysis import AnalysisResponse
from fastapi import APIRouter, HTTPException, status, Query, Request
from backend.app.knowledge_base.schema import DiseaseEntry
from backend.app.services.i18n import resolve_language, load_localized_knowledge_base, get_localized_disease_entry

router = APIRouter(prefix="/diseases", tags=["Agronomic Knowledge Base"])


@router.get("", response_model=List[DiseaseEntry])
async def list_all_diseases(
    request: Request,
    crop: Optional[str] = Query(None, description="Filter by crop name"),
    causal_agent: Optional[str] = Query(None, description="Filter by pathogen type: fungal, bacterial, viral, pest, none"),
    lang: Optional[str] = Query(None, description="Target language code (e.g. en, hi, ta, te, kn)")
):
    """List all 38 verified crop diseases and healthy conditions in the agronomic knowledge base localized to requested language."""
    resolved_lang = resolve_language(lang, request.headers.get("Accept-Language"))
    kb = load_localized_knowledge_base(resolved_lang)
    entries = list(kb.values())

    if crop:
        entries = [e for e in entries if crop.lower() in e.crop.lower() or (e.canonical_crop and crop.lower() in e.canonical_crop.lower())]
    if causal_agent:
        entries = [e for e in entries if causal_agent.lower() in e.causal_agent_type.lower()]

    return entries


@router.get("/{disease_id}", response_model=DiseaseEntry)
async def get_disease_by_id(
    disease_id: str,
    request: Request,
    lang: Optional[str] = Query(None, description="Target language code (e.g. en, hi, ta, te, kn)")
):
    """Fetch complete agronomic monograph, symptoms, favorable weather, organic/chemical controls, and cited sources in requested language."""
    resolved_lang = resolve_language(lang, request.headers.get("Accept-Language"))
    entry = get_localized_disease_entry(disease_id, resolved_lang)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease entry '{disease_id}' not found in knowledge base."
        )

    return entry



@router.post("/localize-result")
async def localize_result(result: AnalysisResponse, request: Request, lang: Optional[str] = Query(None)):
    """Reformat a guest's existing result; no inference, persistence or score changes."""
    from backend.app.services.i18n import translate_message, localize_risk_assessment, UNCERTAINTY
    from backend.app.schemas.risk import RiskAssessment
    resolved = resolve_language(lang, request.headers.get('Accept-Language'))
    entry = get_localized_disease_entry(result.predicted_label, resolved)
    source = result.localization_source or {}
    if not source and result.language == 'en':
        source = {'confidence_display': result.confidence_display, 'risk_assessment': result.risk_assessment.model_dump() if result.risk_assessment else None}
        result.localization_source = source
    if entry:
        result.crop = entry.crop
        result.disease_name = entry.disease_name
        result.disease_details = entry
        result.scientific_name = entry.scientific_name
    for item in result.top_k:
        candidate = get_localized_disease_entry(item.class_id, resolved)
        if candidate:
            item.crop = candidate.crop
            item.disease_name = candidate.disease_name
    result.language = resolved
    result.confidence_display = translate_message(source.get('confidence_display', result.confidence_display), resolved)
    result.uncertainty_reason = translate_message(UNCERTAINTY, resolved) if result.is_uncertain else None
    if source.get('risk_assessment'):
        result.risk_assessment = localize_risk_assessment(RiskAssessment(**source['risk_assessment']), resolved)
    return result
