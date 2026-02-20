# Monitoring & Observability

## Prometheus Metrics (FastAPI)

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
request_count = Counter(
    'requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['endpoint']
)

@app.middleware("http")
async def track_metrics(request, call_next):
    with request_duration.labels(endpoint=request.url.path).time():
        response = await call_next(request)
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Logging Strategy

```python
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None)
        })

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)
```

## Docker Compose with Prometheus

```yaml
version: '3.8'
services:
  backend:
    image: olympus-backend:latest
    ports:
      - "8000:8000"
  
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## prometheus.yml

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'olympus-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## Alerting

```yaml
# alerts.yml
groups:
  - name: olympus
    rules:
      - alert: HighErrorRate
        expr: |
          rate(requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate on {{ $labels.endpoint }}"
```
