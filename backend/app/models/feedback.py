"""User feedback model for prediction verification and retraining datasets."""
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.analysis import Analysis
    from backend.app.models.user import User


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    corrected_label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consent_for_retraining: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="feedbacks")
