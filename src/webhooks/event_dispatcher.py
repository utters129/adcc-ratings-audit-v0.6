"""
Event Dispatcher for ADCC Analysis Engine

This module provides event dispatching functionality for webhooks,
integrating with the webhook manager and delivery queue.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import structlog

from src.config.settings import get_settings
from .webhook_manager import WebhookManager
from .delivery_queue import DeliveryQueue

logger = structlog.get_logger(__name__)
settings = get_settings()


class EventDispatcher:
    """
    Dispatches events to registered webhooks.
    
    Handles event creation, webhook filtering, and delivery coordination
    between the webhook manager and delivery queue.
    """
    
    def __init__(self, webhook_manager: WebhookManager, delivery_queue: DeliveryQueue):
        """
        Initialize the event dispatcher.
        
        Args:
            webhook_manager: Webhook manager instance
            delivery_queue: Delivery queue instance
        """
        self.webhook_manager = webhook_manager
        self.delivery_queue = delivery_queue
        self.event_history: List[Dict[str, Any]] = []
        
        logger.info("Event dispatcher initialized")
    
    async def dispatch_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        source: str = "system",
        priority: str = "normal"
    ) -> List[str]:
        """
        Dispatch an event to all registered webhooks.
        
        Args:
            event_type: Type of event (e.g., "event.processed", "athlete.rating_updated")
            event_data: Event payload data
            source: Source of the event (e.g., "system", "user", "api")
            priority: Event priority ("low", "normal", "high", "critical")
            
        Returns:
            List of webhook IDs that were queued for delivery
        """
        # Create event payload
        event_payload = self._create_event_payload(
            event_type, event_data, source, priority
        )
        
        # Get webhooks subscribed to this event
        webhooks = self.webhook_manager.get_webhooks_for_event(event_type)
        
        if not webhooks:
            logger.debug("No webhooks registered for event", event_type=event_type)
            return []
        
        # Queue delivery for each webhook
        queued_webhooks = []
        for webhook in webhooks:
            try:
                await self.delivery_queue.queue_webhook(
                    webhook_id=webhook["id"],
                    event_type=event_type,
                    payload=event_payload,
                    url=webhook["url"],
                    secret=webhook["secret"]
                )
                queued_webhooks.append(webhook["id"])
                
                logger.debug("Queued webhook for event",
                           webhook_id=webhook["id"],
                           event_type=event_type)
                
            except Exception as e:
                logger.error("Failed to queue webhook for event",
                           webhook_id=webhook["id"],
                           event_type=event_type,
                           error=str(e))
        
        # Record event in history
        self._record_event(event_type, event_data, source, priority, len(queued_webhooks))
        
        logger.info("Dispatched event to webhooks",
                   event_type=event_type,
                   webhook_count=len(queued_webhooks),
                   source=source,
                   priority=priority)
        
        return queued_webhooks
    
    def _create_event_payload(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        source: str,
        priority: str
    ) -> Dict[str, Any]:
        """
        Create standardized event payload.
        
        Args:
            event_type: Type of event
            event_data: Event data
            source: Event source
            priority: Event priority
            
        Returns:
            Standardized event payload
        """
        return {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "priority": priority,
            "version": "0.6.0",
            "data": event_data
        }
    
    def _record_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        source: str,
        priority: str,
        webhook_count: int
    ):
        """Record event in history."""
        event_record = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "priority": priority,
            "webhook_count": webhook_count,
            "data_summary": self._summarize_event_data(event_data)
        }
        
        self.event_history.append(event_record)
        
        # Keep only last 1000 events
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
    
    def _summarize_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of event data for logging.
        
        Args:
            event_data: Event data to summarize
            
        Returns:
            Summary of event data
        """
        summary = {}
        
        for key, value in event_data.items():
            if isinstance(value, (str, int, float, bool)):
                summary[key] = value
            elif isinstance(value, list):
                summary[key] = f"list[{len(value)}]"
            elif isinstance(value, dict):
                summary[key] = f"dict[{len(value)}]"
            else:
                summary[key] = str(type(value).__name__)
        
        return summary
    
    async def dispatch_event_processed(
        self,
        event_id: str,
        event_name: str,
        processing_time: float,
        athlete_count: int,
        match_count: int
    ) -> List[str]:
        """
        Dispatch event processed notification.
        
        Args:
            event_id: Event ID
            event_name: Event name
            processing_time: Processing time in seconds
            athlete_count: Number of athletes processed
            match_count: Number of matches processed
            
        Returns:
            List of webhook IDs queued for delivery
        """
        event_data = {
            "event_id": event_id,
            "event_name": event_name,
            "processing_time": processing_time,
            "athlete_count": athlete_count,
            "match_count": match_count,
            "status": "completed"
        }
        
        return await self.dispatch_event(
            "event.processed",
            event_data,
            source="data_processing",
            priority="normal"
        )
    
    async def dispatch_event_failed(
        self,
        event_id: str,
        event_name: str,
        error_message: str,
        error_type: str = "processing_error"
    ) -> List[str]:
        """
        Dispatch event failed notification.
        
        Args:
            event_id: Event ID
            event_name: Event name
            error_message: Error message
            error_type: Type of error
            
        Returns:
            List of webhook IDs queued for delivery
        """
        event_data = {
            "event_id": event_id,
            "event_name": event_name,
            "error_message": error_message,
            "error_type": error_type,
            "status": "failed"
        }
        
        return await self.dispatch_event(
            "event.failed",
            event_data,
            source="data_processing",
            priority="high"
        )
    
    async def dispatch_athlete_rating_updated(
        self,
        athlete_id: str,
        athlete_name: str,
        age_class: str,
        old_rating: float,
        new_rating: float,
        rating_change: float,
        match_count: int
    ) -> List[str]:
        """
        Dispatch athlete rating update notification.
        
        Args:
            athlete_id: Athlete ID
            athlete_name: Athlete name
            age_class: Age class
            old_rating: Previous rating
            new_rating: New rating
            rating_change: Rating change
            match_count: Total match count
            
        Returns:
            List of webhook IDs queued for delivery
        """
        event_data = {
            "athlete_id": athlete_id,
            "athlete_name": athlete_name,
            "age_class": age_class,
            "old_rating": old_rating,
            "new_rating": new_rating,
            "rating_change": rating_change,
            "match_count": match_count
        }
        
        return await self.dispatch_event(
            "athlete.rating_updated",
            event_data,
            source="analytics",
            priority="normal"
        )
    
    async def dispatch_medal_awarded(
        self,
        athlete_id: str,
        athlete_name: str,
        event_id: str,
        event_name: str,
        medal_type: str,
        division: str
    ) -> List[str]:
        """
        Dispatch medal awarded notification.
        
        Args:
            athlete_id: Athlete ID
            athlete_name: Athlete name
            event_id: Event ID
            event_name: Event name
            medal_type: Type of medal (gold, silver, bronze)
            division: Division name
            
        Returns:
            List of webhook IDs queued for delivery
        """
        event_data = {
            "athlete_id": athlete_id,
            "athlete_name": athlete_name,
            "event_id": event_id,
            "event_name": event_name,
            "medal_type": medal_type,
            "division": division
        }
        
        return await self.dispatch_event(
            "medal.awarded",
            event_data,
            source="analytics",
            priority="normal"
        )
    
    async def dispatch_report_generated(
        self,
        report_type: str,
        report_name: str,
        file_path: str,
        record_count: int,
        generation_time: float
    ) -> List[str]:
        """
        Dispatch report generated notification.
        
        Args:
            report_type: Type of report
            report_name: Report name
            file_path: Path to generated file
            record_count: Number of records in report
            generation_time: Time taken to generate report
            
        Returns:
            List of webhook IDs queued for delivery
        """
        event_data = {
            "report_type": report_type,
            "report_name": report_name,
            "file_path": file_path,
            "record_count": record_count,
            "generation_time": generation_time
        }
        
        return await self.dispatch_event(
            "report.generated",
            event_data,
            source="reporting",
            priority="low"
        )
    
    async def dispatch_system_error(
        self,
        error_message: str,
        error_type: str,
        component: str,
        severity: str = "error"
    ) -> List[str]:
        """
        Dispatch system error notification.
        
        Args:
            error_message: Error message
            error_type: Type of error
            component: Component where error occurred
            severity: Error severity
            
        Returns:
            List of webhook IDs queued for delivery
        """
        event_data = {
            "error_message": error_message,
            "error_type": error_type,
            "component": component,
            "severity": severity
        }
        
        return await self.dispatch_event(
            "system.error",
            event_data,
            source="system",
            priority="high"
        )
    
    async def dispatch_user_login(
        self,
        username: str,
        user_role: str,
        ip_address: str,
        user_agent: str
    ) -> List[str]:
        """
        Dispatch user login notification.
        
        Args:
            username: Username
            user_role: User role
            ip_address: IP address
            user_agent: User agent string
            
        Returns:
            List of webhook IDs queued for delivery
        """
        event_data = {
            "username": username,
            "user_role": user_role,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "action": "login"
        }
        
        return await self.dispatch_event(
            "user.login",
            event_data,
            source="authentication",
            priority="low"
        )
    
    def get_event_history(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get event history with optional filtering.
        
        Args:
            event_type: Filter by event type
            source: Filter by source
            limit: Maximum number of events to return
            
        Returns:
            List of event records
        """
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        if source:
            events = [e for e in events if e["source"] == source]
        
        return events[-limit:]
    
    def get_event_stats(self) -> Dict[str, Any]:
        """
        Get event dispatch statistics.
        
        Returns:
            Dictionary with event statistics
        """
        if not self.event_history:
            return {
                "total_events": 0,
                "events_by_type": {},
                "events_by_source": {},
                "events_by_priority": {}
            }
        
        # Count events by type
        events_by_type = {}
        events_by_source = {}
        events_by_priority = {}
        
        for event in self.event_history:
            # Count by type
            event_type = event["event_type"]
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            # Count by source
            source = event["source"]
            events_by_source[source] = events_by_source.get(source, 0) + 1
            
            # Count by priority
            priority = event["priority"]
            events_by_priority[priority] = events_by_priority.get(priority, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "events_by_type": events_by_type,
            "events_by_source": events_by_source,
            "events_by_priority": events_by_priority
        } 