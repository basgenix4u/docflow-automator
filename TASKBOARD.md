# DocFlow Automator — Master Task Board

`[ ]` Pending · `[~]` In Progress (max **one**) · `[x]` Complete

**Source of truth:** `docs/01-ARCHITECTURE.md` + live FUW portal product behaviour  
**GitHub:** `basgenix4u/docflow-automator`

---

## Stage 1 — Architecture & Design Approval ✅ COMPLETE
- [x] 1.1 Ingest product requirements (architecture spec + implemented student printer)
- [x] 1.2 Propose System Architecture, Schema, API Contracts & Master Task Board
- [x] 1.3 Validate implementation vs architecture (see `docs/02-GAP-ANALYSIS.md`)

---

## Stage 2 — Development Environment Setup ✅ COMPLETE
- [x] 2.1 Scaffold monorepo (`backend/`, `frontend/`, `docs/`)
- [x] 2.2 Configure backend (`requirements.txt`, FastAPI entrypoint)
- [x] 2.3 Configure frontend (`package.json`, `tsconfig.json`, Tailwind v4)
- [x] 2.4 Sanitize environment templates (no real student secrets, portable paths)
- [x] 2.5 Install dependencies & Playwright
- [x] 2.6 Smoke-test health endpoint (`/api/v1/health`)
- [x] 2.7 Verify local tooling

---

## Stage 3 — Backend Core Implementation ✅ COMPLETE
- [x] 3.1 Domain models & database
- [x] 3.2 Authentication core (Argon2id, JWT, user router)
- [x] 3.3 Portal management service & API
- [x] 3.4 Playwright browser automation
- [x] 3.5 Workflow execution & logging
- [x] 3.6 Document detection & A4/A5 PDF exporter
- [x] 3.7 Portal authentication security scanner
- [x] 3.8 Automated unit & integration tests

---

## Stage 4 — Frontend UI & Live Integration ✅ COMPLETE
- [x] 4.1 App shell, navigation & layout
- [x] 4.2 Authentication pages & session state
- [x] 4.3 Portals management dashboard
- [x] 4.4 Workflow builder & execution monitor
- [x] 4.5 Document studio & PDF preview/download
- [x] 4.6 Security testing dashboard
- [x] 4.7 Live API integration (`npm run build` clean)

---

## Stage 5 — Production Readiness & Deployment ✅ COMPLETE
- [x] 5.1 Containerization (`Dockerfile`, `docker-compose.yml`)
- [x] 5.2 CI/CD (`.github/workflows/ci.yml`)
- [x] 5.3 Production README & deployment docs
- [x] 5.4 Integration verification
- [x] 5.5 GitHub repository published

---

## Stage 6 — Production Hardening ✅ COMPLETE
- [x] 6.1 Architecture gap analysis written
- [x] 6.2 Secure configuration: secrets, CORS, admin seed, env templates
- [x] 6.3 RBAC on mutating/admin APIs + block privilege escalation
- [x] 6.4 Rate-limit public portal automation; security headers
- [x] 6.5 Restore `POST /documents/render-pdf`; lock document/run listings
- [x] 6.6 Frontend login/register + JWT client + protect operator pages
- [x] 6.7 Remove committed PII / demo student credentials from templates & UI
- [x] 6.8 Expand automated tests (authz, register role lock, rate limit, health)
- [x] 6.9 Docker/CI/Render/README production polish
- [x] 6.10 All tests pass (`pytest` 10/10); frontend production build succeeds
