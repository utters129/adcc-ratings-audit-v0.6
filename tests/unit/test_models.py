"""
ADCC Analysis Engine v0.6 - Core Models Unit Tests
Tests for Pydantic data models and validation.
"""

import pytest
from datetime import datetime, date
from typing import Dict, Any

from src.core.models import (
    Athlete, Event, Match, Division, Club,
    Gender, SkillLevel, AgeClass, GiStatus
)


class TestEnums:
    """Test enumeration classes."""
    
    def test_gender_enum(self):
        """Test Gender enumeration."""
        assert Gender.MALE == "M"
        assert Gender.FEMALE == "F"
        assert Gender.MALE in Gender
        assert Gender.FEMALE in Gender
    
    def test_skill_level_enum(self):
        """Test SkillLevel enumeration."""
        assert SkillLevel.BEGINNER == "Beginner"
        assert SkillLevel.INTERMEDIATE == "Intermediate"
        assert SkillLevel.ADVANCED == "Advanced"
        assert SkillLevel.EXPERT == "Expert"
    
    def test_age_class_enum(self):
        """Test AgeClass enumeration."""
        assert AgeClass.YOUTH == "youth"
        assert AgeClass.ADULT == "adult"
        assert AgeClass.MASTERS == "masters"
    
    def test_gi_status_enum(self):
        """Test GiStatus enumeration."""
        assert GiStatus.GI == "gi"
        assert GiStatus.NO_GI == "no-gi"


class TestAthleteModel:
    """Test Athlete model."""
    
    def test_valid_athlete_creation(self):
        """Test creating a valid athlete."""
        athlete_data = {
            "id": "A123456",
            "name": "John Doe",
            "age": 25,
            "gender": Gender.MALE,
            "country": "US",
            "skill_level": SkillLevel.ADVANCED,
            "rating": 1500.0,
            "rating_deviation": 350.0,
            "volatility": 0.06
        }
        
        athlete = Athlete(**athlete_data)
        
        assert athlete.id == "A123456"
        assert athlete.name == "John Doe"
        assert athlete.age == 25
        assert athlete.gender == Gender.MALE
        assert athlete.country == "US"
        assert athlete.skill_level == SkillLevel.ADVANCED
        assert athlete.rating == 1500.0
        assert athlete.rating_deviation == 350.0
        assert athlete.volatility == 0.06
        assert isinstance(athlete.created_at, datetime)
        assert isinstance(athlete.updated_at, datetime)
    
    def test_athlete_with_optional_fields(self):
        """Test athlete creation with optional fields."""
        athlete_data = {
            "id": "A789012",
            "name": "Jane Smith",
            "age": 23,
            "gender": Gender.FEMALE,
            "country": "CA",
            "skill_level": SkillLevel.INTERMEDIATE,
            "club_id": "C123"
        }
        
        athlete = Athlete(**athlete_data)
        
        assert athlete.club_id == "C123"
        assert athlete.rating == 1500.0  # Default value
        assert athlete.rating_deviation == 350.0  # Default value
        assert athlete.volatility == 0.06  # Default value
    
    def test_athlete_age_validation(self):
        """Test age validation."""
        # Valid age
        athlete_data = {
            "id": "A123",
            "name": "Test Athlete",
            "age": 25,
            "gender": Gender.MALE,
            "country": "US",
            "skill_level": SkillLevel.BEGINNER
        }
        
        athlete = Athlete(**athlete_data)
        assert athlete.age == 25
        
        # Invalid age (too young)
        with pytest.raises(ValueError):
            Athlete(**{**athlete_data, "age": 3})
        
        # Invalid age (too old)
        with pytest.raises(ValueError):
            Athlete(**{**athlete_data, "age": 150})
    
    def test_athlete_serialization(self):
        """Test athlete model serialization."""
        athlete_data = {
            "id": "A123456",
            "name": "John Doe",
            "age": 25,
            "gender": Gender.MALE,
            "country": "US",
            "skill_level": SkillLevel.ADVANCED
        }
        
        athlete = Athlete(**athlete_data)
        serialized = athlete.dict()
        
        assert serialized["id"] == "A123456"
        assert serialized["name"] == "John Doe"
        assert serialized["age"] == 25
        assert serialized["gender"] == "M"
        assert serialized["skill_level"] == "Advanced"


class TestEventModel:
    """Test Event model."""
    
    def test_valid_event_creation(self):
        """Test creating a valid event."""
        event_date = datetime(2024, 6, 15, 9, 0, 0)
        event_data = {
            "id": "E123456",
            "name": "ADCC World Championship 2024",
            "date": event_date,
            "location": "Las Vegas, NV",
            "divisions": ["Adult_Male_Advanced_Gi", "Adult_Female_Advanced_Gi"]
        }
        
        event = Event(**event_data)
        
        assert event.id == "E123456"
        assert event.name == "ADCC World Championship 2024"
        assert event.date == event_date
        assert event.location == "Las Vegas, NV"
        assert len(event.divisions) == 2
        assert "Adult_Male_Advanced_Gi" in event.divisions
    
    def test_event_without_divisions(self):
        """Test event creation without divisions."""
        event_date = datetime(2024, 6, 15, 9, 0, 0)
        event_data = {
            "id": "E789012",
            "name": "Test Event",
            "date": event_date,
            "location": "Test Location"
        }
        
        event = Event(**event_data)
        
        assert event.divisions == []  # Default empty list
    
    def test_event_serialization(self):
        """Test event model serialization."""
        event_date = datetime(2024, 6, 15, 9, 0, 0)
        event_data = {
            "id": "E123456",
            "name": "Test Event",
            "date": event_date,
            "location": "Test Location"
        }
        
        event = Event(**event_data)
        serialized = event.dict()
        
        assert serialized["id"] == "E123456"
        assert serialized["name"] == "Test Event"
        assert serialized["date"] == event_date.isoformat()
        assert serialized["location"] == "Test Location"


class TestMatchModel:
    """Test Match model."""
    
    def test_valid_match_creation(self):
        """Test creating a valid match."""
        match_date = datetime(2024, 6, 15, 14, 30, 0)
        match_data = {
            "id": "M123456",
            "event_id": "E123456",
            "division_id": "D123456",
            "athlete1_id": "A123456",
            "athlete2_id": "A789012",
            "winner_id": "A123456",
            "win_type": "submission",
            "bracket_round": "final",
            "match_date": match_date
        }
        
        match = Match(**match_data)
        
        assert match.id == "M123456"
        assert match.event_id == "E123456"
        assert match.division_id == "D123456"
        assert match.athlete1_id == "A123456"
        assert match.athlete2_id == "A789012"
        assert match.winner_id == "A123456"
        assert match.win_type == "submission"
        assert match.bracket_round == "final"
        assert match.match_date == match_date
    
    def test_match_without_winner(self):
        """Test match creation without winner (upcoming match)."""
        match_date = datetime(2024, 6, 15, 14, 30, 0)
        match_data = {
            "id": "M789012",
            "event_id": "E123456",
            "division_id": "D123456",
            "athlete1_id": "A123456",
            "athlete2_id": "A789012",
            "match_date": match_date
        }
        
        match = Match(**match_data)
        
        assert match.winner_id is None
        assert match.win_type is None
        assert match.bracket_round is None
    
    def test_match_serialization(self):
        """Test match model serialization."""
        match_date = datetime(2024, 6, 15, 14, 30, 0)
        match_data = {
            "id": "M123456",
            "event_id": "E123456",
            "division_id": "D123456",
            "athlete1_id": "A123456",
            "athlete2_id": "A789012",
            "match_date": match_date
        }
        
        match = Match(**match_data)
        serialized = match.dict()
        
        assert serialized["id"] == "M123456"
        assert serialized["event_id"] == "E123456"
        assert serialized["athlete1_id"] == "A123456"
        assert serialized["athlete2_id"] == "A789012"
        assert serialized["match_date"] == match_date.isoformat()


class TestDivisionModel:
    """Test Division model."""
    
    def test_valid_division_creation(self):
        """Test creating a valid division."""
        division_data = {
            "id": "D123456",
            "name": "Adult Male Advanced Gi",
            "age_class": AgeClass.ADULT,
            "gender": Gender.MALE,
            "skill_level": SkillLevel.ADVANCED,
            "gi_status": GiStatus.GI,
            "event_id": "E123456"
        }
        
        division = Division(**division_data)
        
        assert division.id == "D123456"
        assert division.name == "Adult Male Advanced Gi"
        assert division.age_class == AgeClass.ADULT
        assert division.gender == Gender.MALE
        assert division.skill_level == SkillLevel.ADVANCED
        assert division.gi_status == GiStatus.GI
        assert division.event_id == "E123456"
    
    def test_division_serialization(self):
        """Test division model serialization."""
        division_data = {
            "id": "D123456",
            "name": "Adult Male Advanced Gi",
            "age_class": AgeClass.ADULT,
            "gender": Gender.MALE,
            "skill_level": SkillLevel.ADVANCED,
            "gi_status": GiStatus.GI,
            "event_id": "E123456"
        }
        
        division = Division(**division_data)
        serialized = division.dict()
        
        assert serialized["id"] == "D123456"
        assert serialized["name"] == "Adult Male Advanced Gi"
        assert serialized["age_class"] == "adult"
        assert serialized["gender"] == "M"
        assert serialized["skill_level"] == "Advanced"
        assert serialized["gi_status"] == "gi"


class TestClubModel:
    """Test Club model."""
    
    def test_valid_club_creation(self):
        """Test creating a valid club."""
        club_data = {
            "id": "C123456",
            "name": "Gracie Academy",
            "country": "US",
            "city": "Los Angeles"
        }
        
        club = Club(**club_data)
        
        assert club.id == "C123456"
        assert club.name == "Gracie Academy"
        assert club.country == "US"
        assert club.city == "Los Angeles"
        assert isinstance(club.created_at, datetime)
        assert isinstance(club.updated_at, datetime)
    
    def test_club_without_city(self):
        """Test club creation without city."""
        club_data = {
            "id": "C789012",
            "name": "Test Club",
            "country": "CA"
        }
        
        club = Club(**club_data)
        
        assert club.city is None
    
    def test_club_serialization(self):
        """Test club model serialization."""
        club_data = {
            "id": "C123456",
            "name": "Gracie Academy",
            "country": "US",
            "city": "Los Angeles"
        }
        
        club = Club(**club_data)
        serialized = club.dict()
        
        assert serialized["id"] == "C123456"
        assert serialized["name"] == "Gracie Academy"
        assert serialized["country"] == "US"
        assert serialized["city"] == "Los Angeles"


class TestModelIntegration:
    """Test integration between models."""
    
    def test_athlete_with_club_reference(self):
        """Test athlete with club reference."""
        club = Club(
            id="C123456",
            name="Gracie Academy",
            country="US",
            city="Los Angeles"
        )
        
        athlete = Athlete(
            id="A123456",
            name="John Doe",
            age=25,
            gender=Gender.MALE,
            country="US",
            skill_level=SkillLevel.ADVANCED,
            club_id=club.id
        )
        
        assert athlete.club_id == club.id
    
    def test_match_with_athletes_and_division(self):
        """Test match with athlete and division references."""
        athlete1 = Athlete(
            id="A123456",
            name="John Doe",
            age=25,
            gender=Gender.MALE,
            country="US",
            skill_level=SkillLevel.ADVANCED
        )
        
        athlete2 = Athlete(
            id="A789012",
            name="Jane Smith",
            age=23,
            gender=Gender.FEMALE,
            country="CA",
            skill_level=SkillLevel.INTERMEDIATE
        )
        
        division = Division(
            id="D123456",
            name="Adult Male Advanced Gi",
            age_class=AgeClass.ADULT,
            gender=Gender.MALE,
            skill_level=SkillLevel.ADVANCED,
            gi_status=GiStatus.GI,
            event_id="E123456"
        )
        
        match = Match(
            id="M123456",
            event_id="E123456",
            division_id=division.id,
            athlete1_id=athlete1.id,
            athlete2_id=athlete2.id,
            winner_id=athlete1.id,
            win_type="submission",
            bracket_round="final",
            match_date=datetime(2024, 6, 15, 14, 30, 0)
        )
        
        assert match.athlete1_id == athlete1.id
        assert match.athlete2_id == athlete2.id
        assert match.division_id == division.id
        assert match.winner_id == athlete1.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 