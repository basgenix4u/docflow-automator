# DocFlow Automator — Deployment Guide

## Architecture in production

```
Browser
  └─ Vercel (Next.js frontend + /api/* rewrites)
       └─ Render Docker web service (FastAPI + Playwright Chromium)
            ├─ PostgreSQL (Neon / Render / Supabase)
            └─ Cloudinary (optional durable PDFs)
```

Student document generation is **public** and rate-limited.  
Operator consoles (`/portals`, `/workflows`, `/documents`, `/security`) require JWT.

---

## 1. Local development

```bash
cp .env.example .env
# set SECRET_KEY and optional ADMIN_EMAIL / ADMIN_PASSWORD

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
PYTHONPATH=. python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

- UI: http://localhost:3000  
- API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/v1/health  

---

## 2. Docker Compose

```bash
cp .env.example .env
# fill SECRET_KEY (required for real use)
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000  

---

## 3. Render (backend)

`render.yaml` builds `backend/Dockerfile`.

Set these environment variables in the Render dashboard:

| Key | Required | Notes |
|---|---|---|
| `SECRET_KEY` | Yes | Use Render `generateValue` |
| `DATABASE_URL` | Recommended | Postgres URL; SQLite is ephemeral on free dynos |
| `CORS_ORIGINS` | Yes | Your Vercel origin, e.g. `https://docflow-automator.vercel.app` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Optional | Seeds the first ADMIN once |
| `CLOUDINARY_*` | Optional | Persist PDFs across restarts |
| `DEBUG` | No | Must be `False` |

Free Render instances sleep. First Playwright job after wake can take 30–60s.

---

## 4. Vercel (frontend)

- Root directory: `frontend` **or** repo root with existing `vercel.json` rewrites.
- Set `NEXT_PUBLIC_API_FALLBACK_URL` to the Render API `/api/v1` URL if you change hosts.
- Update `vercel.json` destinations if the backend hostname changes.
- Add the Vercel origin to backend `CORS_ORIGINS`.

---

## 5. Security checklist

- [ ] No student passwords in git, `.env.example`, or compose files
- [ ] `SECRET_KEY` is unique and not the development default
- [ ] CORS is an explicit allow-list
- [ ] Public register is acceptable, or `ALLOW_PUBLIC_REGISTER=False`
- [ ] Operator pages require login
- [ ] Rate limit is enabled for `/documents/auto-generate`
- [ ] Generated PDFs are not committed

---

## 6. CI

GitHub Actions (`.github/workflows/ci.yml`) runs:

1. Backend `pytest` against Postgres 16  
2. Frontend `npm run build`
