"""Weather and place-name geocoding endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from backend.app.schemas.weather import WeatherSummary, GeocodingResult
from backend.app.services.weather import fetch_weather_summary, search_locations

router = APIRouter(tags=["Weather & Geocoding"])


@router.get("/weather", response_model=WeatherSummary)
async def get_weather_forecast(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude")
):
    """Fetch 7-day past environmental telemetry and 7-day daily forecast for coordinates."""
    return await fetch_weather_summary(lat, lon)


@router.get("/geocode", response_model=List[GeocodingResult])
async def geocode_place_search(
    q: str = Query(..., min_length=2, description="Place or town name to search")
):
    """Search for locations and coordinates by name via Open-Meteo Geocoding."""
    return await search_locations(q)
