# DocFlow Automator — Architecture Validation & Gap Analysis

**Date:** 14 August 2026  
**Role:** Principal PM + Lead Architect  
**Baseline:** `docs/01-ARCHITECTURE.md` vs repository `main`

---

## 1. Product that actually shipped

The architecture describes an **enterprise command center** (RBAC, isolated workflows, security scanner).  
The live product is primarily a **public student document printer** for `https://ug.fuwportal.edu.ng/index.php`:

1. Student enters User ID + password.
2. Playwright logs into the FUW portal, intercepts exam card / CRG / receipt / result webviews.
3. A 1-page A4/A5 PDF is stored and opened in the browser.

Both products are valid. Hardening keeps **public generate** for students and **authenticated operator consoles** for portals, workflows, documents, and security scans.

---

## 2. Schema — validated with deltas

| Table | Spec | Implementation | Action |
|---|---|---|---|
| `users` | + `updated_at` | no `updated_at`; has `is_active` | Accept `is_active`; `updated_at` optional |
| `portals` | `credentials_json` encrypted | plaintext `demo_username` / `demo_password` | Never return passwords; stop shipping real demo creds |
| `workflows` | matches | matches | None |
| `workflow_runs` | matches | + `extracted_data_json` | Keep extra field |
| `documents` | matches | matches | Listing must not be world-readable |
| `security_scans` | matches | matches | Protect write + list |

---

## 3. API — validated with deltas

| Contract | Status |
|---|---|
| `POST /auth/login`, `POST /auth/register`, `GET /auth/me` | Present. Register accepted any `role` including `ADMIN` (privilege escalation). |
| Portals CRUD + `test-auth` | Present. **No authn/authz.** |
| Workflows + `POST /{id}/run` | Present. **No authn/authz.** |
| Runs list / get / logs | Present. **World-readable student IDs.** |
| Documents list / view / download | Present. List was public. |
| `POST /documents/render-pdf` | **Missing** from router (frontend already called it). |
| `POST /documents/auto-generate` | Extra student-facing endpoint. Keep public + rate-limit. |
| Security scan | Present. **No authn/authz.** |

---

## 4. Critical security findings (OWASP)

1. **A07 Identification & Authentication Failures** — hardcoded `AdminPassword123!` in `main.py`.
2. **A02 Cryptographic Failures** — default `SECRET_KEY` in source and `.env.example`.
3. **A01 Broken Access Control** — register `role=ADMIN`; all operator APIs unauthenticated.
4. **A04 Insecure Design** — student passwords accepted then not stored (good) but **all generated documents listed to anyone**.
5. **A05 Security Misconfiguration** — `CORS allow_origins=["*"]` + `allow_credentials=True`; `DEBUG=True` default.
6. **Sensitive data in repo** — real student IDs/passwords in `.env.example`, `docker-compose.yml`, tests, and UI placeholders (`BSC/BCH/24/140`, `Omotola`, `olaleke`, named student HTML).
7. **A04 / abuse** — unauthenticated Playwright jobs with no rate limit (DoS + credential stuffing against FUW).

---

## 5. Folder / delivery gaps

- Architecture listed `(auth)/login`, `WorkflowEditor`, `DocumentViewer`, `SecurityReportCard` — login was missing.
- `pyproject.toml` claimed on the task board but absent.
- `.env.example` used `/home/user/...` absolute paths (not portable).
- Frontend Docker image copied `public/` which did not exist.
- `.gitignore` ignored `*.html` / `*.png` (too broad).
- Generated PDFs were committed under `backend/storage/pdfs/`.

---

## 6. Decision (Stage 1 locked)

Proceed with **Stage 6 production hardening** without changing the FUW automation contract:

- Public: health, login, register (ENGINEER only), `POST /documents/auto-generate`, document view/download by UUID.
- Authenticated operator (`ENGINEER`/`ADMIN`): portal/workflow writes, runs, document list, render-pdf, security scans.
- No real student credentials in source, env examples, compose, or tests.
