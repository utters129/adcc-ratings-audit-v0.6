"""
Settings for ADCC Analysis Engine v0.6
Dynamic, runtime-adjustable settings loaded from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Smoothcomp Credentials
    smoothcomp_username: Optional[str] = os.getenv("SMOOTHCOMP_USERNAME")
    smoothcomp_password: Optional[str] = os.getenv("SMOOTHCOMP_PASSWORD")
    
    # Web UI Authentication
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin")
    developer_username: str = os.getenv("DEVELOPER_USERNAME", "developer")
    developer_password: str = os.getenv("DEVELOPER_PASSWORD", "developer")
    secret_key: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    
    # Railway Deployment
    railway_volume_mount_path: Optional[str] = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
