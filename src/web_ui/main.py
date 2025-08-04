"""
ADCC Analysis Engine - Web UI Main Application

This module provides the main FastAPI application for the ADCC analysis engine web interface.
It includes authentication, API routes, and static file serving.
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import structlog

from src.config.settings import get_settings
from src.web_ui.api import auth, athletes, events, leaderboards, admin
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

# Log static file setup
logger.info(f"Static directory: {static_dir}")
logger.info(f"Static directory exists: {static_dir.exists()}")
if static_dir.exists():
    logger.info(f"Static files found: {list(static_dir.rglob('*'))}")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.error(f"Static directory not found: {static_dir}")

logger.info(f"Templates directory: {templates_dir}")
logger.info(f"Templates directory exists: {templates_dir.exists()}")
if templates_dir.exists():
    logger.info(f"Template files found: {list(templates_dir.rglob('*.html'))}")

templates = Jinja2Templates(directory=str(templates_dir))

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(athletes.router, prefix="/api/athletes", tags=["Athletes"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(leaderboards.router, prefix="/api/leaderboards", tags=["Leaderboards"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


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


@app.get("/debug/static")
async def debug_static():
    """Debug endpoint to check static file configuration."""
    static_dir = Path(__file__).parent / "static"
    static_files = []
    
    if static_dir.exists():
        for file_path in static_dir.rglob('*'):
            if file_path.is_file():
                static_files.append(str(file_path.relative_to(static_dir)))
    
    return {
        "static_dir": str(static_dir),
        "static_dir_exists": static_dir.exists(),
        "static_files": static_files,
        "static_url": "/static"
    }


@app.get("/static/js/main.js")
async def serve_main_js():
    """Serve main.js with proper MIME type and CORS headers."""
    from fastapi.responses import Response
    js_file = Path(__file__).parent / "static" / "js" / "main.js"
    if js_file.exists():
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/javascript",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Cache-Control": "no-cache"
            }
        )
    else:
        raise HTTPException(status_code=404, detail="main.js not found")


@app.get("/static/css/style.css")
async def serve_style_css():
    """Serve style.css with proper MIME type and CORS headers."""
    from fastapi.responses import Response
    css_file = Path(__file__).parent / "static" / "css" / "style.css"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="text/css",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Cache-Control": "no-cache"
            }
        )
    else:
        raise HTTPException(status_code=404, detail="style.css not found")


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