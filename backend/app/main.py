"""
Main FastAPI application.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import engine, init_db
from app.api.v1.api import api_router
from app.core.controls.system_controls import SystemControls

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Initialize database
init_db()

# Initialize system controls
system_controls = SystemControls()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "AI Content Agent System",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.schemas import HealthCheck, SystemMode
    from app.core.llm import llm_provider_factory
    from sqlalchemy import text
    from datetime import datetime
    
    # Check database
    db_healthy = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_healthy = True
    except Exception:
        db_healthy = False
    
    # Check Ollama if configured
    ollama_healthy = None
    if settings.LLM_PROVIDER == "ollama":
        provider = await llm_provider_factory.get_provider()
        ollama_healthy = await provider.is_available()
    
    return HealthCheck(
        status="healthy" if db_healthy else "unhealthy",
        timestamp=datetime.now(),
        version=settings.VERSION,
        database=db_healthy,
        ollama=ollama_healthy,
        system_mode=system_controls.get_mode()
    )


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Upload directory: {settings.UPLOAD_DIR}")
    
    # Initialize system controls
    await system_controls.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("Shutting down AI Content Agent System...")
