"""Application configuration and environment variables."""
import os
from typing import Optional


class Settings:
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://olympus_admin:olympus_password@db:5432/olympus_smart_gov",
    )

    # Keycloak
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "olympus")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "olympus-backend")
    KEYCLOAK_CLIENT_SECRET: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "olympus-frontend")

    # Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Security
    VERIFY_SSL: bool = os.getenv("VERIFY_SSL", "true").lower() == "true"

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Olympus Smart Gov")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")

    # App
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    def __init__(self):
        """Validate critical settings on initialization."""
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or self.SECRET_KEY == "":
                raise ValueError("SECRET_KEY must be set in production environment")
            if self.VERIFY_SSL is False:
                raise ValueError("VERIFY_SSL must be True in production environment")


settings = Settings()
