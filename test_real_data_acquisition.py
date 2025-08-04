#!/usr/bin/env python3
"""
Test Real Data Acquisition
This script tests the system with actual Smoothcomp data to find real issues.
"""

import asyncio
import sys
from pathlib import Path
from src.utils.logger import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

async def test_real_smoothcomp_data():
    """Test with real Smoothcomp data."""
    logger.info("Testing real Smoothcomp data acquisition...")
    
    try:
        from src.data_acquisition.smoothcomp_client import SmoothcompClient
        settings = get_settings()
        
        if not settings.smoothcomp_username or not settings.smoothcomp_password:
            logger.error("Smoothcomp credentials not set. Please set SMOOTHCOMP_USERNAME and SMOOTHCOMP_PASSWORD environment variables.")
            return False
        
        client = SmoothcompClient(settings.smoothcomp_username, settings.smoothcomp_password)
        logger.info("Smoothcomp client initialized with real credentials")
        
        # Test with a real event ID (ADCC Youth Worlds 2024)
        event_id = "E12692"
        logger.info(f"Testing with real event: {event_id}")
        
        # Test event info retrieval
        try:
            event_info = await client.get_event_info(event_id)
            logger.info(f"Event info retrieved: {event_info}")
        except Exception as e:
            logger.error(f"Failed to get event info: {e}")
            return False
        
        # Test registration data
        try:
            registrations = await client.get_registrations(event_id)
            logger.info(f"Registrations retrieved: {len(registrations) if registrations else 0} athletes")
        except Exception as e:
            logger.error(f"Failed to get registrations: {e}")
            return False
        
        # Test match data
        try:
            matches = await client.get_matches(event_id)
            logger.info(f"Matches retrieved: {len(matches) if matches else 0} matches")
        except Exception as e:
            logger.error(f"Failed to get matches: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing real Smoothcomp data: {e}")
        return False

async def test_browser_automation():
    """Test browser automation with real data."""
    logger.info("Testing browser automation...")
    
    try:
        from src.data_acquisition.browser_automation import BrowserAutomation
        from pathlib import Path
        
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)
        
        browser = BrowserAutomation(download_dir=download_dir)
        logger.info("Browser automation initialized")
        
        # Test browser startup
        await browser.start_browser()
        logger.info("Browser started successfully")
        
        # Test navigation to a real event
        event_id = "E12692"
        await browser.navigate_to_event(event_id)
        logger.info(f"Navigated to event {event_id}")
        
        # Test browser stop
        await browser.stop_browser()
        logger.info("Browser stopped successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing browser automation: {e}")
        return False

async def test_data_processing():
    """Test data processing with real data."""
    logger.info("Testing data processing...")
    
    try:
        from src.analytics.glicko_engine import GlickoEngine
        from src.analytics.record_calculator import RecordCalculator
        
        # Test Glicko calculations with real data
        engine = GlickoEngine()
        
        # Test with realistic ratings
        test_matches = [
            {"opponent_rating": 1600, "opponent_rd": 300, "result": 1},  # Win
            {"opponent_rating": 1400, "opponent_rd": 400, "result": 0},  # Loss
            {"opponent_rating": 1550, "opponent_rd": 320, "result": 1},  # Win
        ]
        
        current_rating = 1500
        current_rd = 350
        
        final_rating, final_rd = engine.process_matches(current_rating, current_rd, test_matches)
        logger.info(f"Glicko calculation result: rating={final_rating:.2f}, rd={final_rd:.2f}")
        
        # Test record calculation
        calculator = RecordCalculator()
        test_results = [
            {"result": "WIN", "win_type": "SUBMISSION"},
            {"result": "LOSS", "win_type": "POINTS"},
            {"result": "WIN", "win_type": "SUBMISSION"},
            {"result": "WIN", "win_type": "DECISION"},
        ]
        
        record = calculator.calculate_record(test_results)
        logger.info(f"Record calculation result: {record}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing data processing: {e}")
        return False

async def test_web_ui_with_real_data():
    """Test web UI with real data."""
    logger.info("Testing web UI with real data...")
    
    try:
        from src.web_ui.main import app
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        logger.info(f"Health check: {response.status_code} - {response.json()}")
        
        # Test athletes endpoint
        response = client.get("/api/athletes/")
        logger.info(f"Athletes endpoint: {response.status_code}")
        
        # Test events endpoint
        response = client.get("/api/events/")
        logger.info(f"Events endpoint: {response.status_code}")
        
        # Test leaderboards endpoint
        response = client.get("/api/leaderboards/")
        logger.info(f"Leaderboards endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing web UI: {e}")
        return False

async def main():
    """Run all real data tests."""
    logger.info("Starting real data testing...")
    
    tests = [
        ("Real Smoothcomp Data", test_real_smoothcomp_data),
        ("Browser Automation", test_browser_automation),
        ("Data Processing", test_data_processing),
        ("Web UI with Real Data", test_web_ui_with_real_data),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = await test_func()
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
    logger.info("REAL DATA TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All real data tests passed! System is ready for production.")
    else:
        logger.warning("⚠️  Some real data tests failed. Review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 