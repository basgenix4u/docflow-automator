# DocFlow Automator — Enterprise Browser Automation, PDF Processing & Portal Security Engine

> **Target Portal:** Federal University Wukari (`https://ug.fuwportal.edu.ng/index.php`)  
> **Demo Credentials:** User ID `use yours` | Password `****`  
> by (Abdulbasit Abdulalim)  

---

## 🌟 Overview

**DocFlow Automator** is a production-ready application built to orchestrate multi-user browser automation workflows, navigate dynamic web dashboards, extract student profile records, compile standardized A4/A5 PDF reports, and automatically audit web portals for authentication security controls.

### Key Capabilities
- **Playwright Automation Engine**: Headless Chromium worker executing automated login, form submissions, and DOM extraction on `https://ug.fuwportal.edu.ng/index.php`.
- **Standardized A4/A5 PDF Exporter**: High-fidelity PDF compilation with custom print CSS `@page` margins, metadata headers, and downloadable file storage.
- **Authentication Security Scanner**: Automated security auditing for HTTP security headers (HSTS, CSP, X-Frame-Options), CSRF anti-forgery tokens, session cookie security flags (`HttpOnly`, `Secure`), and transport encryption.
- **Interactive Command Center**: Next.js 15 web application with real-time execution logs, document viewer, workflow builder, and security audit dashboards.

---

## 🚀 Quick Start & Local Setup

### 1. Backend Service (FastAPI)
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- **API Health Check**: `http://localhost:8000/api/v1/health`
- **OpenAPI Docs**: `http://localhost:8000/docs`

### 2. Frontend Application (Next.js 15)
```bash
cd frontend
npm install
npm run dev
```
- **Web UI Preview**: `http://localhost:3000`

---

## 🐳 Docker Deployment

To launch the complete application stack with Docker Compose:
```bash
docker-compose up --build -d
```

---

## 🧪 Testing & Quality Assurance

### Run Backend Integration Tests
```bash
cd backend
PYTHONPATH=. pytest tests
```

### Run Frontend Typecheck & Build
```bash
cd frontend
npm run build
```

---

## 🔒 Security Practices & Compliance
- **Password Hashing**: Argon2id via `passlib`.
- **JWT Session Tokens**: Statelessly validated JWTs with short expiration windows.
- **Input Validation**: Strict schema enforcement using Pydantic v2.
- **Protected Credentials**: Demo credentials safely loaded via `.env` environment variables.

---

## 📄 License
MIT License • Built by AI Software Factory
