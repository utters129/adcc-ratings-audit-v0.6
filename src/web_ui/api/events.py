"""
ADCC Analysis Engine - Events API

This module provides event-related endpoints for the web interface.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
import structlog

from src.web_ui.api.auth import get_current_user, get_current_admin_user
from src.web_ui.models.schemas import (
    EventResponse, EventCreate, Division, PaginatedResponse, PaginationInfo,
    ErrorResponse, SuccessResponse
)

# Configure logging
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()

# Mock events database (replace with actual database in production)
MOCK_EVENTS = {
    "E2024001": {
        "id": "E2024001",
        "name": "ADCC World Championship 2024",
        "location": "Las Vegas, USA",
        "date": "2024-08-15T00:00:00Z",
        "division": Division.UNDER_88KG,
        "total_participants": 32,
        "total_matches": 31,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-08-16T00:00:00Z"
    },
    "E2024002": {
        "id": "E2024002",
        "name": "ADCC European Championship 2024",
        "location": "London, UK",
        "date": "2024-06-20T00:00:00Z",
        "division": Division.WOMEN_ABSOLUTE,
        "total_participants": 16,
        "total_matches": 15,
        "status": "completed",
        "created_at": "2024-02-01T00:00:00Z",
        "updated_at": "2024-06-21T00:00:00Z"
    },
    "E2024003": {
        "id": "E2024003",
        "name": "ADCC Asia-Pacific Championship 2024",
        "location": "Tokyo, Japan",
        "date": "2024-10-15T00:00:00Z",
        "division": Division.ABSOLUTE,
        "total_participants": 64,
        "total_matches": 63,
        "status": "upcoming",
        "created_at": "2024-03-01T00:00:00Z",
        "updated_at": "2024-03-01T00:00:00Z"
    }
}


def get_events_by_filters(
    division: Optional[Division] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[EventResponse]:
    """Get events filtered by criteria."""
    results = []
    
    for event in MOCK_EVENTS.values():
        # Apply filters
        if division and event["division"] != division:
            continue
        if status and event["status"] != status:
            continue
        
        results.append(EventResponse(**event))
    
    # Sort by date (newest first)
    results.sort(key=lambda x: x.date, reverse=True)
    
    # Apply pagination
    start = offset
    end = start + limit
    return results[start:end]


def get_event_by_id(event_id: str) -> Optional[EventResponse]:
    """Get event by ID."""
    event_data = MOCK_EVENTS.get(event_id)
    if event_data:
        return EventResponse(**event_data)
    return None


@router.get("/", response_model=PaginatedResponse)
async def get_events(
    division: Optional[Division] = Query(None, description="Filter by division"),
    status: Optional[str] = Query(None, description="Filter by status (completed, upcoming, ongoing)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get events with filtering and pagination."""
    try:
        logger.info("Get events request", 
                   division=division, status=status, limit=limit, offset=offset)
        
        events = get_events_by_filters(division, status, limit, offset)
        total_count = len(MOCK_EVENTS)  # In real implementation, this would be a count query
        
        pagination = PaginationInfo(
            page=(offset // limit) + 1,
            per_page=limit,
            total=total_count,
            pages=(total_count + limit - 1) // limit,
            has_next=offset + limit < total_count,
            has_prev=offset > 0
        )
        
        logger.info("Events retrieved", count=len(events))
        
        return PaginatedResponse(items=events, pagination=pagination)
        
    except Exception as e:
        logger.error("Error getting events", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """Get event by ID."""
    try:
        logger.info("Get event request", event_id=event_id)
        
        event = get_event_by_id(event_id)
        if not event:
            logger.warning("Event not found", event_id=event_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        logger.info("Event retrieved successfully", event_id=event_id)
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting event", event_id=event_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/", response_model=SuccessResponse)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create a new event (admin only)."""
    try:
        logger.info("Create event request", 
                   name=event_data.name, division=event_data.division,
                   username=current_user.username)
        
        # Generate event ID (in real implementation, this would be more sophisticated)
        import uuid
        event_id = f"E{uuid.uuid4().hex[:6].upper()}"
        
        # Create event record
        new_event = {
            "id": event_id,
            "name": event_data.name,
            "location": event_data.location,
            "date": event_data.date.isoformat(),
            "division": event_data.division,
            "total_participants": 0,
            "total_matches": 0,
            "status": "upcoming",
            "created_at": "2024-01-01T00:00:00Z",  # In real implementation, use actual timestamp
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        MOCK_EVENTS[event_id] = new_event
        
        logger.info("Event created successfully", event_id=event_id)
        
        return SuccessResponse(
            message="Event created successfully",
            data={"event_id": event_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during event creation"
        )


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_data: EventCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update event information (admin only)."""
    try:
        logger.info("Update event request", 
                   event_id=event_id, username=current_user.username)
        
        event = get_event_by_id(event_id)
        if not event:
            logger.warning("Event not found for update", event_id=event_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Update event data
        update_data = event_data.dict()
        for field, value in update_data.items():
            if field == "date":
                setattr(event, field, value.isoformat())
            else:
                setattr(event, field, value)
        
        # Update timestamp
        event.updated_at = "2024-01-01T00:00:00Z"  # In real implementation, use actual timestamp
        
        # Update in mock database
        MOCK_EVENTS[event_id] = event.dict()
        
        logger.info("Event updated successfully", event_id=event_id)
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating event", event_id=event_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during event update"
        )


@router.delete("/{event_id}", response_model=SuccessResponse)
async def delete_event(
    event_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete event (admin only)."""
    try:
        logger.info("Delete event request", 
                   event_id=event_id, username=current_user.username)
        
        if event_id not in MOCK_EVENTS:
            logger.warning("Event not found for deletion", event_id=event_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        del MOCK_EVENTS[event_id]
        
        logger.info("Event deleted successfully", event_id=event_id)
        
        return SuccessResponse(message="Event deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting event", event_id=event_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during event deletion"
        )


@router.get("/divisions/{division}/events", response_model=List[EventResponse])
async def get_events_by_division(division: Division):
    """Get all events in a specific division."""
    try:
        logger.info("Get events by division request", division=division)
        
        events = [
            EventResponse(**event) 
            for event in MOCK_EVENTS.values() 
            if event["division"] == division
        ]
        
        # Sort by date (newest first)
        events.sort(key=lambda x: x.date, reverse=True)
        
        logger.info("Division events retrieved", division=division, count=len(events))
        return events
        
    except Exception as e:
        logger.error("Error getting division events", division=division, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/status/{status}/events", response_model=List[EventResponse])
async def get_events_by_status(status: str):
    """Get all events with a specific status."""
    try:
        logger.info("Get events by status request", status=status)
        
        valid_statuses = ["completed", "upcoming", "ongoing"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        events = [
            EventResponse(**event) 
            for event in MOCK_EVENTS.values() 
            if event["status"] == status
        ]
        
        # Sort by date (newest first)
        events.sort(key=lambda x: x.date, reverse=True)
        
        logger.info("Status events retrieved", status=status, count=len(events))
        return events
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting status events", status=status, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/upcoming/events", response_model=List[EventResponse])
async def get_upcoming_events():
    """Get all upcoming events."""
    try:
        logger.info("Get upcoming events request")
        
        events = [
            EventResponse(**event) 
            for event in MOCK_EVENTS.values() 
            if event["status"] == "upcoming"
        ]
        
        # Sort by date (earliest first)
        events.sort(key=lambda x: x.date)
        
        logger.info("Upcoming events retrieved", count=len(events))
        return events
        
    except Exception as e:
        logger.error("Error getting upcoming events", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/recent/events", response_model=List[EventResponse])
async def get_recent_events(limit: int = Query(10, ge=1, le=50, description="Number of recent events")):
    """Get recent completed events."""
    try:
        logger.info("Get recent events request", limit=limit)
        
        events = [
            EventResponse(**event) 
            for event in MOCK_EVENTS.values() 
            if event["status"] == "completed"
        ]
        
        # Sort by date (newest first)
        events.sort(key=lambda x: x.date, reverse=True)
        
        # Limit results
        events = events[:limit]
        
        logger.info("Recent events retrieved", count=len(events))
        return events
        
    except Exception as e:
        logger.error("Error getting recent events", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 