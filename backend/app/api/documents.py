import logging
import os

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_db
from app.core.deps import operator_user
from app.core.rate_limit import enforce_auto_generate_limit
from app.models.domain import Document, User
from app.schemas.dto import AutoGenerateRequest, DocumentResponse, PDFRenderRequest
from app.services.pdf_exporter import render_html_to_pdf
from portal_document_solver import run_portal_document_solver

logger = logging.getLogger("documents")
router = APIRouter(tags=["Documents"])

if settings.CLOUDINARY_CLOUD_NAME:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def _maybe_upload(pdf_path: str, public_id: str) -> str:
    if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY):
        return ""
    try:
        upload_res = cloudinary.uploader.upload(
            pdf_path,
            resource_type="raw",
            folder="docflow_pdfs",
            public_id=public_id,
        )
        return upload_res.get("secure_url", "") or ""
    except Exception as exc:
        logger.warning("Cloudinary upload notice: %s", exc)
        return ""


@router.get("/documents/", response_model=list[DocumentResponse])
@router.get("/api/documents/", response_model=list[DocumentResponse])
@router.get("/api/v1/documents/", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.post("/documents/render-pdf", response_model=DocumentResponse)
@router.post("/api/documents/render-pdf", response_model=DocumentResponse)
@router.post("/api/v1/documents/render-pdf", response_model=DocumentResponse)
async def render_pdf(
    req: PDFRenderRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    pdf_path = await render_html_to_pdf(req.title, req.html_content, req.page_format or "A4")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF renderer failed")

    public_id = os.path.splitext(os.path.basename(pdf_path))[0]
    stored_path = _maybe_upload(pdf_path, public_id) or pdf_path
    doc = Document(
        title=req.title,
        page_format=(req.page_format or "A4").upper(),
        page_count=1,
        file_size_bytes=os.path.getsize(pdf_path),
        file_path=stored_path,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.post("/documents/auto-generate")
@router.post("/api/documents/auto-generate")
@router.post("/api/v1/documents/auto-generate")
async def auto_generate_document(req: AutoGenerateRequest, request: Request):
    enforce_auto_generate_limit(request)
    try:
        if not req.username or not req.password:
            raise HTTPException(status_code=400, detail="Student User ID and password are required.")

        doc_titles = {
            "exam": "Examination Card & Docket",
            "crg": "Completed Course Registration Form",
            "rec": "Official Fee Payment Receipt",
            "result": "Semester Academic Results Transcript",
        }

        doc_title = f"{doc_titles.get(req.document_type, 'Portal Document')} — {req.username}"
        safe_name = req.username.replace("/", "_")
        out_filename = f"FUW_{req.document_type.upper()}_{safe_name}_{req.paper_format.upper()}.pdf"

        pdf_path = await run_portal_document_solver(
            username=req.username,
            password=req.password,
            document_type=req.document_type,
            paper_format=req.paper_format,
            output_filename=out_filename,
        )

        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=400,
                detail="Portal automation could not complete. Please verify student User ID, password, or try again in 1 minute.",
            )

        file_size = os.path.getsize(pdf_path)
        cloudinary_url = _maybe_upload(pdf_path, out_filename.replace(".pdf", ""))

        async with AsyncSessionLocal() as db_session:
            try:
                doc = Document(
                    title=doc_title,
                    page_format=req.paper_format.upper(),
                    page_count=1,
                    file_size_bytes=file_size,
                    file_path=cloudinary_url or pdf_path,
                )
                db_session.add(doc)
                await db_session.commit()
                await db_session.refresh(doc)
                doc_id = doc.id
                doc_created_at = doc.created_at
            except Exception as db_err:
                await db_session.rollback()
                logger.warning("Database insert notice: %s", db_err)
                doc_id = "local_doc"
                doc_created_at = None
            finally:
                await db_session.close()

        return {
            "status": "success",
            "id": doc_id,
            "title": doc_title,
            "page_format": req.paper_format.upper(),
            "page_count": 1,
            "file_size_bytes": file_size,
            "created_at": doc_created_at,
            "view_url": f"/api/v1/documents/{doc_id}/view",
            "download_url": f"/api/v1/documents/{doc_id}/download",
            "cloudinary_url": cloudinary_url,
        }

    except HTTPException:
        raise
    except Exception as top_err:
        logger.exception("auto_generate_document error")
        raise HTTPException(status_code=400, detail="Automation error. Please verify credentials and try again.") from top_err


@router.get("/documents/{document_id}/view")
@router.get("/api/documents/{document_id}/view")
@router.get("/api/v1/documents/{document_id}/view")
async def view_document_inline(document_id: str, db: AsyncSession = Depends(get_db)):
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
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/documents/{document_id}/download")
@router.get("/api/documents/{document_id}/download")
@router.get("/api/v1/documents/{document_id}/download")
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
    return FileResponse(path=doc.file_path, media_type="application/pdf", filename=filename)
