import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def _register_and_login(ac: AsyncClient) -> str:
    email = f"op_{uuid.uuid4().hex[:8]}@docflow.io"
    await ac.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Operator", "password": "SecurePassword123!"},
    )
    login = await ac.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_operator_routes_require_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        assert (await ac.get("/api/v1/documents/")).status_code == 401
        assert (await ac.get("/api/v1/runs/")).status_code == 401
        assert (await ac.get("/api/v1/security/")).status_code == 401
        assert (
            await ac.post(
                "/api/v1/portals/",
                json={"name": "X", "base_url": "https://example.edu"},
            )
        ).status_code == 401


@pytest.mark.asyncio
async def test_operator_can_list_documents_and_create_portal():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = await _register_and_login(ac)
        headers = {"Authorization": f"Bearer {token}"}

        docs = await ac.get("/api/v1/documents/", headers=headers)
        assert docs.status_code == 200
        assert isinstance(docs.json(), list)

        created = await ac.post(
            "/api/v1/portals/",
            headers=headers,
            json={"name": "Example Portal", "base_url": "https://example.edu/login"},
        )
        assert created.status_code == 200
        body = created.json()
        assert body["name"] == "Example Portal"
        assert "demo_password" not in body
