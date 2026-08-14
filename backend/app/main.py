import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import auth, documents, portals, runs, security, workflows
from app.api.documents import auto_generate_document
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, check_database_health, engine
from app.core.security import hash_password
from app.models.domain import Portal, User, Workflow
from app.schemas.dto import AutoGenerateRequest

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("docflow")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
                res_user = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL.lower()))
                if not res_user.scalars().first():
                    session.add(
                        User(
                            email=settings.ADMIN_EMAIL.lower(),
                            full_name=settings.ADMIN_FULL_NAME,
                            hashed_password=hash_password(settings.ADMIN_PASSWORD),
                            role="ADMIN",
                        )
                    )
                    logger.info("Seeded administrator account from environment")
            elif settings.is_insecure_default_secret:
                logger.warning("ADMIN_EMAIL/ADMIN_PASSWORD not set — no default admin was created")

            res_portal = await session.execute(select(Portal).where(Portal.base_url == settings.FUW_PORTAL_URL))
            fuw_portal = res_portal.scalars().first()
            if not fuw_portal:
                fuw_portal = Portal(
                    name="Federal University Wukari — Student Portal",
                    base_url=settings.FUW_PORTAL_URL,
                    auth_type="FORM",
                    username_field="userId",
                    password_field="password",
                    demo_username=None,
                    demo_password=None,
                    status="ACTIVE",
                )
                session.add(fuw_portal)
                await session.commit()
                await session.refresh(fuw_portal)

            res_wf = await session.execute(select(Workflow).where(Workflow.portal_id == fuw_portal.id))
            if not res_wf.scalars().first():
                session.add(
                    Workflow(
                        portal_id=fuw_portal.id,
                        name="FUW Student Portal Exam Card & Course Form Auto-Print",
                        description=(
                            "Navigates to FUW portal, inputs student credentials dynamically, "
                            "selects session/semester, intercepts popup webview, and exports exact A5/A4 PDF."
                        ),
                        steps_json=(
                            '[{"action": "navigate", "value": "https://ug.fuwportal.edu.ng/index.php"}, '
                            '{"action": "fill", "selector": "#userId", "value": "$USERNAME"}, '
                            '{"action": "fill", "selector": "#password", "value": "$PASSWORD"}, '
                            '{"action": "click", "selector": "button, input[type=\'submit\']"}]'
                        ),
                        target_format="A5",
                    )
                )

            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.warning("Lifespan startup warning: %s", exc)
        finally:
            await session.close()

    yield
    await engine.dispose()


app = FastAPI(
    title="DocFlow Automator API Engine",
    version="1.1.0",
    description="Browser Automation, Dynamic Document Processing & Portal Security Testing API",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth.router)
app.include_router(portals.router)
app.include_router(workflows.router)
app.include_router(runs.router)
app.include_router(documents.router)
app.include_router(security.router)


@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "DocFlow Automator Backend Engine Live",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.post("/")
async def root_post(request: Request, body: AutoGenerateRequest | None = None):
    # Compatibility shim for older Vercel rewrite paths.
    query_path = request.query_params.get("path", "")
    if "auto-generate" in query_path and body:
        return await auto_generate_document(body, request)
    return {
        "status": "online",
        "message": "DocFlow Automator API Root POST Endpoint",
    }


@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    db_alive = await check_database_health()
    return {
        "status": "online" if db_alive else "degraded",
        "system": "DocFlow Automator Engine",
        "database_online": db_alive,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target_portal": settings.FUW_PORTAL_URL,
        "storage_ready": os.path.exists(settings.STORAGE_DIR),
        "auth_required_for_operators": True,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
