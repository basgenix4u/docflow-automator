import json
import os
import cloudinary
import cloudinary.uploader
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.config import settings
from app.core.database import get_db, AsyncSessionLocal
from app.models.domain import Workflow, Portal, WorkflowRun, Document, utc_now
from app.schemas.dto import WorkflowCreate, WorkflowResponse, RunExecuteRequest, RunResponse
from portal_document_solver import run_portal_document_solver

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow))
    return result.scalars().all()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(data: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Portal).where(Portal.id == data.portal_id))
    portal = result.scalars().first()
    if not portal:
        raise HTTPException(status_code=404, detail="Associated portal not found")

    steps_serialized = json.dumps([step.model_dump() for step in data.steps])

    workflow = Workflow(
        portal_id=data.portal_id,
        name=data.name,
        description=data.description,
        steps_json=steps_serialized,
        target_format=data.target_format or "A5"
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow

@router.post("/{workflow_id}/run", response_model=RunResponse)
async def run_workflow(
    workflow_id: str,
    req: RunExecuteRequest
):
    """
    Decoupled Production Workflow Execution:
    1. Read workflow config in short 10ms DB session.
    2. Execute Playwright browser automation with NO DB session open.
    3. Execute Cloudinary upload with NO DB session open.
    4. Persist run results & document metadata in short 10ms DB session.
    """
    user_id = req.custom_username if req and req.custom_username else None
    password = req.custom_password if req and req.custom_password else None

    if not user_id or not password:
        raise HTTPException(
            status_code=400,
            detail="User ID and password are required to execute portal automation."
        )

    # STAGE 1: Read Workflow & Portal config in a short DB transaction
    async with AsyncSessionLocal() as session:
        try:
            res_wf = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
            workflow = res_wf.scalars().first()
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")

            p_result = await session.execute(select(Portal).where(Portal.id == workflow.portal_id))
            portal = p_result.scalars().first()

            wf_name = workflow.name
            target_format = workflow.target_format or "A5"
            portal_url = portal.base_url if portal else "https://ug.fuwportal.edu.ng/index.php"

            # Create WorkflowRun record
            run = WorkflowRun(
                workflow_id=workflow.id,
                status="RUNNING",
                started_at=utc_now()
            )
            session.add(run)
            await session.commit()
            await session.refresh(run)

            run_id = run.id
        finally:
            await session.close()

    # STAGE 2: Heavy Playwright Automation Execution (ZERO DB SESSION CHECKED OUT)
    safe_name = user_id.replace('/', '_')
    out_pdf_name = f"FUW_ExamCard_{safe_name}_{target_format}.pdf"

    pdf_path = await run_portal_document_solver(
        username=user_id,
        password=password,
        document_type="exam",
        paper_format=target_format,
        output_filename=out_pdf_name
    )

    is_success = bool(pdf_path and os.path.exists(pdf_path))
    cloudinary_url = ""

    # STAGE 3: Cloudinary Upload (ZERO DB SESSION CHECKED OUT)
    if is_success and settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY:
        try:
            upload_res = cloudinary.uploader.upload(
                pdf_path,
                resource_type="raw",
                folder="docflow_pdfs",
                public_id=out_pdf_name.replace('.pdf', '')
            )
            cloudinary_url = upload_res.get("secure_url", "")
        except Exception as e:
            print("Cloudinary upload notice:", e)

    # STAGE 4: Acquire Fresh Short DB Session to Update Run & Insert Document
    async with AsyncSessionLocal() as session:
        try:
            res_run = await session.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
            run_obj = res_run.scalars().first()

            if run_obj:
                run_obj.status = "COMPLETED" if is_success else "FAILED"
                run_obj.execution_logs = json.dumps([
                    {"timestamp": utc_now().strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO", "message": f"Execution completed for user {user_id}"},
                    {"timestamp": utc_now().strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO" if is_success else "ERROR", "message": f"PDF path: {pdf_path}" if is_success else "Automation failed to capture webview"}
                ])
                run_obj.extracted_data_json = json.dumps({
                    "student_id": user_id,
                    "portal_url": portal_url,
                    "pdf_path": cloudinary_url or pdf_path
                })
                run_obj.error_message = None if is_success else "Automation failed on target portal"
                run_obj.completed_at = utc_now()

                if is_success and pdf_path:
                    doc = Document(
                        workflow_run_id=run_obj.id,
                        title=f"{wf_name} — {user_id}",
                        page_format=target_format,
                        page_count=1,
                        file_size_bytes=os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 1024,
                        file_path=cloudinary_url or pdf_path
                    )
                    session.add(doc)

                await session.commit()
                await session.refresh(run_obj)
                return run_obj
            else:
                raise HTTPException(status_code=404, detail="Workflow run record lost.")
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
