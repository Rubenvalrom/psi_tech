"""Application configuration and environment variables."""
import os
from typing import Optional


class Settings:
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://olympus_admin:olympus_password@localhost:5432/olympus_smart_gov",
    )

    # Keycloak (Fase 2)
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "olympus")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "olympus-backend")
    KEYCLOAK_CLIENT_SECRET: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

    # Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")

    # JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-secret-key-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Olympus Smart Gov"
    PROJECT_VERSION: str = "1.0.0"

    # App
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"


settings = Settings()
