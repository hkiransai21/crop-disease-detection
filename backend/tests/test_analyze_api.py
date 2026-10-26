"""API integration tests for /api/v1/analyze endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_crop_image_guest_flow(client: AsyncClient, sample_leaf_image_bytes: bytes):
    """Verify guest user can analyze image and receive predictions + risk score."""
    files = {
        "image": ("leaf.jpg", sample_leaf_image_bytes, "image/jpeg")
    }
    data = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "location_name": "San Francisco Farm"
    }

    response = await client.post("/api/v1/analyze", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()

    assert "predicted_label" in res_data
    assert "confidence" in res_data
    assert "top_k" in res_data
    assert len(res_data["top_k"]) == 3
    assert "risk_assessment" in res_data
    if res_data['weather_status'] == 'unavailable':
        assert res_data['risk_assessment'] is None
    elif res_data['risk_assessment'] is not None:
        assert res_data['risk_assessment']['risk_score'] >= 0
    assert "disease_details" in res_data


@pytest.mark.asyncio
async def test_analyze_crop_image_authenticated_flow(
    client: AsyncClient,
    sample_leaf_image_bytes: bytes,
    auth_headers: dict
):
    """Verify authenticated user analysis is persisted into database history."""
    files = {
        "image": ("sample.jpg", sample_leaf_image_bytes, "image/jpeg")
    }
    data = {
        "manual_temp_c": 22.5,
        "manual_humidity_pct": 82.0,
        "manual_rainfall_mm": 12.0
    }

    response = await client.post("/api/v1/analyze", files=files, data=data, headers=auth_headers)
    assert response.status_code == 200
    res_data = response.json()
    analysis_id = res_data["id"]

    # Fetch history to verify persistence
    hist_res = await client.get("/api/v1/history", headers=auth_headers)
    assert hist_res.status_code == 200
    history_items = hist_res.json()
    assert any(h["id"] == analysis_id for h in history_items)


@pytest.mark.asyncio
async def test_analyze_invalid_small_image(client: AsyncClient, tiny_invalid_image_bytes: bytes):
    """Verify rejection of images smaller than 32x32."""
    files = {
        "image": ("tiny.jpg", tiny_invalid_image_bytes, "image/jpeg")
    }
    response = await client.post("/api/v1/analyze", files=files)
    assert response.status_code == 400
    assert "too small" in response.json()["detail"].lower()
