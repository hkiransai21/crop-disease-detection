"""Weather and Geocoding service integrating Open-Meteo APIs with async httpx and TTL caching."""
import time
from typing import Dict, Any, List, Optional, Tuple
import httpx
from backend.app.core.config import settings
from backend.app.schemas.weather import WeatherSummary, DailyForecast, GeocodingResult

# In-memory TTL Cache
_WEATHER_CACHE: Dict[str, Tuple[float, WeatherSummary]] = {}
_GEOCODING_CACHE: Dict[str, Tuple[float, List[GeocodingResult]]] = {}


def _get_cache_key(lat: float, lon: float) -> str:
    return f"{round(lat, 3)}_{round(lon, 3)}"


async def search_locations(query: str, count: int = 5) -> List[GeocodingResult]:
    """Search for locations by name using Open-Meteo Geocoding API."""
    clean_query = query.strip().lower()
    now = time.time()
    
    if clean_query in _GEOCODING_CACHE:
        cached_time, cached_results = _GEOCODING_CACHE[clean_query]
        if now - cached_time < settings.WEATHER_CACHE_TTL_SECONDS:
            return cached_results
            
    url = f"{settings.GEOCODING_BASE_URL}/search"
    params = {
        "name": query.strip(),
        "count": count,
        "language": "en",
        "format": "json"
    }
    
    results: List[GeocodingResult] = []
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("results", []):
                    results.append(GeocodingResult(
                        id=item.get("id"),
                        name=item.get("name"),
                        latitude=item.get("latitude"),
                        longitude=item.get("longitude"),
                        elevation=item.get("elevation"),
                        country=item.get("country"),
                        admin1=item.get("admin1")
                    ))
    except Exception as e:
        print(f"Geocoding API error: {e}")
        
    _GEOCODING_CACHE[clean_query] = (now, results)
    return results


async def fetch_weather_summary(latitude: float, longitude: float) -> WeatherSummary:
    """Fetch 7 days of past weather and 7 days of forecast from Open-Meteo API."""
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError('Invalid coordinates')
    cache_key = _get_cache_key(latitude, longitude)
    now = time.time()
    
    if cache_key in _WEATHER_CACHE:
        cached_time, cached_data = _WEATHER_CACHE[cache_key]
        if now - cached_time < settings.WEATHER_CACHE_TTL_SECONDS:
            return cached_data
            
    url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
    params = {
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,surface_pressure,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,relative_humidity_2m_mean,precipitation_sum",
        "past_days": 7,
        "forecast_days": 7,
        "timezone": "auto"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
        summary = _parse_open_meteo_response(data)
        _WEATHER_CACHE[cache_key] = (now, summary)
        return summary
    except Exception as e:
        raise


def _parse_open_meteo_response(data: Dict[str, Any]) -> WeatherSummary:
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})
    
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    precips = hourly.get("precipitation", [])
    
    if not temps or len(temps) != len(humidities) or len(temps) != len(precips) or any(v is None for values in (temps, humidities, precips) for v in values):
        raise ValueError('Incomplete weather observations')
    current = data.get('current', {})
    current_time = current.get('time')
    current_idx = next((i for i, t in enumerate(times) if current_time and t >= current_time[:13] + ':00'), min(7 * 24, len(temps) - 1))
    current_temp = float(temps[current_idx]) if temps else 22.0
    current_humidity = float(humidities[current_idx]) if humidities else 65.0
    current_precip = float(precips[current_idx]) if precips else 0.0
    
    # Past 7 days statistics (first 7*24 hours)
    past_hours = current_idx
    past_temps = temps[:past_hours] if len(temps) >= past_hours else temps
    past_humidities = humidities[:past_hours] if len(humidities) >= past_hours else humidities
    past_precips = precips[:past_hours] if len(precips) >= past_hours else precips
    
    past_7d_mean_temp = float(sum(past_temps) / len(past_temps)) if past_temps else current_temp
    past_7d_mean_humidity = float(sum(past_humidities) / len(past_humidities)) if past_humidities else current_humidity
    past_7d_total_rain = float(sum(past_precips)) if past_precips else 0.0
    past_7d_high_humidity_hours = sum(1 for h in past_humidities if h >= 85.0)
    
    # Forecast 7 days statistics
    fc_temps = temps[past_hours:] if len(temps) > past_hours else temps
    fc_humidities = humidities[past_hours:] if len(humidities) > past_hours else humidities
    fc_precips = precips[past_hours:] if len(precips) > past_hours else precips
    
    fc_mean_temp = float(sum(fc_temps) / len(fc_temps)) if fc_temps else current_temp
    fc_mean_humidity = float(sum(fc_humidities) / len(fc_humidities)) if fc_humidities else current_humidity
    fc_total_rain = float(sum(fc_precips)) if fc_precips else 0.0
    
    # Parse daily forecasts
    daily_dates = daily.get("time", [])
    daily_tmax = daily.get("temperature_2m_max", [])
    daily_tmin = daily.get("temperature_2m_min", [])
    daily_tmean = daily.get("temperature_2m_mean", [])
    daily_hmean = daily.get("relative_humidity_2m_mean", [])
    daily_precip = daily.get("precipitation_sum", [])
    
    daily_forecasts: List[DailyForecast] = []
    for i in range(len(daily_dates)):
        if times and daily_dates[i] < times[current_idx][:10]:
            continue
        d_tmean = float(daily_tmean[i]) if i < len(daily_tmean) and daily_tmean[i] is not None else 20.0
        d_hmean = float(daily_hmean[i]) if i < len(daily_hmean) and daily_hmean[i] is not None else 60.0
        d_rain = float(daily_precip[i]) if i < len(daily_precip) and daily_precip[i] is not None else 0.0
        
        # Approximate high humidity hours
        high_h_hrs = 8 if d_hmean >= 80 else (4 if d_hmean >= 65 else 1)
        
        wetness_risk = "HIGH" if (d_hmean >= 85 or d_rain > 5.0) else ("MODERATE" if (d_hmean >= 70 or d_rain > 1.0) else "LOW")
        
        daily_forecasts.append(DailyForecast(
            date=daily_dates[i],
            temp_max_c=float(daily_tmax[i]) if i < len(daily_tmax) and daily_tmax[i] is not None else d_tmean + 4.0,
            temp_min_c=float(daily_tmin[i]) if i < len(daily_tmin) and daily_tmin[i] is not None else d_tmean - 4.0,
            temp_mean_c=d_tmean,
            humidity_mean_pct=d_hmean,
            precipitation_sum_mm=d_rain,
            high_humidity_hours=high_h_hrs,
            wetness_risk_level=wetness_risk
        ))
        
    winds = hourly.get('wind_speed_10m', [])
    recent_rain = precips[max(0, current_idx-72):current_idx]
    future_rain = precips[current_idx:current_idx+48]
    future_winds = [v for v in winds[current_idx:current_idx+48] if v is not None]
    return WeatherSummary(
        past_72h_rain_mm=round(sum(recent_rain), 2),
        forecast_48h_rain_mm=round(sum(future_rain), 2),
        past_72h_wet_hours=sum(1 for h,p in zip(humidities[max(0,current_idx-72):current_idx], recent_rain) if h >= 85 or p > 0),
        forecast_48h_wind_kmh=round(sum(future_winds)/len(future_winds), 1) if future_winds else None,
        current_temp_c=round(current_temp, 1),
        current_humidity_pct=round(current_humidity, 1),
        current_precipitation_mm=round(current_precip, 2),
        past_7d_mean_temp_c=round(past_7d_mean_temp, 1),
        past_7d_mean_humidity_pct=round(past_7d_mean_humidity, 1),
        past_7d_total_rain_mm=round(past_7d_total_rain, 1),
        past_7d_high_humidity_hours=past_7d_high_humidity_hours,
        forecast_7d_mean_temp_c=round(fc_mean_temp, 1),
        forecast_7d_mean_humidity_pct=round(fc_mean_humidity, 1),
        forecast_7d_total_rain_mm=round(fc_total_rain, 1),
        daily_forecasts=daily_forecasts,
        data_source="Open-Meteo API",
        is_live=True
    )
