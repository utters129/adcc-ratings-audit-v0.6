"""
ADCC Analysis Engine - Athletes API

This module provides athlete-related endpoints for the web interface.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
import structlog

from src.web_ui.api.auth import get_current_user, get_current_admin_user
from src.web_ui.models.schemas import (
    AthleteResponse, AthleteCreate, AthleteUpdate, AthleteQuery, Division,
    PaginatedResponse, PaginationInfo, ErrorResponse, SuccessResponse
)

# Configure logging
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()

# Mock athlete database (replace with actual database in production)
MOCK_ATHLETES = {
    "A123456": {
        "id": "A123456",
        "name": "John Doe",
        "club": "BJJ Academy",
        "country": "USA",
        "division": Division.UNDER_88KG,
        "glicko_rating": 1500.0,
        "glicko_deviation": 350.0,
        "total_matches": 10,
        "wins": 7,
        "losses": 2,
        "draws": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z"
    },
    "A789012": {
        "id": "A789012",
        "name": "Jane Smith",
        "club": "Grappling Club",
        "country": "Brazil",
        "division": Division.WOMEN_ABSOLUTE,
        "glicko_rating": 1650.0,
        "glicko_deviation": 250.0,
        "total_matches": 15,
        "wins": 12,
        "losses": 2,
        "draws": 1,
        "created_at": "2024-01-05T00:00:00Z",
        "updated_at": "2024-01-20T00:00:00Z"
    }
}


def search_athletes(query: AthleteQuery) -> List[AthleteResponse]:
    """Search athletes based on query parameters."""
    results = []
    
    for athlete in MOCK_ATHLETES.values():
        # Apply filters
        if query.name and query.name.lower() not in athlete["name"].lower():
            continue
        if query.club and query.club.lower() not in athlete["club"].lower():
            continue
        if query.country and query.country.lower() not in athlete["country"].lower():
            continue
        if query.division and athlete["division"] != query.division:
            continue
        if query.min_rating and athlete["glicko_rating"] < query.min_rating:
            continue
        if query.max_rating and athlete["glicko_rating"] > query.max_rating:
            continue
        
        results.append(AthleteResponse(**athlete))
    
    # Sort by rating (descending)
    results.sort(key=lambda x: x.glicko_rating, reverse=True)
    
    # Apply pagination
    start = query.offset
    end = start + query.limit
    return results[start:end]


def get_athlete_by_id(athlete_id: str) -> Optional[AthleteResponse]:
    """Get athlete by ID."""
    athlete_data = MOCK_ATHLETES.get(athlete_id)
    if athlete_data:
        return AthleteResponse(**athlete_data)
    return None


@router.get("/", response_model=PaginatedResponse)
async def search_athletes_endpoint(
    name: Optional[str] = Query(None, description="Athlete name (partial match)"),
    club: Optional[str] = Query(None, description="Club name"),
    country: Optional[str] = Query(None, description="Country"),
    division: Optional[Division] = Query(None, description="Division filter"),
    min_rating: Optional[float] = Query(None, ge=0, description="Minimum rating"),
    max_rating: Optional[float] = Query(None, ge=0, description="Maximum rating"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Search athletes with filtering and pagination."""
    try:
        logger.info("Athlete search request", 
                   name=name, club=club, country=country, division=division,
                   min_rating=min_rating, max_rating=max_rating, limit=limit, offset=offset)
        
        query = AthleteQuery(
            name=name,
            club=club,
            country=country,
            division=division,
            min_rating=min_rating,
            max_rating=max_rating,
            limit=limit,
            offset=offset
        )
        
        athletes = search_athletes(query)
        total_count = len(MOCK_ATHLETES)  # In real implementation, this would be a count query
        
        pagination = PaginationInfo(
            page=(offset // limit) + 1,
            per_page=limit,
            total=total_count,
            pages=(total_count + limit - 1) // limit,
            has_next=offset + limit < total_count,
            has_prev=offset > 0
        )
        
        logger.info("Athlete search completed", results_count=len(athletes))
        
        return PaginatedResponse(items=athletes, pagination=pagination)
        
    except Exception as e:
        logger.error("Athlete search error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during athlete search"
        )


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete(athlete_id: str):
    """Get athlete by ID."""
    try:
        logger.info("Get athlete request", athlete_id=athlete_id)
        
        athlete = get_athlete_by_id(athlete_id)
        if not athlete:
            logger.warning("Athlete not found", athlete_id=athlete_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Athlete with ID {athlete_id} not found"
            )
        
        logger.info("Athlete retrieved successfully", athlete_id=athlete_id)
        return athlete
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting athlete", athlete_id=athlete_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/", response_model=SuccessResponse)
async def create_athlete(
    athlete_data: AthleteCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create a new athlete (admin only)."""
    try:
        logger.info("Create athlete request", 
                   name=athlete_data.name, division=athlete_data.division,
                   username=current_user.username)
        
        # Generate athlete ID (in real implementation, this would be more sophisticated)
        import uuid
        athlete_id = f"A{uuid.uuid4().hex[:6].upper()}"
        
        # Create athlete record
        new_athlete = {
            "id": athlete_id,
            "name": athlete_data.name,
            "club": athlete_data.club,
            "country": athlete_data.country,
            "division": athlete_data.division,
            "glicko_rating": 1500.0,  # Default starting rating
            "glicko_deviation": 350.0,  # Default starting deviation
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "created_at": "2024-01-01T00:00:00Z",  # In real implementation, use actual timestamp
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        MOCK_ATHLETES[athlete_id] = new_athlete
        
        logger.info("Athlete created successfully", athlete_id=athlete_id)
        
        return SuccessResponse(
            message="Athlete created successfully",
            data={"athlete_id": athlete_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating athlete", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during athlete creation"
        )


@router.put("/{athlete_id}", response_model=AthleteResponse)
async def update_athlete(
    athlete_id: str,
    athlete_data: AthleteUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update athlete information (admin only)."""
    try:
        logger.info("Update athlete request", 
                   athlete_id=athlete_id, username=current_user.username)
        
        athlete = get_athlete_by_id(athlete_id)
        if not athlete:
            logger.warning("Athlete not found for update", athlete_id=athlete_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Athlete with ID {athlete_id} not found"
            )
        
        # Update athlete data
        update_data = athlete_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(athlete, field, value)
        
        # Update timestamp
        athlete.updated_at = "2024-01-01T00:00:00Z"  # In real implementation, use actual timestamp
        
        # Update in mock database
        MOCK_ATHLETES[athlete_id] = athlete.dict()
        
        logger.info("Athlete updated successfully", athlete_id=athlete_id)
        return athlete
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating athlete", athlete_id=athlete_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during athlete update"
        )


@router.delete("/{athlete_id}", response_model=SuccessResponse)
async def delete_athlete(
    athlete_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete athlete (admin only)."""
    try:
        logger.info("Delete athlete request", 
                   athlete_id=athlete_id, username=current_user.username)
        
        if athlete_id not in MOCK_ATHLETES:
            logger.warning("Athlete not found for deletion", athlete_id=athlete_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Athlete with ID {athlete_id} not found"
            )
        
        del MOCK_ATHLETES[athlete_id]
        
        logger.info("Athlete deleted successfully", athlete_id=athlete_id)
        
        return SuccessResponse(message="Athlete deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting athlete", athlete_id=athlete_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during athlete deletion"
        )


@router.get("/divisions/{division}/athletes", response_model=List[AthleteResponse])
async def get_athletes_by_division(division: Division):
    """Get all athletes in a specific division."""
    try:
        logger.info("Get athletes by division request", division=division)
        
        athletes = [
            AthleteResponse(**athlete) 
            for athlete in MOCK_ATHLETES.values() 
            if athlete["division"] == division
        ]
        
        # Sort by rating (descending)
        athletes.sort(key=lambda x: x.glicko_rating, reverse=True)
        
        logger.info("Division athletes retrieved", division=division, count=len(athletes))
        return athletes
        
    except Exception as e:
        logger.error("Error getting division athletes", division=division, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 