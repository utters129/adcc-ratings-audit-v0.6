"""
ADCC Analysis Engine - Web UI API Schemas

This module defines Pydantic models for API requests and responses used in the web interface.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator
import structlog

logger = structlog.get_logger(__name__)


class UserRole(str, Enum):
    """User roles for authentication and authorization."""
    PUBLIC = "public"
    ADMIN = "admin"
    DEVELOPER = "developer"


class Division(str, Enum):
    """ADCC competition divisions."""
    ABSOLUTE = "absolute"
    UNDER_88KG = "under_88kg"
    UNDER_77KG = "under_77kg"
    UNDER_66KG = "under_66kg"
    WOMEN_ABSOLUTE = "women_absolute"
    WOMEN_UNDER_60KG = "women_under_60kg"


class MatchResult(str, Enum):
    """Possible match results."""
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    SUBMISSION = "submission"
    POINTS = "points"
    ADVANTAGE = "advantage"
    PENALTY = "penalty"


# Authentication Schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=1, description="Password")

    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_role: UserRole = Field(..., description="User role")


class TokenData(BaseModel):
    """Token data schema for JWT payload."""
    username: Optional[str] = None
    role: Optional[UserRole] = None
    exp: Optional[datetime] = None


# Athlete Schemas
class AthleteBase(BaseModel):
    """Base athlete schema."""
    name: str = Field(..., min_length=1, max_length=200, description="Athlete name")
    club: Optional[str] = Field(None, max_length=200, description="Athlete's club")
    country: Optional[str] = Field(None, max_length=100, description="Athlete's country")
    division: Division = Field(..., description="Competition division")


class AthleteCreate(AthleteBase):
    """Schema for creating a new athlete."""
    smoothcomp_id: Optional[int] = Field(None, description="Smoothcomp athlete ID")


class AthleteResponse(AthleteBase):
    """Schema for athlete response."""
    id: str = Field(..., description="Unique athlete ID")
    glicko_rating: float = Field(..., description="Current Glicko rating")
    glicko_deviation: float = Field(..., description="Current Glicko deviation")
    total_matches: int = Field(..., description="Total number of matches")
    wins: int = Field(..., description="Total wins")
    losses: int = Field(..., description="Total losses")
    draws: int = Field(..., description="Total draws")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        schema_extra = {
            "example": {
                "id": "A123456",
                "name": "John Doe",
                "club": "BJJ Academy",
                "country": "USA",
                "division": "under_88kg",
                "glicko_rating": 1500.0,
                "glicko_deviation": 350.0,
                "total_matches": 10,
                "wins": 7,
                "losses": 2,
                "draws": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z"
            }
        }


class AthleteUpdate(BaseModel):
    """Schema for updating athlete information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    club: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    division: Optional[Division] = None


# Event Schemas
class EventBase(BaseModel):
    """Base event schema."""
    name: str = Field(..., min_length=1, max_length=200, description="Event name")
    location: Optional[str] = Field(None, max_length=200, description="Event location")
    date: datetime = Field(..., description="Event date")
    division: Division = Field(..., description="Event division")


class EventCreate(EventBase):
    """Schema for creating a new event."""
    smoothcomp_id: Optional[str] = Field(None, description="Smoothcomp event ID")


class EventResponse(EventBase):
    """Schema for event response."""
    id: str = Field(..., description="Unique event ID")
    total_participants: int = Field(..., description="Total number of participants")
    total_matches: int = Field(..., description="Total number of matches")
    status: str = Field(..., description="Event status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        schema_extra = {
            "example": {
                "id": "E2024001",
                "name": "ADCC World Championship 2024",
                "location": "Las Vegas, USA",
                "date": "2024-08-15T00:00:00Z",
                "division": "under_88kg",
                "total_participants": 32,
                "total_matches": 31,
                "status": "completed",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-08-16T00:00:00Z"
            }
        }


# Match Schemas
class MatchBase(BaseModel):
    """Base match schema."""
    event_id: str = Field(..., description="Event ID")
    athlete1_id: str = Field(..., description="First athlete ID")
    athlete2_id: str = Field(..., description="Second athlete ID")
    result: MatchResult = Field(..., description="Match result")
    winner_id: Optional[str] = Field(None, description="Winner athlete ID")
    method: Optional[str] = Field(None, max_length=100, description="Win method")
    duration: Optional[int] = Field(None, description="Match duration in seconds")


class MatchCreate(MatchBase):
    """Schema for creating a new match."""
    pass


class MatchResponse(MatchBase):
    """Schema for match response."""
    id: str = Field(..., description="Unique match ID")
    round: Optional[str] = Field(None, description="Match round")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        schema_extra = {
            "example": {
                "id": "M2024001001",
                "event_id": "E2024001",
                "athlete1_id": "A123456",
                "athlete2_id": "A789012",
                "result": "submission",
                "winner_id": "A123456",
                "method": "Rear Naked Choke",
                "duration": 180,
                "round": "Quarter Final",
                "created_at": "2024-08-15T10:30:00Z"
            }
        }


# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry."""
    rank: int = Field(..., description="Athlete rank")
    athlete: AthleteResponse = Field(..., description="Athlete information")
    rating_change: Optional[float] = Field(None, description="Rating change from previous period")

    class Config:
        schema_extra = {
            "example": {
                "rank": 1,
                "athlete": {
                    "id": "A123456",
                    "name": "John Doe",
                    "club": "BJJ Academy",
                    "country": "USA",
                    "division": "under_88kg",
                    "glicko_rating": 1850.0,
                    "glicko_deviation": 200.0,
                    "total_matches": 15,
                    "wins": 12,
                    "losses": 2,
                    "draws": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T00:00:00Z"
                },
                "rating_change": 25.5
            }
        }


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""
    division: Division = Field(..., description="Division")
    total_athletes: int = Field(..., description="Total number of athletes")
    last_updated: datetime = Field(..., description="Last update timestamp")
    entries: List[LeaderboardEntry] = Field(..., description="Leaderboard entries")

    class Config:
        schema_extra = {
            "example": {
                "division": "under_88kg",
                "total_athletes": 150,
                "last_updated": "2024-01-15T00:00:00Z",
                "entries": []
            }
        }


# Query Schemas
class AthleteQuery(BaseModel):
    """Schema for athlete search query."""
    name: Optional[str] = Field(None, max_length=200, description="Athlete name (partial match)")
    club: Optional[str] = Field(None, max_length=200, description="Club name")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    division: Optional[Division] = Field(None, description="Division filter")
    min_rating: Optional[float] = Field(None, ge=0, description="Minimum rating")
    max_rating: Optional[float] = Field(None, ge=0, description="Maximum rating")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")

    @validator('min_rating', 'max_rating')
    def validate_rating_range(cls, v, values):
        """Validate rating range."""
        if 'min_rating' in values and 'max_rating' in values:
            if values['min_rating'] and values['max_rating']:
                if values['min_rating'] > values['max_rating']:
                    raise ValueError("min_rating cannot be greater than max_rating")
        return v


# Error Response Schema
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        schema_extra = {
            "example": {
                "error": "Athlete not found",
                "detail": "No athlete found with ID A123456",
                "code": "ATHLETE_NOT_FOUND"
            }
        }


# Pagination Schema
class PaginationInfo(BaseModel):
    """Schema for pagination information."""
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel):
    """Base schema for paginated responses."""
    items: List[Any] = Field(..., description="List of items")
    pagination: PaginationInfo = Field(..., description="Pagination information")


# Success Response Schema
class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

    class Config:
        schema_extra = {
            "example": {
                "message": "Athlete created successfully",
                "data": {"athlete_id": "A123456"}
            }
        } 