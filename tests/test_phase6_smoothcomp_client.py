"""
Test suite for Phase 6.1: Smoothcomp API Client
Tests the smoothcomp_client.py module functionality.
"""

import pytest
import responses
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import shutil

from src.data_acquisition.smoothcomp_client import SmoothcompClient
from src.config.settings import get_settings


class TestSmoothcompClient:
    """Test cases for SmoothcompClient class."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        settings = get_settings()
        return SmoothcompClient(
            username=settings.smoothcomp_username or "test_user",
            password=settings.smoothcomp_password or "test_pass"
        )
    
    @pytest.fixture
    def temp_download_dir(self):
        """Create a temporary download directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_client_initialization(self, client):
        """Test client initialization with credentials."""
        assert client.username == "test_user"
        assert client.password == "test_pass"
        assert client.session is not None
        assert client.base_url == "https://www.smoothcomp.com"
    
    @responses.activate
    def test_successful_login(self, client):
        """Test successful login to Smoothcomp."""
        # Mock login response
        responses.add(
            responses.POST,
            "https://www.smoothcomp.com/en/login",
            status=200,
            json={"success": True}
        )
        
        result = client.login()
        assert result is True
        assert client.is_authenticated is True
    
    @responses.activate
    def test_failed_login(self, client):
        """Test failed login handling."""
        # Mock failed login response
        responses.add(
            responses.POST,
            "https://www.smoothcomp.com/en/login",
            status=401,
            json={"error": "Invalid credentials"}
        )
        
        result = client.login()
        assert result is False
        assert client.is_authenticated is False
    
    @responses.activate
    def test_get_event_registrations(self, client, temp_download_dir):
        """Test downloading event registration data."""
        event_id = "12692"
        
        # Mock successful login
        responses.add(
            responses.POST,
            "https://www.smoothcomp.com/en/login",
            status=200,
            json={"success": True}
        )
        
        # Mock registration data response
        mock_registration_data = [
            {
                "id": 12345,
                "name": "John Doe",
                "club": "Test Club",
                "division": "Adult / Advanced / 70kg"
            }
        ]
        
        responses.add(
            responses.GET,
            f"https://www.smoothcomp.com/en/event/{event_id}/registrations",
            status=200,
            json=mock_registration_data
        )
        
        result = client.get_event_registrations(event_id, temp_download_dir)
        assert result["success"] is True
        assert "registrations.csv" in result["files"]
        assert Path(temp_download_dir / "registrations.csv").exists()
    
    @responses.activate
    def test_get_event_matches(self, client, temp_download_dir):
        """Test downloading event match data."""
        event_id = "12692"
        
        # Mock successful login
        responses.add(
            responses.POST,
            "https://www.smoothcomp.com/en/login",
            status=200,
            json={"success": True}
        )
        
        # Mock match data response
        mock_match_data = [
            {
                "match_id": 1,
                "winner": "John Doe",
                "loser": "Jane Smith",
                "method": "SUBMISSION",
                "time": "2:30"
            }
        ]
        
        responses.add(
            responses.GET,
            f"https://www.smoothcomp.com/en/event/{event_id}/matches",
            status=200,
            json=mock_match_data
        )
        
        result = client.get_event_matches(event_id, temp_download_dir)
        assert result["success"] is True
        assert "matches.xlsx" in result["files"]
        assert Path(temp_download_dir / "matches.xlsx").exists()
    
    @responses.activate
    def test_get_event_info(self, client):
        """Test retrieving event information."""
        event_id = "12692"
        
        # Mock successful login
        responses.add(
            responses.POST,
            "https://www.smoothcomp.com/en/login",
            status=200,
            json={"success": True}
        )
        
        # Mock event info response
        mock_event_info = {
            "id": event_id,
            "name": "ADCC European Championship 2024",
            "date": "2024-03-15",
            "location": "London, UK"
        }
        
        responses.add(
            responses.GET,
            f"https://www.smoothcomp.com/en/event/{event_id}",
            status=200,
            json=mock_event_info
        )
        
        result = client.get_event_info(event_id)
        assert result["success"] is True
        assert result["data"]["name"] == "ADCC European Championship 2024"
    
    def test_validate_event_id(self, client):
        """Test event ID validation."""
        # Valid event ID
        assert client.validate_event_id("12692") is True
        assert client.validate_event_id("E12692") is True
        
        # Invalid event IDs
        assert client.validate_event_id("") is False
        assert client.validate_event_id("invalid") is False
        assert client.validate_event_id("12.34") is False
    
    @responses.activate
    def test_handle_api_error(self, client):
        """Test API error handling."""
        # Mock API error response
        responses.add(
            responses.GET,
            "https://www.smoothcomp.com/en/event/99999",
            status=404,
            json={"error": "Event not found"}
        )
        
        result = client.get_event_info("99999")
        assert result["success"] is False
        assert "error" in result
        assert "Event not found" in result["error"]
    
    def test_save_data_to_file(self, client, temp_download_dir):
        """Test saving data to file."""
        test_data = [{"name": "Test", "value": 123}]
        filename = "test_data.csv"
        
        result = client._save_data_to_file(test_data, filename, temp_download_dir)
        assert result["success"] is True
        assert Path(temp_download_dir / filename).exists()
    
    def test_cleanup_session(self, client):
        """Test session cleanup."""
        client.cleanup()
        assert client.session is None
        assert client.is_authenticated is False


class TestSmoothcompClientIntegration:
    """Integration tests for SmoothcompClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        settings = get_settings()
        return SmoothcompClient(
            username=settings.smoothcomp_username or "test_user",
            password=settings.smoothcomp_password or "test_pass"
        )
    
    @responses.activate
    def test_complete_event_download_workflow(self, client, temp_download_dir):
        """Test complete workflow of downloading event data."""
        event_id = "12692"
        
        # Mock all API responses
        responses.add(
            responses.POST,
            "https://www.smoothcomp.com/en/login",
            status=200,
            json={"success": True}
        )
        
        responses.add(
            responses.GET,
            f"https://www.smoothcomp.com/en/event/{event_id}",
            status=200,
            json={"id": event_id, "name": "Test Event"}
        )
        
        responses.add(
            responses.GET,
            f"https://www.smoothcomp.com/en/event/{event_id}/registrations",
            status=200,
            json=[{"id": 1, "name": "Test Athlete"}]
        )
        
        responses.add(
            responses.GET,
            f"https://www.smoothcomp.com/en/event/{event_id}/matches",
            status=200,
            json=[{"match_id": 1, "winner": "Test Athlete"}]
        )
        
        # Test complete workflow
        result = client.download_complete_event(event_id, temp_download_dir)
        
        assert result["success"] is True
        assert "event_info.json" in result["files"]
        assert "registrations.csv" in result["files"]
        assert "matches.xlsx" in result["files"]
        
        # Verify files exist
        for filename in result["files"]:
            assert Path(temp_download_dir / filename).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 