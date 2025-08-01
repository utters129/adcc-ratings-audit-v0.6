"""
Settings for ADCC Analysis Engine v0.6
Dynamic, runtime-adjustable settings loaded from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# File Paths
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR", "./data/raw"))
PROCESSED_DATA_DIR = Path(os.getenv("PROCESSED_DATA_DIR", "./data/processed"))
DATASTORE_DIR = Path(os.getenv("DATASTORE_DIR", "./data/datastore"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", "./logs"))

# Web Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Authentication
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
DEVELOPER_USERNAME = os.getenv("DEVELOPER_USERNAME", "developer")
DEVELOPER_PASSWORD = os.getenv("DEVELOPER_PASSWORD", "developer")

# Session Management
SESSION_TIMEOUT_ADMIN = int(os.getenv("SESSION_TIMEOUT_ADMIN", "3600"))
SESSION_TIMEOUT_DEVELOPER = int(os.getenv("SESSION_TIMEOUT_DEVELOPER", "1800"))

# Smoothcomp Credentials
SMOOTHCOMP_USERNAME = os.getenv("SMOOTHCOMP_USERNAME")
SMOOTHCOMP_PASSWORD = os.getenv("SMOOTHCOMP_PASSWORD")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "14"))
