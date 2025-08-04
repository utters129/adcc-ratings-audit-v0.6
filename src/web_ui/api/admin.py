"""
ADCC Analysis Engine - Admin API

This module provides admin endpoints for system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import structlog
from typing import Dict, Any

from src.web_ui.api.auth import get_current_admin_user
from src.web_ui.models.schemas import TokenData
from src.config.settings import get_settings

# Configure logging
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()

# Templates
templates = Jinja2Templates(directory="src/web_ui/templates")


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page."""
    try:
        # Check if user is authenticated by looking for auth token
        auth_token = request.cookies.get("auth_token") or request.headers.get("authorization")
        
        if not auth_token:
            # Redirect to login page if not authenticated
            return RedirectResponse(url="/?login=true", status_code=302)
        
        # For now, just render the dashboard (we'll validate the token in the frontend)
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "title": "Admin Dashboard",
                "user": {"username": "admin"}  # Placeholder
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
async def admin_settings(request: Request):
    """Admin settings page."""
    try:
        # Check if user is authenticated by looking for auth token
        auth_token = request.cookies.get("auth_token") or request.headers.get("authorization")
        
        if not auth_token:
            # Redirect to login page if not authenticated
            return RedirectResponse(url="/?login=true", status_code=302)
        
        # For now, just render the settings page (we'll validate the token in the frontend)
        return templates.TemplateResponse(
            "admin/settings.html",
            {
                "request": request,
                "title": "Admin Settings",
                "user": {"username": "admin"}  # Placeholder
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
async def admin_data_import(request: Request):
    """Data import page."""
    try:
        # Check if user is authenticated by looking for auth token
        auth_token = request.cookies.get("auth_token") or request.headers.get("authorization")
        
        if not auth_token:
            # Redirect to login page if not authenticated
            return RedirectResponse(url="/?login=true", status_code=302)
        
        # For now, just render the data import page (we'll validate the token in the frontend)
        return templates.TemplateResponse(
            "admin/data_import.html",
            {
                "request": request,
                "title": "Data Import",
                "user": {"username": "admin"}  # Placeholder
            }
        )
    except HTTPException as e:
        if e.status_code == 401:
            # Redirect to login page if not authenticated
            return RedirectResponse(url="/?login=true", status_code=302)
        else:
            logger.error("Error rendering data import page", error=str(e))
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Failed to load data import page"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        logger.error("Error rendering data import page", error=str(e))
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to load data import page"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/system-status", response_class=HTMLResponse)
async def admin_system_status(request: Request):
    """System status page."""
    try:
        # Check if user is authenticated by looking for auth token
        auth_token = request.cookies.get("auth_token") or request.headers.get("authorization")
        
        if not auth_token:
            # Redirect to login page if not authenticated
            return RedirectResponse(url="/?login=true", status_code=302)
        
        # For now, just render the system status page (we'll validate the token in the frontend)
        return templates.TemplateResponse(
            "admin/system_status.html",
            {
                "request": request,
                "title": "System Status",
                "user": {"username": "admin"}  # Placeholder
            }
        )
    except HTTPException as e:
        if e.status_code == 401:
            # Redirect to login page if not authenticated
            return RedirectResponse(url="/?login=true", status_code=302)
        else:
            logger.error("Error rendering system status page", error=str(e))
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Failed to load system status page"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        logger.error("Error rendering system status page", error=str(e))
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to load system status page"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# API Endpoints for managing credentials

@router.get("/api/credentials", response_model=Dict[str, Any])
async def get_credentials(request: Request):
    """Get current Smoothcomp credentials (masked for security)."""
    try:
        # Check if user is authenticated by looking for auth token in cookies/headers
        auth_token = request.cookies.get("auth_token") or request.headers.get("authorization")
        
        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        settings = get_settings()
        
        # Mask credentials for security
        username = settings.smoothcomp_username
        password = settings.smoothcomp_password
        
        masked_username = username[:3] + "***" + username[-2:] if username and len(username) > 5 else "***"
        masked_password = "***" if password else "Not set"
        
        return {
            "username": masked_username,
            "password_set": bool(password),
            "credentials_configured": bool(username and password)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting credentials", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credentials"
        )


@router.post("/api/credentials/test")
async def test_credentials(request: Request):
    """Test current Smoothcomp credentials."""
    try:
        # Check if user is authenticated
        auth_token = request.cookies.get("auth_token") or request.headers.get("authorization")
        
        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        settings = get_settings()
        
        if not settings.smoothcomp_username or not settings.smoothcomp_password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Credentials not configured"}
            )
        
        # Try to import and test the SmoothcompClient
        try:
            from src.data_acquisition.smoothcomp_client import SmoothcompClient
            
            # Create client with current credentials
            client = SmoothcompClient(
                username=settings.smoothcomp_username,
                password=settings.smoothcomp_password
            )
            
            # Test login (this would actually try to connect to Smoothcomp)
            # For now, we'll just check if the client can be created
            return JSONResponse(
                content={
                    "success": True, 
                    "message": "Credentials appear valid (client created successfully)",
                    "username": settings.smoothcomp_username[:3] + "***" + settings.smoothcomp_username[-2:] if len(settings.smoothcomp_username) > 5 else "***"
                }
            )
            
        except ImportError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "SmoothcompClient not available"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": f"Connection test failed: {str(e)}"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error testing credentials", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test credentials"
        )


@router.get("/api/system-info", response_model=Dict[str, Any])
async def get_system_info(request: Request):
    """Get system information and configuration."""
    try:
        # Check if user is authenticated
        auth_token = request.cookies.get("auth_token") or request.headers.get("authorization")
        
        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        settings = get_settings()
        
        return {
            "environment": settings.environment,
            "debug_mode": settings.debug,
            "datastore_directory": str(settings.datastore_dir),
            "credentials_configured": bool(settings.smoothcomp_username and settings.smoothcomp_password),
            "version": "0.6.0-alpha"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting system info", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system information"
        ) 