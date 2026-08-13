import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal, check_database_health
from app.core.security import hash_password
from app.models.domain import User, Portal, Workflow
from app.api import auth, portals, workflows, runs, documents, security
from app.api.documents import auto_generate_document, AutoGenerateRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed default database records
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            # Seed default admin user if not existing
            res_user = await session.execute(select(User).where(User.email == "admin@docflow.io"))
            if not res_user.scalars().first():
                admin_user = User(
                    email="admin@docflow.io",
                    full_name="DocFlow Production Admin",
                    hashed_password=hash_password("AdminPassword123!"),
                    role="ADMIN"
                )
                session.add(admin_user)

            # Seed default FUW Portal
            res_portal = await session.execute(select(Portal).where(Portal.base_url == settings.FUW_PORTAL_URL))
            fuw_portal = res_portal.scalars().first()
            if not fuw_portal:
                fuw_portal = Portal(
                    name="Federal University Wukari — Student Portal",
                    base_url=settings.FUW_PORTAL_URL,
                    auth_type="FORM",
                    username_field="userId",
                    password_field="password",
                    demo_username="",
                    demo_password="",
                    status="ACTIVE"
                )
                session.add(fuw_portal)
                await session.commit()
                await session.refresh(fuw_portal)

            # Seed default FUW Examination Card Workflow
            res_wf = await session.execute(select(Workflow).where(Workflow.portal_id == fuw_portal.id))
            if not res_wf.scalars().first():
                fuw_workflow = Workflow(
                    portal_id=fuw_portal.id,
                    name="FUW Student Portal Exam Card & Course Form Auto-Print",
                    description="Navigates to FUW portal, inputs student credentials dynamically, selects session/semester, intercepts popup webview, and exports exact A5/A4 PDF.",
                    steps_json='[{"action": "navigate", "value": "https://ug.fuwportal.edu.ng/index.php"}, {"action": "fill", "selector": "#userId", "value": "$USERNAME"}, {"action": "fill", "selector": "#password", "value": "$PASSWORD"}, {"action": "click", "selector": "button, input[type=\'submit\']"}]',
                    target_format="A5"
                )
                session.add(fuw_workflow)

            await session.commit()
        except Exception as e:
            await session.rollback()
            print("Lifespan startup warning:", e)
        finally:
            await session.close()

    yield

    # Shutdown: Gracefully dispose database connection pool
    await engine.dispose()

app = FastAPI(
    title="DocFlow Automator API Engine",
    version="1.0.0",
    description="Browser Automation, Dynamic Document Processing & Portal Security Testing API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
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
        "health": "/api/v1/health"
    }

@app.post("/")
async def root_post(request: Request, body: AutoGenerateRequest = None):
    # Handle Vercel query parameter path rewrites if path query param is provided
    query_path = request.query_params.get("path", "")
    if "auto-generate" in query_path and body:
        return await auto_generate_document(body)
    return {
        "status": "online",
        "message": "DocFlow Automator API Root POST Endpoint"
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
        "storage_ready": os.path.exists(settings.STORAGE_DIR)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
