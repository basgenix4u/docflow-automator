import os
import uuid
import logging
from playwright.async_api import async_playwright
from app.core.config import settings

logger = logging.getLogger("pdf_exporter")

async def render_html_to_pdf(
    title: str,
    html_content: str,
    page_format: str = "A4"
) -> str:
    """
    Renders HTML string into a standardized A4/A5 PDF file using Playwright.
    Returns absolute file path of generated PDF.
    """
    safe_title = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in title)
    filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join(settings.STORAGE_DIR, filename)

    page_format_norm = page_format.upper()
    if page_format_norm not in ("A4", "A5"):
        page_format_norm = "A4"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

        await page.set_content(html_content, wait_until="networkidle")

        await page.pdf(
            path=output_path,
            format=page_format_norm,
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
        )

        await browser.close()

    logger.info(f"Generated PDF [{page_format_norm}] at {output_path}")
    return output_path
