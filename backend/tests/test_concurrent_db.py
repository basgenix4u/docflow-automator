import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_concurrent_db_health_and_portals():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Execute 20 concurrent database requests
        tasks = [ac.get("/api/v1/health") for _ in range(10)] + [ac.get("/api/v1/portals/") for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        for res in responses:
            assert res.status_code == 200
            data = res.json()
            if "status" in data:
                assert data["status"] == "online"
                assert data["database_online"] is True
