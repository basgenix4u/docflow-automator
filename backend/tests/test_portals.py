import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_portals_and_workflows_listing():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # List portals
        res = await ac.get("/api/v1/portals/")
        assert res.status_code == 200
        portals = res.json()
        assert len(portals) >= 1
        fuw_portal = next((p for p in portals if "fuwportal" in p["base_url"]), None)
        assert fuw_portal is not None
        assert fuw_portal["demo_username"] == "BSC/BCH/24/140"

        # List workflows
        res_wf = await ac.get("/api/v1/workflows/")
        assert res_wf.status_code == 200
        workflows = res_wf.json()
        assert len(workflows) >= 1
