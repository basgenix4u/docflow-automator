from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


ALLOWED_ROLES = {"ADMIN", "ENGINEER", "VIEWER"}
ALLOWED_FORMATS = {"A4", "A5", "CUSTOM_PDF"}
ALLOWED_DOC_TYPES = {"exam", "crg", "rec", "result"}


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    role: Optional[str] = "ENGINEER"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> str:
        role = (value or "ENGINEER").upper()
        if role not in ALLOWED_ROLES:
            return "ENGINEER"
        return role


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


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


class PortalCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    base_url: str = Field(min_length=8, max_length=500)
    auth_type: Optional[str] = "FORM"
    username_field: Optional[str] = "userId"
    password_field: Optional[str] = "password"
    demo_username: Optional[str] = None
    demo_password: Optional[str] = None

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return value


class PortalResponse(BaseModel):
    id: str
    name: str
    base_url: str
    auth_type: str
    username_field: str
    password_field: str
    demo_username: Optional[str]
    status: str


class WorkflowStep(BaseModel):
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None
    target_var: Optional[str] = None


class WorkflowCreate(BaseModel):
    portal_id: str
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    steps: list[WorkflowStep]
    target_format: Optional[str] = "A4"

    @field_validator("target_format")
    @classmethod
    def validate_format(cls, value: Optional[str]) -> str:
        fmt = (value or "A4").upper()
        return fmt if fmt in ALLOWED_FORMATS else "A4"


class WorkflowResponse(BaseModel):
    id: str
    portal_id: str
    name: str
    description: Optional[str]
    steps_json: str
    target_format: str


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


class PDFRenderRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    html_content: str = Field(min_length=1, max_length=200_000)
    page_format: Optional[str] = "A4"


class DocumentResponse(BaseModel):
    id: str
    workflow_run_id: Optional[str]
    title: str
    page_format: str
    page_count: int
    file_size_bytes: int
    created_at: Any


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


class AutoGenerateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=128)
    document_type: str = "exam"
    paper_format: str = "A5"

    @field_validator("document_type")
    @classmethod
    def validate_doc_type(cls, value: str) -> str:
        normalized = (value or "exam").lower()
        if normalized not in ALLOWED_DOC_TYPES:
            raise ValueError("document_type must be one of exam, crg, rec, result")
        return normalized

    @field_validator("paper_format")
    @classmethod
    def validate_paper(cls, value: str) -> str:
        fmt = (value or "A5").upper()
        return fmt if fmt in {"A4", "A5"} else "A5"
