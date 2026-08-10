from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Optional[str] = "ENGINEER"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Portal Schemas
class PortalCreate(BaseModel):
    name: str
    base_url: str
    auth_type: Optional[str] = "FORM"
    username_field: Optional[str] = "userId"
    password_field: Optional[str] = "password"
    demo_username: Optional[str] = None
    demo_password: Optional[str] = None

class PortalResponse(BaseModel):
    id: str
    name: str
    base_url: str
    auth_type: str
    username_field: str
    password_field: str
    demo_username: Optional[str]
    status: str

# Workflow Schemas
class WorkflowStep(BaseModel):
    action: str  # navigate, fill, click, extract, wait, render_pdf
    selector: Optional[str] = None
    value: Optional[str] = None
    target_var: Optional[str] = None

class WorkflowCreate(BaseModel):
    portal_id: str
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]
    target_format: Optional[str] = "A4"

class WorkflowResponse(BaseModel):
    id: str
    portal_id: str
    name: str
    description: Optional[str]
    steps_json: str
    target_format: str

# Workflow Run Schemas
class RunExecuteRequest(BaseModel):
    custom_username: Optional[str] = None
    custom_password: Optional[str] = None

class RunResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    execution_logs: str
    extracted_data_json: str
    duration_ms: int
    error_message: Optional[str]
    started_at: Any
    completed_at: Optional[Any]

# Document Schemas
class PDFRenderRequest(BaseModel):
    title: str
    html_content: str
    page_format: Optional[str] = "A4"  # A4 or A5

class DocumentResponse(BaseModel):
    id: str
    workflow_run_id: Optional[str]
    title: str
    page_format: str
    page_count: int
    file_size_bytes: int
    created_at: Any

# Security Scan Schemas
class SecurityScanRequest(BaseModel):
    portal_id: str

class SecurityScanResponse(BaseModel):
    id: str
    portal_id: str
    status: str
    score: int
    vulnerabilities_found: int
    tests_executed_json: str
    report_json: str
    created_at: Any
