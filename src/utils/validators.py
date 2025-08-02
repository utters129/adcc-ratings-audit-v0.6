"""
ADCC Analysis Engine v0.6 - Data Validation Utilities
Comprehensive validation functions for data processing and cleaning.
"""

import re
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import pandas as pd

from src.core.constants import (
    MIN_AGE, MAX_AGE, VALID_GENDERS, VALID_SKILL_LEVELS,
    AGE_CLASSES, ATHLETE_ID_PREFIX, EVENT_ID_PREFIX, 
    DIVISION_ID_PREFIX, MATCH_ID_PREFIX, CLUB_ID_PREFIX,
    GLICKO_STARTING_RATINGS
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def normalize_name(name: str) -> str:
    """
    Normalize athlete names for consistent formatting.
    
    Args:
        name: Raw name string
        
    Returns:
        Normalized name string
    """
    try:
        if not name or not isinstance(name, str):
            return ""
        
        # Remove extra whitespace and convert to title case
        normalized = " ".join(name.strip().split()).title()
        
        # Handle special cases (e.g., "Jr.", "Sr.", "III", etc.)
        suffixes = ["Jr", "Sr", "I", "II", "III", "IV", "V"]
        words = normalized.split()
        
        if len(words) > 1:
            last_word = words[-1].upper()
            if last_word in suffixes:
                # Keep suffix in uppercase
                words[-1] = last_word
                normalized = " ".join(words)
        
        logger.debug(f"Name normalized: '{name}' -> '{normalized}'")
        return normalized
        
    except Exception as e:
        logger.error(f"Failed to normalize name '{name}': {e}")
        return name if isinstance(name, str) else ""


def validate_age(age: Any) -> Optional[int]:
    """
    Validate and convert age to integer.
    
    Args:
        age: Age value (can be string, int, float)
        
    Returns:
        Validated age as integer, or None if invalid
    """
    try:
        if age is None:
            return None
            
        # Convert to int
        age_int = int(float(age))
        
        # Validate range (inclusive)
        if MIN_AGE <= age_int <= MAX_AGE:
            logger.debug(f"Age validated: {age} -> {age_int}")
            return age_int
        else:
            logger.warning(f"Age out of range: {age_int} (valid: {MIN_AGE}-{MAX_AGE})")
            return None
            
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid age value: {age} ({type(age).__name__})")
        return None


def validate_gender(gender: Any) -> Optional[str]:
    """
    Validate gender value.
    
    Args:
        gender: Gender value
        
    Returns:
        Validated gender string, or None if invalid
    """
    try:
        if gender is None:
            return None
            
        gender_str = str(gender).strip().upper()
        
        if gender_str in VALID_GENDERS:
            logger.debug(f"Gender validated: {gender} -> {gender_str}")
            return gender_str
        elif gender_str in ["MALE", "FEMALE"]:
            # Handle full words
            normalized_gender = "M" if gender_str == "MALE" else "F"
            logger.debug(f"Gender validated: {gender} -> {normalized_gender}")
            return normalized_gender
        else:
            logger.warning(f"Invalid gender: {gender_str} (valid: {VALID_GENDERS})")
            return None
            
    except Exception as e:
        logger.error(f"Failed to validate gender '{gender}': {e}")
        return None


def validate_skill_level(skill_level: Any) -> Optional[str]:
    """
    Validate skill level value.
    
    Args:
        skill_level: Skill level value
        
    Returns:
        Validated skill level string, or None if invalid
    """
    try:
        if skill_level is None:
            return None
            
        skill_str = str(skill_level).strip()
        
        # Case-insensitive matching
        for valid_skill in VALID_SKILL_LEVELS:
            if skill_str.lower() == valid_skill.lower():
                logger.debug(f"Skill level validated: {skill_level} -> {valid_skill}")
                return valid_skill
        
        logger.warning(f"Invalid skill level: {skill_str} (valid: {VALID_SKILL_LEVELS})")
        return None
        
    except Exception as e:
        logger.error(f"Failed to validate skill level '{skill_level}': {e}")
        return None


def validate_date(date_value: Any) -> Optional[datetime]:
    """
    Validate and convert date value to datetime.
    
    Args:
        date_value: Date value (string, datetime, date, etc.)
        
    Returns:
        Validated datetime object, or None if invalid
    """
    try:
        if date_value is None:
            return None
            
        # If already a datetime object
        if isinstance(date_value, datetime):
            return date_value
            
        # If it's a date object
        if isinstance(date_value, date):
            return datetime.combine(date_value, datetime.min.time())
            
        # If it's a string, try to parse it
        if isinstance(date_value, str):
            date_str = date_value.strip()
            
            # Try common date formats
            formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    logger.debug(f"Date validated: {date_value} -> {parsed_date}")
                    return parsed_date
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date: {date_value}")
            return None
            
        # If it's a pandas timestamp
        if isinstance(date_value, pd.Timestamp):
            return date_value.to_pydatetime()
            
        logger.warning(f"Unsupported date type: {type(date_value)}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to validate date '{date_value}': {e}")
        return None


def parse_division_string(division_str: str) -> Dict[str, str]:
    """
    Parse division string to extract components.
    
    Args:
        division_str: Division string (e.g., "Adult_Male_Advanced_Gi")
        
    Returns:
        Dictionary with parsed components
    """
    try:
        if not division_str or not isinstance(division_str, str):
            return {}
        
        # Normalize the string
        division = division_str.strip().lower()
        
        # Split by common separators
        parts = re.split(r'[_\-\s]+', division)
        
        result = {}
        
        # Extract age class
        for part in parts:
            if part in AGE_CLASSES:
                result['age_class'] = part
                break
        
        # Extract gender
        for part in parts:
            if part in ['male', 'female', 'm', 'f']:
                result['gender'] = 'M' if part in ['male', 'm'] else 'F'
                break
        
        # Extract skill level
        for part in parts:
            if part in ['beginner', 'intermediate', 'advanced', 'expert']:
                result['skill_level'] = part.title()
                break
        
        # Extract gi status
        for part in parts:
            if part in ['gi', 'no-gi', 'nogi']:
                result['gi_status'] = 'gi' if part == 'gi' else 'no-gi'
                break
        
        logger.debug(f"Division parsed: '{division_str}' -> {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to parse division string '{division_str}': {e}")
        return {}


def generate_athlete_id(name: str, country: str, birth_year: Optional[int] = None) -> str:
    """
    Generate a unique athlete ID.
    
    Args:
        name: Athlete name
        country: Athlete country
        birth_year: Birth year (optional)
        
    Returns:
        Generated athlete ID
    """
    try:
        # Normalize name and country
        normalized_name = normalize_name(name).replace(" ", "").upper()
        normalized_country = country.strip().upper()
        
        # Create base ID
        base_id = f"{normalized_name}_{normalized_country}"
        
        # Add birth year if available
        if birth_year:
            base_id += f"_{birth_year}"
        
        # Add prefix
        athlete_id = f"{ATHLETE_ID_PREFIX}{base_id}"
        
        logger.debug(f"Athlete ID generated: {name} -> {athlete_id}")
        return athlete_id
        
    except Exception as e:
        logger.error(f"Failed to generate athlete ID for '{name}': {e}")
        return f"{ATHLETE_ID_PREFIX}UNKNOWN"


def generate_event_id(name: str, date: datetime) -> str:
    """
    Generate a unique event ID.
    
    Args:
        name: Event name
        date: Event date
        
    Returns:
        Generated event ID
    """
    try:
        # Normalize event name
        normalized_name = re.sub(r'[^a-zA-Z0-9]', '', name).upper()
        
        # Format date
        date_str = date.strftime("%Y%m%d")
        
        # Create event ID
        event_id = f"{EVENT_ID_PREFIX}{normalized_name}_{date_str}"
        
        logger.debug(f"Event ID generated: {name} -> {event_id}")
        return event_id
        
    except Exception as e:
        logger.error(f"Failed to generate event ID for '{name}': {e}")
        return f"{EVENT_ID_PREFIX}UNKNOWN"


def generate_division_id(age_class: str, gender: str, skill_level: str, gi_status: str) -> str:
    """
    Generate a unique division ID.
    
    Args:
        age_class: Age class
        gender: Gender
        skill_level: Skill level
        gi_status: Gi status
        
    Returns:
        Generated division ID
    """
    try:
        # Normalize components
        age_norm = age_class.lower()
        gender_norm = gender.upper()
        skill_norm = skill_level.lower()
        gi_norm = gi_status.lower()
        
        # Create division ID
        division_id = f"{DIVISION_ID_PREFIX}{age_norm}_{gender_norm}_{skill_norm}_{gi_norm}"
        
        logger.debug(f"Division ID generated: {age_class}_{gender}_{skill_level}_{gi_status} -> {division_id}")
        return division_id
        
    except Exception as e:
        logger.error(f"Failed to generate division ID: {e}")
        return f"{DIVISION_ID_PREFIX}UNKNOWN"


def validate_athlete_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validate athlete registration data.
    
    Args:
        data: Raw athlete data dictionary
        
    Returns:
        Tuple of (is_valid, cleaned_data, error_messages)
    """
    errors = []
    cleaned_data = {}
    
    try:
        # Required fields
        required_fields = ['name', 'age', 'gender', 'country', 'skill_level']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
                continue
            
            if field == 'name':
                cleaned_data[field] = normalize_name(data[field])
                if not cleaned_data[field]:
                    errors.append("Invalid name")
                    
            elif field == 'age':
                cleaned_data[field] = validate_age(data[field])
                if cleaned_data[field] is None:
                    errors.append("Invalid age")
                    
            elif field == 'gender':
                cleaned_data[field] = validate_gender(data[field])
                if cleaned_data[field] is None:
                    errors.append("Invalid gender")
                    
            elif field == 'country':
                cleaned_data[field] = str(data[field]).strip()
                if not cleaned_data[field]:
                    errors.append("Invalid country")
                    
            elif field == 'skill_level':
                cleaned_data[field] = validate_skill_level(data[field])
                if cleaned_data[field] is None:
                    errors.append("Invalid skill level")
        
        # Optional fields
        if 'club_id' in data and data['club_id']:
            cleaned_data['club_id'] = str(data['club_id']).strip()
        
        # Generate athlete ID
        cleaned_data['id'] = generate_athlete_id(
            cleaned_data.get('name', ''),
            cleaned_data.get('country', ''),
            cleaned_data.get('birth_year')
        )
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Athlete data validated successfully: {cleaned_data['name']}")
        else:
            logger.warning(f"Athlete data validation failed: {errors}")
        
        return is_valid, cleaned_data, errors
        
    except Exception as e:
        logger.error(f"Failed to validate athlete data: {e}")
        return False, {}, [f"Validation error: {str(e)}"]


def get_starting_rating(skill_level: str) -> float:
    """
    Get starting Glicko rating based on skill level.
    
    Args:
        skill_level: Skill level string
        
    Returns:
        Starting rating value
    """
    try:
        skill_lower = skill_level.lower()
        
        # Map skill levels to starting ratings
        rating_map = {
            'beginner': 800,
            'intermediate': 900,
            'advanced': 1000,
            'expert': 1000,
            'pro': 1000,
            'trials': 1000,
            'world_championship': 1500,
            'world championship': 1500  # Handle space-separated version
        }
        
        starting_rating = rating_map.get(skill_lower, 1000)  # Default to 1000
        
        logger.debug(f"Starting rating for {skill_level}: {starting_rating}")
        return float(starting_rating)
        
    except Exception as e:
        logger.error(f"Failed to get starting rating for {skill_level}: {e}")
        return 1000.0  # Default fallback


def validate_csv_data(df: pd.DataFrame, expected_columns: List[str]) -> Tuple[bool, pd.DataFrame, List[str]]:
    """
    Validate CSV data structure and content.
    
    Args:
        df: Pandas DataFrame
        expected_columns: List of expected column names
        
    Returns:
        Tuple of (is_valid, cleaned_df, error_messages)
    """
    errors = []
    cleaned_df = df.copy()
    
    try:
        # Check for required columns
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing columns: {missing_columns}")
        
        # Remove completely empty rows
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(how='all')
        removed_rows = initial_rows - len(cleaned_df)
        
        # Remove rows where all required columns are empty/null
        if expected_columns:
            # Create a mask for rows where all expected columns are empty
            empty_mask = cleaned_df[expected_columns].isna().all(axis=1) | (cleaned_df[expected_columns] == '').all(axis=1)
            cleaned_df = cleaned_df[~empty_mask]
        
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} empty rows from CSV data")
        
        # Check for minimum data
        if len(cleaned_df) == 0:
            errors.append("No valid data rows found")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"CSV data validated successfully: {len(cleaned_df)} rows")
        else:
            logger.warning(f"CSV data validation failed: {errors}")
        
        return is_valid, cleaned_df, errors
        
    except Exception as e:
        logger.error(f"Failed to validate CSV data: {e}")
        return False, df, [f"Validation error: {str(e)}"] 