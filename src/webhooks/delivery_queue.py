"""
Webhook Delivery Queue for ADCC Analysis Engine

This module provides webhook delivery functionality with retry logic,
queuing, and failure handling.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import structlog

import httpx

from src.config.settings import get_settings
from src.utils.file_handler import save_json_file, load_json_file, ensure_directory_exists
from .security import WebhookSecurity

logger = structlog.get_logger(__name__)
settings = get_settings()


@dataclass
class DeliveryAttempt:
    """Represents a webhook delivery attempt."""
    webhook_id: str
    event_type: str
    payload: str
    url: str
    attempt_number: int
    timestamp: datetime
    status_code: Optional[int] = None
    response_text: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[float] = None


class DeliveryQueue:
    """
    Manages webhook delivery with retry logic and queuing.
    
    Handles asynchronous delivery of webhooks with automatic retries,
    failure tracking, and delivery statistics.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 60.0):
        """
        Initialize the delivery queue.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.settings = get_settings()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.security = WebhookSecurity()
        
        # Queue management
        self.delivery_queue: asyncio.Queue = asyncio.Queue()
        self.failed_deliveries: Dict[str, List[DeliveryAttempt]] = {}
        self.delivery_history: List[DeliveryAttempt] = []
        
        # Statistics
        self.total_deliveries = 0
        self.successful_deliveries = 0
        self.failed_deliveries_count = 0
        
        # Storage
        self.history_file = Path(settings.datastore_dir) / "webhook_delivery_history.json"
        self.failed_file = Path(settings.datastore_dir) / "webhook_failed_deliveries.json"
        
        # Ensure storage directory exists
        ensure_directory_exists(self.history_file.parent)
        
        # Load existing data
        self._load_delivery_data()
        
        # Start delivery worker
        self.delivery_task: Optional[asyncio.Task] = None
        self.running = False
        
        logger.info("Delivery queue initialized", 
                   max_retries=max_retries,
                   retry_delay=retry_delay)
    
    def _load_delivery_data(self):
        """Load delivery history and failed deliveries from storage."""
        try:
            if self.history_file.exists():
                history_data = load_json_file(self.history_file)
                self.delivery_history = []
                for attempt_data in history_data:
                    # Convert ISO format string back to datetime
                    if isinstance(attempt_data.get('timestamp'), str):
                        attempt_data['timestamp'] = datetime.fromisoformat(attempt_data['timestamp'])
                    self.delivery_history.append(DeliveryAttempt(**attempt_data))
                logger.info("Loaded delivery history", count=len(self.delivery_history))
            
            if self.failed_file.exists():
                failed_data = load_json_file(self.failed_file)
                self.failed_deliveries = {}
                for webhook_id, attempts in failed_data.items():
                    self.failed_deliveries[webhook_id] = []
                    for attempt_data in attempts:
                        # Convert ISO format string back to datetime
                        if isinstance(attempt_data.get('timestamp'), str):
                            attempt_data['timestamp'] = datetime.fromisoformat(attempt_data['timestamp'])
                        self.failed_deliveries[webhook_id].append(DeliveryAttempt(**attempt_data))
                logger.info("Loaded failed deliveries", count=len(self.failed_deliveries))
        except Exception as e:
            logger.error("Failed to load delivery data", error=str(e))
    
    def _save_delivery_data(self):
        """Save delivery history and failed deliveries to storage."""
        try:
            # Save delivery history (keep last 1000 entries) with datetime serialization
            history_data = []
            for attempt in self.delivery_history[-1000:]:
                attempt_dict = asdict(attempt)
                # Convert datetime to ISO format string
                if isinstance(attempt_dict.get('timestamp'), datetime):
                    attempt_dict['timestamp'] = attempt_dict['timestamp'].isoformat()
                history_data.append(attempt_dict)
            save_json_file(history_data, self.history_file)
            
            # Save failed deliveries with datetime serialization
            failed_data = {}
            for webhook_id, attempts in self.failed_deliveries.items():
                failed_data[webhook_id] = []
                for attempt in attempts:
                    attempt_dict = asdict(attempt)
                    # Convert datetime to ISO format string
                    if isinstance(attempt_dict.get('timestamp'), datetime):
                        attempt_dict['timestamp'] = attempt_dict['timestamp'].isoformat()
                    failed_data[webhook_id].append(attempt_dict)
            save_json_file(failed_data, self.failed_file)
            
            logger.debug("Saved delivery data", 
                        history_count=len(history_data),
                        failed_count=len(failed_data))
        except Exception as e:
            logger.error("Failed to save delivery data", error=str(e))
    
    async def start(self):
        """Start the delivery queue worker."""
        if self.running:
            logger.warning("Delivery queue already running")
            return
        
        self.running = True
        self.delivery_task = asyncio.create_task(self._delivery_worker())
        logger.info("Delivery queue worker started")
    
    async def stop(self):
        """Stop the delivery queue worker."""
        if not self.running:
            return
        
        self.running = False
        if self.delivery_task:
            self.delivery_task.cancel()
            try:
                await self.delivery_task
            except asyncio.CancelledError:
                pass
        
        # Save data before stopping
        self._save_delivery_data()
        logger.info("Delivery queue worker stopped")
    
    async def queue_webhook(
        self,
        webhook_id: str,
        event_type: str,
        payload: Dict[str, Any],
        url: str,
        secret: str
    ):
        """
        Queue a webhook for delivery.
        
        Args:
            webhook_id: Webhook ID
            event_type: Type of event
            payload: Event payload
            url: Webhook URL
            secret: Webhook secret
        """
        delivery_item = {
            "webhook_id": webhook_id,
            "event_type": event_type,
            "payload": payload,
            "url": url,
            "secret": secret,
            "timestamp": datetime.now()
        }
        
        await self.delivery_queue.put(delivery_item)
        logger.debug("Queued webhook for delivery", 
                    webhook_id=webhook_id,
                    event_type=event_type)
    
    async def _delivery_worker(self):
        """Main delivery worker that processes queued webhooks."""
        while self.running:
            try:
                # Get next delivery item
                delivery_item = await asyncio.wait_for(
                    self.delivery_queue.get(), 
                    timeout=1.0
                )
                
                # Process delivery
                await self._deliver_webhook(delivery_item)
                
                # Mark task as done
                self.delivery_queue.task_done()
                
            except asyncio.TimeoutError:
                # No items in queue, continue
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in delivery worker", error=str(e))
    
    async def _deliver_webhook(self, delivery_item: Dict[str, Any]):
        """
        Deliver a webhook with retry logic.
        
        Args:
            delivery_item: Delivery item from queue
        """
        webhook_id = delivery_item["webhook_id"]
        event_type = delivery_item["event_type"]
        payload = delivery_item["payload"]
        url = delivery_item["url"]
        secret = delivery_item["secret"]
        
        # Convert payload to JSON string
        payload_str = json.dumps(payload, default=str)
        
        # Create headers
        headers = self.security.create_webhook_headers(
            payload_str, secret, event_type, webhook_id
        )
        
        # Attempt delivery with retries
        for attempt in range(self.max_retries + 1):
            attempt_number = attempt + 1
            start_time = time.time()
            
            try:
                # Make HTTP request
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        url,
                        content=payload_str,
                        headers=headers
                    )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Record attempt
                attempt_record = DeliveryAttempt(
                    webhook_id=webhook_id,
                    event_type=event_type,
                    payload=payload_str,
                    url=url,
                    attempt_number=attempt_number,
                    timestamp=datetime.now(),
                    status_code=response.status_code,
                    response_text=response.text,
                    duration_ms=duration_ms
                )
                
                # Check if delivery was successful
                if 200 <= response.status_code < 300:
                    # Success
                    self._record_successful_delivery(attempt_record)
                    logger.info("Webhook delivered successfully",
                               webhook_id=webhook_id,
                               event_type=event_type,
                               status_code=response.status_code,
                               duration_ms=duration_ms)
                    return
                else:
                    # HTTP error
                    attempt_record.error_message = f"HTTP {response.status_code}: {response.text}"
                    self._record_failed_attempt(attempt_record)
                    logger.warning("Webhook delivery failed with HTTP error",
                                  webhook_id=webhook_id,
                                  status_code=response.status_code,
                                  attempt=attempt_number)
                
            except Exception as e:
                # Network or other error
                duration_ms = (time.time() - start_time) * 1000
                attempt_record = DeliveryAttempt(
                    webhook_id=webhook_id,
                    event_type=event_type,
                    payload=payload_str,
                    url=url,
                    attempt_number=attempt_number,
                    timestamp=datetime.now(),
                    error_message=str(e),
                    duration_ms=duration_ms
                )
                
                self._record_failed_attempt(attempt_record)
                logger.warning("Webhook delivery failed with exception",
                              webhook_id=webhook_id,
                              error=str(e),
                              attempt=attempt_number)
            
            # Wait before retry (if not the last attempt)
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay)
        
        # All attempts failed
        logger.error("Webhook delivery failed after all retries",
                    webhook_id=webhook_id,
                    event_type=event_type,
                    max_retries=self.max_retries)
    
    def _record_successful_delivery(self, attempt: DeliveryAttempt):
        """Record a successful delivery attempt."""
        self.delivery_history.append(attempt)
        self.total_deliveries += 1
        self.successful_deliveries += 1
        
        # Remove from failed deliveries if present
        if attempt.webhook_id in self.failed_deliveries:
            self.failed_deliveries[attempt.webhook_id] = [
                a for a in self.failed_deliveries[attempt.webhook_id]
                if a.timestamp != attempt.timestamp
            ]
            if not self.failed_deliveries[attempt.webhook_id]:
                del self.failed_deliveries[attempt.webhook_id]
    
    def _record_failed_attempt(self, attempt: DeliveryAttempt):
        """Record a failed delivery attempt."""
        self.delivery_history.append(attempt)
        self.total_deliveries += 1
        
        # Add to failed deliveries
        if attempt.webhook_id not in self.failed_deliveries:
            self.failed_deliveries[attempt.webhook_id] = []
        self.failed_deliveries[attempt.webhook_id].append(attempt)
        
        # Update failed count if this was the final attempt
        if attempt.attempt_number > self.max_retries:
            self.failed_deliveries_count += 1
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """
        Get delivery statistics.
        
        Returns:
            Dictionary with delivery statistics
        """
        success_rate = (
            self.successful_deliveries / self.total_deliveries 
            if self.total_deliveries > 0 else 0
        )
        
        return {
            "total_deliveries": self.total_deliveries,
            "successful_deliveries": self.successful_deliveries,
            "failed_deliveries": self.failed_deliveries_count,
            "success_rate": success_rate,
            "pending_deliveries": self.delivery_queue.qsize(),
            "failed_webhooks": len(self.failed_deliveries),
            "delivery_history_size": len(self.delivery_history)
        }
    
    def get_failed_deliveries(self, webhook_id: Optional[str] = None) -> List[DeliveryAttempt]:
        """
        Get failed delivery attempts.
        
        Args:
            webhook_id: Optional webhook ID to filter by
            
        Returns:
            List of failed delivery attempts
        """
        if webhook_id:
            return self.failed_deliveries.get(webhook_id, [])
        else:
            all_failed = []
            for attempts in self.failed_deliveries.values():
                all_failed.extend(attempts)
            return all_failed
    
    def retry_failed_deliveries(self, webhook_id: Optional[str] = None):
        """
        Retry failed deliveries.
        
        Args:
            webhook_id: Optional webhook ID to retry specific webhook
        """
        if webhook_id:
            failed_attempts = self.failed_deliveries.get(webhook_id, [])
        else:
            failed_attempts = self.get_failed_deliveries()
        
        for attempt in failed_attempts:
            # Re-queue for delivery
            asyncio.create_task(self.queue_webhook(
                attempt.webhook_id,
                attempt.event_type,
                json.loads(attempt.payload),
                attempt.url,
                ""  # Secret not stored in attempt record
            ))
        
        logger.info("Retrying failed deliveries", 
                   webhook_id=webhook_id,
                   count=len(failed_attempts))
    
    def cleanup_old_history(self, days_to_keep: int = 30):
        """
        Clean up old delivery history.
        
        Args:
            days_to_keep: Number of days of history to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean up delivery history
        original_count = len(self.delivery_history)
        self.delivery_history = [
            attempt for attempt in self.delivery_history
            if attempt.timestamp > cutoff_date
        ]
        
        # Clean up failed deliveries
        for webhook_id in list(self.failed_deliveries.keys()):
            self.failed_deliveries[webhook_id] = [
                attempt for attempt in self.failed_deliveries[webhook_id]
                if attempt.timestamp > cutoff_date
            ]
            if not self.failed_deliveries[webhook_id]:
                del self.failed_deliveries[webhook_id]
        
        # Save cleaned data
        self._save_delivery_data()
        
        removed_count = original_count - len(self.delivery_history)
        logger.info("Cleaned up old delivery history", 
                   removed_count=removed_count,
                   days_to_keep=days_to_keep) 