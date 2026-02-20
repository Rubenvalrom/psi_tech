from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import engine, Base, init_db, close_db
from app.routes import health, expedientes, presupuestos

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://frontend:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    logger.info("Starting up Olympus Backend...")
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown."""
    logger.info("Shutting down Olympus Backend...")
    await close_db()


# Include routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(expedientes.router, prefix=settings.API_V1_STR)
app.include_router(presupuestos.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Olympus Smart Gov Backend API",
        "version": settings.PROJECT_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
