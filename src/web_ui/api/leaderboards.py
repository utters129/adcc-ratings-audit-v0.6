"""
ADCC Analysis Engine - Leaderboards API

This module provides leaderboard-related endpoints for the web interface.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
import structlog

from src.web_ui.api.auth import get_current_user
from src.web_ui.models.schemas import (
    LeaderboardResponse, LeaderboardEntry, Division, PaginatedResponse, PaginationInfo,
    ErrorResponse
)

# Configure logging
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()

# Mock athlete data for leaderboards (in real implementation, this would come from database)
MOCK_LEADERBOARD_DATA = {
    Division.ABSOLUTE: [
        {
            "id": "A123456",
            "name": "John Doe",
            "club": "BJJ Academy",
            "country": "USA",
            "division": Division.ABSOLUTE,
            "glicko_rating": 1850.0,
            "glicko_deviation": 200.0,
            "total_matches": 25,
            "wins": 20,
            "losses": 4,
            "draws": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z"
        },
        {
            "id": "A789012",
            "name": "Jane Smith",
            "club": "Grappling Club",
            "country": "Brazil",
            "division": Division.ABSOLUTE,
            "glicko_rating": 1820.0,
            "glicko_deviation": 180.0,
            "total_matches": 30,
            "wins": 25,
            "losses": 4,
            "draws": 1,
            "created_at": "2024-01-05T00:00:00Z",
            "updated_at": "2024-01-20T00:00:00Z"
        }
    ],
    Division.UNDER_88KG: [
        {
            "id": "A345678",
            "name": "Mike Johnson",
            "club": "Submission Academy",
            "country": "Canada",
            "division": Division.UNDER_88KG,
            "glicko_rating": 1750.0,
            "glicko_deviation": 220.0,
            "total_matches": 18,
            "wins": 15,
            "losses": 2,
            "draws": 1,
            "created_at": "2024-01-10T00:00:00Z",
            "updated_at": "2024-01-25T00:00:00Z"
        },
        {
            "id": "A901234",
            "name": "Sarah Wilson",
            "club": "Elite BJJ",
            "country": "Australia",
            "division": Division.UNDER_88KG,
            "glicko_rating": 1720.0,
            "glicko_deviation": 190.0,
            "total_matches": 22,
            "wins": 18,
            "losses": 3,
            "draws": 1,
            "created_at": "2024-01-12T00:00:00Z",
            "updated_at": "2024-01-28T00:00:00Z"
        }
    ],
    Division.WOMEN_ABSOLUTE: [
        {
            "id": "A567890",
            "name": "Emma Davis",
            "club": "Women's BJJ",
            "country": "UK",
            "division": Division.WOMEN_ABSOLUTE,
            "glicko_rating": 1680.0,
            "glicko_deviation": 210.0,
            "total_matches": 20,
            "wins": 17,
            "losses": 2,
            "draws": 1,
            "created_at": "2024-01-08T00:00:00Z",
            "updated_at": "2024-01-22T00:00:00Z"
        }
    ]
}


def generate_leaderboard(division: Division, limit: Optional[int] = None) -> List[LeaderboardEntry]:
    """Generate leaderboard for a specific division."""
    athletes_data = MOCK_LEADERBOARD_DATA.get(division, [])
    
    # Sort by rating (descending)
    athletes_data.sort(key=lambda x: x["glicko_rating"], reverse=True)
    
    # Apply limit if specified
    if limit:
        athletes_data = athletes_data[:limit]
    
    # Create leaderboard entries with ranks
    entries = []
    for i, athlete_data in enumerate(athletes_data, 1):
        # Calculate rating change (mock data - in real implementation, this would be calculated)
        rating_change = 0.0
        if i == 1:
            rating_change = 25.5
        elif i == 2:
            rating_change = -15.2
        
        entry = LeaderboardEntry(
            rank=i,
            athlete=athlete_data,  # This will be converted to AthleteResponse
            rating_change=rating_change
        )
        entries.append(entry)
    
    return entries


@router.get("/{division}", response_model=LeaderboardResponse)
async def get_leaderboard(
    division: Division,
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of entries")
):
    """Get leaderboard for a specific division."""
    try:
        logger.info("Get leaderboard request", division=division, limit=limit)
        
        entries = generate_leaderboard(division, limit)
        total_athletes = len(MOCK_LEADERBOARD_DATA.get(division, []))
        
        # In real implementation, this would be the actual last update time
        last_updated = "2024-01-15T00:00:00Z"
        
        logger.info("Leaderboard generated", division=division, entries_count=len(entries))
        
        return LeaderboardResponse(
            division=division,
            total_athletes=total_athletes,
            last_updated=last_updated,
            entries=entries
        )
        
    except Exception as e:
        logger.error("Error generating leaderboard", division=division, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{division}/top", response_model=List[LeaderboardEntry])
async def get_top_athletes(
    division: Division,
    limit: int = Query(10, ge=1, le=50, description="Number of top athletes")
):
    """Get top athletes for a specific division."""
    try:
        logger.info("Get top athletes request", division=division, limit=limit)
        
        entries = generate_leaderboard(division, limit)
        
        logger.info("Top athletes retrieved", division=division, count=len(entries))
        return entries
        
    except Exception as e:
        logger.error("Error getting top athletes", division=division, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{division}/rank/{athlete_id}", response_model=dict)
async def get_athlete_rank(division: Division, athlete_id: str):
    """Get specific athlete's rank in a division."""
    try:
        logger.info("Get athlete rank request", division=division, athlete_id=athlete_id)
        
        entries = generate_leaderboard(division)
        
        # Find athlete in leaderboard
        for entry in entries:
            if entry.athlete["id"] == athlete_id:
                logger.info("Athlete rank found", athlete_id=athlete_id, rank=entry.rank)
                return {
                    "athlete_id": athlete_id,
                    "division": division,
                    "rank": entry.rank,
                    "total_athletes": len(entries),
                    "rating": entry.athlete["glicko_rating"],
                    "rating_change": entry.rating_change
                }
        
        logger.warning("Athlete not found in leaderboard", athlete_id=athlete_id, division=division)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Athlete {athlete_id} not found in {division} leaderboard"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting athlete rank", athlete_id=athlete_id, division=division, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/global/top", response_model=List[LeaderboardEntry])
async def get_global_top_athletes(
    limit: int = Query(20, ge=1, le=100, description="Number of top athletes")
):
    """Get top athletes across all divisions."""
    try:
        logger.info("Get global top athletes request", limit=limit)
        
        # Combine all athletes from all divisions
        all_athletes = []
        for division_athletes in MOCK_LEADERBOARD_DATA.values():
            all_athletes.extend(division_athletes)
        
        # Sort by rating (descending)
        all_athletes.sort(key=lambda x: x["glicko_rating"], reverse=True)
        
        # Take top N athletes
        top_athletes = all_athletes[:limit]
        
        # Create leaderboard entries
        entries = []
        for i, athlete_data in enumerate(top_athletes, 1):
            rating_change = 0.0
            if i <= 3:
                rating_change = [25.5, -15.2, 8.7][i-1] if i <= 3 else 0.0
            
            entry = LeaderboardEntry(
                rank=i,
                athlete=athlete_data,
                rating_change=rating_change
            )
            entries.append(entry)
        
        logger.info("Global top athletes retrieved", count=len(entries))
        return entries
        
    except Exception as e:
        logger.error("Error getting global top athletes", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/divisions/summary", response_model=dict)
async def get_divisions_summary():
    """Get summary of all divisions with top athlete in each."""
    try:
        logger.info("Get divisions summary request")
        
        summary = {}
        for division in Division:
            entries = generate_leaderboard(division, limit=1)
            if entries:
                top_athlete = entries[0]
                summary[division.value] = {
                    "top_athlete": {
                        "id": top_athlete.athlete["id"],
                        "name": top_athlete.athlete["name"],
                        "rating": top_athlete.athlete["glicko_rating"],
                        "country": top_athlete.athlete["country"]
                    },
                    "total_athletes": len(MOCK_LEADERBOARD_DATA.get(division, [])),
                    "last_updated": "2024-01-15T00:00:00Z"
                }
            else:
                summary[division.value] = {
                    "top_athlete": None,
                    "total_athletes": 0,
                    "last_updated": "2024-01-15T00:00:00Z"
                }
        
        logger.info("Divisions summary generated")
        return summary
        
    except Exception as e:
        logger.error("Error getting divisions summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{division}/history", response_model=dict)
async def get_leaderboard_history(
    division: Division,
    days: int = Query(30, ge=1, le=365, description="Number of days of history")
):
    """Get leaderboard history for a division (mock data)."""
    try:
        logger.info("Get leaderboard history request", division=division, days=days)
        
        # Mock historical data
        history = {
            "division": division,
            "period_days": days,
            "data_points": [
                {
                    "date": "2024-01-01T00:00:00Z",
                    "top_athlete": {
                        "id": "A123456",
                        "name": "John Doe",
                        "rating": 1800.0
                    }
                },
                {
                    "date": "2024-01-15T00:00:00Z",
                    "top_athlete": {
                        "id": "A123456",
                        "name": "John Doe",
                        "rating": 1850.0
                    }
                }
            ]
        }
        
        logger.info("Leaderboard history retrieved", division=division)
        return history
        
    except Exception as e:
        logger.error("Error getting leaderboard history", division=division, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{division}/stats", response_model=dict)
async def get_division_stats(division: Division):
    """Get statistics for a division."""
    try:
        logger.info("Get division stats request", division=division)
        
        athletes_data = MOCK_LEADERBOARD_DATA.get(division, [])
        
        if not athletes_data:
            return {
                "division": division,
                "total_athletes": 0,
                "average_rating": 0.0,
                "highest_rating": 0.0,
                "lowest_rating": 0.0,
                "total_matches": 0
            }
        
        ratings = [athlete["glicko_rating"] for athlete in athletes_data]
        total_matches = sum(athlete["total_matches"] for athlete in athletes_data)
        
        stats = {
            "division": division,
            "total_athletes": len(athletes_data),
            "average_rating": sum(ratings) / len(ratings),
            "highest_rating": max(ratings),
            "lowest_rating": min(ratings),
            "total_matches": total_matches,
            "average_matches_per_athlete": total_matches / len(athletes_data) if athletes_data else 0
        }
        
        logger.info("Division stats calculated", division=division)
        return stats
        
    except Exception as e:
        logger.error("Error getting division stats", division=division, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 