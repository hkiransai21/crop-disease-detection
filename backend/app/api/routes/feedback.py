"""User feedback endpoint for diagnosis validation and continuous learning dataset creation."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.models.feedback import Feedback
from backend.app.schemas.analysis import FeedbackCreate, FeedbackResponse
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/history", tags=["Diagnosis Feedback"])


@router.post("/{analysis_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_diagnosis_feedback(
    analysis_id: str,
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit user feedback on diagnosis accuracy:
    - Confirms or corrects the predicted disease label.
    - Captures opt-in farmer consent for inclusion in future model retraining cycles.
    """
    stmt = select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found."
        )

    # Check if feedback already submitted for this analysis
    existing_fb_stmt = select(Feedback).where(Feedback.analysis_id == analysis_id, Feedback.user_id == current_user.id)
    existing_fb = (await db.execute(existing_fb_stmt)).scalar_one_or_none()

    if existing_fb:
        # Update existing feedback
        existing_fb.is_correct = feedback_in.is_correct
        existing_fb.corrected_label = feedback_in.corrected_label
        existing_fb.comments = feedback_in.comments
        existing_fb.consent_for_retraining = feedback_in.consent_for_retraining
        await db.commit()
        await db.refresh(existing_fb)
        return existing_fb

    new_feedback = Feedback(
        analysis_id=analysis_id,
        user_id=current_user.id,
        is_correct=feedback_in.is_correct,
        corrected_label=feedback_in.corrected_label,
        comments=feedback_in.comments,
        consent_for_retraining=feedback_in.consent_for_retraining
    )
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    return new_feedback
