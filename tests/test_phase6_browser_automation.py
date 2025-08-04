"""
Test suite for Phase 6.2: Browser Automation
Tests the browser_automation.py and file_monitor.py modules.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import time

from src.data_acquisition.browser_automation import BrowserAutomation
from src.data_acquisition.file_monitor import FileMonitor


class TestBrowserAutomation:
    """Test cases for BrowserAutomation class."""
    
    @pytest.fixture
    def automation(self):
        """Create a test browser automation instance."""
        return BrowserAutomation(
            download_dir=Path("/tmp/test_downloads"),
            headless=True
        )
    
    @pytest.fixture
    def temp_download_dir(self):
        """Create a temporary download directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_download_dir):
        """Test browser automation initialization."""
        automation = BrowserAutomation(
            download_dir=temp_download_dir,
            headless=True
        )
        
        assert automation.download_dir == temp_download_dir
        assert automation.headless is True
        assert automation.driver is None
    
    @patch('selenium.webdriver.Chrome')
    def test_start_browser(self, mock_chrome, automation):
        """Test browser startup."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        result = automation.start_browser()
        
        assert result is True
        assert automation.driver == mock_driver
        mock_chrome.assert_called_once()
    
    @patch('selenium.webdriver.Chrome')
    def test_start_browser_failure(self, mock_chrome, automation):
        """Test browser startup failure."""
        mock_chrome.side_effect = Exception("Chrome driver error")
        
        result = automation.start_browser()
        
        assert result is False
        assert automation.driver is None
    
    def test_stop_browser(self, automation):
        """Test browser shutdown."""
        # Mock driver
        mock_driver = Mock()
        automation.driver = mock_driver
        
        automation.stop_browser()
        
        mock_driver.quit.assert_called_once()
        assert automation.driver is None
    
    def test_stop_browser_no_driver(self, automation):
        """Test browser shutdown when no driver exists."""
        automation.driver = None
        
        # Should not raise an exception
        automation.stop_browser()
        assert automation.driver is None
    
    @patch('selenium.webdriver.Chrome')
    def test_navigate_to_event(self, mock_chrome, automation):
        """Test navigation to event page."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        automation.driver = mock_driver
        
        event_id = "12692"
        result = automation.navigate_to_event(event_id)
        
        assert result is True
        mock_driver.get.assert_called_once_with(
            f"https://www.smoothcomp.com/en/event/{event_id}"
        )
    
    @patch('selenium.webdriver.Chrome')
    def test_navigate_to_event_failure(self, mock_chrome, automation):
        """Test navigation failure."""
        mock_driver = Mock()
        mock_driver.get.side_effect = Exception("Navigation error")
        mock_chrome.return_value = mock_driver
        automation.driver = mock_driver
        
        event_id = "12692"
        result = automation.navigate_to_event(event_id)
        
        assert result is False
    
    @patch('selenium.webdriver.Chrome')
    def test_download_registrations(self, mock_chrome, automation, temp_download_dir):
        """Test downloading registration data."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        automation.driver = mock_driver
        automation.download_dir = temp_download_dir
        
        event_id = "12692"
        result = automation.download_registrations(event_id)
        
        assert result["success"] is True
        # Verify that the download button was clicked
        # This would depend on the actual page structure
    
    @patch('selenium.webdriver.Chrome')
    def test_download_matches(self, mock_chrome, automation, temp_download_dir):
        """Test downloading match data."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        automation.driver = mock_driver
        automation.download_dir = temp_download_dir
        
        event_id = "12692"
        result = automation.download_matches(event_id)
        
        assert result["success"] is True
    
    @patch('selenium.webdriver.Chrome')
    def test_wait_for_download(self, mock_chrome, automation, temp_download_dir):
        """Test waiting for file download."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        automation.driver = mock_driver
        automation.download_dir = temp_download_dir
        
        # Create a test file to simulate download
        test_file = temp_download_dir / "test_file.csv"
        test_file.write_text("test data")
        
        result = automation.wait_for_download("test_file.csv", timeout=5)
        
        assert result is True
    
    def test_wait_for_download_timeout(self, automation, temp_download_dir):
        """Test download timeout."""
        automation.download_dir = temp_download_dir
        
        result = automation.wait_for_download("nonexistent_file.csv", timeout=1)
        
        assert result is False


class TestFileMonitor:
    """Test cases for FileMonitor class."""
    
    @pytest.fixture
    def monitor(self, temp_download_dir):
        """Create a test file monitor instance."""
        return FileMonitor(
            watch_directory=temp_download_dir,
            file_patterns=["*.csv", "*.xlsx"]
        )
    
    @pytest.fixture
    def temp_download_dir(self):
        """Create a temporary download directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_download_dir):
        """Test file monitor initialization."""
        monitor = FileMonitor(
            watch_directory=temp_download_dir,
            file_patterns=["*.csv", "*.xlsx"]
        )
        
        assert monitor.watch_directory == temp_download_dir
        assert monitor.file_patterns == ["*.csv", "*.xlsx"]
        assert monitor.detected_files == []
    
    def test_start_monitoring(self, monitor):
        """Test starting file monitoring."""
        result = monitor.start_monitoring()
        
        assert result is True
        assert monitor.is_monitoring is True
    
    def test_stop_monitoring(self, monitor):
        """Test stopping file monitoring."""
        monitor.is_monitoring = True
        
        monitor.stop_monitoring()
        
        assert monitor.is_monitoring is False
    
    def test_detect_new_files(self, monitor, temp_download_dir):
        """Test detecting new files."""
        # Create a test file
        test_file = temp_download_dir / "test.csv"
        test_file.write_text("test data")
        
        detected_files = monitor.detect_new_files()
        
        assert len(detected_files) == 1
        assert "test.csv" in [f.name for f in detected_files]
    
    def test_move_file_to_processed(self, monitor, temp_download_dir):
        """Test moving file to processed directory."""
        # Create test directories
        processed_dir = temp_download_dir / "processed"
        processed_dir.mkdir()
        
        # Create a test file
        test_file = temp_download_dir / "test.csv"
        test_file.write_text("test data")
        
        result = monitor.move_file_to_processed(test_file, processed_dir)
        
        assert result is True
        assert not test_file.exists()
        assert (processed_dir / "test.csv").exists()
    
    def test_validate_file_format(self, monitor):
        """Test file format validation."""
        # Valid CSV file
        assert monitor.validate_file_format("test.csv") is True
        assert monitor.validate_file_format("test.xlsx") is True
        
        # Invalid file
        assert monitor.validate_file_format("test.txt") is False
    
    def test_get_file_metadata(self, monitor, temp_download_dir):
        """Test getting file metadata."""
        # Create a test file
        test_file = temp_download_dir / "test.csv"
        test_file.write_text("test data")
        
        metadata = monitor.get_file_metadata(test_file)
        
        assert metadata["name"] == "test.csv"
        assert metadata["size"] > 0
        assert "created" in metadata
        assert "modified" in metadata


class TestBrowserAutomationIntegration:
    """Integration tests for browser automation."""
    
    @pytest.fixture
    def automation(self, temp_download_dir):
        """Create a test browser automation instance."""
        return BrowserAutomation(
            download_dir=temp_download_dir,
            headless=True
        )
    
    @pytest.fixture
    def monitor(self, temp_download_dir):
        """Create a test file monitor instance."""
        return FileMonitor(
            watch_directory=temp_download_dir,
            file_patterns=["*.csv", "*.xlsx"]
        )
    
    @pytest.fixture
    def temp_download_dir(self):
        """Create a temporary download directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @patch('selenium.webdriver.Chrome')
    def test_complete_download_workflow(self, mock_chrome, automation, monitor):
        """Test complete download workflow."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        automation.driver = mock_driver
        
        event_id = "12692"
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Navigate and download
        navigation_result = automation.navigate_to_event(event_id)
        download_result = automation.download_registrations(event_id)
        
        # Check for new files
        detected_files = monitor.detect_new_files()
        
        # Stop monitoring
        monitor.stop_monitoring()
        automation.stop_browser()
        
        assert navigation_result is True
        assert download_result["success"] is True
        assert monitor.is_monitoring is False
        assert automation.driver is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 