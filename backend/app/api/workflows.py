import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.domain import Workflow, Portal, WorkflowRun, Document
from app.schemas.dto import WorkflowCreate, WorkflowResponse, RunExecuteRequest, RunResponse
from popup_exam_card_solver import run_popup_exam_card_solver
from app.services.browser_engine import execute_custom_workflow

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
    req: RunExecuteRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    p_result = await db.execute(select(Portal).where(Portal.id == workflow.portal_id))
    portal = p_result.scalars().first()

    # Dynamic credentials supplied by user
    user_id = req.custom_username if req and req.custom_username else (portal.demo_username if portal else None)
    password = req.custom_password if req and req.custom_password else (portal.demo_password if portal else None)

    if not user_id or not password:
        raise HTTPException(
            status_code=400,
            detail="User ID and password are required to execute portal automation."
        )

    run = WorkflowRun(
        workflow_id=workflow.id,
        status="RUNNING",
        started_at=datetime.now(timezone.utc)
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    safe_name = user_id.replace('/', '_')
    out_pdf_name = f"FUW_ExamCard_{safe_name}_{workflow.target_format or 'A5'}.pdf"

    pdf_path = await run_popup_exam_card_solver(
        username=user_id,
        password=password,
        output_filename=out_pdf_name
    )

    is_success = bool(pdf_path)
    run.status = "COMPLETED" if is_success else "FAILED"
    run.execution_logs = json.dumps([
        {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO", "message": f"Execution started for user {user_id}"},
        {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO" if is_success else "ERROR", "message": f"PDF generated: {pdf_path}" if is_success else "Automation failed to capture webview"}
    ])
    run.extracted_data_json = json.dumps({
        "student_id": user_id,
        "portal_url": portal.base_url if portal else "https://ug.fuwportal.edu.ng/index.php",
        "pdf_path": pdf_path
    })
    run.error_message = None if is_success else "Automation failed on target portal"
    run.completed_at = datetime.now(timezone.utc)

    if is_success and pdf_path:
        doc = Document(
            workflow_run_id=run.id,
            title=f"{workflow.name} — {user_id}",
            page_format=workflow.target_format or "A5",
            page_count=1,
            file_size_bytes=1024,
            file_path=pdf_path
        )
        db.add(doc)

    await db.commit()
    await db.refresh(run)
    return run
