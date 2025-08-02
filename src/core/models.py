"""
ADCC Analysis Engine v0.6 - Core Data Models
Pydantic models for data validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "M"
    FEMALE = "F"


class SkillLevel(str, Enum):
    """Skill level enumeration."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class AgeClass(str, Enum):
    """Age class enumeration."""
    YOUTH = "youth"
    ADULT = "adult"
    MASTERS = "masters"


class GiStatus(str, Enum):
    """Gi status enumeration."""
    GI = "gi"
    NO_GI = "no-gi"


class Athlete(BaseModel):
    """Athlete data model."""
    id: str = Field(..., description="Unique athlete ID")
    name: str = Field(..., description="Athlete full name")
    age: int = Field(..., ge=5, le=100, description="Athlete age")
    gender: Gender = Field(..., description="Athlete gender")
    country: str = Field(..., description="Athlete country")
    club_id: Optional[str] = Field(None, description="Club ID")
    skill_level: SkillLevel = Field(..., description="Skill level")
    rating: float = Field(1500.0, description="Current Glicko rating")
    rating_deviation: float = Field(350.0, description="Rating deviation")
    volatility: float = Field(0.06, description="Rating volatility")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class Event(BaseModel):
    """Event data model."""
    id: str = Field(..., description="Unique event ID")
    name: str = Field(..., description="Event name")
    date: datetime = Field(..., description="Event date")
    location: str = Field(..., description="Event location")
    divisions: List[str] = Field(default_factory=list, description="Event divisions")
    created_at: datetime = Field(default_factory=datetime.now)


class Match(BaseModel):
    """Match data model."""
    id: str = Field(..., description="Unique match ID")
    event_id: str = Field(..., description="Event ID")
    division_id: str = Field(..., description="Division ID")
    athlete1_id: str = Field(..., description="First athlete ID")
    athlete2_id: str = Field(..., description="Second athlete ID")
    winner_id: Optional[str] = Field(None, description="Winner athlete ID")
    win_type: Optional[str] = Field(None, description="Win type (submission, points, etc.)")
    bracket_round: Optional[str] = Field(None, description="Bracket round")
    match_date: datetime = Field(..., description="Match date")
    created_at: datetime = Field(default_factory=datetime.now)


class Division(BaseModel):
    """Division data model."""
    id: str = Field(..., description="Unique division ID")
    name: str = Field(..., description="Division name")
    age_class: AgeClass = Field(..., description="Age class")
    gender: Gender = Field(..., description="Gender")
    skill_level: SkillLevel = Field(..., description="Skill level")
    gi_status: GiStatus = Field(..., description="Gi status")
    event_id: str = Field(..., description="Event ID")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class Club(BaseModel):
    """Club data model."""
    id: str = Field(..., description="Unique club ID")
    name: str = Field(..., description="Club name")
    country: str = Field(..., description="Club country")
    city: Optional[str] = Field(None, description="Club city")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 