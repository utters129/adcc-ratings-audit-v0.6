"""
Phase 9: Advanced Features Tests

This module provides comprehensive tests for the advanced features
implemented in Phase 9, including webhook system, audit system,
and performance optimization.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from src.webhooks import WebhookManager, EventDispatcher, DeliveryQueue, WebhookSecurity
from src.utils.audit_logger import AuditLogger
from src.utils.cache_manager import CacheManager, CacheEntry


class TestWebhookSecurity:
    """Test webhook security functionality."""
    
    def test_generate_secret(self):
        """Test secret generation."""
        security = WebhookSecurity()
        secret = security.generate_secret()
        
        assert isinstance(secret, str)
        assert len(secret) > 20
    
    def test_sign_payload(self):
        """Test payload signing."""
        security = WebhookSecurity()
        payload = '{"test": "data"}'
        secret = "test_secret"
        
        signature = security.sign_payload(payload, secret)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex digest length
    
    def test_verify_signature(self):
        """Test signature verification."""
        security = WebhookSecurity()
        payload = '{"test": "data"}'
        secret = "test_secret"
        
        signature = security.sign_payload(payload, secret)
        
        # Valid signature
        assert security.verify_signature(payload, signature, secret)
        
        # Invalid signature
        assert not security.verify_signature(payload, "invalid_signature", secret)
    
    def test_verify_timestamp(self):
        """Test timestamp verification."""
        security = WebhookSecurity()
        current_time = int(datetime.now().timestamp())
        
        # Valid timestamp
        assert security.verify_timestamp(current_time)
        
        # Expired timestamp
        expired_time = current_time - 400  # 400 seconds ago
        assert not security.verify_timestamp(expired_time, tolerance_seconds=300)
    
    def test_create_webhook_headers(self):
        """Test webhook header creation."""
        security = WebhookSecurity()
        payload = '{"test": "data"}'
        secret = "test_secret"
        event_type = "test.event"
        webhook_id = "test_webhook"
        
        headers = security.create_webhook_headers(payload, secret, event_type, webhook_id)
        
        assert "Content-Type" in headers
        assert "X-Event-Type" in headers
        assert "X-Webhook-ID" in headers
        assert "X-Signature" in headers
        assert headers["X-Event-Type"] == event_type
        assert headers["X-Webhook-ID"] == webhook_id


class TestWebhookManager:
    """Test webhook manager functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def webhook_manager(self, temp_dir, monkeypatch):
        """Create webhook manager for testing."""
        # Mock settings to use temp directory
        mock_settings = Mock()
        mock_settings.DATASTORE_DIR = temp_dir
        monkeypatch.setattr("src.webhooks.webhook_manager.settings", mock_settings)
        
        return WebhookManager()
    
    def test_register_webhook(self, webhook_manager):
        """Test webhook registration."""
        webhook_id = webhook_manager.register_webhook(
            url="https://example.com/webhook",
            events=["event.processed", "athlete.rating_updated"],
            description="Test webhook"
        )
        
        assert isinstance(webhook_id, str)
        assert webhook_id.startswith("webhook_")
        
        # Verify webhook was stored
        webhook = webhook_manager.get_webhook(webhook_id)
        assert webhook is not None
        assert webhook["url"] == "https://example.com/webhook"
        assert "event.processed" in webhook["events"]
        assert webhook["active"] is True
    
    def test_register_webhook_invalid_url(self, webhook_manager):
        """Test webhook registration with invalid URL."""
        with pytest.raises(ValueError, match="Invalid webhook URL"):
            webhook_manager.register_webhook(
                url="invalid_url",
                events=["event.processed"]
            )
    
    def test_register_webhook_invalid_events(self, webhook_manager):
        """Test webhook registration with invalid events."""
        with pytest.raises(ValueError, match="Unsupported events"):
            webhook_manager.register_webhook(
                url="https://example.com/webhook",
                events=["invalid.event"]
            )
    
    def test_unregister_webhook(self, webhook_manager):
        """Test webhook unregistration."""
        webhook_id = webhook_manager.register_webhook(
            url="https://example.com/webhook",
            events=["event.processed"]
        )
        
        # Unregister
        result = webhook_manager.unregister_webhook(webhook_id)
        assert result is True
        
        # Verify webhook was removed
        webhook = webhook_manager.get_webhook(webhook_id)
        assert webhook is None
    
    def test_get_webhooks_for_event(self, webhook_manager):
        """Test getting webhooks for specific event."""
        webhook_id1 = webhook_manager.register_webhook(
            url="https://example1.com/webhook",
            events=["event.processed", "athlete.rating_updated"]
        )
        
        webhook_id2 = webhook_manager.register_webhook(
            url="https://example2.com/webhook",
            events=["event.processed"]
        )
        
        webhook_id3 = webhook_manager.register_webhook(
            url="https://example3.com/webhook",
            events=["athlete.rating_updated"]
        )
        
        # Get webhooks for event.processed
        webhooks = webhook_manager.get_webhooks_for_event("event.processed")
        assert len(webhooks) == 2
        webhook_urls = [w["url"] for w in webhooks]
        assert "https://example1.com/webhook" in webhook_urls
        assert "https://example2.com/webhook" in webhook_urls
    
    def test_update_webhook(self, webhook_manager):
        """Test webhook update."""
        webhook_id = webhook_manager.register_webhook(
            url="https://example.com/webhook",
            events=["event.processed"],
            description="Original description"
        )
        
        # Update webhook
        result = webhook_manager.update_webhook(
            webhook_id,
            description="Updated description",
            active=False
        )
        
        assert result is True
        
        # Verify updates
        webhook = webhook_manager.get_webhook(webhook_id)
        assert webhook["description"] == "Updated description"
        assert webhook["active"] is False
    
    def test_get_supported_events(self, webhook_manager):
        """Test getting supported events."""
        events = webhook_manager.get_supported_events()
        
        assert isinstance(events, set)
        assert "event.processed" in events
        assert "athlete.rating_updated" in events
        assert "medal.awarded" in events
        assert "system.error" in events


class TestDeliveryQueue:
    """Test delivery queue functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def delivery_queue(self, temp_dir, monkeypatch):
        """Create delivery queue for testing."""
        # Mock settings to use temp directory
        mock_settings = Mock()
        mock_settings.DATASTORE_DIR = temp_dir
        monkeypatch.setattr("src.webhooks.delivery_queue.settings", mock_settings)
        
        return DeliveryQueue(max_retries=2, retry_delay=0.1)
    
    @pytest.mark.asyncio
    async def test_queue_webhook(self, delivery_queue):
        """Test queuing webhook for delivery."""
        await delivery_queue.queue_webhook(
            webhook_id="test_webhook",
            event_type="test.event",
            payload={"test": "data"},
            url="https://example.com/webhook",
            secret="test_secret"
        )
        
        assert delivery_queue.delivery_queue.qsize() == 1
    
    @pytest.mark.asyncio
    async def test_delivery_worker(self, delivery_queue):
        """Test delivery worker functionality."""
        # Mock HTTP client to return success
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            
            # Create a proper async context manager mock
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            
            # Set up the context manager behavior
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            mock_client.return_value.__aexit__.return_value = None
            
            # Start delivery worker
            await delivery_queue.start()
            
            # Queue a webhook
            await delivery_queue.queue_webhook(
                webhook_id="test_webhook",
                event_type="test.event",
                payload={"test": "data"},
                url="https://example.com/webhook",
                secret="test_secret"
            )
            
            # Wait for processing
            await asyncio.sleep(0.2)
            
            # Stop delivery worker
            await delivery_queue.stop()
            
            # Check statistics
            stats = delivery_queue.get_delivery_stats()
            assert stats["total_deliveries"] > 0
    
    def test_get_delivery_stats(self, delivery_queue):
        """Test delivery statistics."""
        stats = delivery_queue.get_delivery_stats()
        
        assert "total_deliveries" in stats
        assert "successful_deliveries" in stats
        assert "failed_deliveries" in stats
        assert "success_rate" in stats
        assert "pending_deliveries" in stats


class TestEventDispatcher:
    """Test event dispatcher functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def webhook_manager(self, temp_dir, monkeypatch):
        """Create webhook manager for testing."""
        mock_settings = Mock()
        mock_settings.DATASTORE_DIR = temp_dir
        monkeypatch.setattr("src.webhooks.webhook_manager.settings", mock_settings)
        return WebhookManager()
    
    @pytest.fixture
    def delivery_queue(self, temp_dir, monkeypatch):
        """Create delivery queue for testing."""
        mock_settings = Mock()
        mock_settings.DATASTORE_DIR = temp_dir
        monkeypatch.setattr("src.webhooks.delivery_queue.settings", mock_settings)
        return DeliveryQueue(max_retries=2, retry_delay=0.1)
    
    @pytest.fixture
    def event_dispatcher(self, webhook_manager, delivery_queue):
        """Create event dispatcher for testing."""
        return EventDispatcher(webhook_manager, delivery_queue)
    
    @pytest.mark.asyncio
    async def test_dispatch_event(self, event_dispatcher, webhook_manager):
        """Test event dispatching."""
        # Register a webhook
        webhook_id = webhook_manager.register_webhook(
            url="https://example.com/webhook",
            events=["test.event"]
        )
        
        # Dispatch event
        queued_webhooks = await event_dispatcher.dispatch_event(
            event_type="test.event",
            event_data={"test": "data"},
            source="test",
            priority="normal"
        )
        
        assert len(queued_webhooks) == 1
        assert queued_webhooks[0] == webhook_id
    
    @pytest.mark.asyncio
    async def test_dispatch_event_no_webhooks(self, event_dispatcher):
        """Test event dispatching with no registered webhooks."""
        queued_webhooks = await event_dispatcher.dispatch_event(
            event_type="test.event",
            event_data={"test": "data"}
        )
        
        assert len(queued_webhooks) == 0
    
    @pytest.mark.asyncio
    async def test_dispatch_event_processed(self, event_dispatcher, webhook_manager):
        """Test event processed notification."""
        webhook_id = webhook_manager.register_webhook(
            url="https://example.com/webhook",
            events=["event.processed"]
        )
        
        queued_webhooks = await event_dispatcher.dispatch_event_processed(
            event_id="E12345",
            event_name="Test Event",
            processing_time=10.5,
            athlete_count=100,
            match_count=50
        )
        
        assert len(queued_webhooks) == 1
        assert queued_webhooks[0] == webhook_id
    
    def test_get_event_stats(self, event_dispatcher):
        """Test event statistics."""
        stats = event_dispatcher.get_event_stats()
        
        assert "total_events" in stats
        assert "events_by_type" in stats
        assert "events_by_source" in stats
        assert "events_by_priority" in stats


class TestAuditLogger:
    """Test audit logger functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def audit_logger(self, temp_dir, monkeypatch):
        """Create audit logger for testing."""
        mock_settings = Mock()
        mock_settings.DATASTORE_DIR = temp_dir
        monkeypatch.setattr("src.utils.audit_logger.settings", mock_settings)
        return AuditLogger(max_events=100, retention_days=30)
    
    def test_log_event(self, audit_logger):
        """Test basic event logging."""
        audit_logger.log_event(
            event_type="test_event",
            action="test_action",
            resource_type="test_resource",
            resource_id="test_id",
            user_id="test_user",
            success=True
        )
        
        events = audit_logger.get_audit_events()
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == "test_event"
        assert event.action == "test_action"
        assert event.user_id == "test_user"
        assert event.success is True
    
    def test_log_data_access(self, audit_logger):
        """Test data access logging."""
        audit_logger.log_data_access(
            resource_type="athlete",
            resource_id="A12345",
            access_type="read",
            user_id="test_user",
            user_role="admin"
        )
        
        events = audit_logger.get_audit_events(event_type="data_access")
        assert len(events) == 1
        
        event = events[0]
        assert event.resource_type == "athlete"
        assert event.resource_id == "A12345"
        assert event.action == "read"
    
    def test_log_data_modification(self, audit_logger):
        """Test data modification logging."""
        old_data = {"name": "Old Name"}
        new_data = {"name": "New Name"}
        
        audit_logger.log_data_modification(
            resource_type="athlete",
            resource_id="A12345",
            modification_type="update",
            old_data=old_data,
            new_data=new_data,
            user_id="test_user"
        )
        
        events = audit_logger.get_audit_events(event_type="data_modification")
        assert len(events) == 1
        
        event = events[0]
        assert event.details["modification_type"] == "update"
        assert event.details["old_data"] == old_data
        assert event.details["new_data"] == new_data
    
    def test_log_authentication(self, audit_logger):
        """Test authentication logging."""
        audit_logger.log_authentication(
            action="login",
            user_id="test_user",
            user_role="admin",
            ip_address="192.168.1.1",
            success=True
        )
        
        events = audit_logger.get_audit_events(event_type="authentication")
        assert len(events) == 1
        
        event = events[0]
        assert event.action == "login"
        assert event.user_id == "test_user"
        assert event.ip_address == "192.168.1.1"
    
    def test_get_audit_stats(self, audit_logger):
        """Test audit statistics."""
        # Log some events
        audit_logger.log_event("test1", "action1", "resource1", success=True)
        audit_logger.log_event("test2", "action2", "resource2", success=False)
        
        stats = audit_logger.get_audit_stats()
        
        assert stats["total_events"] == 2
        assert stats["successful_events"] == 1
        assert stats["failed_events"] == 1
        assert stats["success_rate"] == 0.5
    
    def test_filter_audit_events(self, audit_logger):
        """Test audit event filtering."""
        # Log events with different types
        audit_logger.log_event("type1", "action1", "resource1", user_id="user1")
        audit_logger.log_event("type2", "action2", "resource2", user_id="user2")
        audit_logger.log_event("type1", "action3", "resource3", user_id="user1")
        
        # Filter by event type
        type1_events = audit_logger.get_audit_events(event_type="type1")
        assert len(type1_events) == 2
        
        # Filter by user
        user1_events = audit_logger.get_audit_events(user_id="user1")
        assert len(user1_events) == 2


class TestCacheManager:
    """Test cache manager functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache_manager(self, temp_dir, monkeypatch):
        """Create cache manager for testing."""
        mock_settings = Mock()
        mock_settings.DATASTORE_DIR = temp_dir
        monkeypatch.setattr("src.utils.cache_manager.settings", mock_settings)
        return CacheManager(max_size=10, default_ttl=3600)
    
    def test_set_and_get(self, cache_manager):
        """Test setting and getting cache values."""
        cache_manager.set("test_key", "test_value")
        
        value = cache_manager.get("test_key")
        assert value == "test_value"
        
        # Test default value for non-existent key
        value = cache_manager.get("non_existent", "default")
        assert value == "default"
    
    def test_cache_expiration(self, cache_manager):
        """Test cache entry expiration."""
        # Set entry with short TTL
        cache_manager.set("test_key", "test_value", ttl=1)
        
        # Should be available immediately
        assert cache_manager.get("test_key") == "test_value"
        
        # Wait for expiration
        import time
        time.sleep(1.1)
        
        # Should be expired
        assert cache_manager.get("test_key") is None
    
    def test_cache_eviction(self, cache_manager):
        """Test cache eviction when max size is reached."""
        # Fill cache to max size
        for i in range(10):
            cache_manager.set(f"key_{i}", f"value_{i}")
        
        assert len(cache_manager.cache) == 10
        
        # Add one more entry (should trigger eviction)
        cache_manager.set("key_10", "value_10")
        
        # Should still be at max size
        assert len(cache_manager.cache) == 10
    
    def test_get_or_set(self, cache_manager):
        """Test get_or_set functionality."""
        def default_func():
            return "computed_value"
        
        # First call should compute and cache
        value = cache_manager.get_or_set("test_key", default_func)
        assert value == "computed_value"
        
        # Second call should return cached value
        value = cache_manager.get_or_set("test_key", default_func)
        assert value == "computed_value"
    
    def test_cache_function_decorator(self, cache_manager):
        """Test cache function decorator."""
        call_count = 0
        
        @cache_manager.cache_function(ttl=3600, key_prefix="test")
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call with same arguments (should use cache)
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Should not increment
        
        # Third call with different arguments
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2  # Should increment
    
    def test_cache_stats(self, cache_manager):
        """Test cache statistics."""
        # Reset stats by clearing cache
        cache_manager.clear()
        
        # Add some cache entries
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        # Access some entries
        cache_manager.get("key1")  # Hit
        cache_manager.get("key1")  # Hit
        cache_manager.get("key2")  # Hit
        cache_manager.get("key3")  # Miss
        
        stats = cache_manager.get_stats()
        
        assert stats["total_entries"] == 2
        assert stats["hits"] == 3  # key1 (2 hits) + key2 (1 hit)
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 3/4
    
    def test_cache_cleanup(self, cache_manager):
        """Test cache cleanup."""
        # Add expired entry by setting TTL to a negative value
        # This will make it expire immediately
        cache_manager.set("expired_key", "value", ttl=-1)
        
        # Add valid entry
        cache_manager.set("valid_key", "value", ttl=3600)
        
        # Cleanup should remove expired entry
        cache_manager.cleanup()
        
        assert cache_manager.get("expired_key") is None
        assert cache_manager.get("valid_key") == "value"
    
    def test_cache_optimization(self, cache_manager):
        """Test cache optimization."""
        # Fill cache beyond target size
        for i in range(15):
            cache_manager.set(f"key_{i}", f"value_{i}")
        
        # Optimize to target size
        cache_manager.optimize(target_size=5)
        
        assert len(cache_manager.cache) == 5


class TestPhase9Integration:
    """Integration tests for Phase 9 components."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def phase9_components(self, temp_dir, monkeypatch):
        """Create all Phase 9 components for integration testing."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.DATASTORE_DIR = temp_dir
        monkeypatch.setattr("src.webhooks.webhook_manager.settings", mock_settings)
        monkeypatch.setattr("src.webhooks.delivery_queue.settings", mock_settings)
        monkeypatch.setattr("src.utils.audit_logger.settings", mock_settings)
        monkeypatch.setattr("src.utils.cache_manager.settings", mock_settings)
        
        # Create components
        webhook_manager = WebhookManager()
        delivery_queue = DeliveryQueue(max_retries=1, retry_delay=0.1)
        event_dispatcher = EventDispatcher(webhook_manager, delivery_queue)
        audit_logger = AuditLogger(max_events=100, retention_days=30)
        cache_manager = CacheManager(max_size=50, default_ttl=3600)
        
        return {
            "webhook_manager": webhook_manager,
            "delivery_queue": delivery_queue,
            "event_dispatcher": event_dispatcher,
            "audit_logger": audit_logger,
            "cache_manager": cache_manager
        }
    
    @pytest.mark.asyncio
    async def test_webhook_event_audit_integration(self, phase9_components):
        """Test integration between webhook system and audit logging."""
        webhook_manager = phase9_components["webhook_manager"]
        event_dispatcher = phase9_components["event_dispatcher"]
        audit_logger = phase9_components["audit_logger"]
        
        # Register webhook
        webhook_id = webhook_manager.register_webhook(
            url="https://example.com/webhook",
            events=["athlete.rating_updated"]
        )
        
        # Log webhook registration
        audit_logger.log_event(
            event_type="webhook_registration",
            action="register",
            resource_type="webhook",
            resource_id=webhook_id,
            user_id="admin",
            success=True
        )
        
        # Dispatch event
        queued_webhooks = await event_dispatcher.dispatch_athlete_rating_updated(
            athlete_id="A12345",
            athlete_name="Test Athlete",
            age_class="adult",
            old_rating=1500.0,
            new_rating=1550.0,
            rating_change=50.0,
            match_count=10
        )
        
        # Log event dispatch
        audit_logger.log_event(
            event_type="event_dispatch",
            action="dispatch",
            resource_type="webhook",
            resource_id=webhook_id,
            user_id="system",
            success=True,
            details={"queued_webhooks": len(queued_webhooks)}
        )
        
        # Verify audit events
        webhook_events = audit_logger.get_audit_events(event_type="webhook_registration")
        assert len(webhook_events) == 1
        
        dispatch_events = audit_logger.get_audit_events(event_type="event_dispatch")
        assert len(dispatch_events) == 1
    
    def test_cache_audit_integration(self, phase9_components):
        """Test integration between cache manager and audit logging."""
        cache_manager = phase9_components["cache_manager"]
        audit_logger = phase9_components["audit_logger"]
        
        # Cache some data
        cache_manager.set("athlete_ratings", {"A12345": 1500.0})
        
        # Log cache operation
        audit_logger.log_event(
            event_type="cache_operation",
            action="set",
            resource_type="cache",
            resource_id="athlete_ratings",
            user_id="system",
            success=True
        )
        
        # Retrieve cached data
        ratings = cache_manager.get("athlete_ratings")
        
        # Log cache access
        audit_logger.log_event(
            event_type="cache_operation",
            action="get",
            resource_type="cache",
            resource_id="athlete_ratings",
            user_id="system",
            success=True
        )
        
        # Verify cache and audit
        assert ratings == {"A12345": 1500.0}
        
        cache_events = audit_logger.get_audit_events(event_type="cache_operation")
        assert len(cache_events) == 2
    
    def test_performance_optimization(self, phase9_components):
        """Test performance optimization through caching."""
        cache_manager = phase9_components["cache_manager"]
        
        # Simulate expensive computation
        def expensive_calculation(athlete_id):
            import time
            time.sleep(0.01)  # Simulate computation time
            return {"rating": 1500.0, "matches": 10}
        
        # First call (expensive)
        start_time = datetime.now()
        result1 = expensive_calculation("A12345")
        first_call_time = (datetime.now() - start_time).total_seconds()
        
        # Cache the result
        cache_manager.set("athlete_A12345", result1)
        
        # Second call (from cache)
        start_time = datetime.now()
        result2 = cache_manager.get("athlete_A12345")
        second_call_time = (datetime.now() - start_time).total_seconds()
        
        # Verify results and performance improvement
        assert result1 == result2
        assert second_call_time < first_call_time  # Cache should be faster
    
    def test_component_statistics(self, phase9_components):
        """Test statistics from all components."""
        webhook_manager = phase9_components["webhook_manager"]
        delivery_queue = phase9_components["delivery_queue"]
        event_dispatcher = phase9_components["event_dispatcher"]
        audit_logger = phase9_components["audit_logger"]
        cache_manager = phase9_components["cache_manager"]
        
        # Generate some activity
        webhook_id = webhook_manager.register_webhook(
            url="https://example.com/webhook",
            events=["event.processed"]
        )
        
        cache_manager.set("test_key", "test_value")
        cache_manager.get("test_key")
        cache_manager.get("non_existent")
        
        audit_logger.log_event("test", "action", "resource", success=True)
        audit_logger.log_event("test", "action", "resource", success=False)
        
        # Get statistics from all components
        webhook_stats = webhook_manager.get_webhook_stats(webhook_id)
        delivery_stats = delivery_queue.get_delivery_stats()
        event_stats = event_dispatcher.get_event_stats()
        audit_stats = audit_logger.get_audit_stats()
        cache_stats = cache_manager.get_stats()
        
        # Verify statistics are available
        assert webhook_stats is not None
        assert "total_deliveries" in delivery_stats
        assert "total_events" in event_stats
        assert "total_events" in audit_stats
        assert "total_entries" in cache_stats 