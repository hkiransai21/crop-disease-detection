"""Pydantic schemas for the Outbreak Risk Prediction Engine."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ContributingFactor(BaseModel):
    factor_name: str
    impact: str = Field(..., description="ELEVATES_RISK | REDUCES_RISK | NEUTRAL")
    explanation: str = Field(..., description="Plain-language agronomic explanation")


class DailyRiskOutlook(BaseModel):
    date: str
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(..., description="LOW | MODERATE | HIGH | VERY HIGH")
    favorable_factors: List[str]


class RiskAssessment(BaseModel):
    crop: str
    target_condition: str
    risk_score: int = Field(..., ge=0, le=100, description="Heuristic score from 0 to 100")
    risk_level: str = Field(..., description="LOW | MODERATE | HIGH | VERY HIGH")
    risk_color: str = Field(..., description="Hex color code for UI rendering")
    headline: str
    summary: str
    contributing_factors: List[ContributingFactor]
    daily_outlook: List[DailyRiskOutlook]
    top_regional_threats: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="For healthy plants, top alternative disease threats based on weather"
    )
    disclaimer: str = Field(
        default="Advisory estimate based on agronomic heuristics and environmental data; not a laboratory-validated forecast. Consult local extension specialists before chemical applications.",
        description="Mandatory advisory heuristic disclaimer"
    )
