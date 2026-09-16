<div align="center">

# 📄 DocFlow Automator

**Enterprise browser automation, A4/A5 PDF compilation, and portal security testing** — built for the Federal University Wukari student portal.

[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Playwright](https://img.shields.io/badge/Playwright-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

**Author:** [Abdulbasit Abdulalim](https://github.com/basgenix4u)

</div>

---

## 🎯 What It Does

| Audience | Capability |
| --- | --- |
| **Students** | Enter your User ID + password and generate an Examination Card, Course Registration Form, Payment Receipt, or Results as a 1-page A4/A5 PDF |
| **Operators** | An authenticated command centre for portals, workflow runs, document studio, and security scans |

Playwright (Chromium) logs into the live portal, intercepts document webviews, and exports **print-faithful PDFs**.

---

## 🏗 Architecture

```text
Next.js 15 (App Router)  ──REST──▶  FastAPI + SQLAlchemy
                                        │
                         Playwright Chromium + PDF storage
                                        │
                              SQLite or PostgreSQL
```

| Resource | Link |
| --- | --- |
| Design spec | [`docs/01-ARCHITECTURE.md`](docs/01-ARCHITECTURE.md) |
| Gap analysis | [`docs/02-GAP-ANALYSIS.md`](docs/02-GAP-ANALYSIS.md) |
| Deployment | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |
| Task board | [`TASKBOARD.md`](TASKBOARD.md) |

---

## ⚡ Quick Start

```bash
cp .env.example .env
# Set SECRET_KEY. Optionally set ADMIN_EMAIL + ADMIN_PASSWORD.

# Backend
cd backend
pip install -r requirements.txt
playwright install chromium
PYTHONPATH=. python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

| Service | URL |
| --- | --- |
| App | http://localhost:3000 |
| Health | http://localhost:8000/api/v1/health |
| OpenAPI | http://localhost:8000/docs |

> 🔒 **Never commit student portal passwords.** Each user types their own credentials at generate time — they are never stored.

### With Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## 🔌 API Surface

### Public
- `GET /api/v1/health`
- `POST /api/v1/auth/register` *(always creates `ENGINEER`)*
- `POST /api/v1/auth/login`
- `GET /api/v1/portals/`, `GET /api/v1/workflows/`
- `POST /api/v1/documents/auto-generate` *(rate limited)*
- `GET /api/v1/documents/{id}/view|download`

### Operator — `Authorization: Bearer <jwt>` (role `ENGINEER` or `ADMIN`)
- `GET /api/v1/auth/me`
- Portal create + `POST /portals/{id}/test-auth`
- Workflow create + `POST /workflows/{id}/run`
- Runs list / detail / logs
- Documents list + `POST /documents/render-pdf`
- Security scans

---

## 🔒 Security Controls

- **Argon2id** password hashing and JWT access tokens
- Public registration **cannot self-promote** to `ADMIN`
- Operator APIs require RBAC
- CORS allow-list via `CORS_ORIGINS`
- Security headers — `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, HSTS outside debug
- In-memory **sliding-window rate limit** on portal automation
- Document listings are not world-readable
- Portal demo passwords are **never returned** in API responses

---

## 🧪 Tests

```bash
cd backend
PYTHONPATH=. pytest tests -q

cd frontend
npm run build
```

> Live FUW portal jobs are **not** executed in unit tests — the automation solver is mocked.

---

## 📄 License

Released under the [MIT License](./LICENSE).

---

<div align="center">

Built by [Abdulbasit Abdulalim](https://github.com/basgenix4u)

</div>
