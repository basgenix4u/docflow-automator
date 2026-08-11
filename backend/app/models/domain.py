import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    # Pure naive datetime object for 100% asyncpg & SQLite compatibility
    return datetime.now().replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="ENGINEER")  # ADMIN, ENGINEER, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), default=utc_now)

class Portal(Base):
    __tablename__ = "portals"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    auth_type = Column(String, default="FORM")
    username_field = Column(String, default="userId")
    password_field = Column(String, default="password")
    demo_username = Column(String, nullable=True)
    demo_password = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime(timezone=False), default=utc_now)

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=generate_uuid)
    portal_id = Column(String, ForeignKey("portals.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    steps_json = Column(Text, nullable=False)  # JSON array of workflow steps
    target_format = Column(String, default="A5")  # A4, A5
    created_at = Column(DateTime(timezone=False), default=utc_now)

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    triggered_by = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    execution_logs = Column(Text, default="[]")  # JSON array of log messages
    extracted_data_json = Column(Text, default="{}")  # Extracted structured portal data
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=False), default=utc_now)
    completed_at = Column(DateTime(timezone=False), nullable=True)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=True)
    title = Column(String, nullable=False)
    page_format = Column(String, default="A5")  # A4, A5
    page_count = Column(Integer, default=1)
    file_size_bytes = Column(Integer, default=0)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=False), default=utc_now)

class SecurityScan(Base):
    __tablename__ = "security_scans"

    id = Column(String, primary_key=True, default=generate_uuid)
    portal_id = Column(String, ForeignKey("portals.id"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    score = Column(Integer, default=100)
    vulnerabilities_found = Column(Integer, default=0)
    tests_executed_json = Column(Text, default="[]")
    report_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=False), default=utc_now)
