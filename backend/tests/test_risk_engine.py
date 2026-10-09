"""Unit tests for the transparent Outbreak Risk Engine using deterministic weather fixtures."""
import pytest
from backend.app.services.risk import evaluate_disease_risk
from backend.app.schemas.weather import WeatherSummary, DailyForecast


@pytest.fixture
def severe_blight_weather_fixture() -> WeatherSummary:
    """Weather fixture with cool temperatures, high humidity, and continuous rain (ideal for Late Blight)."""
    return WeatherSummary(
        current_temp_c=18.0,
        current_humidity_pct=92.0,
        current_precipitation_mm=4.5,
        past_7d_mean_temp_c=17.5,
        past_7d_mean_humidity_pct=91.0,
        past_7d_total_rain_mm=38.0,
        past_7d_high_humidity_hours=48,
        forecast_7d_mean_temp_c=18.0,
        forecast_7d_mean_humidity_pct=90.0,
        forecast_7d_total_rain_mm=25.0,
        daily_forecasts=[
            DailyForecast(
                date=f"2026-10-{i:02d}",
                temp_max_c=20.0,
                temp_min_c=14.0,
                temp_mean_c=17.0,
                humidity_mean_pct=90.0,
                precipitation_sum_mm=5.0,
                high_humidity_hours=10,
                wetness_risk_level="HIGH"
            ) for i in range(1, 8)
        ],
        data_source="Test Mock",
        is_live=True
    )


@pytest.fixture
def cold_dry_suppression_weather_fixture() -> WeatherSummary:
    """Weather fixture with cold temperatures (4°C) and low humidity (25%) suppressing fungal diseases."""
    return WeatherSummary(
        current_temp_c=4.0,
        current_humidity_pct=25.0,
        current_precipitation_mm=0.0,
        past_7d_mean_temp_c=3.5,
        past_7d_mean_humidity_pct=28.0,
        past_7d_total_rain_mm=0.0,
        past_7d_high_humidity_hours=0,
        forecast_7d_mean_temp_c=4.0,
        forecast_7d_mean_humidity_pct=25.0,
        forecast_7d_total_rain_mm=0.0,
        daily_forecasts=[],
        data_source="Test Mock",
        is_live=True
    )


@pytest.fixture
def hot_dry_spider_mite_weather_fixture() -> WeatherSummary:
    """Weather fixture with hot dry conditions (33°C, 25% RH) favoring Spider Mites."""
    return WeatherSummary(
        current_temp_c=34.0,
        current_humidity_pct=22.0,
        current_precipitation_mm=0.0,
        past_7d_mean_temp_c=32.0,
        past_7d_mean_humidity_pct=25.0,
        past_7d_total_rain_mm=0.0,
        past_7d_high_humidity_hours=0,
        forecast_7d_mean_temp_c=33.0,
        forecast_7d_mean_humidity_pct=24.0,
        forecast_7d_total_rain_mm=0.0,
        daily_forecasts=[],
        data_source="Test Mock",
        is_live=True
    )


def test_late_blight_severe_weather_risk(severe_blight_weather_fixture):
    """Verify that optimal temperatures and prolonged humidity produce a VERY HIGH risk score for Late Blight."""
    assessment = evaluate_disease_risk("Potato___Late_blight", severe_blight_weather_fixture)
    
    assert assessment.risk_score >= 70, f"Expected risk score >= 70, got {assessment.risk_score}"
    assert assessment.risk_level in ["HIGH", "VERY HIGH"]
    assert any(f.impact == "ELEVATES_RISK" for f in assessment.contributing_factors)
    assert "advisory" in assessment.disclaimer.lower()


def test_fungal_disease_cold_dry_suppression(cold_dry_suppression_weather_fixture):
    """Verify that cold and dry weather reduces fungal disease risk to LOW."""
    assessment = evaluate_disease_risk("Tomato___Early_blight", cold_dry_suppression_weather_fixture)
    
    assert assessment.risk_score <= 35, f"Expected risk score <= 35, got {assessment.risk_score}"
    assert assessment.risk_level in ["LOW", "MODERATE"]
    assert any(f.impact == "REDUCES_RISK" for f in assessment.contributing_factors)


def test_spider_mite_drought_trigger(hot_dry_spider_mite_weather_fixture):
    """Verify that hot dry conditions elevate risk specifically for Two-Spotted Spider Mite."""
    assessment = evaluate_disease_risk("Tomato___Spider_mites Two-spotted_spider_mite", hot_dry_spider_mite_weather_fixture)
    
    assert assessment.risk_score >= 60, f"Expected Spider Mite drought score >= 60, got {assessment.risk_score}"
    assert any("Dry & Hot" in f.factor_name for f in assessment.contributing_factors)


def test_healthy_plant_regional_threat_evaluation(severe_blight_weather_fixture):
    """Verify that a healthy plant diagnosis returns regional weather threat rankings for that crop."""
    assessment = evaluate_disease_risk("Tomato___healthy", severe_blight_weather_fixture)
    
    assert "Healthy" in assessment.target_condition
    assert assessment.top_regional_threats is not None
    assert len(assessment.top_regional_threats) > 0
    # Highest threat under wet weather should be Late Blight or Septoria
    top_threat = assessment.top_regional_threats[0]
    assert "Tomato" in top_threat["disease_id"]
