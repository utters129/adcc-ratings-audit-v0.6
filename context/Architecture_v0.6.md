# ADCC Competitive Analytics Platform v0.6.0-alpha.6: Comprehensive Architecture Document

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Architecture Principles](#core-architecture-principles)
3. [Data Flow Architecture](#data-flow-architecture)
4. [File Structures and Data Models](#file-structures-and-data-models)
5. [Module Architecture](#module-architecture)
6. [Web UI Architecture](#web-ui-architecture)
7. [Security and Permissions](#security-and-permissions)
8. [Git Version Control Strategy](#git-version-control-strategy)
9. [Deployment Architecture](#deployment-architecture)
10. [Data Validation and Error Handling](#data-validation-and-error-handling)
11. [Performance and Scalability](#performance-and-scalability)
12. [Configuration Management](#configuration-management)
13. [User Experience and Security](#user-experience-and-security)
14. [Development Guidelines](#development-guidelines)
15. [Future Considerations](#future-considerations)

---

## 1. System Overview

### 1.1 Project Purpose
The ADCC Competitive Analytics Platform v0.6.0-alpha.6 is a comprehensive data-driven system designed to support critical decision-making for ADCC competitive operations. The platform automates data collection, processing, and analysis to provide objective tools for:

- **Youth Worlds Invitations**: Data-driven selection based on performance metrics
- **Trials Seeding**: Objective bracket seeding using Glicko-2 ratings
- **Registration Auditing**: Automated sandbagging detection
- **Performance Analytics**: Comprehensive athlete and event statistics

### 1.2 Key Innovations in v0.6.0-alpha.6
- **Semi-Manual File Acquisition**: Cloudflare-resistant data collection with Chrome browser integration
- **Modular Architecture**: Easy swapping between acquisition methods
- **Enhanced UI Permissions**: Developer/Admin/Public access levels
- **Template-Based Data Entry**: Support for non-Smoothcomp events
- **Real-Time Web UI**: Browser-based administration and analysis
- **6-Week Glicko Periods**: Hybrid immediate/periodic rating updates
- **Comprehensive Git Version Control**: Organized branching and release strategy
- **Regional Analysis**: ADCC region mapping for trials eligibility

---

## 2. Core Architecture Principles

### 2.1 Modularity and Separation of Concerns
- **Independent Modules**: Each component operates independently with clear interfaces
- **Easy Swapping**: File acquisition methods can be swapped without affecting other modules
- **Common Utilities**: Shared functions centralized in utility modules
- **Orchestration Files**: Clear separation between orchestration and business logic

### 2.2 ID-Based System
- **Athlete_ID**: `A{smoothcomp_id}` (e.g., A56825)
- **Event_ID**: `E{smoothcomp_event_id}` (e.g., E12692)
- **Division_ID**: `D{age_code}-{gender_code}-{skill_code}-{weight_code}` (e.g., D-A-M-ADV-W91KG)
- **Match_ID**: `M-{event_id}-{division_id}-{match_number}` (e.g., M-E12692-D-A-M-ADV-W91KG-001)
- **Club_ID**: `C{club_id}` (e.g., C32158)

### 2.3 Age Class Separation
- **Three Independent Streams**: Youth, Adult, Masters processed separately
- **No Cross-Contamination**: Ratings and records never mix between age classes
- **Parallel Processing**: All functions executed three times (once per age class)

### 2.4 State Management
- **Chronological Processing**: Events processed in chronological order
- **6-Week Rating Periods**: Glicko calculations finalized every 6 weeks from first event date
- **Automatic Period Detection**: System automatically detects when 6-week periods are complete
- **Period Finalization**: Events finalized in the period they started (multi-day events)
- **Provisional Data**: Historical provisional ratings saved for debugging (developer access only)
- **Rollback Capability**: System can revert to any previous 6-week period
- **Save States**: Complete snapshots after each 6-week rating period
- **Out-of-Order Handling**: Automatic rollback and reprocessing for historical events
- **Hybrid Updates**: Immediate provisional ratings with periodic finalization

---

## 3. Data Flow Architecture

### 3.1 File Acquisition Pipeline

#### 3.1.1 Semi-Manual Smoothcomp Acquisition
```
User Action → Browser Navigation → Manual Download → File Detection → Processing
```

**Step 1: API Registration Data**
- **URL**: `https://adcc.smoothcomp.com/en/organizer/event/{event_id}/registration/api/registrations`
- **Method**: Direct HTTP GET (no authentication required)
- **Output**: JSON file with complete registration metadata
- **Purpose**: Reference data for club IDs, user IDs, and event metadata

**Step 2: Match Data Download**
- **URL**: `https://adcc.smoothcomp.com/en/organizer/event/{event_id}/statistics/matches?export=xlsx`
- **Method**: Direct download link
- **Output**: Excel file with match results
- **Purpose**: Primary data for Glicko calculations and match statistics

**Step 3: Registration CSV Download**
- **URL**: `https://adcc.smoothcomp.com/en/organizer/event/{event_id}/registration#!`
- **Method**: Manual user interaction required
- **Process**:
  1. System opens user's Chrome browser to registration page
  2. User manually clicks download button
  3. System monitors download folder for new file
  4. File automatically moved and renamed
  5. System proceeds to next file or event
- **Output**: CSV file with registration details
- **Purpose**: Division assignments and athlete information
- **Browser Integration**: Uses existing Chrome browser session for web UI

#### 3.1.2 Template-Based Data Entry
- **Web UI Form**: Structured input for non-Smoothcomp events
- **Auto-Suggestions**: Name and team matching from existing database
- **Validation**: Real-time validation of required fields
- **File Upload**: Support for pre-filled template files
- **Output**: Standardized data format matching Smoothcomp structure
- **Event Detection**: System checks existing files to determine missing downloads

### 3.2 Data Processing Pipeline

```
Raw Files → Normalization → ID Generation → Classification → Age Class Split → Analytics → Storage
```

**Stage 1: Data Ingestion**
- Load CSV, Excel, and JSON files using Pandas
- Validate file structure and required columns
- Log data samples for debugging

**Stage 2: Normalization**
- Character encoding standardization (UTF-8)
- Name normalization (lowercase, whitespace removal)
- Date parsing and standardization
- Numeric type conversion

**Stage 3: ID Generation**
- Create all required IDs (Athlete, Event, Division, Match, Club)
- Link Smoothcomp IDs to internal IDs
- Generate division IDs from string parsing

**Stage 4: Classification**
- Parse division strings to extract age class, gender, skill, weight
- Assign canonical division IDs
- Cache division mappings for future use
- Process gi/no-gi event types (separate rating pools for gi vs no-gi)
- Handle multi-day events (period assignment based on start date)

**Stage 5: Age Class Separation**
- Filter data into three independent streams (Youth, Adult, Masters)
- Further separate by gi/no-gi event types
- Process each stream separately
- Maintain complete separation of rating pools (no cross-contamination between age classes or gi/no-gi)

**Stage 6: Analytics Processing**
- Calculate Glicko-2 ratings (provisional and final)
  - **Skill-Level Dependent Starting Ratings**: Athletes start with different ratings based on their initial skill level:
    - Beginner: 800 rating
    - Intermediate: 900 rating  
    - Advanced/Pro/Trials: 1000 rating
    - World Championship level events: 1500 rating
  - **Hybrid Update Model**: Immediate provisional updates + 6-week period finalization
- Update athlete records
- Generate medal reports
- Create historical match data with ratings

**Stage 7: Period Management**
- Automatic detection of completed 6-week periods (based on first event date)
- Finalization of Glicko ratings for completed periods
- Creation of period snapshots
- Preservation of provisional data for debugging
- Multi-day event period assignment (based on start date)

---

## 4. File Structures and Data Models

### 4.1 Input File Structures

#### 4.1.1 Registration CSV Structure
```csv
Firstname,Middle name,Lastname,Club,Team,Birth,Group,Entry,Age,Rank,Weight,Admin note,Payment note,Status note,Public note,Weighin,Weighin weight,Paid,Price,Pricing type,Payment,Payment Method,Approved,Placement,Matches Won,Matches Lost,Matches Draw,Nationality,Nationality code,Gender,Phone,Email,Address,Zip,City,Province,Country,Registration date,User id,Club id,Affiliation id,Federation member,Jiu-Jitsu (BJJ),Judo,Tae Kwon Do,Karate,Luta Livre
```

**Key Fields**:
- `User id`: Links to Smoothcomp user ID
- `Club id`: Links to club database
- `Group`: Division string for classification
- `Placement`: Final tournament placement
- `Matches Won/Lost/Draw`: Match statistics

#### 4.1.2 Match Data Excel Structure
```excel
Group / Bracket,Match,Winner,Won by,Time,Round,Firstname Left,Lastname Left,Firstname Right,Lastname Right,Academy Left,Academy Right,Affiliation Left,Affiliation Right,Class pt Left,Class pt Right,Score Left,Score Right,Match details Left,Match details Right,Profile Left,Profile Right,ID Left,ID Right
```

**Key Fields**:
- `Winner`: Athlete name who won the match
- `Won by`: Victory type (SUBMISSION, POINTS, DECISION, BYE)
- `Time`: Match duration
- `Round`: Tournament round
- `Score Left/Right`: Points scored by each athlete

#### 4.1.3 Registration JSON Structure
```json
{
  "id": 3236294,
  "user_id": 56825,
  "club_id": 32158,
  "affiliation_id": 1,
  "active": 1,
  "trashed": 0,
  "event_group_id": 1262639,
  "approved": 1,
  "status": "ok",
  "entry_id": 137851,
  "seed_position": 11,
  "placement": 5,
  "birth": 1993,
  "age": 32,
  "gender": "M",
  "country": "US",
  "firstname": "Justin",
  "lastname": "Michael",
  "clubName": "10th Planet Masury",
  "affiliationName": "10thplanet JJ",
  "categories": [
    {
      "event_registration_id": 3236294,
      "category_value_id": 2904653,
      "event_category_id": 406131,
      "sort_order": 0,
      "weight_measured": null
    }
  ]
}
```

### 4.2 Output File Structures

#### 4.2.1 Athlete Profiles JSON
```json
{
  "A56825": {
    "smoothcomp_id": 56825,
    "aliases": ["Justin Michael", "J. Michael"],
    "latest_name": "Justin Michael",
    "latest_team": "10thplanet JJ",
    "youth": {
      "highest_skill_level": "Advanced",
      "debut_skill_level": "Intermediate",
      "tournaments": {
        "E98765": {
          "divisions": ["D-Y16U-M-ADV-W70KG"],
          "placement": 1
        }
      }
    },
    "adult": {
      "highest_skill_level": "Professional",
      "debut_skill_level": "Advanced",
      "tournaments": {
        "E12692": {
          "divisions": ["D-A-M-ADV-W91KG", "D-A-M-ADV-ABS"],
          "placement": 5
        }
      }
    },
    "masters": {
      "highest_skill_level": null,
      "debut_skill_level": null,
      "tournaments": {}
    }
  }
}
```

#### 4.2.2 Athlete Scores JSON
```json
{
  "A56825": {
    "youth": {
      "glicko": {
        "rating": 1620.5,
        "rd": 75.3,
        "vol": 0.059
      },
      "record": {
        "wins": 12,
        "losses": 3,
        "draws": 1
      }
    },
    "adult": {
      "glicko": {
        "rating": 1850.1,
        "rd": 55.0,
        "vol": 0.06
      },
      "record": {
        "wins": 5,
        "losses": 1,
        "draws": 0
      }
    },
    "masters": {
      "glicko": {
        "rating": 1500,
        "rd": 350,
        "vol": 0.06
      },
      "record": {
        "wins": 0,
        "losses": 0,
        "draws": 0
      }
    }
  }
}
```

#### 4.2.3 Division Map JSON
```json
{
  "D-A-M-ADV-W91KG": {
    "raw_strings": [
      "Men / Adult / Advanced / -91,0 kg",
      "Men's Adult Advanced -91kg",
      "Adult Male Advanced -91kg"
    ],
    "age_class": "Adult",
    "age_division": "Adult",
    "gender": "Male",
    "skill_level": "Advanced",
    "weight_class": "-91kg"
  },
  "D-Y16U-M-ADV-W70KG": {
    "raw_strings": [
      "Boys / Youth 16U / Advanced / -70,0 kg",
      "Youth 16U Boys Advanced -70kg",
      "16U Male Advanced -70kg"
    ],
    "age_class": "Youth",
    "age_division": "16U",
    "gender": "Male",
    "skill_level": "Advanced",
    "weight_class": "-70kg"
  }
}
```

#### 4.2.4 Clubs JSON
```json
{
  "C32158": {
    "name": "10th Planet Masury",
    "affiliation": "10thplanet JJ",
    "country": "US"
  }
}
```

#### 4.2.5 Processed Match Data (Parquet)
```parquet
event_id: string
division_id: string
match_id: string
winner_id: string
loser_id: string
win_type: string
match_time: string
bracket_round: string
winner_glicko_before: float
winner_glicko_after: float
loser_glicko_before: float
loser_glicko_after: float
winner_record_before: struct<wins:int, losses:int, draws:int>
winner_record_after: struct<wins:int, losses:int, draws:int>
loser_record_before: struct<wins:int, losses:int, draws:int>
loser_record_after: struct<wins:int, losses:int, draws:int>
```

#### 4.2.6 Event Log JSON
```json
{
  "events": [
    {
      "event_id": "E12692",
      "event_date": "2023-07-18",
      "processed_date": "2024-01-15",
      "status": "completed",
      "files_processed": ["registrations.csv", "matches.xlsx", "registrations.json"],
      "files_missing": [],
      "smoothcomp_available": true
    }
  ]
}
```

#### 4.2.7 Medal Report JSON
```json
{
  "A56825": {
    "name": "Justin Michael",
    "total_medals": 8,
    "total_gold": 3,
    "total_silver": 2,
    "total_bronze": 3,
    "youth": {
      "total": 5,
      "gold": 2,
      "silver": 1,
      "bronze": 2,
      "divisions": {
        "D-Y16U-M-ADV-W70KG": {"gold": 1, "silver": 0, "bronze": 1},
        "D-Y18U-M-ADV-W80KG": {"gold": 1, "silver": 1, "bronze": 1}
      }
    },
    "adult": {
      "total": 3,
      "gold": 1,
      "silver": 1,
      "bronze": 1,
      "divisions": {
        "D-A-M-ADV-W91KG": {"gold": 0, "silver": 1, "bronze": 1},
        "D-A-M-ADV-ABS": {"gold": 1, "silver": 0, "bronze": 0}
      }
    },
    "masters": {
      "total": 0,
      "gold": 0,
      "silver": 0,
      "bronze": 0,
      "divisions": {}
    }
  }
}
```

#### 4.2.8 Event Master List JSON
```json
{
  "events": [
    {
      "id": "E12692",
      "name": "ADCC Chicago Open",
      "date": "2023-09-09",
      "type": "open",
      "country": "United States",
      "smoothcomp_available": true,
      "adcc_region": "North American Trials",
      "multi_day": false,
      "gi_event": false,
      "no_gi_event": true,
      "processed": true,
      "files_downloaded": ["registrations.csv", "matches.xlsx", "registrations.json"],
      "files_missing": []
    }
  ]
}
```
```json
{
  "A56825": {
    "name": "Justin Michael",
    "total_medals": 8,
    "total_gold": 3,
    "total_silver": 2,
    "total_bronze": 3,
    "youth": {
      "total": 5,
      "gold": 2,
      "silver": 1,
      "bronze": 2,
      "divisions": {
        "D-Y16U-M-ADV-W70KG": {"gold": 1, "silver": 0, "bronze": 1},
        "D-Y18U-M-ADV-W80KG": {"gold": 1, "silver": 1, "bronze": 1}
      }
    },
    "adult": {
      "total": 3,
      "gold": 1,
      "silver": 1,
      "bronze": 1,
      "divisions": {
        "D-A-M-ADV-W91KG": {"gold": 0, "silver": 1, "bronze": 1},
        "D-A-M-ADV-ABS": {"gold": 1, "silver": 0, "bronze": 0}
      }
    },
    "masters": {
      "total": 0,
      "gold": 0,
      "silver": 0,
      "bronze": 0,
      "divisions": {}
    }
  }
}

#### 4.2.9 Glicko Period Snapshots JSON
```json
{
  "period_2024_01_01_to_2024_02_12": {
    "start_date": "2024-01-01",
    "end_date": "2024-02-12",
    "events_processed": ["E12692", "E12933"],
    "snapshot_date": "2024-02-12",
    "youth_scores": "data/datastore/glicko_snapshots/youth_2024_01_01_to_2024_02_12.json",
    "adult_scores": "data/datastore/glicko_snapshots/adult_2024_01_01_to_2024_02_12.json",
    "masters_scores": "data/datastore/glicko_snapshots/masters_2024_01_01_to_2024_02_12.json"
  }
}
```

#### 4.2.10 Provisional Ratings JSON
```json
{
  "A56825": {
    "youth": {
      "provisional_glicko": {
        "rating": 1620.5,
        "rd": 75.3,
        "vol": 0.059,
        "last_updated": "2024-01-15T10:30:00Z"
      }
    },
    "adult": {
      "provisional_glicko": {
        "rating": 1850.1,
        "rd": 55.0,
        "vol": 0.06,
        "last_updated": "2024-01-15T10:30:00Z"
      }
    },
    "masters": {
      "provisional_glicko": {
        "rating": 1500,
        "rd": 350,
        "vol": 0.06,
        "last_updated": "2024-01-15T10:30:00Z"
      }
    }
  }
}
```

#### 4.2.11 Audit Log JSON
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "user": "developer",
      "action": "update_match",
      "details": {
        "match_id": "M-E12692-D-A-M-ADV-W91KG-001",
        "old_winner": "A12345",
        "new_winner": "A67890",
        "reason": "Correction of match result"
      },
      "ip_address": "192.168.1.100"
    }
  ]
}
```

#### 4.2.12 Favorites JSON
```json
{
  "admin_favorites": [
    {
      "athlete_id": "A56825",
      "added_date": "2024-01-15T10:30:00Z",
      "notes": "Strong performance in recent events",
      "priority": "high"
    }
  ]
}
```

#### 4.2.13 Webhook Registry JSON
```json
{
  "webhooks": [
    {
      "id": "webhook_001",
      "name": "ADCC Notifications",
      "url": "https://adcc.com/api/webhooks/notifications",
      "events": ["athlete.rating_updated", "medal.awarded", "period.finalized"],
      "secret": "webhook_secret_key",
      "active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_delivery": "2024-01-15T11:00:00Z",
      "delivery_count": 45,
      "failure_count": 2
    }
  ]
}
```

#### 4.2.14 Webhook Delivery Log JSON
```json
{
  "deliveries": [
    {
      "webhook_id": "webhook_001",
      "event": "athlete.rating_updated",
      "timestamp": "2024-01-15T10:30:00Z",
      "status": "success",
      "response_code": 200,
      "response_time": 0.5,
      "payload_size": 1024,
      "retry_count": 0
    }
  ]
}
```

---

## 5. Module Architecture

### 5.1 Project Structure
```
adcc_analytics_v0.6/
├── .env                          # Environment variables
├── .gitignore
├── requirements.txt              # Python dependencies
├── main.py                       # Main orchestrator
├── config/
│   ├── __init__.py
│   ├── settings.py              # Global configuration
│   ├── logging_config.json      # Logging configuration
│   └── permissions.py           # Permission definitions
├── data/
│   ├── raw/                     # Downloaded files
│   │   ├── registrations/
│   │   ├── matches/
│   │   └── api_data/
│   ├── processed/               # Cleaned data (Parquet)
│   │   ├── youth/
│   │   ├── adult/
│   │   └── masters/
│   ├── datastore/               # Application data
│   │   ├── athlete_profiles.json
│   │   ├── athlete_scores.json
│   │   ├── division_map.json
│   │   ├── clubs.json
│   │   ├── event_log.json
│   │   ├── medal_report.json
│   │   ├── provisional_ratings.json
│   │   ├── audit_log.json
│   │   ├── favorites.json
│   │   ├── webhook_registry.json
│   │   ├── webhook_delivery_log.json
│   │   └── glicko_snapshots/
│   │       ├── youth/
│   │       ├── adult/
│   │       └── masters/
│   └── reports/                 # Generated reports
│       └── medal_report.xlsx
├── logs/                        # Application logs
│   ├── system.log
│   ├── debug.log
│   └── audit.log
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py            # Data models
│   │   ├── constants.py         # System constants
│   │   └── exceptions.py        # Custom exceptions
│   ├── data_acquisition/
│   │   ├── __init__.py
│   │   ├── smoothcomp_client.py # Smoothcomp API client
│   │   ├── browser_automation.py # Selenium automation
│   │   ├── file_monitor.py      # Download folder monitoring
│   │   └── template_processor.py # Template data entry
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── normalizer.py        # Data normalization
│   │   ├── id_generator.py      # ID generation
│   │   ├── classifier.py        # Division classification
│   │   └── age_classifier.py    # Age class separation
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── glicko_engine.py     # Glicko-2 calculations
│   │   ├── record_calculator.py # Win/loss record tracking
│   │   ├── medal_tracker.py     # Medal counting
│   │   └── report_generator.py  # Report generation
│   ├── web_ui/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── athletes.py      # Athlete endpoints
│   │   │   ├── events.py        # Event endpoints
│   │   │   ├── leaderboards.py  # Leaderboard endpoints
│   │   │   ├── admin.py         # Admin endpoints
│   │   │   └── developer.py     # Developer endpoints
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py       # Pydantic models
│   │   │   └── responses.py     # Response models
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── style.css
│   │   │   └── js/
│   │   │       ├── leaderboard.js
│   │   │       ├── athlete_profile.js
│   │   │       └── admin.js
│   │   └── templates/
│   │       ├── base.html
│   │       ├── leaderboard.html
│   │       ├── athlete_profile.html
│   │       └── admin.html
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_handler.py      # File operations
│   │   ├── logger.py            # Logging utilities
│   │   ├── validators.py        # Data validation
│   │   └── helpers.py           # Common utilities
│   ├── webhooks/
│   │   ├── __init__.py
│   │   ├── webhook_manager.py   # Webhook registration and management
│   │   ├── event_dispatcher.py  # Event dispatching to webhooks
│   │   ├── delivery_queue.py    # Asynchronous webhook delivery
│   │   └── security.py          # Webhook security and signatures
│   └── state_management/
│       ├── __init__.py
│       ├── save_states.py       # State snapshots
│       ├── rollback.py          # Rollback operations
│       └── recovery.py          # Recovery procedures
└── tests/
    ├── __init__.py
    ├── test_data_acquisition.py
    ├── test_data_processing.py
    ├── test_analytics.py
    └── test_web_ui.py
```

### 5.2 Core Modules

#### 5.2.1 Data Acquisition Module
**Purpose**: Handle all data input methods with modular design

**Components**:
- `smoothcomp_client.py`: Direct API calls for registration data
- `browser_automation.py`: Selenium automation for manual downloads
- `file_monitor.py`: Monitor download folder for new files
- `template_processor.py`: Handle template-based data entry

**Key Functions**:
```python
async def download_registration_api(event_id: str) -> dict
async def open_registration_page(event_id: str) -> None
async def monitor_downloads(timeout: int = 300) -> List[str]
async def process_template_data(template_data: dict) -> pd.DataFrame
```

#### 5.2.2 Data Processing Module
**Purpose**: Transform raw data into clean, structured format

**Components**:
- `normalizer.py`: Data cleaning and standardization
- `id_generator.py`: Generate all required IDs
- `classifier.py`: Division string parsing and classification
- `age_classifier.py`: Separate data by age class

**Key Functions**:
```python
def normalize_names(df: pd.DataFrame) -> pd.DataFrame
def generate_athlete_id(smoothcomp_id: int) -> str
def parse_division_string(division_str: str) -> dict
def split_by_age_class(df: pd.DataFrame) -> dict
```

#### 5.2.3 Analytics Module
**Purpose**: Calculate ratings, records, and generate reports

**Components**:
- `glicko_engine.py`: Glicko-2 rating calculations with skill-level dependent starting ratings
- `record_calculator.py`: Win/loss record tracking
- `medal_tracker.py`: Medal counting and reporting
- `report_generator.py`: Generate various reports
- `period_manager.py`: 6-week period detection and finalization

**Key Functions**:
```python
def calculate_glicko_ratings(matches: pd.DataFrame, age_class: str) -> dict
def determine_starting_rating(athlete_id: str, event_type: str, skill_level: str) -> int
def update_athlete_records(matches: pd.DataFrame) -> dict
def generate_medal_report() -> dict
def create_historical_match_data(event_id: str) -> pd.DataFrame
def check_6_week_periods() -> List[str]
def finalize_period_ratings(period_start: str, period_end: str) -> None
```

#### 5.2.4 State Management Module
**Purpose**: Handle system state, rollbacks, and recovery

**Components**:
- `save_states.py`: Create and manage state snapshots
- `rollback.py`: Rollback to previous states
- `recovery.py`: Recovery procedures and error handling

**Key Functions**:
```python
def save_monthly_state(month: str) -> None
def rollback_to_date(target_date: str) -> None
def handle_out_of_order_event(event_id: str) -> None
def hard_reset() -> None
def soft_reset() -> None
```

---

## 6. Web UI Architecture

### 6.1 Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templates
- **Authentication**: Simple username/password system
- **Database**: File-based (JSON/Parquet) with optional SQLite for sessions

### 6.2 Permission Levels

#### 6.2.1 Public Access (No Login Required)
- View leaderboards with filtering
- Search and view athlete profiles
- View basic statistics and reports
- Access to "Did you mean?" name suggestions

#### 6.2.2 Admin Access
**Username/Password**: Single admin account
**Capabilities**:
- All public features
- Run registration auditor for future events
- Add new events via template system
- Generate detailed athlete audits
- Create event statistics reports
- Set tournament seeding with recommendations
- View comprehensive medal reports

#### 6.2.3 Developer Access
**Username/Password**: Single developer account
**Capabilities**:
- All admin features
- Modify configuration variables
- Run system commands (hard reset, soft reset, rollbacks)
- Access debug logs and system status
- Trigger manual data processing
- Manage file acquisitions

### 6.3 API Endpoints

#### 6.3.1 RESTful Endpoint Design
```
GET    /api/athletes              # List athletes
GET    /api/athletes/{id}         # Get specific athlete
POST   /api/athletes              # Create athlete (admin only)
PUT    /api/athletes/{id}         # Update athlete (admin only)
DELETE /api/athletes/{id}         # Delete athlete (admin only)

GET    /api/events                # List events
GET    /api/events/{id}/matches   # Get event matches
POST   /api/events                # Create event (admin only)
```

#### 6.3.2 Response Format Standards
```json
{
    "success": true,
    "data": { },
    "meta": {
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "0.6.0"
    },
    "errors": null
}
```

#### 6.3.3 Error Handling Patterns
```python
class APIError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

# Usage
raise APIError("Athlete not found", "ATHLETE_NOT_FOUND", 404)
```

#### 6.3.4 Public Endpoints
```python
GET /api/athletes                    # List athletes with filtering
GET /api/athlete/{athlete_id}        # Get athlete profile
GET /api/leaderboards               # Get filtered leaderboards
GET /api/search/{query}             # Search with suggestions
```

#### 6.3.4 Admin Endpoints
```python
POST /api/admin/audit_event         # Run registration auditor
POST /api/admin/add_event           # Add event via template
GET /api/admin/athlete_audit/{id}   # Detailed athlete audit
GET /api/admin/event_stats/{id}     # Event statistics
POST /api/admin/seeding             # Generate seeding recommendations
POST /api/admin/delete_file         # Delete specific files
GET /api/admin/check_missing_files  # Check for missing files
POST /api/admin/download_files      # Trigger file downloads
POST /api/admin/favorite_athlete    # Add athlete to favorites
DELETE /api/admin/favorite_athlete  # Remove athlete from favorites
GET /api/admin/favorites            # Get list of favorite athletes
```

#### 6.3.5 Developer Endpoints
```python
POST /api/dev/hard_reset            # Hard reset system
POST /api/dev/soft_reset            # Soft reset system
POST /api/dev/rollback              # Rollback to date
POST /api/dev/glicko_reanalysis     # Reanalyze Glicko scores
GET /api/dev/system_status          # System status
POST /api/dev/process_event         # Manual event processing
POST /api/dev/delete_file           # Delete individual files
POST /api/dev/delete_event          # Delete entire event
GET /api/dev/search_matches         # Search matches by ID or criteria
PUT /api/dev/update_match           # Update match results
POST /api/dev/manual_event_input    # Manually input event data
POST /api/dev/webhook/register      # Register new webhook endpoint
DELETE /api/dev/webhook/{id}        # Delete webhook endpoint
GET /api/dev/webhook/list           # List all webhook endpoints
POST /api/dev/webhook/test          # Test webhook delivery
```

### 6.4 UI Features

#### 6.4.1 Leaderboard Page
- **Dynamic Filtering**: Age class, gender, skill level, weight, date range
- **Sorting**: By rating, points, medals, weight
- **Export**: CSV/Excel download
- **Pagination**: Handle large datasets

#### 6.4.2 Athlete Profile Page
- **Summary Section**: Current rating, record, basic info
- **Historical Graph**: Glicko rating over time
- **Medal Breakdown**: Detailed medal counts by division
- **Match History**: Complete match results with ratings
- **International Status**: Competition history

#### 6.4.3 Admin Dashboard
- **Event Management**: Add/process events, update master list
- **File Management**: Check missing files, delete files, trigger downloads
- **Audit Tools**: Registration auditor interface
- **Report Generation**: Medal reports (JSON/Excel), statistics
- **Seeding Assistant**: Tournament seeding tools
- **Regional Analysis**: ADCC region mapping and trials eligibility

#### 6.4.4 Developer Console
- **System Commands**: All terminal functions as buttons
- **Configuration**: Modify settings, event master list, regional mapping
- **Logs**: Real-time log viewing
- **Status**: System health monitoring
- **Data Management**: Delete files/events, rollback operations
- **Glicko Management**: Manual reanalysis, period finalization
- **Webhook Management**: Register, test, and monitor webhook endpoints

#### 6.4.4 Event Creation Form
**Purpose**: Add new events to the system (both Smoothcomp and non-Smoothcomp events)

**Form Fields**:
- **Event ID**: Unique identifier (E + numbers, e.g., "E12692")
- **Event Name**: Human-readable event name
- **Event Date**: Date in YYYY-MM-DD format
- **Event Type**: Dropdown (open, national, trials, etc.)
- **Country**: Country where event was held
- **ADCC Region**: Auto-populated based on country selection
- **Smoothcomp Available**: Checkbox to indicate if event data is on Smoothcomp
- **Multi-Day Event**: Checkbox to indicate if event spans multiple days
- **Gi Event**: Checkbox to indicate if event includes gi divisions
- **No-Gi Event**: Checkbox to indicate if event includes no-gi divisions
- **Notes**: Optional additional information

**Validation Rules**:
- Event ID must be unique and follow format "E" + numbers
- Date must be in valid YYYY-MM-DD format
- At least one of "Gi Event" or "No-Gi Event" must be selected
- Country must be valid and map to an ADCC region
- If Smoothcomp Available is checked, system will attempt to download files

**Auto-Suggestions**:
- Country field provides dropdown with all valid countries
- ADCC Region auto-populates based on selected country
- Event Type provides common options (open, national, trials, etc.)

**Processing**:
- If Smoothcomp Available: Triggers file download process
- If not Smoothcomp Available: Provides template for manual data entry
- Updates EVENT_MASTER_LIST in configuration
- Logs event creation in audit log

---

## 7. Security and Permissions

### 7.1 Authentication System
```python
# Simple username/password system
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secure_password_hash"
DEVELOPER_USERNAME = "developer"
DEVELOPER_PASSWORD = "secure_password_hash"
```

### 7.2 Permission Matrix
| Feature | Public | Admin | Developer |
|---------|--------|-------|-----------|
| View leaderboards | ✅ | ✅ | ✅ |
| View athlete profiles | ✅ | ✅ | ✅ |
| Search athletes | ✅ | ✅ | ✅ |
| Run registration auditor | ❌ | ✅ | ✅ |
| Add events | ❌ | ✅ | ✅ |
| Generate reports | ❌ | ✅ | ✅ |
| Delete files/events | ❌ | ✅ | ✅ |
| System commands | ❌ | ❌ | ✅ |
| Configuration access | ❌ | ❌ | ✅ |
| Rollback operations | ❌ | ❌ | ✅ |
| Glicko reanalysis | ❌ | ❌ | ✅ |

### 7.3 Data Security
- **Environment Variables**: Sensitive data in .env file
- **Input Validation**: All user inputs validated
- **File Permissions**: Secure file access controls
- **Logging**: Audit trail for all admin actions

---

## 8. Git Version Control Strategy

### 8.1 Branching Strategy
**Main Branches**:
- `main`: Production-ready code, stable releases
- `develop`: Integration branch for features
- `release/v0.6.x`: Release preparation branches

**Feature Branches**:
- `feature/module-name`: Individual module development
- `feature/data-acquisition`: File acquisition improvements
- `feature/web-ui`: UI enhancements
- `feature/analytics`: Analytics engine improvements

**Hotfix Branches**:
- `hotfix/critical-bug`: Emergency fixes for production

### 8.2 Version Naming Convention
**Format**: `v0.6.x.y-alpha.z` or `v0.6.x.y-beta.z` or `v0.6.x.y`
- `0.6`: Major version (v0.6)
- `x`: Minor version (feature additions)
- `y`: Patch version (bug fixes)
- `alpha.z`: Alpha version number (for pre-release development)
- `beta.z`: Beta version number (for pre-release testing)

**Examples**:
- `v0.6.0-alpha.6`: Current alpha version (6th alpha)
- `v0.6.0-alpha.7`: Next alpha version
- `v0.6.0-beta.1`: First beta version
- `v0.6.0`: Final release of v0.6.0
- `v0.6.1.0`: First feature update
- `v0.6.1.1`: Bug fix for v0.6.1.0

### 8.3 Commit Message Standards
**Format**: `type(scope): description`
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples**:
- `feat(data-acquisition): add Chrome browser integration`
- `fix(glicko-engine): correct 6-week period calculation`
- `docs(architecture): update deployment instructions`

### 8.4 Release Process
1. **Feature Development**: Work on feature branches
2. **Integration**: Merge features into `develop`
3. **Testing**: Comprehensive testing on `develop`
4. **Release Branch**: Create `release/v0.6.x` from `develop`
5. **Final Testing**: Test release branch thoroughly
6. **Production**: Merge to `main` and tag release
7. **Deployment**: Deploy to Railway

### 8.5 Tagging Strategy
- **Release Tags**: `v0.6.0`, `v0.6.1.0`, etc.
- **Pre-release Tags**: `v0.6.0-alpha.6`, `v0.6.0-beta.1`, `v0.6.1.0-rc1`
- **Development Tags**: `v0.6.0-alpha.7-dev.1`

---

## 9. Deployment Architecture

### 9.1 Hosting Platform: Railway

#### 9.1.1 Railway Configuration
```json
// railway.json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn src.web_ui.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### 9.1.2 Environment Variables
```bash
# Required Railway environment variables
SMOOTHCOMP_USERNAME=your_username
SMOOTHCOMP_PASSWORD=your_password
ADMIN_PASSWORD=secure_hash
DEVELOPER_PASSWORD=secure_hash
LOG_LEVEL=INFO
WEBHOOK_SECRET=your_secret_key
```

#### 9.1.3 Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    """Railway health check endpoint."""
    try:
        # Check file system access
        file_system_ok = os.access(DATA_DIR, os.W_OK)
        
        # Check memory usage
        memory_ok = psutil.virtual_memory().percent < 90
        
        # Check processing queue
        queue_ok = not is_processing_running()
        
        status = "healthy" if all([file_system_ok, memory_ok, queue_ok]) else "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.6.0",
            "file_system": file_system_ok,
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": queue_ok
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

#### 9.1.4 Railway-Specific Optimizations
```python
# Railway uses ephemeral file system - need to handle this
import os

# Use Railway's persistent storage
DATA_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "./data")

# Ensure directories exist
os.makedirs(f"{DATA_DIR}/raw", exist_ok=True)
os.makedirs(f"{DATA_DIR}/processed", exist_ok=True)
os.makedirs(f"{DATA_DIR}/datastore", exist_ok=True)

# Memory management for Railway limits
def check_memory_usage():
    """Monitor memory usage for Railway limits."""
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        logger.warning(f"High memory usage: {memory.percent}%")
        gc.collect()
```

#### 9.1.5 Railway Advantages
- Simple deployment process
- Excellent Python support
- File system persistence
- Easy scaling and monitoring
- Automatic HTTPS
- Good for data processing applications

#### 9.1.6 Railway Considerations
- **File Persistence**: Use Railway volumes for persistent data storage
- **Resource Limits**: Memory limits (512MB-8GB), CPU constraints
- **Scaling Strategy**: Start with hobby plan, upgrade to pro for production
- **Backup Strategy**: Implement backup for critical data
- **Ephemeral File System**: Handle Railway's file system limitations

#### 9.1.7 Deployment Process
1. Connect GitHub repository to Railway
2. Configure environment variables
3. Set build commands and start commands
4. Deploy automatically on push to main
5. Monitor deployment logs and health

### 9.2 Environment Configuration
**Production Environment**:
- Railway production environment
- Production database and file storage
- SSL certificates automatically managed
- Performance monitoring enabled

**Staging Environment**:
- Railway preview deployments
- Separate staging data
- Testing environment for new features

### 9.3 Local Development
- **Development Server**: `uvicorn src.web_ui.main:app --reload`
- **Environment**: Virtual environment with requirements.txt
- **Data Storage**: Local file system
- **Database**: Local JSON/Parquet files



---

## 10. Data Validation and Error Handling

### 10.1 Input Validation

#### 10.1.1 Athlete Name Validation
```python
def validate_athlete_name(name: str) -> bool:
    """Validate athlete name format."""
    # Allow international characters
    # Minimum 2 characters, maximum 100
    # No excessive whitespace
    pattern = r'^[a-zA-ZÀ-ÿ\s\-\.\']{2,100}$'
    return bool(re.match(pattern, name.strip()))
```

#### 10.1.2 Event Date Validation
- Ensure dates are in ISO format (YYYY-MM-DD)
- Validate date ranges (no future events)
- Handle timezone conversions consistently
- Log date parsing errors for debugging

#### 10.1.3 Division String Validation
- Validate against known division patterns
- Handle international character encoding
- Normalize division strings consistently
- Log unknown division formats for review

#### 10.1.4 Match Data Validation
- Winner/loser consistency checks
- Score validation and range checking
- Cross-reference with registration data
- Validate match time and duration

#### 10.1.5 Data Integrity Checks
- Cross-reference athlete IDs across files
- Validate match data against registration data
- Check for duplicate entries
- Verify chronological consistency

### 10.2 Error Recovery Strategies

#### 10.2.1 File Processing Errors
- **Dummy Athlete System**: Replace corrupted records with placeholder
- **Partial Processing**: Continue with valid records
- **Error Logging**: Detailed error reports with context
- **Data Validation**: Pre-processing validation with detailed error messages

#### 10.2.2 Network Errors
- **Retry Logic**: Automatic retry for failed downloads with exponential backoff
- **Fallback Methods**: Alternative data sources when available
- **Graceful Degradation**: Continue with available data
- **Connection Monitoring**: Track connection health and performance

#### 10.2.3 Data Corruption
- **Validation**: Data integrity checks at multiple stages
- **Backup Restoration**: Restore from previous state
- **Manual Intervention**: Admin tools for data repair
- **File Versioning**: Keep multiple versions of raw files

### 10.3 Comprehensive Logging
```python
# Logging levels and purposes
DEBUG: Detailed debugging information
INFO: General operational messages
WARNING: Potential issues
ERROR: Error conditions
CRITICAL: System failures
```

### 10.3 Error Recovery Strategies

#### 10.3.1 File Processing Errors
- **Dummy Athlete System**: Replace corrupted records with placeholder
- **Partial Processing**: Continue with valid records
- **Error Logging**: Detailed error reports

#### 10.3.2 Network Errors
- **Retry Logic**: Automatic retry for failed downloads
- **Fallback Methods**: Alternative data sources
- **Graceful Degradation**: Continue with available data

#### 10.3.3 Data Corruption
- **Validation**: Data integrity checks
- **Backup Restoration**: Restore from previous state
- **Manual Intervention**: Admin tools for data repair

### 10.4 Monitoring and Alerts
- **System Health**: Regular status checks
- **Error Thresholds**: Alert on repeated failures
- **Performance Monitoring**: Track processing times
- **Data Quality Metrics**: Monitor data completeness and accuracy
- **User Activity Tracking**: Monitor system usage patterns

---

## 11. Performance and Scalability

### 11.1 Large Dataset Handling
- **Pagination**: Implement pagination for leaderboards and athlete lists
- **Streaming**: Stream large datasets for web UI responses
- **Lazy Loading**: Load data on-demand for athlete profiles
- **File I/O Optimization**: Optimize Parquet file reading with column selection

### 11.2 Concurrent Operation Handling
- Implement **operation locking** for conflicting functions
- Use file-based locks for data processing operations
- Prevent simultaneous data downloads/processing
- Queue conflicting operations with clear error messages
- Log all concurrent access attempts

### 11.3 File-Based Data Optimization
- Optimize Parquet file reading with column selection
- Implement efficient JSON file parsing
- Cache frequently accessed data in memory
- Monitor file I/O performance

### 11.2 Caching Strategy
- **Memory Caching**: Cache frequently accessed athlete profiles
- **Redis Integration**: Optional Redis for distributed caching
- **Cache Invalidation**: Smart cache invalidation on data updates
- **Static Asset Caching**: Cache CSS, JS, and image files

### 11.3 Background Processing
- **Async Tasks**: Implement background processing for long-running operations
- **Task Queue**: Queue system for Glicko calculations and data processing
- **Progress Tracking**: Real-time progress updates for background tasks
- **Task Management**: Web UI for monitoring and managing background tasks

### 11.4 File Management
- **File Versioning**: Keep multiple versions of raw files
- **Compression**: Optional compression for old files (when storage becomes an issue)
- **Storage Monitoring**: Track disk usage and implement cleanup strategies
- **Backup Strategy**: Automated backups before major operations

---

## 12. Configuration Management

### 12.1 Configuration File Structure
```python
# config/settings.py
class Settings:
    # File paths
    RAW_DATA_DIR = "data/raw"
    PROCESSED_DATA_DIR = "data/processed"
    DATASTORE_DIR = "data/datastore"
    
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
    
    # Win type weights
    WIN_WEIGHTS = {
        "SUBMISSION": 1.2,
        "POINTS": 1.1,
        "DECISION": 1.0,
        "BYE": 0.0
    }
    
    # Age class definitions
    AGE_CLASSES = ["youth", "adult", "masters"]
    
    # Regional analysis
    ADCC_REGIONS = ["North American Trials", "South American Trials", "European Trials", "Asia & Oceania Trials"]
    
    # Event master list (dynamically updated)
    EVENT_MASTER_LIST = [
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
            "no_gi_event": True
        }
    ]
    
    # Regional mapping (static, manually updated)
    ADCC_REGION_COUNTRY_MAP = {
        "North American Trials": [
            "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada",
            "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "El Salvador",
            "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica", "Mexico",
            "Nicaragua", "Panama", "Saint Kitts and Nevis", "Saint Lucia",
            "Saint Vincent and the Grenadines", "Trinidad and Tobago", "United States"
        ],
        "South American Trials": [
            "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
            "Falkland Islands", "French Guiana", "Guyana", "Paraguay", "Peru",
            "Suriname", "Uruguay", "Venezuela"
        ],
        "European Trials": [
            "Albania", "Andorra", "Austria", "Belarus", "Belgium",
            "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
            "Czech Republic", "Denmark", "Estonia", "Faroe Islands", "Finland",
            "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland",
            "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania",
            "Luxembourg", "Macedonia", "Malta", "Moldova", "Monaco",
            "Montenegro", "Netherlands", "Norway", "Poland", "Portugal",
            "Romania", "Russia", "San Marino", "Serbia", "Slovakia",
            "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey",
            "Ukraine", "United Kingdom", "Vatican City"
        ],
        "Asia & Oceania Trials": [
            "Afghanistan", "Armenia", "Azerbaijan", "Bangladesh", "Bhutan",
            "Brunei", "Cambodia", "China", "Georgia", "Hong Kong", "India",
            "Indonesia", "Japan", "Kazakhstan", "Kyrgyzstan", "Laos", "Macau",
            "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal",
            "North Korea", "Pakistan", "Philippines", "Singapore",
            "South Korea", "Sri Lanka", "Taiwan", "Tajikistan", "Thailand",
            "Timor-Leste", "Turkmenistan", "Uzbekistan", "Vietnam",
            "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia",
            "Nauru", "New Zealand", "Palau", "Papua New Guinea", "Samoa",
            "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu"
        ]
    }
    
    # File acquisition settings
    DOWNLOAD_TIMEOUT = 300
    MAX_RETRIES = 3
    
    # Web UI settings
    ADMIN_USERNAME = "admin"
    DEVELOPER_USERNAME = "developer"
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/system.log"
    DEBUG_FILE = "logs/debug.log"
    
    # Webhook settings
    WEBHOOK_SECRET = "your_webhook_secret_key"
    WEBHOOK_TIMEOUT = 30
    WEBHOOK_MAX_RETRIES = 3
    WEBHOOK_RETRY_DELAY = 60
```

### 12.2 Environment Variables
```bash
# .env file
ADMIN_PASSWORD=secure_hash_here
DEVELOPER_PASSWORD=secure_hash_here
SMOOTHCOMP_API_KEY=optional_api_key
DATABASE_URL=optional_sql_url
```

### 12.3 Runtime Configuration
- **Web UI Configuration**: Modify settings through developer interface
- **Dynamic Updates**: Configuration changes without restart
- **Validation**: All configuration changes validated

---

## 13. User Experience and Security

### 13.1 User Experience Enhancements
- **Progress Indicators**: Real-time progress bars for long-running operations
- **Real-time Notifications**: WebSocket-based notifications for completed operations
- **Favorites System**: Bookmark athletes for Youth Worlds consideration (admin feature)
- **Session Management**: Configurable session timeouts for admin/developer accounts
- **Responsive Design**: Mobile-friendly interface for global access

### 13.2 Security and Access Control
- **Session Timeouts**: Configurable timeouts for admin/developer sessions
- **Audit Logging**: Comprehensive audit trail for all data modifications
- **API Rate Limiting**: Rate limiting for public API access with IP whitelist
- **Input Sanitization**: All user inputs validated and sanitized
- **Access Logging**: Track all login attempts and access patterns

### 13.3 Data Modification Tools
- **Match Editing**: Developer-level tool to search and modify match results
- **Event Management**: Add/delete events from configuration via web UI
- **Manual Event Input**: Option to manually input events even if available on Smoothcomp
- **File Management**: Delete individual files or entire events through web UI

---

## 14. Development Guidelines

### 14.1 Code Standards
- **PEP 8**: Python style guide compliance
- **Type Hints**: All functions with type annotations
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Robust exception handling

### 14.2 Testing Strategy
- **Unit Tests**: Individual module testing
- **Integration Tests**: End-to-end workflow testing
- **Data Validation**: Input/output validation tests
- **Performance Tests**: Processing time benchmarks

### 14.3 Debugging Support
- **Extensive Logging**: Debug information at every step
- **Data Snapshots**: Before/after data samples
- **Error Context**: Detailed error information
- **Recovery Tools**: Built-in debugging utilities

---

## 15. Future Considerations

### 15.1 Advanced Features Roadmap

#### Phase 1: Enhanced Analytics 
- **Predictive Analytics**: Machine learning models for athlete performance prediction
- **Trend Analysis**: Historical performance trends and pattern recognition
- **Advanced Statistics**: Comprehensive statistical analysis (win rates, submission percentages, etc.)
- **Performance Heatmaps**: Visual representation of athlete performance across divisions
- **Head-to-Head Analysis**: Detailed comparison tools for athlete matchups

#### Phase 2: AI & Automation 
- **AI-Powered Insights**: Automated analysis and recommendations
- **Smart Seeding**: AI-enhanced tournament seeding algorithms
- **Predictive Matchmaking**: Advanced match prediction models
- **Automated Reporting**: AI-generated tournament reports and insights
- **Natural Language Queries**: Chatbot interface for data queries

#### Phase 3: Enterprise Features 
- **Multi-Organization Support**: Support for multiple ADCC regions/organizations
- **Advanced User Management**: Role-based access control and permissions
- **API Marketplace**: Public API for third-party integrations
- **Data Export/Import**: Advanced data migration and backup tools
- **Custom Dashboards**: Configurable dashboards for different user types

#### Phase 4: Mobile & Social 
- **Mobile Application**: Native iOS/Android app with push notifications
- **Athlete Profiles**: Enhanced profiles with social media integration
- **Fan Engagement**: Public-facing athlete profiles with achievements and statistics
- **Social Features**: Athlete following, achievements sharing, community features
- **Real-time Updates**: Live tournament updates and notifications

#### Phase 5: Advanced Integrations 
- **Video Analysis**: Integration with match video analysis tools
- **Biometric Data**: Integration with wearable devices and biometric sensors
- **Tournament Management**: Full tournament lifecycle management
- **Financial Tracking**: Prize money tracking and financial analytics
- **International Expansion**: Multi-language support and regional customization

### 15.2 Alternative Data Sources
- **Flo Arena Integration**: Potential integration with Flo Arena for additional ADCC events
- **Template System Enhancement**: Improved template system for non-Smoothcomp events
- **API Standardization**: Standardized API for multiple competition platforms

### 15.3 Smoothcomp API Integration
- **Modular Design**: Easy swap when API becomes available
- **Scheduled Processing**: Automated nightly updates
- **Real-time Updates**: Live data synchronization

### 15.4 Scalability Improvements
- **Database Migration**: SQL database for large datasets
- **Caching**: Redis for performance optimization
- **Microservices**: Service-oriented architecture

### 15.5 Feature Enhancements
- **User Accounts**: Full user management system
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: Native mobile application
- **API Access**: Public API for third-party integrations

---

This architecture document provides a comprehensive foundation for v0.6.0-alpha.6 of the ADCC Competitive Analytics Platform. The modular design ensures maintainability and extensibility while the detailed file structures and data models provide clear implementation guidance. 