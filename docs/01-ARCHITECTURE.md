# DocFlow Automator — System Architecture & Design Specification

> **AI Software Factory Proposal**  
> **Role:** Principal PM & Lead Architect  
> **Project:** DocFlow Automator — Browser Automation, Dynamic Document Processing & Portal Security Testing Platform  
> **Date:** August 10, 2026  

---

## 1. Executive Overview

**DocFlow Automator** is an enterprise-grade platform engineered to orchestrate isolated multi-user browser workflows, navigate dynamic web dashboards, extract structured content, render and convert documents into standardized A4/A5 PDF formats, and automatically audit target portals for authentication vulnerabilities.

### Key Capabilities
1. **Isolated Workflow Orchestration**: Headless browser workers executing multi-step navigation, DOM manipulation, form interaction, and session management in completely isolated browser contexts.
2. **Dynamic Document Extraction & PDF Rendering**: Automated detection of dashboard reports/DOM nodes, Jinja2/HTML template rendering, and high-fidelity A4/A5 PDF exports with custom margins, headers, footers, and page numbers.
3. **Portal Authentication & Security Testing**: Automated test runner evaluating CSRF protections, session token freshness, MFA enforcement, role-based access control (RBAC) boundaries, and rate-limiting resilience.
4. **Interactive Command Center**: Next.js 15 web interface featuring real-time execution logs, document previewers, workflow builders, portal status monitors, and security audit reports.

---

## 2. System Architecture & Component Design

```
+-----------------------------------------------------------------------------------+
|                                  USER BROWSER                                     |
|                       Next.js 15 Web Dashboard & Monitoring                       |
+-----------------------------------------------------------------------------------+
                                         │
                                   HTTP / REST API
                                         ▼
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────────────┐  |
|  │  Auth & RBAC      │  │  Workflow Engine   │  │  Document & PDF Service      │  |
|  └───────────────────┘  └────────────────────┘  └──────────────────────────────┘  |
|  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────────────┐  |
|  │ Portal Registry   │  │ Security Scanner   │  │ Audit & Logging Service      │  |
|  └───────────────────┘  └────────────────────┘  └──────────────────────────────┘  |
+-----------------------------------------------------------------------------------+
       │                             │                              │
       ▼                             ▼                              ▼
+───────────────+           +─────────────────+            +──────────────────+
|  SQLite / DB  |           | Playwright Engine|            | Storage / PDFs   |
|  (WAL Mode)   |           | Isolated Context|            | (A4/A5 Reports)  |
+───────────────+           +─────────────────+            +──────────────────+
```

---

## 3. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend UI** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS v4, Lucide Icons | Responsive, accessible, strongly typed UI with live status updates and document previews. |
| **Backend API** | Python 3.13 + FastAPI + Pydantic v2 + SQLAlchemy 2.0 | High performance, native async IO support, auto-generated OpenAPI spec, robust data validation. |
| **Browser Engine** | Playwright Python (Chromium) | Industry standard for reliable browser automation, parallel execution, isolated browser contexts, PDF printing. |
| **PDF Converter** | Playwright PDF / WeasyPrint | Pixel-perfect A4 and A5 PDF compilation with CSS `@page` media rules, custom page headers, footers, and page counters. |
| **Database** | SQLite with WAL mode / PostgreSQL | Zero-config, low-latency, ACID compliant storage with JSON column support for workflow definitions and test logs. |
| **Security Core** | Argon2id + Passlib, PyJWT (RS256/HS256), Security Headers | OWASP compliant password hashing, statelessly validated JWT session tokens, and input sanitization. |

---

## 4. Database Schema (ERD Specification)

### `users` Table
- `id` (UUID / String, PK)
- `email` (String, Unique, Indexed)
- `hashed_password` (String)
- `full_name` (String)
- `role` (Enum: `ADMIN`, `ENGINEER`, `VIEWER`)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### `portals` Table
- `id` (UUID / String, PK)
- `name` (String)
- `base_url` (String)
- `auth_type` (Enum: `FORM`, `BEARER`, `BASIC`, `OAUTH2`)
- `credentials_json` (Encrypted JSON string)
- `status` (Enum: `ACTIVE`, `INACTIVE`, `ERROR`)
- `created_at` (DateTime)

### `workflows` Table
- `id` (UUID / String, PK)
- `portal_id` (String, FK -> `portals.id`)
- `name` (String)
- `description` (Text)
- `steps_json` (JSON: Array of navigation, input, click, extract actions)
- `target_format` (Enum: `A4`, `A5`, `CUSTOM_PDF`)
- `created_at` (DateTime)

### `workflow_runs` Table
- `id` (UUID / String, PK)
- `workflow_id` (String, FK -> `workflows.id`)
- `triggered_by` (String, FK -> `users.id`)
- `status` (Enum: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`)
- `execution_logs` (Text / JSON)
- `duration_ms` (Integer)
- `error_message` (Text, Nullable)
- `started_at` (DateTime)
- `completed_at` (DateTime, Nullable)

### `documents` Table
- `id` (UUID / String, PK)
- `workflow_run_id` (String, FK -> `workflow_runs.id`)
- `title` (String)
- `page_format` (Enum: `A4`, `A5`)
- `page_count` (Integer)
- `file_size_bytes` (Integer)
- `file_path` (String)
- `created_at` (DateTime)

### `security_scans` Table
- `id` (UUID / String, PK)
- `portal_id` (String, FK -> `portals.id`)
- `status` (Enum: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`)
- `tests_executed` (JSON: array of test results)
- `vulnerabilities_found` (Integer)
- `score` (Integer 0-100)
- `report_json` (JSON)
- `created_at` (DateTime)

---

## 5. API Contracts

### Authentication Router (`/api/v1/auth`)
- `POST /login` -> `{ access_token, token_type, user }`
- `POST /register` -> `{ id, email, full_name, role }`
- `GET /me` -> `{ user }`

### Portals Router (`/api/v1/portals`)
- `GET /` -> `List[Portal]`
- `POST /` -> `Portal`
- `GET /{id}` -> `Portal`
- `POST /{id}/test-auth` -> `{ status, response_time_ms, csrf_detected, details }`

### Workflows Router (`/api/v1/workflows`)
- `GET /` -> `List[Workflow]`
- `POST /` -> `Workflow`
- `POST /{id}/run` -> `WorkflowRun`

### Workflow Runs Router (`/api/v1/runs`)
- `GET /` -> `List[WorkflowRun]`
- `GET /{id}` -> `WorkflowRun`
- `GET /{id}/logs` -> `{ logs: List[LogEntry] }`

### Documents Router (`/api/v1/documents`)
- `GET /` -> `List[Document]`
- `POST /render-pdf` -> `Document`
- `GET /{id}/download` -> PDF Binary File Stream

### Security Scanner Router (`/api/v1/security`)
- `POST /scan` -> `SecurityScan`
- `GET /scans/{id}` -> `SecurityScan`

---

## 6. Project Folder Structure

```
docflow-automator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── portals.py
│   │   │   ├── workflows.py
│   │   │   ├── runs.py
│   │   │   ├── documents.py
│   │   │   └── security.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   └── domain.py
│   │   ├── schemas/
│   │   │   └── dto.py
│   │   ├── services/
│   │   │   ├── browser_engine.py
│   │   │   ├── pdf_exporter.py
│   │   │   └── security_scanner.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_workflows.py
│   │   ├── test_pdf_exporter.py
│   │   └── test_security.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/login/page.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── portals/page.tsx
│   │   │   ├── workflows/page.tsx
│   │   │   ├── documents/page.tsx
│   │   │   ├── security/page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── WorkflowEditor.tsx
│   │   │   ├── DocumentViewer.tsx
│   │   │   └── SecurityReportCard.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
├── docs/
│   └── 01-ARCHITECTURE.md
├── TASKBOARD.md
├── docker-compose.yml
└── README.md
```
