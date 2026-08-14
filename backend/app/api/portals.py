from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.deps import operator_user
from app.models.domain import Portal, User
from app.schemas.dto import PortalCreate, PortalResponse
from app.services.security_scanner import scan_portal_security

router = APIRouter(prefix="/api/v1/portals", tags=["Portals"])


@router.get("/", response_model=list[PortalResponse])
async def list_portals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Portal))
    return result.scalars().all()


@router.post("/", response_model=PortalResponse)
async def create_portal(
    data: PortalCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    portal = Portal(
        name=data.name,
        base_url=data.base_url,
        auth_type=data.auth_type or "FORM",
        username_field=data.username_field or "userId",
        password_field=data.password_field or "password",
        demo_username=data.demo_username,
        demo_password=data.demo_password,
    )
    db.add(portal)
    await db.commit()
    await db.refresh(portal)
    return portal


@router.get("/{portal_id}", response_model=PortalResponse)
async def get_portal(portal_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Portal).where(Portal.id == portal_id))
    portal = result.scalars().first()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal not found")
    return portal


@router.post("/{portal_id}/test-auth")
async def test_portal_auth(
    portal_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(operator_user),
):
    result = await db.execute(select(Portal).where(Portal.id == portal_id))
    portal = result.scalars().first()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal not found")

    score, vulns, tests, _report = await scan_portal_security(portal.base_url)
    return {
        "portal_id": portal.id,
        "portal_name": portal.name,
        "url": portal.base_url,
        "security_score": score,
        "vulnerabilities": vulns,
        "tests_summary": len(tests),
    }
