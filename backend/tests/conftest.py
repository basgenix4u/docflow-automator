import pytest_asyncio
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.domain import Portal, Workflow


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Portal).where(Portal.base_url == settings.FUW_PORTAL_URL))
        portal = res.scalars().first()
        if not portal:
            portal = Portal(
                name="Federal University Wukari — Student Portal",
                base_url=settings.FUW_PORTAL_URL,
                auth_type="FORM",
                status="ACTIVE",
            )
            session.add(portal)
            await session.commit()
            await session.refresh(portal)

        wf = await session.execute(select(Workflow).where(Workflow.portal_id == portal.id))
        if not wf.scalars().first():
            session.add(
                Workflow(
                    portal_id=portal.id,
                    name="FUW Student Portal Exam Card & Course Form Auto-Print",
                    description="Test workflow",
                    steps_json="[]",
                    target_format="A5",
                )
            )
            await session.commit()
    yield


def pytest_configure():
    # Explicit loop scope for pytest-asyncio 0.25+
    pass
