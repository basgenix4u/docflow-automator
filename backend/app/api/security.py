import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.deps import operator_user
from app.models.domain import Portal, SecurityScan, User
from app.schemas.dto import SecurityScanRequest, SecurityScanResponse
from app.services.security_scanner import scan_portal_security

router = APIRouter(prefix="/api/v1/security", tags=["Security Scanner"])


@router.get("/", response_model=list[SecurityScanResponse])
async def list_security_scans(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(SecurityScan).order_by(SecurityScan.created_at.desc()))
    return result.scalars().all()


@router.post("/scan", response_model=SecurityScanResponse)
async def trigger_security_scan(
    req: SecurityScanRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(Portal).where(Portal.id == req.portal_id))
    portal = result.scalars().first()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal not found")

    score, vulns_count, tests_executed, report = await scan_portal_security(portal.base_url)

    scan = SecurityScan(
        portal_id=portal.id,
        status="COMPLETED",
        score=score,
        vulnerabilities_found=vulns_count,
        tests_executed_json=json.dumps(tests_executed),
        report_json=json.dumps(report),
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan


@router.get("/scans/{scan_id}", response_model=SecurityScanResponse)
async def get_security_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(SecurityScan).where(SecurityScan.id == scan_id))
    scan = result.scalars().first()
    if not scan:
        raise HTTPException(status_code=404, detail="Security scan record not found")
    return scan
