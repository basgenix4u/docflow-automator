import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_user_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register new engineer
        reg_payload = {
            "email": "test_engineer@docflow.io",
            "full_name": "Test QA Engineer",
            "password": "SecurePassword123!",
            "role": "ENGINEER"
        }
        res_reg = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 200
        reg_data = res_reg.json()
        assert reg_data["email"] == "test_engineer@docflow.io"

        # Login
        login_payload = {
            "email": "test_engineer@docflow.io",
            "password": "SecurePassword123!"
        }
        res_login = await ac.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200
        login_data = res_login.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        # Fetch /me
        res_me = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        me_data = res_me.json()
        assert me_data["email"] == "test_engineer@docflow.io"
