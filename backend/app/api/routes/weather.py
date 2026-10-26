"""Weather and place-name geocoding endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from backend.app.schemas.weather import WeatherSummary, GeocodingResult
from backend.app.services.weather import fetch_weather_summary, search_locations

router = APIRouter(tags=["Weather & Geocoding"])


@router.get('/risk')
async def get_live_risk(class_id: str, lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180), lang: str = 'en'):
    from backend.app.services.risk import evaluate_disease_risk
    from backend.app.services.i18n import canonical_class_key, localize_risk_assessment
    try:
        canonical_class_key(class_id)
    except KeyError:
        raise HTTPException(404, detail='The requested record was not found.')
    weather = await get_weather_forecast(lat, lon)
    return localize_risk_assessment(evaluate_disease_risk(class_id, weather), lang)


@router.get("/weather", response_model=WeatherSummary)
async def get_weather_forecast(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude")
):
    """Fetch 7-day past environmental telemetry and 7-day daily forecast for coordinates."""
    try:
        return await fetch_weather_summary(lat, lon)
    except Exception:
        raise HTTPException(503, detail='The service is unavailable. Please try again later.')


@router.get("/geocode", response_model=List[GeocodingResult])
async def geocode_place_search(
    q: str = Query(..., min_length=2, description="Place or town name to search")
):
    """Search for locations and coordinates by name via Open-Meteo Geocoding."""
    return await search_locations(q)
