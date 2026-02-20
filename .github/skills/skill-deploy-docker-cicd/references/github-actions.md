# GitHub Actions CI/CD Workflow

```yaml
name: Build & Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm --prefix frontend ci
      - run: npm --prefix frontend run test
      - run: npm --prefix frontend run lint

  build-and-push:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: myrepo/olympus-backend:${{ github.sha }}
      
      - uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: myrepo/olympus-frontend:${{ github.sha }}
```

# Secrets Management

```yaml
# In GitHub Actions, reference secrets:
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  KEYCLOAK_CLIENT_SECRET: ${{ secrets.KEYCLOAK_CLIENT_SECRET }}
  OLLAMA_API_KEY: ${{ secrets.OLLAMA_API_KEY }}
```

Set secrets in GitHub repo settings → Secrets and variables → Actions
