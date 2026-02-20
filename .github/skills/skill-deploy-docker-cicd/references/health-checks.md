# Health Checks & Validation

## FastAPI Liveness & Readiness

```python
# main.py
from fastapi import APIRouter, HTTPException
import httpx

health_router = APIRouter()

@health_router.get("/health/live")
async def liveness():
    """Liveness probe: service running?"""
    return {"status": "alive"}

@health_router.get("/health/ready")
async def readiness():
    """Readiness probe: dependencies available?"""
    try:
        # Check DB
        await db.execute("SELECT 1")
        
        # Check Keycloak
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{KEYCLOAK_URL}/auth/realms/{KEYCLOAK_REALM}",
                timeout=5
            )
            resp.raise_for_status()
        
        # Check Ollama
        resp = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        
        return {"status": "ready", "checks": ["db", "keycloak", "ollama"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

app.include_router(health_router)
```

## Docker Healthcheck

```dockerfile
FROM python:3.11-slim

# ... install dependencies ...

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ready || exit 1
```

## Kubernetes Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: olympus-backend
spec:
  containers:
  - name: backend
    image: olympus-backend:latest
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 5
```

## Load Balancer Validation

```bash
# Test endpoint before routing traffic
while ! curl -f http://backend:8000/health/ready; do
  sleep 1
done
echo "Backend ready!"
```
