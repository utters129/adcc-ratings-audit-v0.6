"""
Phase 8: Integration & Testing - Comprehensive Test Suite

This module contains comprehensive integration tests for all Phase 8 components
including system integration, performance monitoring, and deployment preparation.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.integration.system_integrator import SystemIntegrator, run_integration_test
from src.integration.performance_monitor import (
    PerformanceMonitor, PerformanceMetric, 
    get_performance_monitor, monitor_performance, monitor_async_performance
)
from src.integration.deployment_manager import DeploymentManager, prepare_railway_deployment


class TestSystemIntegrator:
    """Test the SystemIntegrator class for end-to-end integration testing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.integrator = SystemIntegrator()
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'integrator'):
            self.integrator.cleanup()
    
    def test_initialization(self):
        """Test that the system integrator initializes correctly."""
        assert self.integrator is not None
        assert hasattr(self.integrator, 'smoothcomp_client')
        assert hasattr(self.integrator, 'browser_automation')
        assert hasattr(self.integrator, 'file_monitor')
        assert hasattr(self.integrator, 'template_processor')
        assert hasattr(self.integrator, 'normalizer')
        assert hasattr(self.integrator, 'id_generator')
        assert hasattr(self.integrator, 'classifier')
        assert hasattr(self.integrator, 'glicko_engine')
        assert hasattr(self.integrator, 'record_calculator')
        assert hasattr(self.integrator, 'medal_tracker')
        assert hasattr(self.integrator, 'report_generator')
        assert hasattr(self.integrator, 'state_manager')
        assert hasattr(self.integrator, 'web_client')
    
    @pytest.mark.asyncio
    async def test_end_to_end_test_structure(self):
        """Test the structure of end-to-end test results."""
        with patch.object(self.integrator, '_test_data_acquisition') as mock_acquisition, \
             patch.object(self.integrator, '_test_data_processing') as mock_processing, \
             patch.object(self.integrator, '_test_analytics_processing') as mock_analytics, \
             patch.object(self.integrator, '_test_web_ui_integration') as mock_web_ui:
            
            # Mock return values
            mock_acquisition.return_value = {"status": "PASS", "duration": 1.0}
            mock_processing.return_value = {"status": "PASS", "duration": 2.0}
            mock_analytics.return_value = {"status": "PASS", "duration": 3.0}
            mock_web_ui.return_value = {"status": "PASS", "duration": 4.0}
            
            results = await self.integrator.run_end_to_end_test("test_event_001")
            
            assert "test_id" in results
            assert "test_event_id" in results
            assert "total_duration" in results
            assert "acquisition" in results
            assert "processing" in results
            assert "analytics" in results
            assert "web_ui" in results
            assert "performance" in results
            assert "errors" in results
            assert "overall_status" in results
    
    @pytest.mark.asyncio
    async def test_data_acquisition_test(self):
        """Test the data acquisition testing functionality."""
        result = await self.integrator._test_data_acquisition("test_event_001")
        
        assert "status" in result
        assert "duration" in result
        assert "smoothcomp_client" in result
        assert "browser_automation" in result
        assert "file_monitoring" in result
        assert "template_processing" in result
    
    @pytest.mark.asyncio
    async def test_data_processing_test(self):
        """Test the data processing testing functionality."""
        result = await self.integrator._test_data_processing("test_event_001")
        
        assert "status" in result
        assert "duration" in result
        assert "normalization" in result
        assert "id_generation" in result
        assert "classification" in result
    
    @pytest.mark.asyncio
    async def test_analytics_processing_test(self):
        """Test the analytics processing testing functionality."""
        result = await self.integrator._test_analytics_processing("test_event_001")
        
        assert "status" in result
        assert "duration" in result
        assert "glicko_calculations" in result
        assert "record_calculations" in result
        assert "medal_tracking" in result
        assert "report_generation" in result
    
    def test_web_ui_integration_test(self):
        """Test the web UI integration testing functionality."""
        result = asyncio.run(self.integrator._test_web_ui_integration())
        
        assert "status" in result
        assert "duration" in result
        assert "health_check" in result
        assert "authentication" in result
        assert "athletes" in result
        assert "events" in result
        assert "leaderboards" in result
    
    def test_api_health_check(self):
        """Test API health check functionality."""
        result = self.integrator._test_api_health()
        
        assert "status" in result
        assert "status_code" in result
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints testing."""
        result = self.integrator._test_authentication_endpoints()
        
        assert "status" in result
        assert "login_status_code" in result
    
    def test_athlete_endpoints(self):
        """Test athlete endpoints testing."""
        result = self.integrator._test_athlete_endpoints()
        
        assert "status" in result
        assert "search_status_code" in result
    
    def test_event_endpoints(self):
        """Test event endpoints testing."""
        result = self.integrator._test_event_endpoints()
        
        assert "status" in result
        assert "list_status_code" in result
    
    def test_leaderboard_endpoints(self):
        """Test leaderboard endpoints testing."""
        result = self.integrator._test_leaderboard_endpoints()
        
        assert "status" in result
        assert "leaderboard_status_code" in result
    
    def test_performance_analysis(self):
        """Test performance analysis functionality."""
        result = self.integrator._analyze_performance()
        
        assert "total_time" in result
        assert "component_times" in result
        assert "performance_grade" in result
    
    def test_error_analysis(self):
        """Test error analysis functionality."""
        result = self.integrator._analyze_errors()
        
        assert "total_errors" in result
        assert "critical_errors" in result
        assert "high_errors" in result
        assert "medium_errors" in result
        assert "low_errors" in result
    
    def test_performance_grade_calculation(self):
        """Test performance grade calculation."""
        assert self.integrator._calculate_performance_grade(15) == "A"
        assert self.integrator._calculate_performance_grade(45) == "B"
        assert self.integrator._calculate_performance_grade(90) == "C"
        assert self.integrator._calculate_performance_grade(150) == "D"
    
    def test_integration_report_generation(self):
        """Test integration report generation."""
        report = self.integrator.generate_integration_report()
        
        assert "report_timestamp" in report
        assert "test_results" in report
        assert "performance_metrics" in report
        assert "error_analysis" in report
        assert "recommendations" in report
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        recommendations = self.integrator._generate_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_run_integration_test_function(self):
        """Test the convenience function for running integration tests."""
        with patch.object(SystemIntegrator, 'run_end_to_end_test') as mock_run:
            mock_run.return_value = {"status": "PASS"}
            
            result = await run_integration_test("test_event_001")
            
            assert result == {"status": "PASS"}
            mock_run.assert_called_once_with("test_event_001")


class TestPerformanceMonitor:
    """Test the PerformanceMonitor class for performance monitoring."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor(max_history=100)
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'monitor'):
            self.monitor.cleanup()
    
    def test_initialization(self):
        """Test that the performance monitor initializes correctly."""
        assert self.monitor is not None
        assert self.monitor.max_history == 100
        assert self.monitor.monitoring_enabled is True
        assert len(self.monitor.metrics) == 0
        assert len(self.monitor.component_stats) == 0
        assert len(self.monitor.active_monitors) == 0
    
    def test_start_monitoring(self):
        """Test starting performance monitoring."""
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        
        assert monitor_id != ""
        assert monitor_id in self.monitor.active_monitors
        assert self.monitor.active_monitors[monitor_id]["component"] == "test_component"
        assert self.monitor.active_monitors[monitor_id]["operation"] == "test_operation"
    
    def test_stop_monitoring_success(self):
        """Test stopping performance monitoring with success."""
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        
        metric = self.monitor.stop_monitoring(monitor_id, success=True)
        
        assert metric is not None
        assert metric.component == "test_component"
        assert metric.operation == "test_operation"
        assert metric.success is True
        assert metric.duration > 0
        assert monitor_id not in self.monitor.active_monitors
    
    def test_stop_monitoring_failure(self):
        """Test stopping performance monitoring with failure."""
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        
        metric = self.monitor.stop_monitoring(
            monitor_id, 
            success=False, 
            error_message="Test error"
        )
        
        assert metric is not None
        assert metric.success is False
        assert metric.error_message == "Test error"
    
    def test_stop_monitoring_invalid_id(self):
        """Test stopping monitoring with invalid monitor ID."""
        metric = self.monitor.stop_monitoring("invalid_id")
        
        assert metric is None
    
    def test_component_stats(self):
        """Test component statistics tracking."""
        # Start and stop a few monitors
        monitor_id1 = self.monitor.start_monitoring("component1", "operation1")
        self.monitor.stop_monitoring(monitor_id1, success=True)
        
        monitor_id2 = self.monitor.start_monitoring("component1", "operation2")
        self.monitor.stop_monitoring(monitor_id2, success=False)
        
        stats = self.monitor.get_component_stats("component1")
        
        assert stats["total_operations"] == 2
        assert stats["successful_operations"] == 1
        assert stats["failed_operations"] == 1
        assert stats["success_rate"] == 0.5
        assert stats["failure_rate"] == 0.5
    
    def test_overall_stats(self):
        """Test overall statistics calculation."""
        # Add some metrics
        monitor_id1 = self.monitor.start_monitoring("component1", "operation1")
        self.monitor.stop_monitoring(monitor_id1, success=True)
        
        monitor_id2 = self.monitor.start_monitoring("component2", "operation1")
        self.monitor.stop_monitoring(monitor_id2, success=True)
        
        stats = self.monitor.get_overall_stats()
        
        assert stats["total_operations"] == 2
        assert stats["successful_operations"] == 2
        assert stats["failed_operations"] == 0
        assert stats["success_rate"] == 1.0
        assert stats["failure_rate"] == 0.0
        assert stats["component_count"] == 2
    
    def test_recent_metrics(self):
        """Test getting recent metrics."""
        # Add a metric
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        self.monitor.stop_monitoring(monitor_id, success=True)
        
        recent_metrics = self.monitor.get_recent_metrics(minutes=60)
        
        assert len(recent_metrics) == 1
        assert recent_metrics[0].component == "test_component"
        assert recent_metrics[0].operation == "test_operation"
    
    def test_slowest_operations(self):
        """Test getting slowest operations."""
        # Add metrics with different durations
        monitor_id1 = self.monitor.start_monitoring("component1", "fast_operation")
        self.monitor.stop_monitoring(monitor_id1, success=True)
        
        monitor_id2 = self.monitor.start_monitoring("component2", "slow_operation")
        # Simulate longer duration by adding a metric directly
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            component="component2",
            operation="slow_operation",
            duration=10.0,
            memory_usage=1000000,
            cpu_usage=50.0,
            success=True
        )
        self.monitor._record_metric(metric)
        
        slowest_ops = self.monitor.get_slowest_operations(limit=5)
        
        assert len(slowest_ops) >= 1
        assert slowest_ops[0]["operation"] == "slow_operation"
        assert slowest_ops[0]["duration"] == 10.0
    
    def test_performance_alerts(self):
        """Test performance alerts generation."""
        # Add a slow operation
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            component="test_component",
            operation="slow_operation",
            duration=35.0,  # > 30 seconds
            memory_usage=1000000,
            cpu_usage=50.0,
            success=True
        )
        self.monitor._record_metric(metric)
        
        alerts = self.monitor.get_performance_alerts()
        
        assert len(alerts) > 0
        assert any(alert["type"] == "slow_operation" for alert in alerts)
    
    def test_performance_report(self):
        """Test performance report generation."""
        # Add some metrics
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        self.monitor.stop_monitoring(monitor_id, success=True)
        
        report = self.monitor.generate_performance_report()
        
        assert "report_timestamp" in report
        assert "overall_stats" in report
        assert "component_breakdown" in report
        assert "alerts" in report
        assert "slowest_operations" in report
        assert "memory_trend" in report
        assert "recommendations" in report
    
    def test_enable_disable_monitoring(self):
        """Test enabling and disabling monitoring."""
        self.monitor.disable_monitoring()
        assert self.monitor.monitoring_enabled is False
        
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        assert monitor_id == ""  # Should return empty string when disabled
        
        self.monitor.enable_monitoring()
        assert self.monitor.monitoring_enabled is True
        
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        assert monitor_id != ""  # Should return valid ID when enabled
    
    def test_reset_stats(self):
        """Test resetting statistics."""
        # Add some metrics
        monitor_id = self.monitor.start_monitoring("test_component", "test_operation")
        self.monitor.stop_monitoring(monitor_id, success=True)
        
        assert len(self.monitor.metrics) > 0
        assert len(self.monitor.component_stats) > 0
        
        self.monitor.reset_stats()
        
        assert len(self.monitor.metrics) == 0
        assert len(self.monitor.component_stats) == 0
        assert len(self.monitor.active_monitors) == 0


class TestPerformanceMonitorDecorators:
    """Test the performance monitoring decorators."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor()
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'monitor'):
            self.monitor.cleanup()
    
    def test_monitor_performance_decorator(self):
        """Test the monitor_performance decorator."""
        @monitor_performance("test_component", "test_operation")
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        
        # Check that metrics were recorded
        stats = self.monitor.get_component_stats("test_component")
        assert stats["total_operations"] == 1
        assert stats["successful_operations"] == 1
    
    def test_monitor_performance_decorator_with_exception(self):
        """Test the monitor_performance decorator with exception."""
        @monitor_performance("test_component", "test_operation")
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_function()
        
        # Check that metrics were recorded
        stats = self.monitor.get_component_stats("test_component")
        assert stats["total_operations"] == 1
        assert stats["failed_operations"] == 1
    
    @pytest.mark.asyncio
    async def test_monitor_async_performance_decorator(self):
        """Test the monitor_async_performance decorator."""
        @monitor_async_performance("test_component", "test_operation")
        async def test_async_function():
            return "success"
        
        result = await test_async_function()
        
        assert result == "success"
        
        # Check that metrics were recorded
        stats = self.monitor.get_component_stats("test_component")
        assert stats["total_operations"] == 1
        assert stats["successful_operations"] == 1
    
    @pytest.mark.asyncio
    async def test_monitor_async_performance_decorator_with_exception(self):
        """Test the monitor_async_performance decorator with exception."""
        @monitor_async_performance("test_component", "test_operation")
        async def test_async_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await test_async_function()
        
        # Check that metrics were recorded
        stats = self.monitor.get_component_stats("test_component")
        assert stats["total_operations"] == 1
        assert stats["failed_operations"] == 1


class TestDeploymentManager:
    """Test the DeploymentManager class for deployment preparation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.manager = DeploymentManager(self.project_root)
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test that the deployment manager initializes correctly."""
        assert self.manager is not None
        assert self.manager.project_root == self.project_root
        assert isinstance(self.manager.deployment_config, dict)
        assert isinstance(self.manager.environment_vars, dict)
        assert isinstance(self.manager.deployment_status, dict)
    
    def test_validate_project_structure_missing_files(self):
        """Test project structure validation with missing files."""
        result = self.manager._validate_project_structure()
        
        assert result["status"] == "FAIL"
        assert len(result["missing_files"]) > 0
        assert len(result["missing_directories"]) > 0
    
    def test_validate_project_structure_complete(self):
        """Test project structure validation with complete structure."""
        # Create required files and directories
        (self.project_root / "requirements.txt").touch()
        (self.project_root / "src" / "web_ui" / "main.py").parent.mkdir(parents=True, exist_ok=True)
        (self.project_root / "src" / "web_ui" / "main.py").touch()
        (self.project_root / "src" / "config" / "settings.py").parent.mkdir(parents=True, exist_ok=True)
        (self.project_root / "src" / "config" / "settings.py").touch()
        (self.project_root / "src" / "integration" / "system_integrator.py").parent.mkdir(parents=True, exist_ok=True)
        (self.project_root / "src" / "integration" / "system_integrator.py").touch()
        (self.project_root / "src" / "integration" / "performance_monitor.py").touch()
        (self.project_root / "src" / "web_ui" / "templates").mkdir(parents=True, exist_ok=True)
        (self.project_root / "src" / "web_ui" / "static").mkdir(parents=True, exist_ok=True)
        (self.project_root / "src" / "web_ui" / "api").mkdir(parents=True, exist_ok=True)
        (self.project_root / "tests").mkdir(exist_ok=True)
        
        result = self.manager._validate_project_structure()
        
        assert result["status"] == "PASS"
        assert len(result["missing_files"]) == 0
        assert len(result["missing_directories"]) == 0
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        result = self.manager._check_dependencies()
        
        assert "status" in result
        assert "missing_packages" in result
        assert "available_packages" in result
        assert "total_required" in result
    
    def test_generate_deployment_config(self):
        """Test deployment configuration generation."""
        result = self.manager._generate_deployment_config("production")
        
        assert result["status"] == "PASS"
        assert result["config_generated"] is True
        assert result["environment"] == "production"
        assert "build" in self.manager.deployment_config
        assert "deploy" in self.manager.deployment_config
    
    def test_prepare_environment_variables(self):
        """Test environment variable preparation."""
        result = self.manager._prepare_environment_variables("production")
        
        assert result["status"] == "PASS"
        assert result["base_variables"] > 0
        assert result["sensitive_variables"] > 0
        assert result["total_variables"] > 0
    
    def test_create_deployment_files(self):
        """Test deployment file creation."""
        # First generate config
        self.manager._generate_deployment_config("production")
        
        result = self.manager._create_deployment_files("production")
        
        assert result["status"] == "PASS"
        assert len(result["files_created"]) > 0
        assert result["total_files"] > 0
    
    def test_pre_deployment_tests(self):
        """Test pre-deployment tests."""
        result = self.manager._run_pre_deployment_tests()
        
        assert "status" in result
        assert "import_test" in result
        assert "config_test" in result
        assert "web_test" in result
        assert "api_test" in result
        assert "total_tests" in result
        assert "passed_tests" in result
    
    def test_prepare_deployment(self):
        """Test complete deployment preparation."""
        # Create minimal required structure
        (self.project_root / "requirements.txt").touch()
        (self.project_root / "src" / "web_ui" / "main.py").parent.mkdir(parents=True, exist_ok=True)
        (self.project_root / "src" / "web_ui" / "main.py").touch()
        
        result = self.manager.prepare_deployment("production")
        
        assert "environment" in result
        assert "timestamp" in result
        assert "overall_status" in result
        assert "structure_validation" in result
        assert "dependency_check" in result
        assert "config_generation" in result
        assert "env_preparation" in result
        assert "file_creation" in result
        assert "pre_deployment_tests" in result
    
    def test_generate_deployment_instructions(self):
        """Test deployment instructions generation."""
        instructions = self.manager.generate_deployment_instructions()
        
        assert "railway_setup" in instructions
        assert "environment_variables" in instructions
        assert "deployment_commands" in instructions
        assert "monitoring" in instructions
        assert "rollback" in instructions
    
    def test_create_deployment_report(self):
        """Test deployment report creation."""
        # Prepare deployment first
        (self.project_root / "requirements.txt").touch()
        (self.project_root / "src" / "web_ui" / "main.py").parent.mkdir(parents=True, exist_ok=True)
        (self.project_root / "src" / "web_ui" / "main.py").touch()
        
        self.manager.prepare_deployment("production")
        report = self.manager.create_deployment_report()
        
        assert "report_timestamp" in report
        assert "deployment_status" in report
        assert "instructions" in report
        assert "recommendations" in report
        assert "next_steps" in report
    
    def test_cleanup_deployment_files(self):
        """Test deployment file cleanup."""
        # Create some test files
        (self.project_root / "railway.json").touch()
        (self.project_root / "Procfile").touch()
        
        removed_files = self.manager.cleanup_deployment_files()
        
        assert len(removed_files) > 0
        assert not (self.project_root / "railway.json").exists()
        assert not (self.project_root / "Procfile").exists()


class TestDeploymentIntegration:
    """Test deployment integration functions."""
    
    def test_prepare_railway_deployment(self):
        """Test the prepare_railway_deployment convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create minimal required structure
            (project_root / "requirements.txt").touch()
            (project_root / "src" / "web_ui" / "main.py").parent.mkdir(parents=True, exist_ok=True)
            (project_root / "src" / "web_ui" / "main.py").touch()
            
            with patch('src.integration.deployment_manager.DeploymentManager') as mock_manager_class:
                mock_manager = Mock()
                mock_manager_class.return_value = mock_manager
                mock_manager.prepare_deployment.return_value = {"status": "READY"}
                mock_manager.create_deployment_report.return_value = {"report": "data"}
                
                result = prepare_railway_deployment("production")
                
                assert "preparation_results" in result
                assert "deployment_report" in result
                mock_manager.prepare_deployment.assert_called_once_with("production")
                mock_manager.create_deployment_report.assert_called_once()


class TestPhase8Integration:
    """Test Phase 8 integration with all components."""
    
    def test_phase8_components_import(self):
        """Test that all Phase 8 components can be imported."""
        from src.integration.system_integrator import SystemIntegrator
        from src.integration.performance_monitor import PerformanceMonitor
        from src.integration.deployment_manager import DeploymentManager
        
        assert SystemIntegrator is not None
        assert PerformanceMonitor is not None
        assert DeploymentManager is not None
    
    def test_phase8_component_integration(self):
        """Test integration between Phase 8 components."""
        # Test that components can work together
        monitor = PerformanceMonitor()
        integrator = SystemIntegrator()
        
        # Test performance monitoring with system integrator
        monitor_id = monitor.start_monitoring("system_integrator", "test_operation")
        monitor.stop_monitoring(monitor_id, success=True)
        
        stats = monitor.get_component_stats("system_integrator")
        assert stats["total_operations"] == 1
        assert stats["successful_operations"] == 1
        
        # Cleanup
        monitor.cleanup()
        integrator.cleanup()
    
    def test_phase8_error_handling(self):
        """Test error handling in Phase 8 components."""
        # Test system integrator error handling
        integrator = SystemIntegrator()
        
        # Add an error to the error log
        integrator.error_log.append({
            "timestamp": datetime.now().isoformat(),
            "component": "test_component",
            "error": "Test error",
            "severity": "high"
        })
        
        error_analysis = integrator._analyze_errors()
        assert error_analysis["total_errors"] == 1
        assert error_analysis["high_errors"] == 1
        
        integrator.cleanup()


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 