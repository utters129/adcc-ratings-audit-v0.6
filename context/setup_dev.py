#!/usr/bin/env python3
"""
Development setup script for ADCC Analysis Engine v0.6
Creates necessary directories and initial files for development.
"""

import os
import json
from pathlib import Path

def create_directory_structure():
    """Create the basic directory structure."""
    directories = [
        "src/data_acquisition",
        "src/data_processing", 
        "src/analytics",
        "src/web_ui",
        "src/utils",
        "src/config",
        "data/raw",
        "data/processed",
        "data/datastore",
        "logs",
        "tests",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_initial_files():
    """Create initial files with basic structure."""
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/data_acquisition/__init__.py",
        "src/data_processing/__init__.py",
        "src/analytics/__init__.py",
        "src/web_ui/__init__.py",
        "src/utils/__init__.py",
        "src/config/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✓ Created: {init_file}")
    
    # Create basic constants file
    constants_content = '''"""
Constants for ADCC Analysis Engine v0.6
Static system-wide constants that rarely change.
"""

# ID Prefixes
ATHLETE_ID_PREFIX = "A"
EVENT_ID_PREFIX = "E"
DIVISION_ID_PREFIX = "D"
MATCH_ID_PREFIX = "M"
CLUB_ID_PREFIX = "C"

# Glicko-2 parameters
GLICKO_TAU = 0.5
GLICKO_DEFAULT_RD = 350
GLICKO_DEFAULT_VOL = 0.06
GLICKO_PERIOD_WEEKS = 6

# Skill-level dependent starting ratings
GLICKO_STARTING_RATINGS = {
    "beginner": 800,
    "intermediate": 900,
    "advanced": 1000,
    "pro": 1000,
    "trials": 1000,
    "world_championship": 1500
}

# Age Classes
AGE_CLASSES = ["youth", "adult", "masters"]

# File Extensions
SUPPORTED_RAW_FORMATS = [".csv", ".xlsx", ".json"]
SUPPORTED_PROCESSED_FORMATS = [".parquet", ".json"]

# API Endpoints
SMOOTHCOMP_API_BASE = "https://adcc.smoothcomp.com/en/organizer/event"
SMOOTHCOMP_REGISTRATIONS_API = "{event_id}/registration/api/registrations"
SMOOTHCOMP_MATCHES_API = "{event_id}/statistics/matches?export=xlsx"
'''
    
    with open("src/config/constants.py", "w") as f:
        f.write(constants_content)
    print("✓ Created: src/config/constants.py")
    
    # Create basic settings file
    settings_content = '''"""
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
'''
    
    with open("src/config/settings.py", "w") as f:
        f.write(settings_content)
    print("✓ Created: src/config/settings.py")

def create_sample_data_files():
    """Create sample data files for testing."""
    
    # Sample athlete profiles
    sample_athlete_profiles = {
        "A123456": {
            "smoothcomp_id": 123456,
            "aliases": ["John Doe", "J. Doe"],
            "latest_name": "John Doe",
            "latest_team": "Team Alpha BJJ",
            "youth": {
                "highest_skill_level": "Advanced",
                "debut_skill_level": "Intermediate",
                "tournaments": {
                    "E98765": {
                        "divisions": ["D001", "D002"],
                        "placement": 1
                    }
                }
            },
            "adult": {
                "highest_skill_level": "Advanced",
                "debut_skill_level": "Advanced",
                "tournaments": {}
            },
            "masters": {
                "highest_skill_level": "Intermediate",
                "debut_skill_level": "Intermediate",
                "tournaments": {}
            }
        }
    }
    
    with open("data/datastore/athlete_profiles.json", "w") as f:
        json.dump(sample_athlete_profiles, f, indent=2)
    print("✓ Created: data/datastore/athlete_profiles.json")
    
    # Sample event master list
    sample_event_master = {
        "events": [
            {
                "id": "E12692",
                "name": "ADCC Chicago Open",
                "date": "2023-09-09",
                "type": "open",
                "country": "United States",
                "smoothcomp_available": True,
                "adcc_region": "North American Trials",
                "multi_day": False,
                "gi_event": False,
                "no_gi_event": True,
                "processed": True,
                "files_downloaded": ["registrations.csv", "matches.xlsx", "registrations.json"],
                "files_missing": []
            }
        ]
    }
    
    with open("data/datastore/event_master_list.json", "w") as f:
        json.dump(sample_event_master, f, indent=2)
    print("✓ Created: data/datastore/event_master_list.json")

def main():
    """Main setup function."""
    print("🚀 Setting up ADCC Analysis Engine v0.6 development environment...\n")
    
    create_directory_structure()
    print()
    
    create_initial_files()
    print()
    
    create_sample_data_files()
    print()
    
    print("✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Copy env.example to .env and configure your settings")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Install pre-commit hooks: pre-commit install")
    print("4. Start coding! Follow the development roadmap in context/Development_Roadmap_v0.6.md")

if __name__ == "__main__":
    main() 