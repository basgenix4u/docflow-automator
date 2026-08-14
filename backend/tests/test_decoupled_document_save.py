import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app


@pytest.mark.asyncio
async def test_auto_generate_decoupled_document_pipeline(tmp_path):
    pdf_path = Path(settings.STORAGE_DIR) / "FUW_CRG_TEST_A4.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test document")

    with patch(
        "app.api.documents.run_portal_document_solver",
        new=AsyncMock(return_value=str(pdf_path)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            payload = {
                "username": "TEST/STU/00/001",
                "password": "not-a-real-password",
                "document_type": "crg",
                "paper_format": "A4",
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
