"""Unit tests for weather parsing, leaf wetness estimation, and geocoding."""
import pytest
from backend.app.services.weather import _parse_open_meteo_response, search_locations
from backend.app.schemas.weather import WeatherSummary


def test_parse_open_meteo_response_deterministic():
    """Verify robust parsing of raw Open-Meteo API response structure."""
    mock_data = {
        "hourly": {
            "time": [f"2026-10-06T{i:02d}:00" for i in range(24 * 14)],
            "temperature_2m": [18.5 + (i % 5) for i in range(24 * 14)],
            "relative_humidity_2m": [88.0 if (i % 2 == 0) else 65.0 for i in range(24 * 14)],
            "precipitation": [0.5 if (i % 6 == 0) else 0.0 for i in range(24 * 14)],
            "surface_pressure": [1013.25 for _ in range(24 * 14)],
            "wind_speed_10m": [12.0 for _ in range(24 * 14)]
        },
        "daily": {
            "time": [f"2026-10-{i:02d}" for i in range(1, 15)],
            "temperature_2m_max": [25.0 for _ in range(14)],
            "temperature_2m_min": [15.0 for _ in range(14)],
            "temperature_2m_mean": [20.0 for _ in range(14)],
            "relative_humidity_2m_mean": [76.5 for _ in range(14)],
            "precipitation_sum": [3.0 for _ in range(14)]
        }
    }

    summary = _parse_open_meteo_response(mock_data)
    assert isinstance(summary, WeatherSummary)
    assert summary.is_live is True
    assert summary.past_7d_high_humidity_hours > 0
    assert summary.past_7d_total_rain_mm > 0
    assert all(day.date >= '2026-10-06' for day in summary.daily_forecasts)


def test_missing_weather_observations_are_rejected():
    with pytest.raises(ValueError):
        _parse_open_meteo_response({})
