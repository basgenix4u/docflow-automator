import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.deps import operator_user
from app.models.domain import User, WorkflowRun
from app.schemas.dto import RunResponse

router = APIRouter(tags=["Workflow Runs"])


@router.get("/runs/", response_model=list[RunResponse])
@router.get("/api/runs/", response_model=list[RunResponse])
@router.get("/api/v1/runs/", response_model=list[RunResponse])
async def list_runs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(WorkflowRun).order_by(WorkflowRun.started_at.desc()))
    return result.scalars().all()


@router.get("/runs/{run_id}", response_model=RunResponse)
@router.get("/api/runs/{run_id}", response_model=RunResponse)
@router.get("/api/v1/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/logs")
@router.get("/api/runs/{run_id}/logs")
@router.get("/api/v1/runs/{run_id}/logs")
async def get_run_logs(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run_id": run.id,
        "status": run.status,
        "logs": json.loads(run.execution_logs or "[]"),
    }
