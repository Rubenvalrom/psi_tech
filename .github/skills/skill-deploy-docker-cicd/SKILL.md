---
name: skill-deploy-docker-cicd
description: Deploy FastAPI + React + PostgreSQL stack using Docker, docker-compose, and GitHub Actions CI/CD. Includes multi-stage builds, secrets management, health checks, and automated testing/building/pushing pipelines. Use when orchestrating containerized applications from development to production with reliability and compliance requirements.
---

# Docker & CI/CD Deployment

## Multi-Stage Docker Builds

**Backend (FastAPI)**:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend (React + Vite)**:
```dockerfile
# Stage 1: Build
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

## GitHub Actions CI/CD

See [references/github-actions.md](references/github-actions.md):
- Run tests on push
- Build Docker images
- Push to registry (Docker Hub, GCP Artifact Registry)
- Deploy to production

See [references/secrets-management.md](references/secrets-management.md):
- Store secrets in GitHub (DATABASE_URL, API_KEYS)
- Use GitHub Secrets in workflows
- Vault integration (optional)

See [references/health-checks.md](references/health-checks.md):
- Liveness & readiness probes
- Kubernetes integration
- Graceful shutdown

See [references/monitoring.md](references/monitoring.md):
- Logging (structured JSON)
- Prometheus metrics (optional)
- Error tracking (Sentry, DataDog)
