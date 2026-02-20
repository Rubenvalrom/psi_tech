# Olympus Smart Gov - Skills Architecture

Complete skill documentation for the Olympus Smart Gov platform development. These skills capture specialized knowledge for building government digital services using FastAPI, React, PostgreSQL, and AI/LLM integration.

## 📚 Complete Skills Index

### **Core Services (3 skills)**

#### 1. [skill-keycloak-fastapi-oauth2](./skill-keycloak-fastapi-oauth2)
**OAuth2/OIDC Authentication & RBAC**
- Keycloak realm and client configuration
- JWT token validation in FastAPI
- Role-based access control (RBAC) patterns
- Integration with Pydantic dependency injection
- **Files**: SKILL.md (380 lines), 3 references, 2 executable scripts
- **Key Scripts**: keycloak_init.py, test_keycloak.py
- **Use When**: Integrating user authentication, enforcing role-based permissions, managing Keycloak realms

#### 2. [skill-ollama-llm-prompts](./skill-ollama-llm-prompts)
**Local LLM Integration & Prompt Engineering**
- Ollama client with async/retry logic
- RAG (Retrieval-Augmented Generation) patterns
- Prompt templates for 4 use cases (autofill, recommendations, forecasting, classification)
- Reliability patterns: circuit breaker, fallback handling, metrics
- **Files**: SKILL.md (350 lines), 3 comprehensive references, 2 executable scripts
- **Key Scripts**: ollama_client.py, test_prompts.py
- **Models**: Mistral 7B, Llama 2, nomic-embed-text for semantic search
- **Use When**: Generating content, analyzing documents, making recommendations, building RAG pipelines

#### 3. [skill-pgvector-semantic-search](./skill-pgvector-semantic-search)
**PostgreSQL Vector Similarity Search**
- pgvector extension setup and HNSW indexing
- Embedding generation (OpenAI API or Ollama)
- Cosine similarity queries
- Hybrid search (vector + keyword)
- **Files**: SKILL.md (280 lines), 3 references, 2 executable scripts
- **Key Scripts**: pgvector_setup.sql, test_vectors.py
- **Performance**: ~10-20ms query time for 10K documents with HNSW index
- **Use When**: Building document search, RAG retrieval, semantic similarity matching

---

### **Backend Patterns (3 skills)**

#### 4. [skill-fastapi-modular-arch](./skill-fastapi-modular-arch)
**Modular FastAPI Architecture**
- APIRouter pattern per resource
- Pydantic schemas (Create/Read/Update)
- Dependency injection with `Depends()`
- Module isolation and testing
- **Files**: SKILL.md, 3 references, 2 scaffold scripts
- **Key Scripts**: scaffold_module.py (auto-generates modules), validate_structure.py (linter)
- **Usage**: Define routes, CRUD operations, validation in isolated modules
- **Use When**: Organizing FastAPI codebase, adding new resources, enforcing consistent structure

#### 5. [skill-bpmn-workflow-engine](./skill-bpmn-workflow-engine)
**Lightweight BPMN Workflow Orchestration**
- Step-based workflow execution
- Conditional transitions and state machines
- Workflow definitions as JSON
- Async step handling
- **Files**: SKILL.md, 2 references, 2 executable scripts
- **Key Scripts**: workflow_engine.py (engine), test_workflows.py (pytest suite)
- **State Machines**: validación → evaluación → aprobación → notificación
- **Use When**: Modeling government procedures, automating multi-step processes, implementing approval chains

#### 6. [skill-digital-signing-crypto](./skill-digital-signing-crypto)
**X.509 Certificates & eIDAS Digital Signatures**
- Certificate generation and validation
- RSA-SHA256 digital signatures
- Audit trail implementation (6-year retention, Spain's LAC)
- Certificate expiration monitoring
- **Files**: SKILL.md, 2 references, 1 executable script
- **Key Scripts**: crypto_utils.py (cert/signature operations, audit logging)
- **Standards**: eIDAS compliance (ES), X.509 v3 certificates
- **Use When**: Signing government documents, ensuring non-repudiation, maintaining audit trails

---

### **Frontend (2 skills)**

#### 7. [skill-react-state-management](./skill-react-state-management)
**Zustand State Management**
- Store setup with async actions
- DevTools + persistence middleware
- Combining multiple stores
- Immer integration for immutability
- **Files**: SKILL.md, 2 references
- **Reference Stores**: useExpedientesStore, useAuthStore, useUserPreferences
- **Async Patterns**: Loading states, error handling, retries
- **Use When**: Managing app state, caching API responses, coordinating component updates

#### 8. [skill-react-testing-vitest](./skill-react-testing-vitest)
**React Component Testing (Vitest + React Testing Library)**
- Component rendering and interaction tests
- Hook testing with renderHook
- Mocking (API, modules, stores, localStorage)
- Event simulation and async assertions
- **Files**: SKILL.md, 3 references, 1 conftest fixture script
- **Mocking Patterns**: HTTP, modules, Zustand stores, localStorage, timers, MSW
- **Coverage Target**: 60%+ for core components
- **Use When**: Writing unit tests, testing hooks, mocking dependencies, ensuring component behavior

---

### **Domain Knowledge (2 skills)**

#### 9. [skill-accounting-budget-schema](./skill-accounting-budget-schema)
**Spanish Public Accounting & Budget Management**
- Budget states: Presupuestado → Comprometido → Obligado → Pagado
- Budget execution reports and variance analysis
- VAT (IVA) calculation (21%, 10%, 4%, exempt)
- Chart of accounts (Plan Contable)
- **Files**: SKILL.md, 2 references, 1 SQL schema script
- **Key Tables**: partida_presupuestaria, compromiso, factura, asiento_contable
- **Compliance**: Spain's LAC 6-year audit retention minimum
- **Use When**: Managing budgets, tracking expenses, financial reporting, VAT compliance

#### 10. [skill-document-analysis-ocr](./skill-document-analysis-ocr)
**OCR & Document Processing**
- PDF/image OCR (pytesseract, pdf2image)
- Metadata extraction via Ollama LLM
- Quality assessment and confidence scoring
- Document validation (invoices, contracts)
- **Files**: SKILL.md, 2 references, 1 service script
- **Key Scripts**: ocr_service.py (async OCR processor)
- **Quality Thresholds**: Excellent (90-100%), Good (70-90%), Fair (50-70%), Poor (<50%)
- **Use When**: Processing government forms, extracting invoice data, document digitization

---

### **Operations (2 skills)**

#### 11. [skill-testing-fastapi-pytest](./skill-testing-fastapi-pytest)
**FastAPI Backend Testing**
- Unit tests with mocking (Keycloak, Ollama, DB)
- Integration tests (database + API)
- Async test fixtures and conftest setup
- Concurrent request testing
- **Files**: SKILL.md, 2 references, 1 conftest fixture script
- **Fixture Setup**: Test database, authenticated client, mocks
- **Coverage Strategy**: 60%+ for critical endpoints
- **Use When**: Testing API endpoints, mocking external services, validating workflows

#### 12. [skill-deploy-docker-cicd](./skill-deploy-docker-cicd)
**Docker & GitHub Actions CI/CD**
- Multi-stage Dockerfile builds
- Docker Compose production setup (5 services)
- GitHub Actions CI/CD pipeline (build → test → push → deploy)
- Health checks and Prometheus monitoring
- **Files**: SKILL.md, 4 references, 4 executable scripts, 1 workflow file
- **Key Scripts**: build_and_push.sh, health_check.py, docker-compose.prod.yml
- **Workflow**: .github/workflows/deploy.yml (test, lint, build, push, deploy)
- **Monitoring**: Prometheus + Grafana dashboards
- **Use When**: Containerizing services, automating deployments, monitoring production

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                                                           │
│  Frontend (React + Vitest)          [skill-7, skill-8]   │
│  ├─ Zustand state stores                                 │
│  ├─ Component tests                                       │
│  └─ Mocked API calls                                     │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  API Gateway / Authentication       [skill-1]            │
│  ├─ Keycloak OAuth2/OIDC                                 │
│  ├─ JWT validation                                        │
│  └─ RBAC enforcement                                      │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Backend Services (FastAPI)    [skill-4, skill-5, skill-6] │
│  ├─ Modular routes (APIRouter)                           │
│  ├─ BPMN workflows (tramitación)                         │
│  ├─ Digital signatures (eIDAS)                           │
│  └─ FastAPI patterns & testing [skill-11]                │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Data & Intelligence Layer          [skill-3, skill-2]  │
│  ├─ PostgreSQL + pgvector semantic search                │
│  ├─ Ollama local LLM (recommendations, RAG)              │
│  └─ Document OCR & metadata [skill-10]                   │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Accounting Layer                  [skill-9]             │
│  ├─ Budget execution (Presupuestado → Pagado)            │
│  ├─ Financial reporting                                   │
│  └─ Compliance & audit trails                            │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Deployment & Monitoring            [skill-12]           │
│  ├─ Docker Compose (6 services)                          │
│  ├─ GitHub Actions CI/CD                                 │
│  ├─ Health checks & metrics                              │
│  └─ Prometheus + Grafana                                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. **Authentication Setup**
```bash
# Initialize Keycloak realm and roles
python .github/skills/skill-keycloak-fastapi-oauth2/scripts/keycloak_init.py
```

### 2. **Database & Vector Search**
```bash
# Create database schema with pgvector
psql -U olympus < .github/skills/skill-pgvector-semantic-search/scripts/pgvector_setup.sql

# Initialize accounting schema
psql -U olympus < .github/skills/skill-accounting-budget-schema/scripts/accounting_schema.sql
```

### 3. **Backend Module Generation**
```bash
# Scaffold a new resource module
python .github/skills/skill-fastapi-modular-arch/scripts/scaffold_module.py \
  --module expedientes \
  --model Expediente
```

### 4. **Workflow Testing**
```bash
# Test BPMN workflow engine
pytest .github/skills/skill-bpmn-workflow-engine/scripts/test_workflows.py -v
```

### 5. **Build & Deploy**
```bash
# Build and push Docker images
bash .github/skills/skill-deploy-docker-cicd/scripts/build_and_push.sh 

# Validate deployment health
python .github/skills/skill-deploy-docker-cicd/scripts/health_check.py
```

## 📋 Skills Usage Reference

| Task | Skills | Scripts |
|------|--------|---------|
| Add user authentication | #1 | keycloak_init.py |
| Search documents | #3, #2 | pgvector_setup.sql, ollama_client.py |
| Create new API resource | #4 | scaffold_module.py |
| Implement approval workflow | #5 | workflow_engine.py |
| Sign government documents | #6 | crypto_utils.py |
| Build React forms | #7, #8 | N/A (reference patterns) |
| Process invoices | #10 | ocr_service.py |
| Track budget execution | #9 | accounting_schema.sql |
| Test API endpoints | #11 | conftest.py, pytest fixtures |
| Deploy to production | #12 | docker-compose.prod.yml, deploy.yml |

## 🔗 Cross-Skill Integration

**Example: Complete Document Processing Workflow**
1. User uploads invoice PDF → [skill-10] OCR extraction
2. Extract metadata (supplier, amount) → [skill-2] Ollama LLM
3. Validate against DB → [skill-3] pgvector similarity search
4. Create commitment → [skill-5] BPMN workflow
5. Sign legally → [skill-6] Digital signatures
6. Track budget → [skill-9] Accounting schema
7. Authenticate user → [skill-1] Keycloak RBAC
8. Store in modular backend → [skill-4] FastAPI routes
9. Test with → [skill-11] pytest + conftest
10. Deploy via → [skill-12] GitHub Actions + Docker

---

## 📞 Support & Questions

Each skill's SKILL.md contains:
- Description & quick start
- File structure
- Key APIs and patterns
- Common use cases
- Troubleshooting tips

Additional details in each skill's `references/` directory for domain-specific knowledge.

Executable scripts in `scripts/` are ready to run for:
- Initialization (Keycloak, databases)
- Testing (pytest, vitest)
- Deployment (Docker, CI/CD)

---

**Version**: 1.0  
**Last Updated**: 2024  
**Target Audience**: Team Olympus developers  
**Stack**: FastAPI, React, PostgreSQL, Keycloak, Ollama, Docker
