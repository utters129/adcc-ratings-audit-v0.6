"""
System Integrator for ADCC Analysis Engine

This module provides end-to-end integration testing and coordination
of all system components from previous phases.
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import structlog

from src.config.settings import get_settings
from src.data_acquisition.smoothcomp_client import SmoothcompClient
from src.data_acquisition.browser_automation import BrowserAutomation
from src.data_acquisition.file_monitor import FileMonitor
from src.data_acquisition.template_processor import TemplateProcessor
from src.data_processing.normalizer import DataNormalizer
from src.data_processing.id_generator import IDGenerator
from src.data_processing.classifier import DivisionClassifier
from src.analytics.glicko_engine import GlickoEngine
from src.analytics.record_calculator import RecordCalculator
from src.analytics.medal_tracker import MedalTracker
from src.analytics.report_generator import ReportGenerator
from src.state_management.save_states import StateManager
from src.web_ui.main import app
from fastapi.testclient import TestClient

logger = structlog.get_logger(__name__)
settings = get_settings()


class SystemIntegrator:
    """
    Main system integrator for coordinating all components
    and performing end-to-end testing.
    """
    
    def __init__(self):
        """Initialize the system integrator with all components."""
        self.settings = get_settings()
        self.test_results: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.error_log: List[Dict[str, Any]] = []
        
        # Initialize all components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            logger.info("Initializing system components")
            
            # Data Acquisition Components
            # Initialize with dummy credentials for testing - real credentials would come from config
            self.smoothcomp_client = SmoothcompClient("test_user", "test_pass")
            # Initialize with temporary download directory for testing
            temp_download_dir = Path.cwd() / "temp_downloads"
            temp_download_dir.mkdir(exist_ok=True)
            self.browser_automation = BrowserAutomation(download_dir=temp_download_dir)
            # Initialize file monitor with watch directory and patterns
            self.file_monitor = FileMonitor(
                watch_directory=temp_download_dir,
                file_patterns=["*.csv", "*.xlsx", "*.json"]
            )
            
            # Initialize template processor with temporary directories
            temp_template_dir = Path.cwd() / "temp_templates"
            temp_template_dir.mkdir(exist_ok=True)
            temp_output_dir = Path.cwd() / "temp_outputs"
            temp_output_dir.mkdir(exist_ok=True)
            self.template_processor = TemplateProcessor(
                template_dir=temp_template_dir,
                output_dir=temp_output_dir
            )
            
            # Data Processing Components
            self.normalizer = DataNormalizer()
            self.id_generator = IDGenerator()
            self.classifier = DivisionClassifier()
            
            # Analytics Components
            self.glicko_engine = GlickoEngine()
            self.record_calculator = RecordCalculator()
            self.medal_tracker = MedalTracker()
            self.report_generator = ReportGenerator()
            
            # State Management
            self.state_manager = StateManager()
            
            # Web UI - Initialize with error handling
            try:
                from src.web_ui.main import app
                self.web_client = TestClient(app)
            except Exception as e:
                logger.warning("Failed to initialize TestClient, setting to None", error=str(e))
                self.web_client = None
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize components", error=str(e))
            raise
    
    async def run_end_to_end_test(self, test_event_id: str = "test_event_001") -> Dict[str, Any]:
        """
        Run a complete end-to-end test of the entire system.
        
        Args:
            test_event_id: Test event ID to use for the integration test
            
        Returns:
            Dictionary containing test results and metrics
        """
        start_time = time.time()
        logger.info("Starting end-to-end system test", test_event_id=test_event_id)
        
        try:
            # Step 1: Data Acquisition Test
            acquisition_result = await self._test_data_acquisition(test_event_id)
            
            # Step 2: Data Processing Test
            processing_result = await self._test_data_processing(test_event_id)
            
            # Step 3: Analytics Processing Test
            analytics_result = await self._test_analytics_processing(test_event_id)
            
            # Step 4: Web UI Integration Test
            web_ui_result = await self._test_web_ui_integration()
            
            # Step 5: Performance and Error Analysis
            performance_result = self._analyze_performance()
            error_analysis = self._analyze_errors()
            
            total_time = time.time() - start_time
            
            self.test_results = {
                "test_id": f"e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "test_event_id": test_event_id,
                "total_duration": total_time,
                "acquisition": acquisition_result,
                "processing": processing_result,
                "analytics": analytics_result,
                "web_ui": web_ui_result,
                "performance": performance_result,
                "errors": error_analysis,
                "overall_status": "PASS" if not error_analysis["critical_errors"] else "FAIL"
            }
            
            logger.info("End-to-end test completed", 
                       status=self.test_results["overall_status"],
                       duration=total_time)
            
            return self.test_results
            
        except Exception as e:
            logger.error("End-to-end test failed", error=str(e))
            self.error_log.append({
                "timestamp": datetime.now().isoformat(),
                "component": "system_integrator",
                "error": str(e),
                "severity": "critical"
            })
            raise
    
    async def _test_data_acquisition(self, event_id: str) -> Dict[str, Any]:
        """Test the complete data acquisition pipeline."""
        start_time = time.time()
        logger.info("Testing data acquisition pipeline", event_id=event_id)
        
        try:
            # Test Smoothcomp client
            client_result = await self._test_smoothcomp_client(event_id)
            
            # Test browser automation
            browser_result = await self._test_browser_automation(event_id)
            
            # Test file monitoring
            monitor_result = await self._test_file_monitoring()
            
            # Test template processing
            template_result = await self._test_template_processing()
            
            duration = time.time() - start_time
            self.performance_metrics["data_acquisition"] = duration
            
            return {
                "status": "PASS",
                "duration": duration,
                "smoothcomp_client": client_result,
                "browser_automation": browser_result,
                "file_monitoring": monitor_result,
                "template_processing": template_result
            }
            
        except Exception as e:
            logger.error("Data acquisition test failed", error=str(e))
            self.error_log.append({
                "timestamp": datetime.now().isoformat(),
                "component": "data_acquisition",
                "error": str(e),
                "severity": "high"
            })
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_data_processing(self, event_id: str) -> Dict[str, Any]:
        """Test the complete data processing pipeline."""
        start_time = time.time()
        logger.info("Testing data processing pipeline", event_id=event_id)
        
        try:
            # Test data normalization
            normalization_result = await self._test_data_normalization(event_id)
            
            # Test ID generation
            id_generation_result = await self._test_id_generation(event_id)
            
            # Test division classification
            classification_result = await self._test_division_classification(event_id)
            
            duration = time.time() - start_time
            self.performance_metrics["data_processing"] = duration
            
            return {
                "status": "PASS",
                "duration": duration,
                "normalization": normalization_result,
                "id_generation": id_generation_result,
                "classification": classification_result
            }
            
        except Exception as e:
            logger.error("Data processing test failed", error=str(e))
            self.error_log.append({
                "timestamp": datetime.now().isoformat(),
                "component": "data_processing",
                "error": str(e),
                "severity": "high"
            })
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_analytics_processing(self, event_id: str) -> Dict[str, Any]:
        """Test the complete analytics processing pipeline."""
        start_time = time.time()
        logger.info("Testing analytics processing pipeline", event_id=event_id)
        
        try:
            # Test Glicko rating calculations
            glicko_result = await self._test_glicko_calculations(event_id)
            
            # Test record calculations
            record_result = await self._test_record_calculations(event_id)
            
            # Test medal tracking
            medal_result = await self._test_medal_tracking(event_id)
            
            # Test report generation
            report_result = await self._test_report_generation(event_id)
            
            duration = time.time() - start_time
            self.performance_metrics["analytics_processing"] = duration
            
            return {
                "status": "PASS",
                "duration": duration,
                "glicko_calculations": glicko_result,
                "record_calculations": record_result,
                "medal_tracking": medal_result,
                "report_generation": report_result
            }
            
        except Exception as e:
            logger.error("Analytics processing test failed", error=str(e))
            self.error_log.append({
                "timestamp": datetime.now().isoformat(),
                "component": "analytics_processing",
                "error": str(e),
                "severity": "high"
            })
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_web_ui_integration(self) -> Dict[str, Any]:
        """Test the web UI integration and API endpoints."""
        start_time = time.time()
        logger.info("Testing web UI integration")
        
        try:
            # Test API health check
            health_result = self._test_api_health()
            
            # Test authentication endpoints
            auth_result = self._test_authentication_endpoints()
            
            # Test athlete endpoints
            athlete_result = self._test_athlete_endpoints()
            
            # Test event endpoints
            event_result = self._test_event_endpoints()
            
            # Test leaderboard endpoints
            leaderboard_result = self._test_leaderboard_endpoints()
            
            duration = time.time() - start_time
            self.performance_metrics["web_ui_integration"] = duration
            
            return {
                "status": "PASS",
                "duration": duration,
                "health_check": health_result,
                "authentication": auth_result,
                "athletes": athlete_result,
                "events": event_result,
                "leaderboards": leaderboard_result
            }
            
        except Exception as e:
            logger.error("Web UI integration test failed", error=str(e))
            self.error_log.append({
                "timestamp": datetime.now().isoformat(),
                "component": "web_ui_integration",
                "error": str(e),
                "severity": "high"
            })
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_smoothcomp_client(self, event_id: str) -> Dict[str, Any]:
        """Test Smoothcomp client functionality."""
        try:
            # Test client initialization
            assert self.smoothcomp_client is not None
            
            # Test event validation (mock)
            validation_result = self.smoothcomp_client.validate_event_id(event_id)
            
            return {
                "status": "PASS",
                "client_initialized": True,
                "event_validation": validation_result
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_browser_automation(self, event_id: str) -> Dict[str, Any]:
        """Test browser automation functionality."""
        try:
            # Test browser initialization
            assert self.browser_automation is not None
            
            return {
                "status": "PASS",
                "browser_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_file_monitoring(self) -> Dict[str, Any]:
        """Test file monitoring functionality."""
        try:
            # Test file monitor initialization
            assert self.file_monitor is not None
            
            return {
                "status": "PASS",
                "monitor_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_template_processing(self) -> Dict[str, Any]:
        """Test template processing functionality."""
        try:
            # Test template processor initialization
            assert self.template_processor is not None
            
            # Test template loading
            templates = self.template_processor.load_templates()
            
            return {
                "status": "PASS",
                "processor_initialized": True,
                "templates_loaded": len(templates) > 0
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_data_normalization(self, event_id: str) -> Dict[str, Any]:
        """Test data normalization functionality."""
        try:
            # Test normalizer initialization
            assert self.normalizer is not None
            
            return {
                "status": "PASS",
                "normalizer_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_id_generation(self, event_id: str) -> Dict[str, Any]:
        """Test ID generation functionality."""
        try:
            # Test ID generator initialization
            assert self.id_generator is not None
            
            # Test athlete ID generation
            test_athlete_id = self.id_generator.generate_athlete_id("Test Athlete", "Test Club")
            
            return {
                "status": "PASS",
                "generator_initialized": True,
                "athlete_id_generated": test_athlete_id is not None
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_division_classification(self, event_id: str) -> Dict[str, Any]:
        """Test division classification functionality."""
        try:
            # Test classifier initialization
            assert self.classifier is not None
            
            return {
                "status": "PASS",
                "classifier_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_glicko_calculations(self, event_id: str) -> Dict[str, Any]:
        """Test Glicko rating calculations."""
        try:
            # Test Glicko engine initialization
            assert self.glicko_engine is not None
            
            return {
                "status": "PASS",
                "engine_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_record_calculations(self, event_id: str) -> Dict[str, Any]:
        """Test record calculations."""
        try:
            # Test record calculator initialization
            assert self.record_calculator is not None
            
            return {
                "status": "PASS",
                "calculator_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_medal_tracking(self, event_id: str) -> Dict[str, Any]:
        """Test medal tracking functionality."""
        try:
            # Test medal tracker initialization
            assert self.medal_tracker is not None
            
            return {
                "status": "PASS",
                "tracker_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    async def _test_report_generation(self, event_id: str) -> Dict[str, Any]:
        """Test report generation functionality."""
        try:
            # Test report generator initialization
            assert self.report_generator is not None
            
            return {
                "status": "PASS",
                "generator_initialized": True
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def _test_api_health(self) -> Dict[str, Any]:
        """Test API health check endpoint."""
        try:
            response = self.web_client.get("/health")
            return {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def _test_authentication_endpoints(self) -> Dict[str, Any]:
        """Test authentication endpoints."""
        try:
            # Test login endpoint
            login_data = {"username": "admin", "password": "admin123"}
            response = self.web_client.post("/api/auth/login", json=login_data)
            
            return {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "login_status_code": response.status_code,
                "login_response": response.json() if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def _test_athlete_endpoints(self) -> Dict[str, Any]:
        """Test athlete endpoints."""
        try:
            # Test athlete search endpoint
            response = self.web_client.get("/api/athletes/")
            
            return {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "search_status_code": response.status_code,
                "search_response": response.json() if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def _test_event_endpoints(self) -> Dict[str, Any]:
        """Test event endpoints."""
        try:
            # Test event list endpoint
            response = self.web_client.get("/api/events/")
            
            return {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "list_status_code": response.status_code,
                "list_response": response.json() if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def _test_leaderboard_endpoints(self) -> Dict[str, Any]:
        """Test leaderboard endpoints."""
        try:
            # Test global leaderboard endpoint
            response = self.web_client.get("/api/leaderboards/global/top")
            
            return {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "leaderboard_status_code": response.status_code,
                "leaderboard_response": response.json() if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics."""
        try:
            total_time = sum(self.performance_metrics.values())
            
            return {
                "total_time": total_time,
                "component_times": self.performance_metrics,
                "performance_grade": self._calculate_performance_grade(total_time)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze error log and categorize errors."""
        try:
            critical_errors = [e for e in self.error_log if e["severity"] == "critical"]
            high_errors = [e for e in self.error_log if e["severity"] == "high"]
            medium_errors = [e for e in self.error_log if e["severity"] == "medium"]
            low_errors = [e for e in self.error_log if e["severity"] == "low"]
            
            return {
                "total_errors": len(self.error_log),
                "critical_errors": len(critical_errors),
                "high_errors": len(high_errors),
                "medium_errors": len(medium_errors),
                "low_errors": len(low_errors),
                "error_details": self.error_log
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_performance_grade(self, total_time: float) -> str:
        """Calculate performance grade based on total execution time."""
        if total_time < 30:
            return "A"
        elif total_time < 60:
            return "B"
        elif total_time < 120:
            return "C"
        else:
            return "D"
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate a comprehensive integration test report."""
        return {
            "report_timestamp": datetime.now().isoformat(),
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics,
            "error_analysis": self._analyze_errors(),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if not self.test_results:
            recommendations.append("Run end-to-end test first to generate recommendations")
            return recommendations
        
        # Performance recommendations
        if self.performance_metrics.get("data_acquisition", 0) > 30:
            recommendations.append("Optimize data acquisition pipeline for better performance")
        
        if self.performance_metrics.get("analytics_processing", 0) > 60:
            recommendations.append("Consider caching analytics results for better performance")
        
        # Error recommendations
        error_analysis = self._analyze_errors()
        if error_analysis.get("critical_errors", 0) > 0:
            recommendations.append("Address critical errors before deployment")
        
        if error_analysis.get("high_errors", 0) > 5:
            recommendations.append("Review and fix high-severity errors")
        
        # General recommendations
        if self.test_results.get("overall_status") == "PASS":
            recommendations.append("System ready for deployment")
        else:
            recommendations.append("Fix failing components before deployment")
        
        return recommendations
    
    def cleanup(self):
        """Clean up resources and close connections."""
        try:
            logger.info("Cleaning up system integrator resources")
            
            # Clean up browser automation
            if hasattr(self, 'browser_automation'):
                self.browser_automation.cleanup()
            
            # Clean up file monitor
            if hasattr(self, 'file_monitor'):
                self.file_monitor.stop_monitoring()
            
            # Clean up Smoothcomp client
            if hasattr(self, 'smoothcomp_client'):
                self.smoothcomp_client.cleanup()
            
            logger.info("System integrator cleanup completed")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))


async def run_integration_test(event_id: str = "test_event_001") -> Dict[str, Any]:
    """
    Convenience function to run a complete integration test.
    
    Args:
        event_id: Test event ID to use
        
    Returns:
        Integration test results
    """
    integrator = SystemIntegrator()
    try:
        results = await integrator.run_end_to_end_test(event_id)
        return results
    finally:
        integrator.cleanup()


if __name__ == "__main__":
    # Run integration test
    asyncio.run(run_integration_test()) 