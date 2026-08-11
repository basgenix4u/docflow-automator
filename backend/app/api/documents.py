import os
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import get_db
from app.models.domain import Document
from app.schemas.dto import PDFRenderRequest, DocumentResponse
from app.services.pdf_exporter import render_html_to_pdf
from portal_document_solver import run_portal_document_solver

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

if settings.CLOUDINARY_CLOUD_NAME:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

class AutoGenerateRequest(BaseModel):
    username: str
    password: str
    document_type: str = "exam" # exam, crg, rec, result
    paper_format: str = "A5"

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()

@router.post("/auto-generate")
async def auto_generate_document(req: AutoGenerateRequest, db: AsyncSession = Depends(get_db)):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Student User ID and password are required.")

    doc_titles = {
        "exam": "Examination Card & Docket",
        "crg": "Completed Course Registration Form",
        "rec": "Official Fee Payment Receipt",
        "result": "Semester Academic Results Transcript"
    }

    doc_title = f"{doc_titles.get(req.document_type, 'Portal Document')} — {req.username}"
    safe_name = req.username.replace('/', '_')
    out_filename = f"FUW_{req.document_type.upper()}_{safe_name}_{req.paper_format.upper()}.pdf"

    pdf_path = await run_portal_document_solver(
        username=req.username,
        password=req.password,
        document_type=req.document_type,
        paper_format=req.paper_format,
        output_filename=out_filename
    )

    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to generate portal document. Please verify user ID and password.")

    file_size = os.path.getsize(pdf_path)
    cloudinary_url = ""

    # Optional Cloudinary upload if credentials configured
    if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY:
        try:
            upload_res = cloudinary.uploader.upload(
                pdf_path,
                resource_type="raw",
                folder="docflow_pdfs",
                public_id=out_filename.replace('.pdf', '')
            )
            cloudinary_url = upload_res.get("secure_url", "")
        except Exception as e:
            print("Cloudinary upload warning:", e)

    doc = Document(
        title=doc_title,
        page_format=req.paper_format.upper(),
        page_count=1,
        file_size_bytes=file_size,
        file_path=cloudinary_url or pdf_path
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return {
        "id": doc.id,
        "title": doc.title,
        "page_format": doc.page_format,
        "page_count": doc.page_count,
        "file_size_bytes": doc.file_size_bytes,
        "created_at": doc.created_at,
        "view_url": f"/api/v1/documents/{doc.id}/view",
        "download_url": f"/api/v1/documents/{doc.id}/download",
        "cloudinary_url": cloudinary_url
    }

@router.get("/{document_id}/view")
async def view_document_inline(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Opens and renders the PDF directly INLINE in the browser tab.
    """
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.file_path.startswith("http://") or doc.file_path.startswith("https://"):
        return RedirectResponse(url=doc.file_path)

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    filename = os.path.basename(doc.file_path)
    return FileResponse(
        path=doc.file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )

@router.get("/{document_id}/download")
async def download_document(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.file_path.startswith("http://") or doc.file_path.startswith("https://"):
        return RedirectResponse(url=doc.file_path)

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    filename = os.path.basename(doc.file_path)
    return FileResponse(
        path=doc.file_path,
        media_type="application/pdf",
        filename=filename
    )
