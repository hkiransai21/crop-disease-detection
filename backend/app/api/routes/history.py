from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.models.feedback import Feedback
from backend.app.schemas.analysis import AnalysisResponse, AnalysisHistoryItem, PredictionItem
from backend.app.schemas.weather import WeatherSummary
from backend.app.schemas.risk import RiskAssessment
from backend.app.services.i18n import resolve_language, get_localized_disease_entry, load_localized_knowledge_base, localize_risk_assessment, translate_message, UNCERTAINTY
from backend.app.services.risk import load_knowledge_base
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/history", tags=["Diagnosis History"])


@router.get("", response_model=List[AnalysisHistoryItem])
async def list_user_history(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    lang: Optional[str] = Query(None, description="Target language code"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve chronologically ordered past crop diagnoses for the authenticated farmer localized to requested language."""
    stmt = (
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(desc(Analysis.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    analyses = result.scalars().all()

    resolved_lang = resolve_language(lang, request.headers.get("Accept-Language"))
    kb = load_localized_knowledge_base(resolved_lang)

    # Check feedback status for each analysis
    history_items = []
    for a in analyses:
        file_rel = a.image_path.replace("./backend/app", "").replace("backend/app", "")
        img_url = f"/static{file_rel}" if not file_rel.startswith("/static") else file_rel

        # Localize crop and disease names
        entry = kb.get(a.predicted_label)
        crop = entry.crop if entry else "Plant"
        disease = entry.disease_name if entry else a.predicted_label

        has_fb = len(a.feedbacks) > 0
        fb_correct = a.feedbacks[0].is_correct if has_fb else None

        history_items.append(AnalysisHistoryItem(
            id=a.id,
            canonical_key=a.predicted_label,
            scientific_name=entry.scientific_name if entry else None,
            language=resolved_lang,
            disease_details=entry,
            risk_assessment=localize_risk_assessment(RiskAssessment(**a.risk_assessment), resolved_lang) if a.risk_assessment else None,
            uncertainty_reason=translate_message(UNCERTAINTY, resolved_lang) if a.is_uncertain else None,
            predicted_label=a.predicted_label,
            crop=crop,
            disease_name=disease,
            confidence=a.confidence,
            is_uncertain=a.is_uncertain,
            image_url=img_url,
            location_name=a.location_name,
            created_at=a.created_at,
            has_feedback=has_fb,
            is_feedback_correct=fb_correct
        ))

    return history_items


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_detail(
    analysis_id: str,
    request: Request,
    lang: Optional[str] = Query(None, description="Target language code"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete diagnostic details, weather conditions, risk score, and treatment guide for an analysis in requested language."""
    stmt = select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found or access unauthorized."
        )

    file_rel = analysis.image_path.replace("./backend/app", "").replace("backend/app", "")
    img_url = f"/static{file_rel}" if not file_rel.startswith("/static") else file_rel

    resolved_lang = resolve_language(lang, request.headers.get("Accept-Language"))
    disease_entry = get_localized_disease_entry(analysis.predicted_label, resolved_lang)
    crop = disease_entry.crop if disease_entry else "Plant"
    disease = disease_entry.disease_name if disease_entry else analysis.predicted_label

    kb_loc = load_localized_knowledge_base(resolved_lang)
    top_k_items = []
    if analysis.top_k:
        for item in analysis.top_k:
            loc_e = kb_loc.get(item["class_id"])
            top_k_items.append(PredictionItem(
                class_id=item["class_id"],
                crop=loc_e.crop if loc_e else item.get("crop", "Plant"),
                disease_name=loc_e.disease_name if loc_e else item.get("disease_name", item["class_id"]),
                confidence=item["confidence"],
                confidence_percentage=item.get("confidence_percentage", round(item["confidence"] * 100, 1)),
                is_healthy=item.get("is_healthy", False)
            ))

    weather = WeatherSummary(**analysis.weather_snapshot) if analysis.weather_snapshot else None
    raw_risk = RiskAssessment(**analysis.risk_assessment) if analysis.risk_assessment else None
    localized_risk = localize_risk_assessment(raw_risk, resolved_lang) if raw_risk else None

    # Confidence display
    if analysis.confidence >= 0.85:
        conf_display = "Very High Confidence"
    elif analysis.confidence >= 0.65:
        conf_display = "High Confidence"
    elif analysis.confidence >= 0.45:
        conf_display = "Moderate Confidence"
    else:
        conf_display = "Low / Uncertain"

    return AnalysisResponse(
        id=analysis.id,
        canonical_key=analysis.predicted_label,
        scientific_name=disease_entry.scientific_name if disease_entry else None,
        language=resolved_lang,
        predicted_label=analysis.predicted_label,
        crop=crop,
        disease_name=disease,
        confidence=analysis.confidence,
        confidence_display=translate_message(conf_display, resolved_lang),
        uncertainty_reason=translate_message(UNCERTAINTY, resolved_lang) if analysis.is_uncertain else None,
        is_uncertain=analysis.is_uncertain,
        top_k=top_k_items,
        model_version=analysis.model_version,
        image_url=img_url,
        location_name=analysis.location_name,
        latitude=analysis.latitude,
        longitude=analysis.longitude,
        weather_summary=weather,
        risk_assessment=localized_risk,
        disease_details=disease_entry,
        created_at=analysis.created_at
    )



@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a past analysis record and its associated feedback."""
    stmt = select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found or access unauthorized."
        )

    await db.delete(analysis)
    await db.commit()
    return None
