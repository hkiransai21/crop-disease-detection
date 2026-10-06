"""Unit and API tests for user registration, JWT authentication, /me, and deletion."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # 1. Register
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newfarmer@example.com",
            "password": "strongpassword123",
            "full_name": "New Farmer"
        }
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["email"] == "newfarmer@example.com"
    assert "id" in reg_data

    # 2. Duplicate registration fails
    dup_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newfarmer@example.com",
            "password": "strongpassword123"
        }
    )
    assert dup_res.status_code == 400

    # 3. Login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "newfarmer@example.com",
            "password": "strongpassword123"
        }
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 4. Get /me
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "newfarmer@example.com"

    # 5. Delete account
    del_res = await client.delete(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_invalid_login_credentials(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert res.status_code == 401
