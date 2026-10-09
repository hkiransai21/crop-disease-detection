"""API tests for diagnosis history listing, detail, deletion, and cross-user isolation."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_history_crud_and_user_isolation(
    client: AsyncClient,
    sample_leaf_image_bytes: bytes,
    auth_headers: dict,
    auth_headers_user2: dict
):
    # 1. User 1 submits an analysis
    files = {"image": ("leaf.jpg", sample_leaf_image_bytes, "image/jpeg")}
    post_res = await client.post("/api/v1/analyze", files=files, headers=auth_headers)
    assert post_res.status_code == 200
    u1_analysis_id = post_res.json()["id"]

    # 2. User 1 can see their analysis in history
    u1_hist = await client.get("/api/v1/history", headers=auth_headers)
    assert u1_hist.status_code == 200
    assert any(item["id"] == u1_analysis_id for item in u1_hist.json())

    # 3. User 2 CANNOT see User 1's analysis in their history list (isolation)
    u2_hist = await client.get("/api/v1/history", headers=auth_headers_user2)
    assert u2_hist.status_code == 200
    assert not any(item["id"] == u1_analysis_id for item in u2_hist.json())

    # 4. User 2 CANNOT fetch User 1's detail (404/unauthorized isolation)
    u2_get = await client.get(f"/api/v1/history/{u1_analysis_id}", headers=auth_headers_user2)
    assert u2_get.status_code == 404

    # 5. User 1 can fetch their detail
    u1_get = await client.get(f"/api/v1/history/{u1_analysis_id}", headers=auth_headers)
    assert u1_get.status_code == 200
    assert u1_get.json()["id"] == u1_analysis_id

    # 6. User 1 deletes their record
    del_res = await client.delete(f"/api/v1/history/{u1_analysis_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 7. Record is no longer present
    after_del = await client.get(f"/api/v1/history/{u1_analysis_id}", headers=auth_headers)
    assert after_del.status_code == 404
