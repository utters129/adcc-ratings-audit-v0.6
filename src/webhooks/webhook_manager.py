"""
Webhook Manager for ADCC Analysis Engine

This module provides webhook registration, validation, and management functionality.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import structlog

from src.config.settings import get_settings
from src.utils.file_handler import save_json_file, load_json_file, ensure_directory_exists
from .security import WebhookSecurity

logger = structlog.get_logger(__name__)
settings = get_settings()


class WebhookManager:
    """
    Manages webhook registrations and configurations.
    
    Handles webhook registration, validation, and lifecycle management.
    """
    
    def __init__(self):
        """Initialize the webhook manager."""
        self.settings = get_settings()
        self.webhooks_file = Path(settings.datastore_dir) / "webhooks.json"
        self.registrations: Dict[str, Dict[str, Any]] = {}
        self.security = WebhookSecurity()
        
        # Ensure webhooks directory exists
        ensure_directory_exists(self.webhooks_file.parent)
        
        # Load existing webhooks
        self._load_webhooks()
        
        logger.info("Webhook manager initialized", webhook_count=len(self.registrations))
    
    def _load_webhooks(self):
        """Load webhook registrations from file."""
        try:
            if self.webhooks_file.exists():
                self.registrations = load_json_file(self.webhooks_file)
                logger.info("Loaded webhook registrations", count=len(self.registrations))
            else:
                self.registrations = {}
                self._save_webhooks()
                logger.info("Created new webhooks file")
        except Exception as e:
            logger.error("Failed to load webhooks", error=str(e))
            self.registrations = {}
    
    def _save_webhooks(self):
        """Save webhook registrations to file."""
        try:
            save_json_file(self.registrations, self.webhooks_file)
            logger.debug("Saved webhook registrations", count=len(self.registrations))
        except Exception as e:
            logger.error("Failed to save webhooks", error=str(e))
    
    def register_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
        description: str = "",
        active: bool = True
    ) -> str:
        """
        Register a new webhook.
        
        Args:
            url: Webhook endpoint URL
            events: List of events to subscribe to
            secret: Optional webhook secret for security
            description: Human-readable description
            active: Whether webhook is active
            
        Returns:
            Webhook ID
            
        Raises:
            ValueError: If URL is invalid or events are not supported
        """
        # Validate URL
        if not self._validate_url(url):
            raise ValueError(f"Invalid webhook URL: {url}")
        
        # Validate events
        supported_events = self.get_supported_events()
        invalid_events = [e for e in events if e not in supported_events]
        if invalid_events:
            raise ValueError(f"Unsupported events: {invalid_events}")
        
        # Generate webhook ID
        webhook_id = f"webhook_{int(time.time())}_{len(self.registrations)}"
        
        # Create webhook registration
        webhook_data = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "secret": secret or self.security.generate_secret(),
            "description": description,
            "active": active,
            "created_at": datetime.now().isoformat(),
            "last_delivery": None,
            "delivery_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "retry_count": 0
        }
        
        # Store webhook
        self.registrations[webhook_id] = webhook_data
        self._save_webhooks()
        
        logger.info("Registered webhook", 
                   webhook_id=webhook_id, 
                   url=url, 
                   events=events)
        
        return webhook_id
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Unregister a webhook.
        
        Args:
            webhook_id: ID of webhook to unregister
            
        Returns:
            True if webhook was unregistered, False if not found
        """
        if webhook_id in self.registrations:
            webhook = self.registrations.pop(webhook_id)
            self._save_webhooks()
            
            logger.info("Unregistered webhook", 
                       webhook_id=webhook_id, 
                       url=webhook["url"])
            return True
        
        logger.warning("Webhook not found for unregistration", webhook_id=webhook_id)
        return False
    
    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get webhook registration by ID.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            Webhook registration data or None if not found
        """
        return self.registrations.get(webhook_id)
    
    def get_webhooks_for_event(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get all webhooks subscribed to a specific event.
        
        Args:
            event_type: Event type to filter by
            
        Returns:
            List of webhook registrations
        """
        webhooks = []
        for webhook in self.registrations.values():
            if webhook["active"] and event_type in webhook["events"]:
                webhooks.append(webhook)
        
        return webhooks
    
    def update_webhook(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        description: Optional[str] = None,
        active: Optional[bool] = None
    ) -> bool:
        """
        Update webhook registration.
        
        Args:
            webhook_id: Webhook ID
            url: New URL (optional)
            events: New events list (optional)
            description: New description (optional)
            active: New active status (optional)
            
        Returns:
            True if webhook was updated, False if not found
        """
        if webhook_id not in self.registrations:
            logger.warning("Webhook not found for update", webhook_id=webhook_id)
            return False
        
        webhook = self.registrations[webhook_id]
        
        # Update fields if provided
        if url is not None:
            if not self._validate_url(url):
                raise ValueError(f"Invalid webhook URL: {url}")
            webhook["url"] = url
        
        if events is not None:
            supported_events = self.get_supported_events()
            invalid_events = [e for e in events if e not in supported_events]
            if invalid_events:
                raise ValueError(f"Unsupported events: {invalid_events}")
            webhook["events"] = events
        
        if description is not None:
            webhook["description"] = description
        
        if active is not None:
            webhook["active"] = active
        
        self._save_webhooks()
        
        logger.info("Updated webhook", webhook_id=webhook_id)
        return True
    
    def get_supported_events(self) -> Set[str]:
        """
        Get list of supported event types.
        
        Returns:
            Set of supported event types
        """
        return {
            "event.processed",
            "event.failed",
            "athlete.rating_updated",
            "athlete.record_updated",
            "medal.awarded",
            "report.generated",
            "system.error",
            "system.warning",
            "user.login",
            "user.logout",
            "data.imported",
            "data.exported",
            "test.event"
        }
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate webhook URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            # Basic URL validation
            if not url.startswith(("http://", "https://")):
                return False
            
            # Check for valid domain
            if len(url.split("/")) < 3:
                return False
            
            return True
        except Exception:
            return False
    
    def get_webhook_stats(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get webhook delivery statistics.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            Statistics dictionary or None if webhook not found
        """
        webhook = self.get_webhook(webhook_id)
        if not webhook:
            return None
        
        return {
            "delivery_count": webhook["delivery_count"],
            "success_count": webhook["success_count"],
            "failure_count": webhook["failure_count"],
            "retry_count": webhook["retry_count"],
            "success_rate": (
                webhook["success_count"] / webhook["delivery_count"] 
                if webhook["delivery_count"] > 0 else 0
            ),
            "last_delivery": webhook["last_delivery"]
        }
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """
        Get list of all webhook registrations.
        
        Returns:
            List of webhook registrations
        """
        return list(self.registrations.values())
    
    def cleanup_inactive_webhooks(self, days_inactive: int = 30) -> int:
        """
        Remove webhooks that have been inactive for specified days.
        
        Args:
            days_inactive: Number of days of inactivity before cleanup
            
        Returns:
            Number of webhooks removed
        """
        cutoff_time = datetime.now().timestamp() - (days_inactive * 24 * 60 * 60)
        removed_count = 0
        
        webhook_ids_to_remove = []
        for webhook_id, webhook in self.registrations.items():
            if not webhook["active"]:
                created_time = datetime.fromisoformat(webhook["created_at"]).timestamp()
                if created_time < cutoff_time:
                    webhook_ids_to_remove.append(webhook_id)
        
        for webhook_id in webhook_ids_to_remove:
            self.unregister_webhook(webhook_id)
            removed_count += 1
        
        if removed_count > 0:
            logger.info("Cleaned up inactive webhooks", removed_count=removed_count)
        
        return removed_count 