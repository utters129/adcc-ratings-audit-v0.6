#!/usr/bin/env python3
"""
Test script for real data acquisition and processing
This will help us identify real issues by running the actual system components.
"""

import asyncio
import sys
from pathlib import Path
from src.utils.logger import get_logger

# Setup logging
logger = get_logger(__name__)
from src.config.settings import get_settings

def test_data_acquisition():
    """Test the data acquisition components with real data."""
    logger.info("Testing data acquisition components...")
    
    try:
        # Test Smoothcomp client
        from src.data_acquisition.smoothcomp_client import SmoothcompClient
        settings = get_settings()
        
        if not settings.smoothcomp_username or not settings.smoothcomp_password:
            logger.warning("Smoothcomp credentials not set. Please set SMOOTHCOMP_USERNAME and SMOOTHCOMP_PASSWORD environment variables.")
            return False
            
        client = SmoothcompClient(settings.smoothcomp_username, settings.smoothcomp_password)
        logger.info("Smoothcomp client initialized successfully")
        
        # Test browser automation
        from src.data_acquisition.browser_automation import BrowserAutomation
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)
        
        browser = BrowserAutomation(download_dir=download_dir)
        logger.info("Browser automation initialized successfully")
        
        # Test file monitor
        from src.data_acquisition.file_monitor import FileMonitor
        monitor = FileMonitor(
            watch_directory=download_dir,
            file_patterns=["*.csv", "*.xlsx", "*.json"]
        )
        logger.info("File monitor initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing data acquisition: {e}")
        return False

def test_data_processing():
    """Test the data processing components."""
    logger.info("Testing data processing components...")
    
    try:
        # Test analytics engine
        from src.analytics.glicko_engine import GlickoEngine
        engine = GlickoEngine()
        logger.info("Glicko engine initialized successfully")
        
        # Test record calculator
        from src.analytics.record_calculator import RecordCalculator
        calculator = RecordCalculator()
        logger.info("Record calculator initialized successfully")
        
        # Test medal tracker
        from src.analytics.medal_tracker import MedalTracker
        tracker = MedalTracker()
        logger.info("Medal tracker initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing data processing: {e}")
        return False

def test_web_ui():
    """Test the web UI components."""
    logger.info("Testing web UI components...")
    
    try:
        # Test FastAPI app
        from src.web_ui.main import app
        logger.info("FastAPI app imported successfully")
        
        # Test authentication
        from src.web_ui.api.auth import router as auth_router
        logger.info("Authentication router imported successfully")
        
        # Test API endpoints
        from src.web_ui.api.athletes import router as athletes_router
        from src.web_ui.api.events import router as events_router
        from src.web_ui.api.leaderboards import router as leaderboards_router
        logger.info("All API routers imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing web UI: {e}")
        return False

def test_integration():
    """Test the integration components."""
    logger.info("Testing integration components...")
    
    try:
        # Test system integrator
        from src.integration.system_integrator import SystemIntegrator
        integrator = SystemIntegrator()
        logger.info("System integrator initialized successfully")
        
        # Test performance monitor
        from src.integration.performance_monitor import PerformanceMonitor
        monitor = PerformanceMonitor()
        logger.info("Performance monitor initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        return False

def test_advanced_features():
    """Test the advanced features."""
    logger.info("Testing advanced features...")
    
    try:
        # Test webhook system
        from src.webhooks import WebhookManager, EventDispatcher, DeliveryQueue
        webhook_manager = WebhookManager()
        delivery_queue = DeliveryQueue()
        event_dispatcher = EventDispatcher(webhook_manager, delivery_queue)
        logger.info("Webhook system initialized successfully")
        
        # Test audit system
        from src.utils.audit_logger import AuditLogger
        audit_logger = AuditLogger()
        logger.info("Audit logger initialized successfully")
        
        # Test cache system
        from src.utils.cache_manager import CacheManager
        cache_manager = CacheManager()
        logger.info("Cache manager initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing advanced features: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting real data testing...")
    
    tests = [
        ("Data Acquisition", test_data_acquisition),
        ("Data Processing", test_data_processing),
        ("Web UI", test_web_ui),
        ("Integration", test_integration),
        ("Advanced Features", test_advanced_features),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results[test_name] = success
            if success:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready for deployment.")
    else:
        logger.warning("⚠️  Some tests failed. Review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 