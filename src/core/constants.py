"""
ADCC Analysis Engine v0.6 - Application Constants
All non-sensitive configuration values that don't change between environments.
"""

from pathlib import Path

# Project root and data paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATASTORE_DIR = DATA_DIR / "datastore"
LOGS_DIR = PROJECT_ROOT / "logs"

# Web Server Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = False

# Session Management
SESSION_TIMEOUT_ADMIN = 3600  # 1 hour
SESSION_TIMEOUT_DEVELOPER = 1800  # 30 minutes

# API Rate Limiting
RATE_LIMIT_PUBLIC = 100  # requests per hour
RATE_LIMIT_ADMIN = 1000
RATE_LIMIT_DEVELOPER = 5000

# Glicko-2 Rating System Parameters
GLICKO_TAU = 0.5  # System volatility
GLICKO_DEFAULT_RD = 350  # Default rating deviation
GLICKO_DEFAULT_VOL = 0.06  # Default volatility
GLICKO_PERIOD_WEEKS = 6  # Rating period in weeks

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_RETENTION_DAYS = 14

# File Processing
MAX_FILE_SIZE_MB = 50
ALLOWED_FILE_TYPES = ["csv", "xlsx", "json"]
BACKUP_FILES = True

# Browser Automation
CHROME_DRIVER_PATH = PROJECT_ROOT / "drivers" / "chromedriver.exe"
HEADLESS_BROWSER = True

# Database Configuration
DATABASE_URL = f"sqlite:///{DATA_DIR}/adcc_ratings.db"

# Development Settings
TESTING = False
VERBOSE_LOGGING = True

# File Naming Conventions
REGISTRATION_FILE_PREFIX = "registrations_"
MATCH_DATA_FILE_PREFIX = "match_data_"
ATHLETE_PROFILES_FILE = "athlete_profiles.json"
EVENT_MASTER_LIST_FILE = "event_master_list.json"

# Data Validation
MIN_AGE = 5
MAX_AGE = 100
VALID_GENDERS = ["M", "F"]
VALID_SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

# Tournament Configuration
DEFAULT_TOURNAMENT_NAME = "ADCC Tournament"
DEFAULT_DIVISION_FORMAT = "{age_class}_{gender}_{skill_level}_{gi_status}"

# ID Prefixes
ATHLETE_ID_PREFIX = "A"
EVENT_ID_PREFIX = "E"
DIVISION_ID_PREFIX = "D"
MATCH_ID_PREFIX = "M"
CLUB_ID_PREFIX = "C"

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
