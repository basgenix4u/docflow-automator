from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.rate_limit import limiter
from app.main import app


@pytest.mark.asyncio
async def test_auto_generate_rate_limited(tmp_path):
    limiter._hits.clear()
    pdf_path = Path(settings.STORAGE_DIR) / "rate_limit.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    original_limit = settings.AUTO_GENERATE_RATE_LIMIT
    settings.AUTO_GENERATE_RATE_LIMIT = 2
    try:
        with patch(
            "app.api.documents.run_portal_document_solver",
            new=AsyncMock(return_value=str(pdf_path)),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                payload = {
                    "username": "TEST/STU/00/002",
                    "password": "not-a-real-password",
                    "document_type": "exam",
                    "paper_format": "A5",
                }
                assert (await ac.post("/api/v1/documents/auto-generate", json=payload)).status_code == 200
                assert (await ac.post("/api/v1/documents/auto-generate", json=payload)).status_code == 200
                limited = await ac.post("/api/v1/documents/auto-generate", json=payload)
                assert limited.status_code == 429
    finally:
        settings.AUTO_GENERATE_RATE_LIMIT = original_limit
        limiter._hits.clear()
