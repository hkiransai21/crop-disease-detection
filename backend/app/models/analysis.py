"""Crop Disease Analysis database model."""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.feedback import Feedback


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Image file details
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # ML Prediction outputs
    predicted_label: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    is_uncertain: Mapped[bool] = mapped_column(Boolean, default=False)
    top_k: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Location & Environmental data
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    weather_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    risk_assessment: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="analyses")
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
