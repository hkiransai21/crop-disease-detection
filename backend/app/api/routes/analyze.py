"""Crop disease image analysis and outbreak risk diagnosis endpoint."""
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.schemas.analysis import AnalysisResponse, PredictionItem
from backend.app.schemas.weather import WeatherSummary, DailyForecast
from backend.app.api.deps import get_optional_current_user, get_current_user, limiter
from backend.app.services.image_storage import validate_and_process_image
from backend.app.services.weather import fetch_weather_summary
from backend.app.services.risk import evaluate_disease_risk, load_knowledge_base
from backend.app.ml.inference import predict_disease

router = APIRouter(tags=["Crop Disease Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
@limiter.limit(settings.RATE_LIMIT_ANALYZE)
async def analyze_crop_image(
    request: Request,
    image: UploadFile = File(..., description="Crop leaf image file"),
    latitude: Optional[float] = Form(None, description="GPS Latitude (-90 to 90)"),
    longitude: Optional[float] = Form(None, description="GPS Longitude (-180 to 180)"),
    location_name: Optional[str] = Form(None, description="Optional city / district name"),
    manual_temp_c: Optional[float] = Form(None, description="Manual temperature fallback"),
    manual_humidity_pct: Optional[float] = Form(None, description="Manual relative humidity fallback"),
    manual_rainfall_mm: Optional[float] = Form(None, description="Manual 7-day rainfall fallback"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Primary Diagnosis Endpoint:
    1. Validates and strips EXIF privacy data from uploaded image.
    2. Runs high-performance ONNX neural network inference for top-k disease predictions and entropy uncertainty detection.
    3. Fetches live environmental/weather data from Open-Meteo for the farmer's coordinates.
    4. Computes rule-based transparent outbreak risk score (0-100) and contributing weather factors.
    5. Retrieves curated university extension prevention and treatment protocols.
    6. Persists analysis to user history if authenticated.
    """
    if not image.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    file_bytes = await image.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 1. Image processing & EXIF stripping
    saved_path, clean_pil_image, width, height = validate_and_process_image(file_bytes, image.filename)

    # 2. Run ML inference in threadpool
    loop = asyncio.get_running_loop()
    pred_result = await loop.run_in_executor(None, predict_disease, clean_pil_image, 3)

    # 3. Weather Integration
    weather_summary: Optional[WeatherSummary] = None
    if latitude is not None and longitude is not None:
        try:
            weather_summary = await fetch_weather_summary(latitude, longitude)
        except Exception as e:
            print(f"Weather fetch exception: {e}")
    elif manual_temp_c is not None and manual_humidity_pct is not None:
        # Construct manual weather summary
        weather_summary = WeatherSummary(
            current_temp_c=manual_temp_c,
            current_humidity_pct=manual_humidity_pct,
            current_precipitation_mm=manual_rainfall_mm or 0.0,
            past_7d_mean_temp_c=manual_temp_c,
            past_7d_mean_humidity_pct=manual_humidity_pct,
            past_7d_total_rain_mm=manual_rainfall_mm or 0.0,
            past_7d_high_humidity_hours=24 if manual_humidity_pct >= 85 else 4,
            forecast_7d_mean_temp_c=manual_temp_c,
            forecast_7d_mean_humidity_pct=manual_humidity_pct,
            forecast_7d_total_rain_mm=manual_rainfall_mm or 0.0,
            daily_forecasts=[],
            data_source="Manual Farmer Input",
            is_live=False
        )

    # 4. Outbreak Risk Assessment
    risk_assessment = evaluate_disease_risk(pred_result["predicted_label"], weather_summary)

    # 5. Knowledge Base details
    kb = load_knowledge_base()
    disease_entry = kb.get(pred_result["predicted_label"])

    # Build image URL
    file_rel = saved_path.replace("\\", "/").replace("./backend/app", "").replace("backend/app", "")
    if not file_rel.startswith("/"):
        file_rel = "/" + file_rel
    image_url = f"/static{file_rel}" if not file_rel.startswith("/static") else file_rel

    # 6. Persist to Database if user is authenticated
    analysis_id = "guest_" + pred_result["model_version"]
    if current_user:
        analysis_record = Analysis(
            user_id=current_user.id,
            image_path=saved_path,
            original_filename=image.filename,
            predicted_label=pred_result["predicted_label"],
            confidence=pred_result["confidence"],
            is_uncertain=pred_result["is_uncertain"],
            top_k=pred_result["top_k"],
            model_version=pred_result["model_version"],
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            weather_snapshot=weather_summary.model_dump() if weather_summary else None,
            risk_assessment=risk_assessment.model_dump()
        )
        db.add(analysis_record)
        await db.commit()
        await db.refresh(analysis_record)
        analysis_id = analysis_record.id

    from datetime import datetime, timezone
    return AnalysisResponse(
        id=analysis_id,
        predicted_label=pred_result["predicted_label"],
        crop=pred_result["crop"],
        disease_name=pred_result["disease_name"],
        confidence=pred_result["confidence"],
        confidence_display=pred_result["confidence_display"],
        is_uncertain=pred_result["is_uncertain"],
        uncertainty_reason=pred_result["uncertainty_reason"],
        top_k=[PredictionItem(**item) for item in pred_result["top_k"]],
        model_version=pred_result["model_version"],
        image_url=image_url,
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        weather_summary=weather_summary,
        risk_assessment=risk_assessment,
        disease_details=disease_entry,
        created_at=datetime.now(timezone.utc)
    )
