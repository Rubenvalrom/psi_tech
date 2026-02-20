# Secrets & Environment Management

## Docker Secrets (Swarm Mode)

```bash
# Create secret
echo "supersecret" | docker secret create db_password -

# Use in compose
version: '3.8'
services:
  backend:
    image: olympus-backend:latest
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    external: true
```

## .env File Hierarchy

```
.env.local          (git-ignored, local development)
.env.production     (git-ignored, production values)
.env.example        (git-tracked, template with dummy values)

# Docker build args
docker build \
  --build-arg DATABASE_URL=postgres://... \
  --build-arg KEYCLOAK_SECRET=... \
  -t olympus-backend:latest .
```

## Environment Variables by Service

```python
# FastAPI: validate on startup
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    keycloak_secret: str
    ollama_api_key: str
    jwt_secret: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Kubernetes Secrets (for orchestration)

```bash
# Create from file
kubectl create secret generic olympus-secrets \
  --from-file=.env \
  -n olympus

# Use in pod
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: olympus-secrets
        key: database_url
```
