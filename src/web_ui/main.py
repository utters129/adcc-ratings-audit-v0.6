"""
ADCC Analysis Engine - Web UI Main Application

This module provides the main FastAPI application for the ADCC analysis engine web interface.
It includes authentication, API routes, and static file serving.
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import structlog

from src.config.settings import get_settings
from src.web_ui.api import auth, athletes, events, leaderboards
from src.web_ui.models.schemas import ErrorResponse

# Configure logging
logger = structlog.get_logger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="ADCC Analysis Engine",
    description="Web interface for ADCC competition analysis and ratings",
    version="0.6.0-alpha",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(templates_dir))

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(athletes.router, prefix="/api/athletes", tags=["Athletes"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(leaderboards.router, prefix="/api/leaderboards", tags=["Leaderboards"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting ADCC Analysis Engine Web UI")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down ADCC Analysis Engine Web UI")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main application page."""
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "ADCC Analysis Engine"}
        )
    except Exception as e:
        logger.error("Error rendering index page", error=str(e))
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to load page"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.6.0-alpha"}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Page not found"},
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    logger.error("Internal server error", error=str(exc))
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Internal server error"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.web_ui.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 