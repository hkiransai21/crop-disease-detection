"""Pydantic schemas for the curated agronomic knowledge base."""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class EnvironmentalConditions(BaseModel):
    temp_min_c: float = Field(..., description="Minimum temperature in Celsius favoring disease development")
    temp_max_c: float = Field(..., description="Maximum temperature in Celsius favoring disease development")
    temp_optimal_c: Optional[float] = Field(None, description="Optimal temperature in Celsius")
    humidity_min_pct: float = Field(..., description="Minimum relative humidity percentage favoring disease")
    leaf_wetness_hours_min: float = Field(..., description="Minimum consecutive wet/dew hours required for infection")
    rainfall_favorable: bool = Field(..., description="Whether frequent rainfall significantly accelerates spread")
    wind_spread: bool = Field(False, description="Whether wind contributes to spore dispersal")


class DiseaseEntry(BaseModel):
    id: str = Field(..., description="Unique machine-readable identifier matching PlantVillage label")
    crop: str = Field(..., description="Crop common name")
    disease_name: str = Field(..., description="Plain language disease name")
    scientific_name: Optional[str] = Field(None, description="Scientific binomial name of the pathogen or agent")
    causal_agent_type: str = Field(..., description="fungal | bacterial | viral | pest | abiotic | none")
    is_healthy: bool = Field(False, description="Whether this class represents a healthy crop")
    symptoms: str = Field(..., description="Diagnostic visual symptoms on leaves/stems/fruit")
    spread_mechanism: str = Field(..., description="How the pathogen or vector disseminates")
    favorable_conditions: EnvironmentalConditions = Field(..., description="Agronomic environmental triggers")
    prevention_steps: List[str] = Field(..., description="Preventative cultural and sanitation practices")
    organic_controls: List[str] = Field(..., description="Organic, biological, and non-synthetic control methods")
    chemical_controls: List[str] = Field(..., description="Generic active ingredients and mode of action categories")
    severity: str = Field(..., description="LOW | MODERATE | HIGH | CRITICAL")
    when_to_consult_expert: str = Field(..., description="Specific escalation criteria for agricultural extension officers")
    safety_notes: List[str] = Field(..., description="Mandatory pesticide safety and handling guidelines")
    sources: List[str] = Field(..., description="Citations to verified university extension and agricultural research services")
    canonical_crop: Optional[str] = Field(None, description="Canonical English crop name")
    canonical_disease_name: Optional[str] = Field(None, description="Canonical English disease name")
    review_status: Optional[str] = Field("expert_reviewed", description="draft | machine_suggested | expert_reviewed")
    language: Optional[str] = Field("en", description="Language code of this entry")



class KnowledgeBase(BaseModel):
    version: str = Field(..., description="Knowledge base version")
    last_updated: str = Field(..., description="ISO date of last update")
    diseases: List[DiseaseEntry] = Field(..., description="List of disease entries covering all classes")
