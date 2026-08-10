import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.domain import Workflow, Portal, WorkflowRun, Document
from app.schemas.dto import WorkflowCreate, WorkflowResponse, RunExecuteRequest, RunResponse
from app.services.fuw_portal import execute_fuw_portal_automation
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
        target_format=data.target_format or "A4"
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow

@router.post("/{workflow_id}/run", response_model=RunResponse)
async def run_workflow(
    workflow_id: str,
    req: RunExecuteRequest = None,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    p_result = await db.execute(select(Portal).where(Portal.id == workflow.portal_id))
    portal = p_result.scalars().first()

    demo_user = (req.custom_username if req and req.custom_username else None) or (portal.demo_username if portal else "BSC/BCH/24/140")
    demo_pass = (req.custom_password if req and req.custom_password else None) or (portal.demo_password if portal else "Omotola")

    # Create WorkflowRun record
    run = WorkflowRun(
        workflow_id=workflow.id,
        status="RUNNING",
        started_at=datetime.now(timezone.utc)
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Check if this is the FUW Portal specialization or generic browser engine
    if portal and "fuwportal.edu.ng" in portal.base_url.lower():
        extracted_data, logs, pdf_path = await execute_fuw_portal_automation(
            username=demo_user,
            password=demo_pass,
            portal_url=portal.base_url,
            page_format=workflow.target_format or "A4"
        )
    else:
        steps = json.loads(workflow.steps_json)
        extracted_data, logs = await execute_custom_workflow(
            portal_url=portal.base_url if portal else "https://ug.fuwportal.edu.ng/index.php",
            steps=steps,
            demo_username=demo_user,
            demo_password=demo_pass
        )
        pdf_path = ""

    is_success = "error" not in extracted_data
    run.status = "COMPLETED" if is_success else "FAILED"
    run.execution_logs = json.dumps(logs)
    run.extracted_data_json = json.dumps(extracted_data)
    run.error_message = extracted_data.get("error")
    run.completed_at = datetime.now(timezone.utc)

    if is_success and pdf_path:
        doc = Document(
            workflow_run_id=run.id,
            title=f"{workflow.name} — {extracted_data.get('full_name', demo_user)}",
            page_format=workflow.target_format or "A4",
            page_count=1,
            file_size_bytes=1024,
            file_path=pdf_path
        )
        db.add(doc)

    await db.commit()
    await db.refresh(run)
    return run
