"""
Phase 6 Verification Test - File Acquisition System
Tests all Phase 6 components: Smoothcomp API Client, Browser Automation, and Template System.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import responses

from src.data_acquisition.smoothcomp_client import SmoothcompClient
from src.data_acquisition.browser_automation import BrowserAutomation
from src.data_acquisition.file_monitor import FileMonitor
from src.data_acquisition.template_processor import TemplateProcessor
from src.config.settings import get_settings


class TestPhase6Integration:
    """Integration tests for Phase 6 components."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        download_dir = tempfile.mkdtemp()
        template_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        watch_dir = tempfile.mkdtemp()
        
        yield {
            "download": Path(download_dir),
            "template": Path(template_dir),
            "output": Path(output_dir),
            "watch": Path(watch_dir)
        }
        
        # Cleanup
        shutil.rmtree(download_dir)
        shutil.rmtree(template_dir)
        shutil.rmtree(output_dir)
        shutil.rmtree(watch_dir)
    
    @pytest.fixture
    def components(self, temp_dirs):
        """Create all Phase 6 components."""
        settings = get_settings()
        
        # Create components
        smoothcomp_client = SmoothcompClient(
            username=settings.smoothcomp_username or "test_user",
            password=settings.smoothcomp_password or "test_pass"
        )
        
        browser_automation = BrowserAutomation(
            download_dir=temp_dirs["download"],
            headless=True
        )
        
        file_monitor = FileMonitor(
            watch_directory=temp_dirs["watch"],
            file_patterns=["*.csv", "*.xlsx"]
        )
        
        template_processor = TemplateProcessor(
            template_dir=temp_dirs["template"],
            output_dir=temp_dirs["output"]
        )
        
        return {
            "smoothcomp_client": smoothcomp_client,
            "browser_automation": browser_automation,
            "file_monitor": file_monitor,
            "template_processor": template_processor
        }
    
    def test_component_initialization(self, components):
        """Test that all components initialize correctly."""
        # Test SmoothcompClient
        client = components["smoothcomp_client"]
        assert client.username == "test_user"
        assert client.password == "test_pass"
        assert client.base_url == "https://www.smoothcomp.com"
        assert client.session is not None
        
        # Test BrowserAutomation
        automation = components["browser_automation"]
        assert automation.download_dir.exists()
        assert automation.headless is True
        assert automation.driver is None
        
        # Test FileMonitor
        monitor = components["file_monitor"]
        assert monitor.watch_directory.exists()
        assert monitor.file_patterns == ["*.csv", "*.xlsx"]
        assert monitor.is_monitoring is False
        
        # Test TemplateProcessor
        processor = components["template_processor"]
        assert processor.template_dir.exists()
        assert processor.output_dir.exists()
        assert isinstance(processor.templates, dict)
        
        print("✅ All Phase 6 components initialized successfully")
    
    @responses.activate
    def test_smoothcomp_client_functionality(self, components):
        """Test SmoothcompClient functionality."""
        client = components["smoothcomp_client"]
        
        # Mock successful login
        responses.add(
            responses.POST,
            "https://www.smoothcomp.com/en/login",
            status=200,
            json={"success": True}
        )
        
        # Test login
        login_result = client.login()
        assert login_result is True
        assert client.is_authenticated is True
        
        # Test event ID validation
        assert client.validate_event_id("12692") is True
        assert client.validate_event_id("E12692") is True
        assert client.validate_event_id("invalid") is False
        
        # Test cleanup
        client.cleanup()
        assert client.session is None
        assert client.is_authenticated is False
        
        print("✅ SmoothcompClient functionality verified")
    
    @patch('selenium.webdriver.Chrome')
    def test_browser_automation_functionality(self, mock_chrome, components):
        """Test BrowserAutomation functionality."""
        automation = components["browser_automation"]
        
        # Mock Chrome driver
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        # Test browser startup
        start_result = automation.start_browser()
        assert start_result is True
        assert automation.driver == mock_driver
        
        # Test navigation
        navigation_result = automation.navigate_to_event("12692")
        assert navigation_result is True
        mock_driver.get.assert_called_once_with("https://www.smoothcomp.com/en/event/12692")
        
        # Test browser shutdown
        automation.stop_browser()
        mock_driver.quit.assert_called_once()
        assert automation.driver is None
        
        print("✅ BrowserAutomation functionality verified")
    
    def test_file_monitor_functionality(self, components, temp_dirs):
        """Test FileMonitor functionality."""
        monitor = components["file_monitor"]
        
        # Test monitoring start
        start_result = monitor.start_monitoring()
        assert start_result is True
        assert monitor.is_monitoring is True
        
        # Test file detection
        test_file = temp_dirs["watch"] / "test.csv"
        test_file.write_text("test data")
        
        new_files = monitor.detect_new_files()
        assert len(new_files) == 1
        assert new_files[0].name == "test.csv"
        
        # Test file validation
        assert monitor.validate_file_format("test.csv") is True
        assert monitor.validate_file_format("test.txt") is False
        
        # Test file metadata
        metadata = monitor.get_file_metadata(test_file)
        assert metadata["name"] == "test.csv"
        assert metadata["size"] > 0
        assert "created" in metadata
        
        # Test monitoring stop
        monitor.stop_monitoring()
        assert monitor.is_monitoring is False
        
        print("✅ FileMonitor functionality verified")
    
    def test_template_processor_functionality(self, components):
        """Test TemplateProcessor functionality."""
        processor = components["template_processor"]
        
        # Test template creation
        reg_template_result = processor.create_registration_template()
        assert reg_template_result["success"] is True
        assert "template_file" in reg_template_result
        
        match_template_result = processor.create_match_template()
        assert match_template_result["success"] is True
        assert "template_file" in match_template_result
        
        # Test data validation
        valid_reg_data = {
            "name": "John Doe",
            "club": "Test Club",
            "division": "Adult / Advanced / 70kg"
        }
        reg_validation = processor.validate_registration_data(valid_reg_data)
        assert reg_validation["valid"] is True
        
        valid_match_data = {
            "match_id": "M001",
            "winner": "John Doe",
            "loser": "Jane Smith",
            "method": "SUBMISSION"
        }
        match_validation = processor.validate_match_data(valid_match_data)
        assert match_validation["valid"] is True
        
        # Test auto-suggestions
        suggestions = processor.get_auto_suggestions("athlete_name", "Jo")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        print("✅ TemplateProcessor functionality verified")
    
    def test_complete_workflow_simulation(self, components, temp_dirs):
        """Test complete workflow simulation."""
        client = components["smoothcomp_client"]
        automation = components["browser_automation"]
        monitor = components["file_monitor"]
        processor = components["template_processor"]
        
        # Simulate complete workflow
        event_id = "12692"
        
        # 1. Start file monitoring
        monitor.start_monitoring()
        assert monitor.is_monitoring is True
        
        # 2. Create templates
        reg_template = processor.create_registration_template()
        match_template = processor.create_match_template()
        assert reg_template["success"] is True
        assert match_template["success"] is True
        
        # 3. Simulate file download (create test files)
        test_reg_file = temp_dirs["watch"] / "registrations.csv"
        test_reg_file.write_text("Name,Club,Division\nJohn Doe,Test Club,Adult / Advanced / 70kg")
        
        test_match_file = temp_dirs["watch"] / "matches.xlsx"
        test_match_file.write_text("Match ID,Winner,Loser,Method\nM001,John Doe,Jane Smith,SUBMISSION")
        
        # 4. Detect downloaded files
        new_files = monitor.detect_new_files()
        assert len(new_files) == 2
        
        # 5. Process files with templates
        reg_data = [
            {"name": "John Doe", "club": "Test Club", "division": "Adult / Advanced / 70kg"}
        ]
        
        reg_result = processor.process_registration_data(
            reg_data, 
            Path(reg_template["template_file"])
        )
        assert reg_result["success"] is True
        
        # 6. Cleanup
        monitor.stop_monitoring()
        assert monitor.is_monitoring is False
        
        print("✅ Complete workflow simulation successful")
    
    def test_error_handling(self, components):
        """Test error handling across components."""
        client = components["smoothcomp_client"]
        automation = components["browser_automation"]
        monitor = components["file_monitor"]
        processor = components["template_processor"]
        
        # Test invalid event ID
        assert client.validate_event_id("") is False
        assert client.validate_event_id("invalid") is False
        
        # Test invalid registration data
        invalid_reg_data = {
            "name": "John Doe"
            # Missing required fields
        }
        reg_validation = processor.validate_registration_data(invalid_reg_data)
        assert reg_validation["valid"] is False
        assert len(reg_validation["errors"]) > 0
        
        # Test invalid match data
        invalid_match_data = {
            "match_id": "M001"
            # Missing required fields
        }
        match_validation = processor.validate_match_data(invalid_match_data)
        assert match_validation["valid"] is False
        assert len(match_validation["errors"]) > 0
        
        print("✅ Error handling verified")
    
    def test_performance_characteristics(self, components):
        """Test performance characteristics."""
        processor = components["template_processor"]
        
        # Test template creation performance
        import time
        start_time = time.time()
        
        for i in range(10):
            processor.create_registration_template()
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should complete in reasonable time (less than 5 seconds)
        assert creation_time < 5.0
        
        # Test data validation performance
        start_time = time.time()
        
        test_data = {
            "name": "John Doe",
            "club": "Test Club",
            "division": "Adult / Advanced / 70kg"
        }
        
        for i in range(100):
            processor.validate_registration_data(test_data)
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Should complete quickly (less than 1 second)
        assert validation_time < 1.0
        
        print("✅ Performance characteristics verified")
    
    def test_data_integrity(self, components, temp_dirs):
        """Test data integrity across components."""
        processor = components["template_processor"]
        
        # Create template
        template_result = processor.create_registration_template()
        template_file = Path(template_result["template_file"])
        
        # Test data
        original_data = [
            {"name": "John Doe", "club": "Test Club", "division": "Adult / Advanced / 70kg"},
            {"name": "Jane Smith", "club": "Another Club", "division": "Adult / Advanced / 65kg"}
        ]
        
        # Process data
        result = processor.process_registration_data(original_data, template_file)
        assert result["success"] is True
        
        # Verify output file
        output_file = Path(result["output_file"])
        assert output_file.exists()
        
        # Read and verify content
        content = output_file.read_text(encoding='utf-8')
        assert "John Doe" in content
        assert "Jane Smith" in content
        assert "Test Club" in content
        assert "Another Club" in content
        
        print("✅ Data integrity verified")


def run_phase6_verification():
    """Run comprehensive Phase 6 verification."""
    print("🚀 Starting Phase 6 Verification - File Acquisition System")
    print("=" * 60)
    
    # Create test instance
    test_instance = TestPhase6Integration()
    
    # Run all tests
    test_methods = [
        "test_component_initialization",
        "test_smoothcomp_client_functionality", 
        "test_browser_automation_functionality",
        "test_file_monitor_functionality",
        "test_template_processor_functionality",
        "test_complete_workflow_simulation",
        "test_error_handling",
        "test_performance_characteristics",
        "test_data_integrity"
    ]
    
    passed_tests = 0
    total_tests = len(test_methods)
    
    for test_method in test_methods:
        try:
            print(f"\n📋 Running {test_method}...")
            
            # Create fresh temp directories for each test
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dirs = {
                    "download": Path(temp_dir) / "download",
                    "template": Path(temp_dir) / "template", 
                    "output": Path(temp_dir) / "output",
                    "watch": Path(temp_dir) / "watch"
                }
                
                for dir_path in temp_dirs.values():
                    dir_path.mkdir(parents=True, exist_ok=True)
                
                # Run test
                test_func = getattr(test_instance, test_method)
                test_func(temp_dirs)
                passed_tests += 1
                
        except Exception as e:
            print(f"❌ {test_method} failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Phase 6 Verification Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 Phase 6 Verification COMPLETED SUCCESSFULLY!")
        print("✅ All File Acquisition System components working correctly")
        return True
    else:
        print("⚠️  Phase 6 Verification completed with issues")
        print("🔧 Some components may need attention")
        return False


if __name__ == "__main__":
    success = run_phase6_verification()
    exit(0 if success else 1) 