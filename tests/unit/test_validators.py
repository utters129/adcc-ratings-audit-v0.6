"""
ADCC Analysis Engine v0.6 - Validators Unit Tests
Tests for data validation utilities.
"""

import pytest
import pandas as pd
from datetime import datetime, date
from typing import Dict, Any

from src.utils.validators import (
    normalize_name, validate_age, validate_gender, validate_skill_level,
    validate_date, parse_division_string, generate_athlete_id,
    generate_event_id, generate_division_id, validate_athlete_data,
    get_starting_rating, validate_csv_data
)


class TestNameNormalization:
    """Test name normalization functions."""
    
    def test_normalize_name_basic(self):
        """Test basic name normalization."""
        assert normalize_name("john doe") == "John Doe"
        assert normalize_name("JANE SMITH") == "Jane Smith"
        assert normalize_name("  bob   johnson  ") == "Bob Johnson"
    
    def test_normalize_name_with_suffixes(self):
        """Test name normalization with suffixes."""
        assert normalize_name("john doe jr") == "John Doe JR"
        assert normalize_name("jane smith sr") == "Jane Smith SR"
        assert normalize_name("robert jones iii") == "Robert Jones III"
        assert normalize_name("william smith iv") == "William Smith IV"
    
    def test_normalize_name_edge_cases(self):
        """Test name normalization edge cases."""
        assert normalize_name("") == ""
        assert normalize_name(None) == ""
        assert normalize_name("   ") == ""
        assert normalize_name("a") == "A"
        assert normalize_name("a b c") == "A B C"
    
    def test_normalize_name_special_characters(self):
        """Test name normalization with special characters."""
        assert normalize_name("john-doe") == "John Doe"
        assert normalize_name("jane_smith") == "Jane Smith"
        assert normalize_name("bob.johnson") == "Bob Johnson"


class TestAgeValidation:
    """Test age validation functions."""
    
    def test_validate_age_valid(self):
        """Test valid age values."""
        assert validate_age(25) == 25
        assert validate_age("25") == 25
        assert validate_age(25.0) == 25
        assert validate_age(5) == 5
        assert validate_age(100) == 100
    
    def test_validate_age_invalid(self):
        """Test invalid age values."""
        assert validate_age(3) is None  # Too young
        assert validate_age(150) is None  # Too old
        assert validate_age(-5) is None  # Negative
        assert validate_age("invalid") is None  # Non-numeric string
        assert validate_age(None) is None  # None value
    
    def test_validate_age_edge_cases(self):
        """Test age validation edge cases."""
        assert validate_age(0) is None  # Zero
        assert validate_age(4.9) == 4  # Float below minimum
        assert validate_age(100.1) is None  # Float above maximum


class TestGenderValidation:
    """Test gender validation functions."""
    
    def test_validate_gender_valid(self):
        """Test valid gender values."""
        assert validate_gender("M") == "M"
        assert validate_gender("F") == "F"
        assert validate_gender("m") == "M"
        assert validate_gender("f") == "F"
        assert validate_gender(" male ") == "M"
        assert validate_gender(" female ") == "F"
    
    def test_validate_gender_invalid(self):
        """Test invalid gender values."""
        assert validate_gender("X") is None
        assert validate_gender("male") is None  # Not in VALID_GENDERS
        assert validate_gender("female") is None  # Not in VALID_GENDERS
        assert validate_gender("") is None
        assert validate_gender(None) is None
        assert validate_gender(123) is None
    
    def test_validate_gender_edge_cases(self):
        """Test gender validation edge cases."""
        assert validate_gender(" M ") == "M"
        assert validate_gender(" F ") == "F"


class TestSkillLevelValidation:
    """Test skill level validation functions."""
    
    def test_validate_skill_level_valid(self):
        """Test valid skill level values."""
        assert validate_skill_level("Beginner") == "Beginner"
        assert validate_skill_level("Intermediate") == "Intermediate"
        assert validate_skill_level("Advanced") == "Advanced"
        assert validate_skill_level("Expert") == "Expert"
        assert validate_skill_level("beginner") == "Beginner"
        assert validate_skill_level("INTERMEDIATE") == "Intermediate"
    
    def test_validate_skill_level_invalid(self):
        """Test invalid skill level values."""
        assert validate_skill_level("Novice") is None
        assert validate_skill_level("Pro") is None
        assert validate_skill_level("") is None
        assert validate_skill_level(None) is None
        assert validate_skill_level(123) is None
    
    def test_validate_skill_level_edge_cases(self):
        """Test skill level validation edge cases."""
        assert validate_skill_level(" beginner ") == "Beginner"
        assert validate_skill_level("BEGINNER") == "Beginner"


class TestDateValidation:
    """Test date validation functions."""
    
    def test_validate_date_datetime(self):
        """Test datetime object validation."""
        test_date = datetime(2024, 6, 15, 14, 30, 0)
        result = validate_date(test_date)
        assert result == test_date
    
    def test_validate_date_date(self):
        """Test date object validation."""
        test_date = date(2024, 6, 15)
        result = validate_date(test_date)
        assert result == datetime(2024, 6, 15, 0, 0, 0)
    
    def test_validate_date_string_formats(self):
        """Test string date format validation."""
        # Valid formats
        assert validate_date("2024-06-15") == datetime(2024, 6, 15, 0, 0, 0)
        assert validate_date("06/15/2024") == datetime(2024, 6, 15, 0, 0, 0)
        assert validate_date("15/06/2024") == datetime(2024, 6, 15, 0, 0, 0)
        assert validate_date("2024-06-15 14:30:00") == datetime(2024, 6, 15, 14, 30, 0)
        assert validate_date("06/15/2024 14:30:00") == datetime(2024, 6, 15, 14, 30, 0)
    
    def test_validate_date_invalid(self):
        """Test invalid date values."""
        assert validate_date("invalid-date") is None
        assert validate_date("2024-13-45") is None  # Invalid month/day
        assert validate_date("") is None
        assert validate_date(None) is None
        assert validate_date(123) is None
    
    def test_validate_date_pandas_timestamp(self):
        """Test pandas timestamp validation."""
        test_timestamp = pd.Timestamp("2024-06-15 14:30:00")
        result = validate_date(test_timestamp)
        assert result == datetime(2024, 6, 15, 14, 30, 0)


class TestDivisionStringParsing:
    """Test division string parsing functions."""
    
    def test_parse_division_string_valid(self):
        """Test valid division string parsing."""
        result = parse_division_string("Adult_Male_Advanced_Gi")
        assert result["age_class"] == "adult"
        assert result["gender"] == "M"
        assert result["skill_level"] == "Advanced"
        assert result["gi_status"] == "gi"
    
    def test_parse_division_string_variations(self):
        """Test division string parsing with variations."""
        # Different separators
        result1 = parse_division_string("Adult-Male-Advanced-Gi")
        assert result1["age_class"] == "adult"
        assert result1["gender"] == "M"
        
        result2 = parse_division_string("Adult Male Advanced Gi")
        assert result2["age_class"] == "adult"
        assert result2["gender"] == "M"
        
        # Different gender formats
        result3 = parse_division_string("Adult_Female_Intermediate_No-Gi")
        assert result3["gender"] == "F"
        assert result3["gi_status"] == "no-gi"
    
    def test_parse_division_string_invalid(self):
        """Test invalid division string parsing."""
        assert parse_division_string("") == {}
        assert parse_division_string(None) == {}
        assert parse_division_string("Invalid_Division") == {}
    
    def test_parse_division_string_partial(self):
        """Test partial division string parsing."""
        result = parse_division_string("Adult_Male")
        assert result["age_class"] == "adult"
        assert result["gender"] == "M"
        assert "skill_level" not in result
        assert "gi_status" not in result


class TestIDGeneration:
    """Test ID generation functions."""
    
    def test_generate_athlete_id(self):
        """Test athlete ID generation."""
        athlete_id = generate_athlete_id("John Doe", "US")
        assert athlete_id.startswith("A")
        assert "JOHNDOE" in athlete_id
        assert "US" in athlete_id
        
        # With birth year
        athlete_id_with_year = generate_athlete_id("Jane Smith", "CA", 1995)
        assert "1995" in athlete_id_with_year
    
    def test_generate_event_id(self):
        """Test event ID generation."""
        event_date = datetime(2024, 6, 15)
        event_id = generate_event_id("ADCC World Championship", event_date)
        assert event_id.startswith("E")
        assert "ADCCWORLDCHAMPIONSHIP" in event_id
        assert "20240615" in event_id
    
    def test_generate_division_id(self):
        """Test division ID generation."""
        division_id = generate_division_id("adult", "M", "Advanced", "gi")
        assert division_id.startswith("D")
        assert "adult" in division_id
        assert "M" in division_id
        assert "advanced" in division_id
        assert "gi" in division_id
    
    def test_id_generation_edge_cases(self):
        """Test ID generation edge cases."""
        # Empty values
        athlete_id = generate_athlete_id("", "")
        assert athlete_id.startswith("A")
        
        # Special characters
        event_id = generate_event_id("Test Event (2024)!", datetime(2024, 1, 1))
        assert "TESTEVENT2024" in event_id


class TestAthleteDataValidation:
    """Test athlete data validation functions."""
    
    def test_validate_athlete_data_valid(self):
        """Test valid athlete data validation."""
        athlete_data = {
            "name": "John Doe",
            "age": 25,
            "gender": "M",
            "country": "US",
            "skill_level": "Advanced"
        }
        
        is_valid, cleaned_data, errors = validate_athlete_data(athlete_data)
        
        assert is_valid
        assert len(errors) == 0
        assert cleaned_data["name"] == "John Doe"
        assert cleaned_data["age"] == 25
        assert cleaned_data["gender"] == "M"
        assert cleaned_data["country"] == "US"
        assert cleaned_data["skill_level"] == "Advanced"
        assert "id" in cleaned_data
    
    def test_validate_athlete_data_invalid(self):
        """Test invalid athlete data validation."""
        athlete_data = {
            "name": "",  # Invalid name
            "age": 150,  # Invalid age
            "gender": "X",  # Invalid gender
            "country": "",  # Invalid country
            "skill_level": "Invalid"  # Invalid skill level
        }
        
        is_valid, cleaned_data, errors = validate_athlete_data(athlete_data)
        
        assert not is_valid
        assert len(errors) > 0
        assert "Invalid name" in errors
        assert "Invalid age" in errors
        assert "Invalid gender" in errors
        assert "Invalid country" in errors
        assert "Invalid skill level" in errors
    
    def test_validate_athlete_data_missing_fields(self):
        """Test athlete data validation with missing fields."""
        athlete_data = {
            "name": "John Doe"
            # Missing required fields
        }
        
        is_valid, cleaned_data, errors = validate_athlete_data(athlete_data)
        
        assert not is_valid
        assert len(errors) > 0
        assert "Missing required field: age" in errors
        assert "Missing required field: gender" in errors
        assert "Missing required field: country" in errors
        assert "Missing required field: skill_level" in errors
    
    def test_validate_athlete_data_with_optional_fields(self):
        """Test athlete data validation with optional fields."""
        athlete_data = {
            "name": "John Doe",
            "age": 25,
            "gender": "M",
            "country": "US",
            "skill_level": "Advanced",
            "club_id": "C123"
        }
        
        is_valid, cleaned_data, errors = validate_athlete_data(athlete_data)
        
        assert is_valid
        assert cleaned_data["club_id"] == "C123"


class TestStartingRating:
    """Test starting rating functions."""
    
    def test_get_starting_rating(self):
        """Test starting rating calculation."""
        assert get_starting_rating("Beginner") == 800.0
        assert get_starting_rating("Intermediate") == 900.0
        assert get_starting_rating("Advanced") == 1000.0
        assert get_starting_rating("Expert") == 1000.0
        assert get_starting_rating("Pro") == 1000.0
        assert get_starting_rating("World Championship") == 1500.0
    
    def test_get_starting_rating_case_insensitive(self):
        """Test starting rating case insensitivity."""
        assert get_starting_rating("beginner") == 800.0
        assert get_starting_rating("BEGINNER") == 800.0
        assert get_starting_rating("Beginner") == 800.0
    
    def test_get_starting_rating_invalid(self):
        """Test starting rating with invalid skill level."""
        assert get_starting_rating("Invalid") == 1000.0  # Default fallback
        assert get_starting_rating("") == 1000.0
        assert get_starting_rating(None) == 1000.0


class TestCSVDataValidation:
    """Test CSV data validation functions."""
    
    def test_validate_csv_data_valid(self):
        """Test valid CSV data validation."""
        df = pd.DataFrame({
            "name": ["John Doe", "Jane Smith"],
            "age": [25, 23],
            "gender": ["M", "F"],
            "country": ["US", "CA"],
            "skill_level": ["Advanced", "Intermediate"]
        })
        
        expected_columns = ["name", "age", "gender", "country", "skill_level"]
        
        is_valid, cleaned_df, errors = validate_csv_data(df, expected_columns)
        
        assert is_valid
        assert len(errors) == 0
        assert len(cleaned_df) == 2
    
    def test_validate_csv_data_missing_columns(self):
        """Test CSV data validation with missing columns."""
        df = pd.DataFrame({
            "name": ["John Doe"],
            "age": [25]
            # Missing required columns
        })
        
        expected_columns = ["name", "age", "gender", "country", "skill_level"]
        
        is_valid, cleaned_df, errors = validate_csv_data(df, expected_columns)
        
        assert not is_valid
        assert len(errors) > 0
        assert "Missing columns" in errors[0]
    
    def test_validate_csv_data_empty_rows(self):
        """Test CSV data validation with empty rows."""
        df = pd.DataFrame({
            "name": ["John Doe", "", None],
            "age": [25, None, None],
            "gender": ["M", "", ""],
            "country": ["US", "", ""],
            "skill_level": ["Advanced", "", ""]
        })
        
        expected_columns = ["name", "age", "gender", "country", "skill_level"]
        
        is_valid, cleaned_df, errors = validate_csv_data(df, expected_columns)
        
        assert is_valid
        assert len(cleaned_df) == 1  # Only one valid row
        assert cleaned_df.iloc[0]["name"] == "John Doe"
    
    def test_validate_csv_data_no_valid_rows(self):
        """Test CSV data validation with no valid rows."""
        df = pd.DataFrame({
            "name": ["", None],
            "age": [None, None],
            "gender": ["", ""],
            "country": ["", ""],
            "skill_level": ["", ""]
        })
        
        expected_columns = ["name", "age", "gender", "country", "skill_level"]
        
        is_valid, cleaned_df, errors = validate_csv_data(df, expected_columns)
        
        assert not is_valid
        assert "No valid data rows found" in errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 