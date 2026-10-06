"""API tests for diagnosis feedback submission and retraining consent."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_submit_and_update_feedback(
    client: AsyncClient,
    sample_leaf_image_bytes: bytes,
    auth_headers: dict
):
    # 1. Create analysis
    files = {"image": ("leaf.jpg", sample_leaf_image_bytes, "image/jpeg")}
    post_res = await client.post("/api/v1/analyze", files=files, headers=auth_headers)
    analysis_id = post_res.json()["id"]

    # 2. Submit initial feedback
    fb_res = await client.post(
        f"/api/v1/history/{analysis_id}/feedback",
        json={
            "is_correct": False,
            "corrected_label": "Tomato___Early_blight",
            "comments": "Confirmed with field agronomist on site.",
            "consent_for_retraining": True
        },
        headers=auth_headers
    )
    assert fb_res.status_code == 201
    fb_data = fb_res.json()
    assert fb_data["is_correct"] is False
    assert fb_data["corrected_label"] == "Tomato___Early_blight"

    # 3. Update feedback
    fb_update = await client.post(
        f"/api/v1/history/{analysis_id}/feedback",
        json={
            "is_correct": True,
            "comments": "Re-verified: diagnosis was actually correct.",
            "consent_for_retraining": True
        },
        headers=auth_headers
    )
    assert fb_update.status_code == 201
    assert fb_update.json()["is_correct"] is True
