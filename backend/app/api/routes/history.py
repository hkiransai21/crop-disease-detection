"""History endpoints for retrieving and managing past farmer diagnoses."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.models.feedback import Feedback
from backend.app.schemas.analysis import AnalysisResponse, AnalysisHistoryItem, PredictionItem
from backend.app.schemas.weather import WeatherSummary
from backend.app.schemas.risk import RiskAssessment
from backend.app.services.risk import load_knowledge_base
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/history", tags=["Diagnosis History"])


@router.get("", response_model=List[AnalysisHistoryItem])
async def list_user_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve chronologically ordered past crop diagnoses for the authenticated farmer."""
    stmt = (
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(desc(Analysis.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    analyses = result.scalars().all()

    # Check feedback status for each analysis
    history_items = []
    for a in analyses:
        file_rel = a.image_path.replace("./backend/app", "").replace("backend/app", "")
        img_url = f"/static{file_rel}" if not file_rel.startswith("/static") else file_rel

        # Parse crop and disease names
        crop = "Plant"
        disease = a.predicted_label
        if "___" in a.predicted_label:
            crop_part, dis_part = a.predicted_label.split("___", 1)
            crop = crop_part.replace("_", " ").replace("(maize)", "").replace("(including sour)", "").strip()
            disease = dis_part.replace("_", " ").strip()

        has_fb = len(a.feedbacks) > 0
        fb_correct = a.feedbacks[0].is_correct if has_fb else None

        history_items.append(AnalysisHistoryItem(
            id=a.id,
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete diagnostic details, weather conditions, risk score, and treatment guide for an analysis."""
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

    crop = "Plant"
    disease = analysis.predicted_label
    if "___" in analysis.predicted_label:
        crop_part, dis_part = analysis.predicted_label.split("___", 1)
        crop = crop_part.replace("_", " ").replace("(maize)", "").replace("(including sour)", "").strip()
        disease = dis_part.replace("_", " ").strip()

    kb = load_knowledge_base()
    disease_entry = kb.get(analysis.predicted_label)

    top_k_items = [PredictionItem(**item) for item in analysis.top_k] if analysis.top_k else []
    weather = WeatherSummary(**analysis.weather_snapshot) if analysis.weather_snapshot else None
    risk = RiskAssessment(**analysis.risk_assessment) if analysis.risk_assessment else None

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
        predicted_label=analysis.predicted_label,
        crop=crop,
        disease_name=disease,
        confidence=analysis.confidence,
        confidence_display=conf_display,
        is_uncertain=analysis.is_uncertain,
        top_k=top_k_items,
        model_version=analysis.model_version,
        image_url=img_url,
        location_name=analysis.location_name,
        latitude=analysis.latitude,
        longitude=analysis.longitude,
        weather_summary=weather,
        risk_assessment=risk,
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
