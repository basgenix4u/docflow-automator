# DocFlow Automator

Enterprise browser automation, A4/A5 PDF compilation, and portal security testing — built for the Federal University Wukari student portal (`https://ug.fuwportal.edu.ng/index.php`).

**Author:** Abdulbasit Abdulalim  
**Repository:** [basgenix4u/docflow-automator](https://github.com/basgenix4u/docflow-automator)

---

## What it does

| Audience | Capability |
|---|---|
| Students | Enter User ID + password, generate Examination Card, Course Registration Form, Payment Receipt, or Results as a 1-page A4/A5 PDF |
| Operators | Authenticated command center for portals, workflow runs, document studio, and security scans |

Playwright (Chromium) logs into the live portal, intercepts document webviews, and exports print-faithful PDFs.

---

## Architecture

```
Next.js 15 (App Router)  ──REST──▶  FastAPI + SQLAlchemy
                                        │
                         Playwright Chromium + PDF storage
                                        │
                              SQLite or PostgreSQL
```

Design spec: [`docs/01-ARCHITECTURE.md`](docs/01-ARCHITECTURE.md)  
Gap analysis: [`docs/02-GAP-ANALYSIS.md`](docs/02-GAP-ANALYSIS.md)  
Deploy: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)  
Task board: [`TASKBOARD.md`](TASKBOARD.md)

---

## Quick start

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

- App: http://localhost:3000  
- Health: http://localhost:8000/api/v1/health  
- OpenAPI: http://localhost:8000/docs  

**Never commit student portal passwords.** Each user types their own credentials at generate time; they are not stored.

---

## Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## API surface

### Public
- `GET /api/v1/health`
- `POST /api/v1/auth/register` (always creates `ENGINEER`)
- `POST /api/v1/auth/login`
- `GET /api/v1/portals/`, `GET /api/v1/workflows/`
- `POST /api/v1/documents/auto-generate` (rate limited)
- `GET /api/v1/documents/{id}/view|download`

### Operator (`Authorization: Bearer <jwt>`, role `ENGINEER` or `ADMIN`)
- `GET /api/v1/auth/me`
- Portal create + `POST /portals/{id}/test-auth`
- Workflow create + `POST /workflows/{id}/run`
- Runs list / detail / logs
- Documents list + `POST /documents/render-pdf`
- Security scans

---

## Security controls

- Argon2id password hashing, JWT access tokens
- Public registration cannot self-promote to `ADMIN`
- Operator APIs require RBAC
- CORS allow-list via `CORS_ORIGINS`
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, HSTS in non-debug)
- In-memory sliding-window rate limit on portal automation
- Document listings are not world-readable
- Portal demo passwords are never returned in API responses

---

## Tests

```bash
cd backend
PYTHONPATH=. pytest tests -q

cd frontend
npm run build
```

Live FUW portal jobs are **not** executed in unit tests. The automation solver is mocked.

---

## License

MIT License
