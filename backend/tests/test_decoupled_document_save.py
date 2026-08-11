import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_auto_generate_decoupled_document_pipeline():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "username": "ENG/COE/21/013",
            "password": "olaleke",
            "document_type": "crg",
            "paper_format": "A4"
        }
        response = await ac.post("/api/v1/documents/auto-generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["page_format"] == "A4"
        assert data["page_count"] == 1
        assert "Completed Course Registration Form" in data["title"]
        assert "view_url" in data
        assert "download_url" in data

        doc_id = data["id"]
        res_view = await ac.get(f"/api/v1/documents/{doc_id}/view")
        assert res_view.status_code in (200, 307, 302)
