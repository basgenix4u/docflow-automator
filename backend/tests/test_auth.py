import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_user_register_and_login():
    unique_email = f"test_{uuid.uuid4().hex[:6]}@docflow.io"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg_payload = {
            "email": unique_email,
            "full_name": "Test QA Engineer",
            "password": "SecurePassword123!",
            "role": "ENGINEER",
        }
        res_reg = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 200
        reg_data = res_reg.json()
        assert reg_data["email"] == unique_email
        assert reg_data["role"] == "ENGINEER"

        login_payload = {"email": unique_email, "password": "SecurePassword123!"}
        res_login = await ac.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200
        login_data = res_login.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        res_me = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        me_data = res_me.json()
        assert me_data["email"] == unique_email


@pytest.mark.asyncio
async def test_register_cannot_self_assign_admin():
    unique_email = f"admintry_{uuid.uuid4().hex[:6]}@docflow.io"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "full_name": "Attacker",
                "password": "SecurePassword123!",
                "role": "ADMIN",
            },
        )
        assert res.status_code == 200
        assert res.json()["role"] == "ENGINEER"


@pytest.mark.asyncio
async def test_login_rejects_bad_password():
    unique_email = f"badpw_{uuid.uuid4().hex[:6]}@docflow.io"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "full_name": "User",
                "password": "SecurePassword123!",
            },
        )
        res = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "wrong-password"},
        )
        assert res.status_code == 401
