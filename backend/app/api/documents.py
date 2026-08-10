import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.domain import Document
from app.schemas.dto import PDFRenderRequest, DocumentResponse
from app.services.pdf_exporter import render_html_to_pdf

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()

@router.post("/render-pdf", response_model=DocumentResponse)
async def render_pdf_document(req: PDFRenderRequest, db: AsyncSession = Depends(get_db)):
    pdf_path = await render_html_to_pdf(
        title=req.title,
        html_content=req.html_content,
        page_format=req.page_format or "A4"
    )

    file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0

    doc = Document(
        title=req.title,
        page_format=req.page_format or "A4",
        page_count=1,
        file_size_bytes=file_size,
        file_path=pdf_path
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc

@router.get("/{document_id}/download")
async def download_document(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    filename = os.path.basename(doc.file_path)
    return FileResponse(
        path=doc.file_path,
        media_type="application/pdf",
        filename=filename
    )
