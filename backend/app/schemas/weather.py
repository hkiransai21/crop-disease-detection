"""Pydantic schemas for weather and geocoding responses."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HourlyWeather(BaseModel):
    time: List[str]
    temperature_2m: List[float]
    relative_humidity_2m: List[float]
    precipitation: List[float]
    surface_pressure: Optional[List[float]] = None
    wind_speed_10m: Optional[List[float]] = None


class DailyForecast(BaseModel):
    date: str
    temp_max_c: float
    temp_min_c: float
    temp_mean_c: float
    humidity_mean_pct: float
    precipitation_sum_mm: float
    high_humidity_hours: int = Field(0, description="Hours with RH >= 85%")
    wetness_risk_level: str = "LOW"


class WeatherSummary(BaseModel):
    current_temp_c: float
    current_humidity_pct: float
    current_precipitation_mm: float
    past_7d_mean_temp_c: float
    past_7d_mean_humidity_pct: float
    past_7d_total_rain_mm: float
    past_7d_high_humidity_hours: int
    forecast_7d_mean_temp_c: float
    forecast_7d_mean_humidity_pct: float
    forecast_7d_total_rain_mm: float
    daily_forecasts: List[DailyForecast]
    data_source: str = "Open-Meteo API"
    is_live: bool = True


class GeocodingResult(BaseModel):
    id: Optional[int] = None
    name: str
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    country: Optional[str] = None
    admin1: Optional[str] = None
