"""Additional test suite ensuring comprehensive coverage across all routes and services."""
import io
import pytest
from httpx import AsyncClient
from PIL import Image
from backend.app.core.security import create_access_token, create_refresh_token, decode_token
from backend.app.services.image_storage import validate_and_process_image
from backend.app.services.weather import fetch_weather_summary, search_locations
from fastapi import HTTPException, UploadFile


@pytest.mark.asyncio
async def test_auth_refresh_and_invalid_token(client: AsyncClient):
    # 0. Register user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refreshtest@example.com", "password": "securepassword123"}
    )

    # 1. Login to get refresh token
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "refreshtest@example.com", "password": "securepassword123"}
    )
    assert login_res.status_code == 200
    refresh_tok = login_res.json()["refresh_token"]

    # 2. Use refresh token to get new access token
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_tok}
    )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()

    # 3. Invalid refresh token fails
    invalid_refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.jwt.token"}
    )
    assert invalid_refresh.status_code == 401

    # 4. Invalid Bearer header on protected endpoint
    bad_auth = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-token"})
    assert bad_auth.status_code == 401

    # 5. Wrong password for existing user
    wrong_pw = await client.post(
        "/api/v1/auth/login",
        json={"email": "refreshtest@example.com", "password": "incorrectpassword"}
    )
    assert wrong_pw.status_code == 401


@pytest.mark.asyncio
async def test_diseases_api_endpoints(client: AsyncClient):
    # 1. List all diseases
    list_res = await client.get("/api/v1/diseases")
    assert list_res.status_code == 200
    diseases = list_res.json()
    assert len(diseases) == 38

    # 2. Filter by crop
    crop_res = await client.get("/api/v1/diseases?crop=Tomato")
    assert crop_res.status_code == 200
    tomato_diseases = crop_res.json()
    assert len(tomato_diseases) > 0
    assert all(d["crop"] == "Tomato" for d in tomato_diseases)

    # 3. Search query
    search_res = await client.get("/api/v1/diseases?q=blight")
    assert search_res.status_code == 200
    blight_diseases = search_res.json()
    assert len(blight_diseases) > 0

    # 4. Get specific disease by class_name
    one_res = await client.get("/api/v1/diseases/Tomato___Early_blight")
    assert one_res.status_code == 200
    data = one_res.json()
    assert data["id"] == "Tomato___Early_blight"
    assert "prevention_steps" in data
    assert len(data["sources"]) > 0

    # 5. Non-existent disease returns 404
    not_found = await client.get("/api/v1/diseases/NonExistent___Disease")
    assert not_found.status_code == 404


@pytest.mark.asyncio
async def test_weather_and_geocode_routes(client: AsyncClient):
    # 1. Weather endpoint with query params
    res = await client.get("/api/v1/weather?lat=37.77&lon=-122.41")
    assert res.status_code == 200
    w_data = res.json()
    assert "current_temp_c" in w_data
    assert "past_7d_mean_humidity_pct" in w_data

    # 2. Geocoding search endpoint
    geo_res = await client.get("/api/v1/geocode?q=Fresno")
    assert geo_res.status_code == 200
    assert isinstance(geo_res.json(), list)


@pytest.mark.asyncio
async def test_history_and_feedback_edge_cases(
    client: AsyncClient,
    sample_leaf_image_bytes: bytes,
    auth_headers: dict,
    auth_headers_user2: dict
):
    # 1. Delete non-existent history returns 404
    del_404 = await client.delete("/api/v1/history/999999", headers=auth_headers)
    assert del_404.status_code == 404

    # 2. Get non-existent history returns 404
    get_404 = await client.get("/api/v1/history/999999", headers=auth_headers)
    assert get_404.status_code == 404

    # 3. Create analysis for User 1
    files = {"image": ("leaf.jpg", sample_leaf_image_bytes, "image/jpeg")}
    create_res = await client.post("/api/v1/analyze", files=files, headers=auth_headers)
    u1_analysis_id = create_res.json()["id"]

    # 4. User 2 cannot submit feedback for User 1's analysis
    unauth_fb = await client.post(
        f"/api/v1/history/{u1_analysis_id}/feedback",
        json={"is_correct": False, "corrected_label": "Tomato___Early_blight"},
        headers=auth_headers_user2
    )
    assert unauth_fb.status_code == 404

    # 5. Submit feedback for non-existent analysis
    fb_404 = await client.post(
        "/api/v1/history/888888/feedback",
        json={"is_correct": True},
        headers=auth_headers
    )
    assert fb_404.status_code == 404


def test_image_storage_validation():
    # 1. Reject invalid MIME type / extension
    with pytest.raises(HTTPException) as exc_info:
        validate_and_process_image(b"Hello world text file content", "test.txt")
    assert exc_info.value.status_code == 400

    # 2. Reject corrupt image data
    with pytest.raises(HTTPException) as exc_info:
        validate_and_process_image(b"\xff\xd8\xff\xe0notarealjpegimage", "bad.jpg")
    assert exc_info.value.status_code == 400

    # 3. Reject tiny image (<32x32)
    tiny_img = Image.new("RGB", (16, 16), color="green")
    tiny_buf = io.BytesIO()
    tiny_img.save(tiny_buf, format="JPEG")
    with pytest.raises(HTTPException) as exc_info:
        validate_and_process_image(tiny_buf.getvalue(), "tiny.jpg")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_model_info_and_ready(client: AsyncClient):
    # 1. /ready
    ready_res = await client.get("/api/v1/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"

    # 2. /model/info
    info_res = await client.get("/api/v1/model/info")
    assert info_res.status_code == 200
    data = info_res.json()
    assert data["num_classes"] == 38
