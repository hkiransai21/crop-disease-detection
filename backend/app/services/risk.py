"""Transparent, rule-based Outbreak Risk Prediction Engine based on agronomic thresholds."""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.schemas.weather import WeatherSummary, DailyForecast
from backend.app.schemas.risk import RiskAssessment, ContributingFactor, DailyRiskOutlook
from backend.app.knowledge_base.schema import DiseaseEntry, KnowledgeBase

_KB_CACHE: Optional[Dict[str, DiseaseEntry]] = None


def load_knowledge_base() -> Dict[str, DiseaseEntry]:
    """Load and parse the 38-class disease knowledge base."""
    global _KB_CACHE
    if _KB_CACHE is not None:
        return _KB_CACHE
        
    kb_path = Path(settings.KNOWLEDGE_BASE_PATH)
    if not kb_path.exists():
        # Fallback location
        kb_path = Path("backend/app/knowledge_base/diseases.yaml")
        
    with open(kb_path, "r") as f:
        raw_yaml = yaml.safe_load(f)
        
    kb = KnowledgeBase(**raw_yaml)
    _KB_CACHE = {entry.id: entry for entry in kb.diseases}
    return _KB_CACHE


def evaluate_disease_risk(
    predicted_label: str,
    weather: Optional[WeatherSummary] = None
) -> RiskAssessment:
    """Compute transparent 0-100 outbreak risk score for a diagnosed disease or healthy crop."""
    kb = load_knowledge_base()
    disease_entry = kb.get(predicted_label)
    
    if disease_entry is None:
        # Fallback entry
        return RiskAssessment(
            crop="Unknown Crop",
            target_condition=predicted_label,
            risk_score=50,
            risk_level="MODERATE",
            risk_color="#f59e0b",
            headline="Moderate Baseline Risk (Uncataloged Condition)",
            summary="Standard agronomic monitoring recommended.",
            contributing_factors=[],
            daily_outlook=[]
        )

    # If it's a healthy crop, evaluate all diseases of this crop
    if disease_entry.is_healthy:
        return _evaluate_healthy_crop_threats(disease_entry.crop, weather, kb)

    # For diagnosed disease, evaluate specific favorable rules
    cond = disease_entry.favorable_conditions
    factors: List[ContributingFactor] = []
    
    if weather is None:
        # No weather provided -> return neutral baseline
        return RiskAssessment(
            crop=disease_entry.crop,
            target_condition=disease_entry.disease_name,
            risk_score=40,
            risk_level="MODERATE",
            risk_color="#f59e0b",
            headline=f"Moderate Spread Potential for {disease_entry.disease_name}",
            summary="Environmental data unavailable. Standard preventative sanitation recommended.",
            contributing_factors=[
                ContributingFactor(
                    factor_name="Environmental Sensor Data Missing",
                    impact="NEUTRAL",
                    explanation="No local weather coordinates supplied. Risk score is computed from baseline crop susceptibility."
                )
            ],
            daily_outlook=[]
        )

    # 1. Temperature Scoring (0 to 35 points)
    # Check if forecast and current temp falls within favorable window
    temp_score = 0
    t_mean = weather.forecast_7d_mean_temp_c
    if cond.temp_min_c <= t_mean <= cond.temp_max_c:
        if cond.temp_optimal_c and abs(t_mean - cond.temp_optimal_c) <= 3.0:
            temp_score = 35
            factors.append(ContributingFactor(
                factor_name="Optimal Pathogen Temperature",
                impact="ELEVATES_RISK",
                explanation=f"Forecast mean temperature of {t_mean}°C aligns closely with pathogen optimum ({cond.temp_optimal_c}°C)."
            ))
        else:
            temp_score = 25
            factors.append(ContributingFactor(
                factor_name="Favorable Temperature Range",
                impact="ELEVATES_RISK",
                explanation=f"Forecast mean temperature ({t_mean}°C) falls inside pathogen activity range ({cond.temp_min_c}°C - {cond.temp_max_c}°C)."
            ))
    elif t_mean < cond.temp_min_c - 5.0 or t_mean > cond.temp_max_c + 5.0:
        temp_score = 5
        factors.append(ContributingFactor(
            factor_name="Unfavorable Temperature Suppression",
            impact="REDUCES_RISK",
            explanation=f"Forecast mean temperature ({t_mean}°C) is outside favorable development limits."
        ))
    else:
        temp_score = 15

    # 2. Humidity & Leaf Wetness Scoring (0 to 40 points)
    humidity_score = 0
    h_mean = weather.forecast_7d_mean_humidity_pct
    high_h_hours = weather.past_7d_high_humidity_hours
    
    # Special case: Two-Spotted Spider Mite thrives in low humidity / drought
    if "Spider_mites" in disease_entry.id:
        if h_mean <= 45.0:
            humidity_score = 40
            factors.append(ContributingFactor(
                factor_name="Dry & Hot Conditions Favour Spider Mites",
                impact="ELEVATES_RISK",
                explanation=f"Low relative humidity ({h_mean}%) combined with heat triggers explosive spider mite reproduction."
            ))
        else:
            humidity_score = 10
            factors.append(ContributingFactor(
                factor_name="High Humidity Suppresses Mite Outbreaks",
                impact="REDUCES_RISK",
                explanation=f"Elevated humidity ({h_mean}%) supports natural fungal entomopathogens that attack mites."
            ))
    else:
        # Standard fungal / bacterial diseases require moisture
        if h_mean >= cond.humidity_min_pct:
            humidity_score = 30
            factors.append(ContributingFactor(
                factor_name="High Atmospheric Humidity",
                impact="ELEVATES_RISK",
                explanation=f"Forecast humidity of {h_mean}% exceeds minimum infection threshold of {cond.humidity_min_pct}%."
            ))
        elif h_mean >= cond.humidity_min_pct - 15.0:
            humidity_score = 18
            factors.append(ContributingFactor(
                factor_name="Moderate Humidity Levels",
                impact="NEUTRAL",
                explanation=f"Forecast humidity ({h_mean}%) is moderate but near threshold ({cond.humidity_min_pct}%)."
            ))
        else:
            humidity_score = 5
            factors.append(ContributingFactor(
                factor_name="Dry Air Suppresses Spore Germination",
                impact="REDUCES_RISK",
                explanation=f"Low humidity ({h_mean}%) significantly impedes fungal spore germination and penetration."
            ))
            
        if high_h_hours >= 30:
            humidity_score = min(40, humidity_score + 10)
            factors.append(ContributingFactor(
                factor_name="Prolonged Leaf Wetness / High Humidity Hours",
                impact="ELEVATES_RISK",
                explanation=f"{high_h_hours} hours with RH >= 85% recorded over the last 7 days, promoting fungal sporulation."
            ))

    # 3. Rainfall & Splash Dispersal (0 to 25 points)
    rain_score = 0
    rain_total = weather.forecast_7d_total_rain_mm + (weather.past_7d_total_rain_mm * 0.5)
    if cond.rainfall_favorable:
        if rain_total >= 20.0:
            rain_score = 25
            factors.append(ContributingFactor(
                factor_name="Heavy Rain & Splash Dispersal",
                impact="ELEVATES_RISK",
                explanation=f"Cumulative rainfall of {rain_total:.1f} mm facilitates rapid splash dispersal and spore wash."
            ))
        elif rain_total >= 5.0:
            rain_score = 15
            factors.append(ContributingFactor(
                factor_name="Periodic Rainfall",
                impact="ELEVATES_RISK",
                explanation=f"Moderate rainfall ({rain_total:.1f} mm) maintains foliar moisture necessary for infection."
            ))
        else:
            rain_score = 5
            factors.append(ContributingFactor(
                factor_name="Minimal Precipitation",
                impact="REDUCES_RISK",
                explanation=f"Dry conditions ({rain_total:.1f} mm) limit rain-splash disease transmission."
            ))
    else:
        # Diseases like powdery mildew or viral vectors favored by dry conditions
        if rain_total < 5.0:
            rain_score = 20
            factors.append(ContributingFactor(
                factor_name="Dry Foliage Favors Disease / Vector",
                impact="ELEVATES_RISK",
                explanation="Lack of rain allows powdery mildew conidia and insect vectors (whiteflies/psyllids) to flourish."
            ))
        else:
            rain_score = 8
            factors.append(ContributingFactor(
                factor_name="Rain Washing",
                impact="REDUCES_RISK",
                explanation="Rainfall physically washes powdery mildew spores and small insect vectors off foliage."
            ))

    total_score = min(100, max(0, temp_score + humidity_score + rain_score))
    
    if total_score >= 75:
        level = "VERY HIGH"
        color = "#ef4444" # Red
        headline = f"CRITICAL: High Outbreak Risk for {disease_entry.disease_name}"
        summary = f"Current and forecast weather conditions are exceptionally favorable for {disease_entry.disease_name} proliferation and rapid secondary spread."
    elif total_score >= 50:
        level = "HIGH"
        color = "#f97316" # Orange
        headline = f"High Environmental Outbreak Risk for {disease_entry.disease_name}"
        summary = f"Favorable environmental triggers detected. Active preventative scouting and protective measures are strongly advised."
    elif total_score >= 25:
        level = "MODERATE"
        color = "#eab308" # Yellow
        headline = f"Moderate Outbreak Risk for {disease_entry.disease_name}"
        summary = f"Weather conditions partially favor disease development. Maintain routine field hygiene and monitor canopy moisture."
    else:
        level = "LOW"
        color = "#22c55e" # Green
        headline = f"Low Outbreak Risk for {disease_entry.disease_name}"
        summary = f"Environmental conditions are currently unfavorable for rapid spread of {disease_entry.disease_name}."

    # Compute 7-day daily outlook
    daily_outlook: List[DailyRiskOutlook] = []
    for day in weather.daily_forecasts:
        day_temp_score = 30 if (cond.temp_min_c <= day.temp_mean_c <= cond.temp_max_c) else 10
        day_hum_score = 35 if day.humidity_mean_pct >= cond.humidity_min_pct else 10
        day_rain_score = 25 if (cond.rainfall_favorable and day.precipitation_sum_mm > 2.0) else 10
        day_score = min(100, day_temp_score + day_hum_score + day_rain_score)
        
        day_level = "HIGH" if day_score >= 60 else ("MODERATE" if day_score >= 35 else "LOW")
        day_factors = []
        if day.humidity_mean_pct >= cond.humidity_min_pct:
            day_factors.append(f"High RH ({day.humidity_mean_pct:.0f}%)")
        if day.precipitation_sum_mm > 2.0:
            day_factors.append(f"Rain ({day.precipitation_sum_mm:.1f} mm)")
            
        daily_outlook.append(DailyRiskOutlook(
            date=day.date,
            risk_score=day_score,
            risk_level=day_level,
            favorable_factors=day_factors if day_factors else ["Favorable temperature window"]
        ))

    return RiskAssessment(
        crop=disease_entry.crop,
        target_condition=disease_entry.disease_name,
        risk_score=total_score,
        risk_level=level,
        risk_color=color,
        headline=headline,
        summary=summary,
        contributing_factors=factors,
        daily_outlook=daily_outlook,
        top_regional_threats=None
    )


def _evaluate_healthy_crop_threats(
    crop_name: str,
    weather: Optional[WeatherSummary],
    kb: Dict[str, DiseaseEntry]
) -> RiskAssessment:
    """For a healthy plant, evaluate regional weather susceptibility to common diseases of that crop."""
    crop_diseases = [d for d in kb.values() if d.crop.lower() in crop_name.lower() and not d.is_healthy]
    
    threat_scores = []
    for d in crop_diseases:
        assessment = evaluate_disease_risk(d.id, weather)
        threat_scores.append({
            "disease_id": d.id,
            "disease_name": d.disease_name,
            "scientific_name": d.scientific_name,
            "causal_agent_type": d.causal_agent_type,
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "risk_color": assessment.risk_color,
            "headline": assessment.headline,
            "summary": assessment.summary,
            "prevention_steps": d.prevention_steps[:2]
        })
        
    threat_scores.sort(key=lambda x: x["risk_score"], reverse=True)
    
    top_score = threat_scores[0]["risk_score"] if threat_scores else 20
    top_disease = threat_scores[0]["disease_name"] if threat_scores else "Foliar Blights"
    
    if top_score >= 70:
        level = "HIGH"
        color = "#f97316"
        headline = f"Preventative Advisory: High Weather Threat for {top_disease}"
        summary = f"Although this leaf sample is healthy, current regional weather is highly favorable for {top_disease}. Preventative scouting advised."
    elif top_score >= 40:
        level = "MODERATE"
        color = "#eab308"
        headline = f"Preventative Advisory: Moderate Threat for {top_disease}"
        summary = f"Leaf is healthy. Monitor for early symptoms of {top_disease} under current humidity and temperature."
    else:
        level = "LOW"
        color = "#22c55e"
        headline = f"Healthy Crop Foliage - Low Disease Pressure"
        summary = "No immediate elevated weather outbreak risks detected. Maintain standard agronomic practices."

    daily_outlook: List[DailyRiskOutlook] = []
    if weather and weather.daily_forecasts:
        for day in weather.daily_forecasts:
            day_score = 30 if day.humidity_mean_pct >= 80 else 15
            day_level = "MODERATE" if day_score >= 30 else "LOW"
            daily_outlook.append(DailyRiskOutlook(
                date=day.date,
                risk_score=day_score,
                risk_level=day_level,
                favorable_factors=[f"RH: {day.humidity_mean_pct:.0f}%"]
            ))

    return RiskAssessment(
        crop=crop_name,
        target_condition=f"Healthy {crop_name}",
        risk_score=top_score,
        risk_level=level,
        risk_color=color,
        headline=headline,
        summary=summary,
        contributing_factors=[
            ContributingFactor(
                factor_name="Crop Foliage Verified Healthy",
                impact="REDUCES_RISK",
                explanation=f"Visual diagnostic confirmed no active lesion or necrosis on the submitted {crop_name} foliage."
            ),
            ContributingFactor(
                factor_name=f"Top Weather Susceptibility: {top_disease}",
                impact="ELEVATES_RISK" if top_score >= 50 else "NEUTRAL",
                explanation=f"Regional weather patterns indicate {top_disease} is the highest environmental threat for {crop_name} at this time."
            )
        ],
        daily_outlook=daily_outlook,
        top_regional_threats=threat_scores[:3]
    )
