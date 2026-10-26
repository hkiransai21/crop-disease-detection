"""Pydantic schemas for Analysis requests, predictions, results, and feedback."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.weather import WeatherSummary
from backend.app.schemas.risk import RiskAssessment
from backend.app.knowledge_base.schema import DiseaseEntry


class PredictionItem(BaseModel):
    class_id: str
    crop: str
    disease_name: str
    confidence: float
    confidence_percentage: float
    is_healthy: bool


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    localization_source: Optional[Dict[str, Any]] = None
    image_sha256: Optional[str] = None
    entropy: Optional[float] = None
    weather_status: str = 'location_required'
    id: str
    canonical_key: Optional[str] = None
    scientific_name: Optional[str] = None
    language: str = "en"
    predicted_label: str
    crop: str
    disease_name: str
    confidence: float
    confidence_display: str
    is_uncertain: bool
    uncertainty_reason: Optional[str] = None
    top_k: List[PredictionItem]
    model_version: str
    image_url: str
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    weather_summary: Optional[WeatherSummary] = None
    risk_assessment: Optional[RiskAssessment] = None
    disease_details: Optional[DiseaseEntry] = None
    created_at: datetime


class AnalysisHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    canonical_key: Optional[str] = None
    scientific_name: Optional[str] = None
    language: str = "en"
    predicted_label: str
    crop: str
    disease_name: str
    confidence: float
    is_uncertain: bool
    image_url: str
    location_name: Optional[str]
    created_at: datetime
    disease_details: Optional[DiseaseEntry] = None
    risk_assessment: Optional[RiskAssessment] = None
    uncertainty_reason: Optional[str] = None
    has_feedback: bool = False
    is_feedback_correct: Optional[bool] = None


class FeedbackCreate(BaseModel):
    is_correct: bool
    corrected_label: Optional[str] = None
    comments: Optional[str] = None
    consent_for_retraining: bool = True


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    is_correct: bool
    corrected_label: Optional[str]
    comments: Optional[str]
    created_at: datetime
