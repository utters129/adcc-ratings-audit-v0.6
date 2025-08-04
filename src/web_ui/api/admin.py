"""
ADCC Analysis Engine - Admin API

This module provides admin endpoints for system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import structlog

from src.web_ui.api.auth import get_current_admin_user
from src.web_ui.models.schemas import TokenData

# Configure logging
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()

# Templates
templates = Jinja2Templates(directory="src/web_ui/templates")


async def get_current_user_or_redirect(request: Request):
    """Get current user or redirect to login if not authenticated."""
    try:
        from src.web_ui.api.auth import get_current_user
        return await get_current_user()
    except HTTPException:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/?login=true", status_code=302)


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: TokenData = Depends(get_current_user_or_redirect)):
    """Admin dashboard page."""
    try:
        # Check if user has admin privileges
        if current_user.role not in ["admin", "developer"]:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Insufficient permissions. Admin access required."},
                status_code=status.HTTP_403_FORBIDDEN
            )
            
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "title": "Admin Dashboard",
                "user": current_user
            }
        )
    except Exception as e:
        logger.error("Error rendering admin dashboard", error=str(e))
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to load admin dashboard"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, current_user: TokenData = Depends(get_current_user_or_redirect)):
    """Admin settings page."""
    try:
        # Check if user has admin privileges
        if current_user.role not in ["admin", "developer"]:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Insufficient permissions. Admin access required."},
                status_code=status.HTTP_403_FORBIDDEN
            )
            
        return templates.TemplateResponse(
            "admin/settings.html",
            {
                "request": request,
                "title": "Admin Settings",
                "user": current_user
            }
        )
    except Exception as e:
        logger.error("Error rendering admin settings", error=str(e))
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to load admin settings"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/data-import", response_class=HTMLResponse)
async def admin_data_import(request: Request, current_user: TokenData = Depends(get_current_user_or_redirect)):
    """Data import page."""
    try:
        # Check if user has admin privileges
        if current_user.role not in ["admin", "developer"]:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Insufficient permissions. Admin access required."},
                status_code=status.HTTP_403_FORBIDDEN
            )
            
        return templates.TemplateResponse(
            "admin/data_import.html",
            {
                "request": request,
                "title": "Data Import",
                "user": current_user
            }
        )
    except Exception as e:
        logger.error("Error rendering data import page", error=str(e))
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to load data import page"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/system-status", response_class=HTMLResponse)
async def admin_system_status(request: Request, current_user: TokenData = Depends(get_current_user_or_redirect)):
    """System status page."""
    try:
        # Check if user has admin privileges
        if current_user.role not in ["admin", "developer"]:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Insufficient permissions. Admin access required."},
                status_code=status.HTTP_403_FORBIDDEN
            )
            
        return templates.TemplateResponse(
            "admin/system_status.html",
            {
                "request": request,
                "title": "System Status",
                "user": current_user
            }
        )
    except Exception as e:
        logger.error("Error rendering system status page", error=str(e))
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to load system status page"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 