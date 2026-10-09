"""API tests for health, ready, model info, diseases, and Prometheus metrics."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_and_ready_endpoints(client: AsyncClient):
    h_res = await client.get("/api/v1/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "healthy"

    r_res = await client.get("/api/v1/ready")
    assert r_res.status_code == 200
    assert "status" in r_res.json()


@pytest.mark.asyncio
async def test_model_info_endpoint(client: AsyncClient):
    m_res = await client.get("/api/v1/model/info")
    assert m_res.status_code == 200
    m_data = m_res.json()
    assert "model_version" in m_data
    assert "architecture" in m_data
    assert m_data["num_classes"] == 38


@pytest.mark.asyncio
async def test_diseases_encyclopedia_endpoints(client: AsyncClient):
    # List all
    d_res = await client.get("/api/v1/diseases")
    assert d_res.status_code == 200
    diseases = d_res.json()
    assert len(diseases) >= 38

    # Filter by crop
    tomato_res = await client.get("/api/v1/diseases?crop=Tomato")
    assert tomato_res.status_code == 200
    assert all("tomato" in d["crop"].lower() for d in tomato_res.json())

    # Get single entry
    single_res = await client.get("/api/v1/diseases/Tomato___Early_blight")
    assert single_res.status_code == 200
    assert single_res.json()["disease_name"] == "Early Blight"


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(client: AsyncClient):
    metrics_res = await client.get("/metrics")
    assert metrics_res.status_code == 200
    assert "http_requests_total" in metrics_res.text or "http_request_duration_seconds" in metrics_res.text or "process_cpu_seconds_total" in metrics_res.text
