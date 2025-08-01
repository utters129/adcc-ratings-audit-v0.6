"""
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
