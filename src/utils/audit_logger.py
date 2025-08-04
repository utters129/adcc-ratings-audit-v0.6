"""
Audit Logger for ADCC Analysis Engine

This module provides comprehensive audit logging functionality for
tracking data modifications, access patterns, and system activities.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import structlog

from src.config.settings import get_settings
from src.utils.file_handler import save_json_file, load_json_file, ensure_directory_exists

logger = structlog.get_logger(__name__)
settings = get_settings()


@dataclass
class AuditEvent:
    """Represents an audit event."""
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    user_role: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None


class AuditLogger:
    """
    Comprehensive audit logging system.
    
    Tracks data modifications, access patterns, and system activities
    for security and compliance purposes.
    """
    
    def __init__(self, max_events: int = 10000, retention_days: int = 90):
        """
        Initialize the audit logger.
        
        Args:
            max_events: Maximum number of events to keep in memory
            retention_days: Number of days to retain audit logs
        """
        self.settings = get_settings()
        self.max_events = max_events
        self.retention_days = retention_days
        
        # Storage
        self.audit_file = Path(settings.datastore_dir) / "audit_log.json"
        self.audit_events: List[AuditEvent] = []
        
        # Ensure storage directory exists
        ensure_directory_exists(self.audit_file.parent)
        
        # Load existing audit events
        self._load_audit_events()
        
        logger.info("Audit logger initialized", 
                   max_events=max_events,
                   retention_days=retention_days)
    
    def _load_audit_events(self):
        """Load audit events from storage."""
        try:
            if self.audit_file.exists():
                events_data = load_json_file(self.audit_file)
                self.audit_events = []
                for event_data in events_data:
                    # Convert ISO format string back to datetime
                    if isinstance(event_data.get('timestamp'), str):
                        event_data['timestamp'] = datetime.fromisoformat(event_data['timestamp'])
                    self.audit_events.append(AuditEvent(**event_data))
                logger.info("Loaded audit events", count=len(self.audit_events))
            else:
                self.audit_events = []
                self._save_audit_events()
                logger.info("Created new audit log file")
        except Exception as e:
            logger.error("Failed to load audit events", error=str(e))
            self.audit_events = []
    
    def _save_audit_events(self):
        """Save audit events to storage."""
        try:
            # Convert events to dictionaries with datetime serialization
            events_data = []
            for event in self.audit_events:
                event_dict = asdict(event)
                # Convert datetime to ISO format string
                if isinstance(event_dict.get('timestamp'), datetime):
                    event_dict['timestamp'] = event_dict['timestamp'].isoformat()
                events_data.append(event_dict)
            save_json_file(events_data, self.audit_file)
            logger.debug("Saved audit events", count=len(events_data))
        except Exception as e:
            logger.error("Failed to save audit events", error=str(e))
    
    def log_event(
        self,
        event_type: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (e.g., "data_access", "data_modification", "user_action")
            action: Specific action performed
            resource_type: Type of resource affected
            resource_id: ID of the resource
            details: Additional event details
            user_id: User ID performing the action
            user_role: Role of the user
            ip_address: IP address of the user
            user_agent: User agent string
            success: Whether the action was successful
            error_message: Error message if action failed
            session_id: Session ID
            request_id: Request ID
        """
        audit_event = AuditEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            success=success,
            error_message=error_message,
            session_id=session_id,
            request_id=request_id
        )
        
        # Add to events list
        self.audit_events.append(audit_event)
        
        # Keep only the most recent events
        if len(self.audit_events) > self.max_events:
            self.audit_events = self.audit_events[-self.max_events:]
        
        # Save to storage
        self._save_audit_events()
        
        # Log to structured logger
        if success:
            logger.info("Audit event logged",
                      event_type=event_type,
                      action=action,
                      resource_type=resource_type,
                      resource_id=resource_id,
                      user_id=user_id,
                      user_role=user_role,
                      success=success)
        else:
            logger.error("Audit event logged",
                        event_type=event_type,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        user_id=user_id,
                        user_role=user_role,
                        success=success)
    
    def log_data_access(
        self,
        resource_type: str,
        resource_id: str,
        access_type: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log data access event.
        
        Args:
            resource_type: Type of resource accessed
            resource_id: ID of the resource
            access_type: Type of access (read, write, delete, etc.)
            user_id: User ID
            user_role: User role
            ip_address: IP address
            user_agent: User agent
            success: Whether access was successful
            error_message: Error message if access failed
            session_id: Session ID
            request_id: Request ID
        """
        details = {
            "access_type": access_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_event(
            event_type="data_access",
            action=access_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            session_id=session_id,
            request_id=request_id
        )
    
    def log_data_modification(
        self,
        resource_type: str,
        resource_id: str,
        modification_type: str,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log data modification event.
        
        Args:
            resource_type: Type of resource modified
            resource_id: ID of the resource
            modification_type: Type of modification (create, update, delete)
            old_data: Previous data state
            new_data: New data state
            user_id: User ID
            user_role: User role
            ip_address: IP address
            user_agent: User agent
            success: Whether modification was successful
            error_message: Error message if modification failed
            session_id: Session ID
            request_id: Request ID
        """
        details = {
            "modification_type": modification_type,
            "old_data": old_data,
            "new_data": new_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_event(
            event_type="data_modification",
            action=modification_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            session_id=session_id,
            request_id=request_id
        )
    
    def log_user_action(
        self,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log user action event.
        
        Args:
            action: Action performed
            details: Action details
            user_id: User ID
            user_role: User role
            ip_address: IP address
            user_agent: User agent
            success: Whether action was successful
            error_message: Error message if action failed
            session_id: Session ID
            request_id: Request ID
        """
        self.log_event(
            event_type="user_action",
            action=action,
            resource_type="system",
            details=details,
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            session_id=session_id,
            request_id=request_id
        )
    
    def log_system_event(
        self,
        event_type: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Log system event.
        
        Args:
            event_type: Type of system event
            action: Action performed
            details: Event details
            success: Whether event was successful
            error_message: Error message if event failed
        """
        self.log_event(
            event_type=event_type,
            action=action,
            resource_type="system",
            details=details,
            success=success,
            error_message=error_message
        )
    
    def log_authentication(
        self,
        action: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """
        Log authentication event.
        
        Args:
            action: Authentication action (login, logout, failed_login)
            user_id: User ID
            user_role: User role
            ip_address: IP address
            user_agent: User agent
            success: Whether authentication was successful
            error_message: Error message if authentication failed
            session_id: Session ID
        """
        details = {
            "authentication_action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_event(
            event_type="authentication",
            action=action,
            resource_type="user",
            resource_id=user_id,
            details=details,
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            session_id=session_id
        )
    
    def get_audit_events(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success_only: Optional[bool] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Get audit events with filtering.
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_date: Filter by start date
            end_date: Filter by end date
            success_only: Filter by success status
            limit: Maximum number of events to return
            
        Returns:
            List of audit events
        """
        events = self.audit_events
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]
        
        if resource_id:
            events = [e for e in events if e.resource_id == resource_id]
        
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        
        if success_only is not None:
            events = [e for e in events if e.success == success_only]
        
        # Return most recent events up to limit
        return events[-limit:]
    
    def get_audit_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit statistics.
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with audit statistics
        """
        events = self.audit_events
        
        # Apply date filters
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        
        if not events:
            return {
                "total_events": 0,
                "successful_events": 0,
                "failed_events": 0,
                "events_by_type": {},
                "events_by_user": {},
                "events_by_resource": {}
            }
        
        # Calculate statistics
        total_events = len(events)
        successful_events = len([e for e in events if e.success])
        failed_events = total_events - successful_events
        
        # Events by type
        events_by_type = {}
        for event in events:
            event_type = event.event_type
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
        # Events by user
        events_by_user = {}
        for event in events:
            user_id = event.user_id or "anonymous"
            events_by_user[user_id] = events_by_user.get(user_id, 0) + 1
        
        # Events by resource
        events_by_resource = {}
        for event in events:
            resource_type = event.resource_type
            events_by_resource[resource_type] = events_by_resource.get(resource_type, 0) + 1
        
        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": successful_events / total_events if total_events > 0 else 0,
            "events_by_type": events_by_type,
            "events_by_user": events_by_user,
            "events_by_resource": events_by_resource
        }
    
    def cleanup_old_events(self, days_to_keep: Optional[int] = None):
        """
        Clean up old audit events.
        
        Args:
            days_to_keep: Number of days to keep (uses retention_days if not specified)
        """
        if days_to_keep is None:
            days_to_keep = self.retention_days
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        original_count = len(self.audit_events)
        
        self.audit_events = [
            event for event in self.audit_events
            if event.timestamp > cutoff_date
        ]
        
        # Save cleaned events
        self._save_audit_events()
        
        removed_count = original_count - len(self.audit_events)
        logger.info("Cleaned up old audit events", 
                   removed_count=removed_count,
                   days_to_keep=days_to_keep)
    
    def export_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Export audit log.
        
        Args:
            start_date: Start date for export
            end_date: End date for export
            format: Export format ("json" or "csv")
            
        Returns:
            Exported audit log data
        """
        events = self.get_audit_events(
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Large limit for export
        )
        
        if format == "json":
            return [asdict(event) for event in events]
        elif format == "csv":
            # Convert to CSV format
            csv_lines = []
            if events:
                # Header
                headers = list(asdict(events[0]).keys())
                csv_lines.append(",".join(headers))
                
                # Data rows
                for event in events:
                    event_dict = asdict(event)
                    row = [str(event_dict.get(header, "")) for header in headers]
                    csv_lines.append(",".join(row))
            
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}") 