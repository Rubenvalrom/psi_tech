# Olympus Smart Gov - Platform de Tramitación Inteligente

**Hackathon Project | Administración Pública Inteligente | FastAPI + React + PostgreSQL + Ollama**

---

## 📊 Project Status

| Fase | Status | Completitud | Fecha |
|------|--------|------------|-------|
| **Fase 1** | ✅ COMPLETADA | 100% | 2026-02-20 |
| **Fase 2** | 🚀 EN PLANIFICACIÓN | Planning phase | 2026-02-24 |
| Fase 3-6 | 📅 Planeadas | - | 2026-03-05 onwards |

**Current:** Infrastructure + Base API ready. Awaiting authentication layer (Phase 2) to unlock development of tramitación module, financial module, and advanced AI features.

---

## 🎯 What is Olympus Smart Gov?

### Mission
Modernize Spanish public administration through intelligent document processing, workflow automation, and AI-powered decision support for administrative procedures (tramitaciones).

### Key Features (Roadmap)
- 🔐 **Secure Authentication** - OAuth2 via Keycloak with role-based access
- 📄 **Intelligent Document Processing** - OCR + LLM-powered metadata extraction
- ⚙️ **Workflow Automation** - BPMN-style state machines for procedures
- 💰 **Financial Management** - Budget tracking, invoices, accounting
- 🤖 **AI Assistant** - Multi-turn conversational support + predictive analytics
- 🔍 **Vector Search** - Semantic search on expedientes via pgvector

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Port 3000, 5000, 8000, 8080, 11434 available

### Run Development Stack

```bash
cd c:\Users\rubi6\Desktop\Proyectos\Startup\psi_tech

# Start all services (PostgreSQL, Keycloak, Ollama, Backend, Frontend)
docker compose up -d

# Wait ~30 seconds for services to initialize

# Verify everything is healthy
docker compose ps
# All 5 containers should show "Up" ✅

# Test Backend API
curl http://localhost:8000/api/v1/health

# Open Frontend
# Visit http://localhost:3000 in your browser
```

### Useful Commands

```bash
# View logs
docker compose logs -f                     # All services
docker compose logs -f olympus_backend     # Backend only
docker compose logs -f olympus_frontend    # Frontend only

# Stop services
docker compose down

# Clean (remove volumes)
docker compose down -v

# Run database migrations
docker compose exec olympus_backend python -m alembic upgrade head

# Access API documentation
# Browser: http://localhost:8000/docs (Swagger UI)

# Access Keycloak admin
# Browser: http://localhost:8080 (user: admin, password: admin_password)
```

---

## 📚 Documentation & Planning

### For Project Managers / Leaders
- **[ROADMAP.md](ROADMAP.md)** - Visual timeline, risks, success metrics (5 min read)
- **[PHASE_2_PLAN.md](PHASE_2_PLAN.md)** - Detailed Fase 2 execution plan with tasks, timeline, deliverables
- **[plan-olympusSmartGov.md](plan-olympusSmartGov.md)** - Master plan with all 6 phases (historical reference)

### For Developers
- **[PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md)** - Complete specification of Phase 1 (what was built)
- **[PHASE_1_VERIFICATION.md](PHASE_1_VERIFICATION.md)** - Checklist to verify Phase 1 completeness (5 min)
- **[backend/README.md](backend/README.md)** - Backend architecture, models, endpoints (incoming Phase 2)
- **[frontend/README.md](frontend/README.md)** - Frontend setup, components, testing (incoming Phase 2)

### For DevOps
- **[docker-compose.yml](docker-compose.yml)** - Full stack orchestration with 5 services
- Health checks configured for all containers
- Volume mounts for hot reload (backend, frontend)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Browser (Port 3000)                   │
├─────────────────────────────────────────────────────────────────┤
│  ProtectedRoute → useAuth Hook → API Client (axios)             │
│  Pages: Login, Dashboard, ExpedientesListado, PresupuestosPage  │
│  Components: NavBar, Layout, CargaDocumentos (Phase 2)           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP: /api/v1/*
┌──────────────────────────┴──────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                         │
├─────────────────────────────────────────────────────────────────┤
│  Routes: health, expedientes, presupuestos, pasos                │
│  Security: @require_auth decorator (Phase 2: JWT)               │
│  Models: User, Expediente, Documento, PartidaPresupuestaria     │
│  Services: Keycloak, Ollama (OCR+IA Phase 2), Database          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQL: psycopg2
┌──────────────────────────┴──────────────────────────────────────┐
│         PostgreSQL 16 + pgvector (Port 5432)                     │
├─────────────────────────────────────────────────────────────────┤
│  Tables:                                                         │
│  • user (auth, roles)                                            │
│  • expediente (procedures, estado, responsable)                  │
│  • documento (PDFs, OCR metadata)                                │
│  • paso_tramitacion (workflow history)                           │
│  • partida_presupuestaria (budget execution)                     │
│  • factura (invoices, payments)                                  │
│  • document_embedding (vectors for RAG - Phase 5)                │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│          Supporting Services                                     │
├─────────────────────────────────────────────────────────────────┤
│  🔐 Keycloak (Port 8080): OAuth2/OIDC identity (Phase 2)        │
│  🤖 Ollama (Port 11434): Local LLM (Llama 2) for AI (Phase 2)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
olympus-smartgov/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # Config/env
│   │   │   ├── database.py       # SQLAlchemy setup
│   │   │   ├── security.py       # JWT, @require_auth (Phase 2)
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── expediente.py
│   │   │   ├── documento.py      # metadatos_extraidos (Phase 2)
│   │   │   ├── financiero.py     # Presupuestos, Facturas
│   │   │
│   │   ├── schemas/              # Pydantic validators
│   │   │
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── expedientes.py    # CRUD expedientes
│   │   │   ├── presupuestos.py   # Budget endpoints
│   │   │   ├── auth.py           # LOGIN (Phase 2)
│   │   │   ├── documentos.py     # OCR+IA analyze (Phase 2)
│   │   │
│   │   └── services/             # Business logic
│   │       ├── ollama_service.py  # LLM calls (Phase 2)
│   │       ├── ocr_service.py     # pytesseract (Phase 2)
│   │
│   ├── alembic/                  # DB migrations
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── frontend/                     # React + Vite
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx         # Keycloak redirect (Phase 2)
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ExpedientesListado.jsx
│   │   │   └── PresupuestosPage.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── NavBar.jsx
│   │   │   ├── Layout.jsx
│   │   │   ├── CargaDocumentos.jsx  # (Phase 2)
│   │   │   └── CardMetadatos.jsx    # (Phase 2)
│   │   │
│   │   ├── services/
│   │   │   ├── api.js           # axios client
│   │   │   └── auth.js          # Keycloak (Phase 2)
│   │   │
│   │   ├── hooks/
│   │   │   └── useAuth.js       # Auth context hook (Phase 2)
│   │   │
│   │   └── stores/              # Zustand state (placeholder)
│   │
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── docker-compose.yml            # Full stack orchestration
├── PHASE_1_COMPLETE.md           # Fase 1 specification
├── PHASE_1_VERIFICATION.md       # Fase 1 checklist
├── PHASE_2_PLAN.md              # Detailed Fase 2 plan
├── ROADMAP.md                    # Visual timeline + risks
├── plan-olympusSmartGov.md      # Master plan (historical)
├── README.md                     # This file
└── LICENSE                       # Apache 2.0
```

---

## 🔐 Security & Compliance

- **Authentication:** OAuth2/OIDC via Keycloak (Phase 2)
- **Authorization:** Role-Based Access Control (ADMIN, FUNCIONARIO, GESTOR_FINANCIERO, VIEWER)
- **Data:** PostgreSQL with encryption at rest (configurable)
- **API:** JWT tokens with 48h expiry, refresh token flow
- **Logging:** All auth attempts logged with timestamp
- **Compliance:** Arquitectura alineada con RGPD, contabilidad pública española (Phase 4), eIDAS digital signatures (Phase 3)

---

## 🧪 Testing

### Phase 1 (Current)
- ✅ Health check endpoint
- ✅ CRUD operations testeable via Postman/curl

### Phase 2 (Incoming)
- pytest backend (auth, OCR, Ollama services) - target >60% coverage
- vitest React components - ProtectedRoute, CargaDocumentos, etc.

### Phase 6 (Final)
- CI/CD pipeline (GitHub Actions)
- Automated testing on every PR
- Coverage reports

---

## 🚀 Deployment

### Current (Development)
```bash
docker compose up -d
# All services start locally
```

### Production (Phase 6)
- Kubernetes manifests (configmaps, secrets, deployments)
- GitHub Actions CI/CD for auto-build & push to registry
- Health checks + auto-scaling
- Monitoring + logging integration

---

## 📋 Roadmap Summary

| Phase | Timeline | Focus | Status |
|-------|----------|-------|--------|
| **1** | Week 1 | Infrastructure, base API, DB schema | ✅ DONE |
| **2** | Week 2-3 | Auth (OAuth2) + IA PoC (OCR+Ollama) | 🚀 KICKOFF Feb 24 |
| **3** | Week 3-4 | Tramitación workflows (BPMN) + e-signatures | 📅 Planned |
| **4** | Week 4-5 | Economic module (presupuestos, facturas) | 📅 Planned |
| **5** | Week 5-6 | Advanced AI (RAG, assistants, vector search) | 📅 Planned |
| **6** | Week 6-7 | Testing (60%+), CI/CD, documentation | 📅 Planned |

**Est. completion:** End of April 2026

---

## 🤝 Contributing

- Create feature branches: `git checkout -b feature/X`
- Write tests for new code
- Submit PR with description linking to issue/task
- Ensure ESLint (frontend) & Flake8 (backend) pass

---

## 📞 Contact

**Project Lead:** Roberto (rubi6)

**Questions?**
- Technical: Refer to [PHASE_2_PLAN.md](PHASE_2_PLAN.md)
- Architecture: See [ROADMAP.md](ROADMAP.md)
- Status check: [PHASE_1_VERIFICATION.md](PHASE_1_VERIFICATION.md)

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE)

---

**Last Updated:** 2026-02-20 | **Version:** v0.1.0 (Phase 1 Complete) | **Next:** v0.2.0 (Phase 2)
