"""Pydantic schemas for multilingual i18n data, glossaries, and TTS synthesis."""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LanguageConfig(BaseModel):
    code: str
    name: str
    native_name: str
    script_direction: str = "ltr"
    tts_voice: str
    tts_fallback_voice: Optional[str] = None
    review_status: str = "machine_suggested"  # expert_reviewed | machine_suggested | draft
    is_active: bool = True


class SupportedLanguagesResponse(BaseModel):
    default_language: str
    languages: List[LanguageConfig]


class GlossaryDiseaseEntry(BaseModel):
    id: str = Field(..., description="Canonical PlantVillage label, e.g., Tomato___Early_blight")
    common_name: str = Field(..., description="Local name used by farmers in native script")
    alt_names: List[str] = Field(default_factory=list, description="Regional or colloquial synonyms")
    transliteration: str = Field(..., description="Latin-script phonetic rendering for search & low-literacy")
    scientific_name: Optional[str] = Field(None, description="Pathogen binomial name (unchanged)")
    tts_text: str = Field(..., description="Phonetically safe pronunciation for audio narration")
    source: str = Field(..., description="Authoritative agricultural university or ICAR extension citation")
    review_status: str = Field("machine_suggested", description="draft | machine_suggested | expert_reviewed")


class GlossaryTermEntry(BaseModel):
    term_key: str = Field(..., description="English canonical term key, e.g. fungicide, crop_rotation")
    english: str
    localized_term: str = Field(..., description="Term in native script")
    transliteration: str
    definition: str
    tts_text: str


class LanguageGlossary(BaseModel):
    language: str
    language_name: str
    diseases: Dict[str, GlossaryDiseaseEntry]
    agronomic_terms: Dict[str, GlossaryTermEntry]


class LocalizedEnvironmentalConditions(BaseModel):
    temp_min_c: float
    temp_max_c: float
    temp_optimal_c: Optional[float] = None
    humidity_min_pct: float
    leaf_wetness_hours_min: float
    rainfall_favorable: bool
    wind_spread: bool = False


class LocalizedDiseaseEntry(BaseModel):
    id: str = Field(..., description="Canonical PlantVillage label")
    canonical_crop: str = Field(..., description="Canonical English crop name")
    canonical_disease_name: str = Field(..., description="Canonical English disease name")
    crop: str = Field(..., description="Localized crop name in native script")
    disease_name: str = Field(..., description="Localized disease name in native script")
    scientific_name: Optional[str] = Field(None, description="Scientific binomial name")
    causal_agent_type: str = Field(..., description="fungal | bacterial | viral | pest | abiotic | none")
    is_healthy: bool = Field(False)
    symptoms: str = Field(..., description="Localized plain-language diagnostic symptoms")
    spread_mechanism: str = Field(..., description="Localized spread description")
    favorable_conditions: LocalizedEnvironmentalConditions
    prevention_steps: List[str] = Field(..., description="Localized cultural and preventative steps")
    organic_controls: List[str] = Field(..., description="Localized organic and bio-control methods")
    chemical_controls: List[str] = Field(..., description="Localized chemical protectant methods with exact dosages")
    severity: str = Field(..., description="LOW | MODERATE | HIGH | CRITICAL")
    when_to_consult_expert: str = Field(..., description="Localized extension officer escalation criteria")
    safety_notes: List[str] = Field(..., description="Localized mandatory pesticide handling safety warnings")
    sources: List[str] = Field(default_factory=list)
    review_status: str = Field("machine_suggested", description="draft | machine_suggested | expert_reviewed")


class LocalizedKnowledgeBase(BaseModel):
    language: str
    version: str = "1.0.0"
    last_updated: str
    diseases: List[LocalizedDiseaseEntry]


class AudioSynthesizeRequest(BaseModel):
    text: str = Field(..., max_length=2000, description="Text to synthesize to audio")
    lang: str = Field("en", max_length=10, description="Language code")
    voice: Optional[str] = Field(None, description="Optional explicit voice override")
    rate: float = Field(1.0, ge=0.5, le=2.0, description="Speech rate multiplier")
