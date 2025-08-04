"""
ADCC Analysis Engine - Authentication API

This module provides authentication endpoints for the web interface.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import structlog

from src.config.settings import get_settings
from src.web_ui.models.schemas import (
    LoginRequest, LoginResponse, TokenData, UserRole, ErrorResponse
)

# Configure logging
logger = structlog.get_logger(__name__)

# Get settings
settings = get_settings()

# Create router
router = APIRouter()

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = settings.secret_key or "your-secret-key-here"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock user database (replace with actual database in production)
MOCK_USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": UserRole.ADMIN
    },
    "developer": {
        "username": "developer", 
        "hashed_password": pwd_context.hash("dev123"),
        "role": UserRole.DEVELOPER
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str) -> Optional[dict]:
    """Get user from database."""
    return MOCK_USERS.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        exp: datetime = payload.get("exp")
        
        if username is None:
            return None
            
        return TokenData(
            username=username,
            role=UserRole(role) if role else None,
            exp=datetime.fromtimestamp(exp) if exp else None
        )
    except JWTError as e:
        logger.error("JWT token verification failed", error=str(e))
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Get current authenticated user from token."""
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


async def get_current_admin_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Get current admin user."""
    if current_user.role not in [UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


async def get_current_developer_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Get current developer user."""
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer access required"
        )
    return current_user


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return access token."""
    try:
        logger.info("Login attempt", username=login_data.username)
        
        user = authenticate_user(login_data.username, login_data.password)
        if not user:
            logger.warning("Login failed", username=login_data.username, reason="invalid_credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"].value},
            expires_delta=access_token_expires
        )
        
        logger.info("Login successful", username=login_data.username, role=user["role"].value)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_role=user["role"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", username=login_data.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """Logout user (token invalidation would be handled on client side)."""
    try:
        logger.info("User logout", username=current_user.username)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error("Logout error", username=current_user.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information."""
    try:
        return {
            "username": current_user.username,
            "role": current_user.role.value if current_user.role else None,
            "expires_at": current_user.exp.isoformat() if current_user.exp else None
        }
    except Exception as e:
        logger.error("Error getting user info", username=current_user.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/verify", response_model=dict)
async def verify_token_endpoint(current_user: TokenData = Depends(get_current_user)):
    """Verify if current token is valid."""
    try:
        return {
            "valid": True,
            "username": current_user.username,
            "role": current_user.role.value if current_user.role else None
        }
    except Exception as e:
        logger.error("Token verification error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 