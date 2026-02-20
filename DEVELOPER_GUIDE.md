# Olympus Smart Gov - Guía del Desarrollador 🏗️

## Arquitectura del Sistema
El sistema sigue una arquitectura modular y distribuida basada en microservicios contenerizados:

1.  **Backend (FastAPI):** Lógica de negocio, orquestación de workflows y servicios económicos.
2.  **Frontend (React + Vite):** Interfaz de usuario responsive con soporte para OIDC.
3.  **Keycloak:** Gestión centralizada de identidad y acceso (SSO/RBAC).
4.  **Ollama:** Motor de IA local para OCR, extracción de metadatos y RAG.
5.  **PostgreSQL + pgvector:** Persistencia relacional y búsqueda semántica.

## Estructura de "Skills"
El desarrollo se basa en un sistema de habilidades modulares situadas en `.github/skills/`. Cada habilidad define:
- **Modelo de datos:** Extensiones al esquema SQL.
- **Servicios:** Lógica de negocio específica (ej. `WorkflowService`).
- **Interfaces:** Endpoints y componentes UI asociados.

## Configuración del Entorno de Desarrollo
```bash
# 1. Clonar el repositorio
git clone <repo_url>

# 2. Levantar la infraestructura
docker compose up -d

# 3. Inicializar Keycloak y Usuarios
docker compose exec backend python app/services/keycloak_setup.py

# 4. Descargar modelos de IA
docker compose exec ollama ollama run llama2
```

## Pruebas
- **Backend:** `cd backend && pytest --cov=app tests/`
- **Frontend:** `cd frontend && npm test`

## Roadmap Técnico
- **Fase 6:** Finalizada. Próxima etapa: Despliegue en Kubernetes y escalabilidad horizontal.
