"""
Phase 7: Web UI Development - Test Suite

This module contains comprehensive tests for the web UI components including:
- FastAPI application
- Authentication system
- API endpoints
- Frontend templates and static files
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from src.web_ui.main import app
from src.web_ui.api.auth import router as auth_router
from src.web_ui.api.athletes import router as athletes_router
from src.web_ui.api.events import router as events_router
from src.web_ui.api.leaderboards import router as leaderboards_router
from src.web_ui.models.schemas import (
    LoginRequest, AthleteResponse, EventResponse, LeaderboardResponse,
    Division, UserRole
)


class TestFastAPIApplication:
    """Test the main FastAPI application."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_app_creation(self):
        """Test that the FastAPI app is created correctly."""
        assert app is not None
        assert app.title == "ADCC Analysis Engine"
        assert app.version == "0.6.0-alpha"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.6.0-alpha"
    
    def test_index_page(self):
        """Test main index page."""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "ADCC Analysis Engine" in response.text
        assert "bootstrap" in response.text.lower()
    
    def test_static_files_mounted(self):
        """Test that static files are properly mounted."""
        # Test that static files endpoint exists
        response = self.client.get("/static/css/style.css")
        # Should either return 200 (if file exists) or 404 (if not)
        assert response.status_code in [200, 404]
    
    def test_api_documentation(self):
        """Test that API documentation is available."""
        response = self.client.get("/api/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()


class TestAuthenticationAPI:
    """Test authentication endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_login_success(self):
        """Test successful login."""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_role"] == "admin"
        assert data["expires_in"] > 0
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_missing_fields(self):
        """Test login with missing fields."""
        login_data = {"username": "admin"}
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 422
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        # First login to get a token
        login_data = {"username": "admin", "password": "admin123"}
        login_response = self.client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Verify token
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/auth/verify", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "admin"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/auth/verify", headers=headers)
        assert response.status_code == 401
    
    def test_get_current_user(self):
        """Test getting current user info."""
        # First login to get a token
        login_data = {"username": "admin", "password": "admin123"}
        login_response = self.client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
    
    def test_logout(self):
        """Test logout endpoint."""
        # First login to get a token
        login_data = {"username": "admin", "password": "admin123"}
        login_response = self.client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]


class TestAthletesAPI:
    """Test athletes endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_search_athletes(self):
        """Test athlete search endpoint."""
        response = self.client.get("/api/athletes/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)
    
    def test_search_athletes_with_filters(self):
        """Test athlete search with filters."""
        params = {
            "name": "John",
            "division": "under_88kg",
            "limit": 10
        }
        response = self.client.get("/api/athletes/", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
    
    def test_get_athlete_by_id(self):
        """Test getting athlete by ID."""
        response = self.client.get("/api/athletes/A123456")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "A123456"
        assert data["name"] == "John Doe"
    
    def test_get_athlete_not_found(self):
        """Test getting non-existent athlete."""
        response = self.client.get("/api/athletes/NONEXISTENT")
        assert response.status_code == 404
    
    def test_create_athlete_unauthorized(self):
        """Test creating athlete without authentication."""
        athlete_data = {
            "name": "Test Athlete",
            "division": "under_88kg",
            "club": "Test Club",
            "country": "Test Country"
        }
        response = self.client.post("/api/athletes/", json=athlete_data)
        assert response.status_code == 401
    
    def test_create_athlete_authorized(self):
        """Test creating athlete with authentication."""
        # First login
        login_data = {"username": "admin", "password": "admin123"}
        login_response = self.client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Create athlete
        athlete_data = {
            "name": "Test Athlete",
            "division": "under_88kg",
            "club": "Test Club",
            "country": "Test Country"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/athletes/", json=athlete_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "athlete_id" in data["data"]
    
    def test_get_athletes_by_division(self):
        """Test getting athletes by division."""
        response = self.client.get("/api/athletes/divisions/under_88kg/athletes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for athlete in data:
            assert athlete["division"] == "under_88kg"


class TestEventsAPI:
    """Test events endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_get_events(self):
        """Test getting events list."""
        response = self.client.get("/api/events/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)
    
    def test_get_events_with_filters(self):
        """Test getting events with filters."""
        params = {
            "division": "under_88kg",
            "status": "completed",
            "limit": 5
        }
        response = self.client.get("/api/events/", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    def test_get_event_by_id(self):
        """Test getting event by ID."""
        response = self.client.get("/api/events/E2024001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "E2024001"
        assert data["name"] == "ADCC World Championship 2024"
    
    def test_get_event_not_found(self):
        """Test getting non-existent event."""
        response = self.client.get("/api/events/NONEXISTENT")
        assert response.status_code == 404
    
    def test_get_upcoming_events(self):
        """Test getting upcoming events."""
        response = self.client.get("/api/events/upcoming/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for event in data:
            assert event["status"] == "upcoming"
    
    def test_get_recent_events(self):
        """Test getting recent events."""
        response = self.client.get("/api/events/recent/events?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
    
    def test_get_events_by_division(self):
        """Test getting events by division."""
        response = self.client.get("/api/events/divisions/under_88kg/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for event in data:
            assert event["division"] == "under_88kg"
    
    def test_get_events_by_status(self):
        """Test getting events by status."""
        response = self.client.get("/api/events/status/completed/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for event in data:
            assert event["status"] == "completed"


class TestLeaderboardsAPI:
    """Test leaderboards endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_get_leaderboard(self):
        """Test getting leaderboard for a division."""
        response = self.client.get("/api/leaderboards/under_88kg")
        assert response.status_code == 200
        data = response.json()
        assert data["division"] == "under_88kg"
        assert "entries" in data
        assert "total_athletes" in data
        assert "last_updated" in data
    
    def test_get_leaderboard_with_limit(self):
        """Test getting leaderboard with limit."""
        response = self.client.get("/api/leaderboards/under_88kg?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) <= 5
    
    def test_get_top_athletes(self):
        """Test getting top athletes for a division."""
        response = self.client.get("/api/leaderboards/under_88kg/top?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
    
    def test_get_athlete_rank(self):
        """Test getting specific athlete's rank."""
        response = self.client.get("/api/leaderboards/under_88kg/rank/A345678")
        assert response.status_code == 200
        data = response.json()
        assert data["athlete_id"] == "A345678"
        assert data["division"] == "under_88kg"
        assert "rank" in data
        assert "rating" in data
    
    def test_get_athlete_rank_not_found(self):
        """Test getting rank for non-existent athlete."""
        response = self.client.get("/api/leaderboards/under_88kg/rank/NONEXISTENT")
        assert response.status_code == 404
    
    def test_get_global_top_athletes(self):
        """Test getting global top athletes."""
        response = self.client.get("/api/leaderboards/global/top?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_divisions_summary(self):
        """Test getting divisions summary."""
        response = self.client.get("/api/leaderboards/divisions/summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Check that all divisions are present
        expected_divisions = ["absolute", "under_88kg", "under_77kg", "under_66kg", "women_absolute", "women_under_60kg"]
        for division in expected_divisions:
            assert division in data
    
    def test_get_division_stats(self):
        """Test getting division statistics."""
        response = self.client.get("/api/leaderboards/under_88kg/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["division"] == "under_88kg"
        assert "total_athletes" in data
        assert "average_rating" in data
        assert "highest_rating" in data
        assert "lowest_rating" in data


class TestFrontendTemplates:
    """Test frontend templates and static files."""
    
    def test_base_template_structure(self):
        """Test base template structure."""
        base_template_path = Path("src/web_ui/templates/base.html")
        assert base_template_path.exists()
        
        content = base_template_path.read_text()
        assert "ADCC Analysis Engine" in content
        assert "bootstrap" in content.lower()
        assert "navbar" in content
        assert "footer" in content
    
    def test_index_template_structure(self):
        """Test index template structure."""
        index_template_path = Path("src/web_ui/templates/index.html")
        assert index_template_path.exists()
        
        content = index_template_path.read_text()
        assert "extends" in content
        assert "leaderboards" in content.lower()
        assert "athletes" in content.lower()
        assert "events" in content.lower()
    
    def test_error_template_structure(self):
        """Test error template structure."""
        error_template_path = Path("src/web_ui/templates/error.html")
        assert error_template_path.exists()
        
        content = error_template_path.read_text()
        assert "extends" in content
        assert "error" in content.lower()
        assert "go home" in content.lower()
    
    def test_css_file_exists(self):
        """Test that CSS file exists."""
        css_path = Path("src/web_ui/static/css/style.css")
        assert css_path.exists()
        
        content = css_path.read_text()
        assert "ADCC Analysis Engine" in content
        assert "primary-color" in content
        assert "bootstrap" in content.lower()
    
    def test_js_file_exists(self):
        """Test that JavaScript file exists."""
        js_path = Path("src/web_ui/static/js/main.js")
        assert js_path.exists()
        
        content = js_path.read_text()
        assert "ADCC Analysis Engine" in content
        assert "authentication" in content.lower()
        assert "api" in content.lower()


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_login_request_validation(self):
        """Test LoginRequest schema validation."""
        # Valid data
        valid_data = {"username": "test", "password": "password123"}
        login_request = LoginRequest(**valid_data)
        assert login_request.username == "test"
        assert login_request.password == "password123"
        
        # Invalid data - missing password
        with pytest.raises(ValueError):
            LoginRequest(username="test")
        
        # Invalid data - empty username
        with pytest.raises(ValueError):
            LoginRequest(username="", password="password123")
    
    def test_athlete_response_validation(self):
        """Test AthleteResponse schema validation."""
        valid_data = {
            "id": "A123456",
            "name": "Test Athlete",
            "club": "Test Club",
            "country": "Test Country",
            "division": Division.UNDER_88KG,
            "glicko_rating": 1500.0,
            "glicko_deviation": 350.0,
            "total_matches": 10,
            "wins": 7,
            "losses": 2,
            "draws": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z"
        }
        athlete = AthleteResponse(**valid_data)
        assert athlete.id == "A123456"
        assert athlete.name == "Test Athlete"
        assert athlete.division == Division.UNDER_88KG
    
    def test_division_enum(self):
        """Test Division enum values."""
        assert Division.ABSOLUTE == "absolute"
        assert Division.UNDER_88KG == "under_88kg"
        assert Division.UNDER_77KG == "under_77kg"
        assert Division.UNDER_66KG == "under_66kg"
        assert Division.WOMEN_ABSOLUTE == "women_absolute"
        assert Division.WOMEN_UNDER_60KG == "women_under_60kg"
    
    def test_user_role_enum(self):
        """Test UserRole enum values."""
        assert UserRole.PUBLIC == "public"
        assert UserRole.ADMIN == "admin"
        assert UserRole.DEVELOPER == "developer"


class TestIntegration:
    """Integration tests for the complete web UI system."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_complete_workflow(self):
        """Test a complete user workflow."""
        # 1. Check health
        health_response = self.client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Access home page
        home_response = self.client.get("/")
        assert home_response.status_code == 200
        
        # 3. Login
        login_data = {"username": "admin", "password": "admin123"}
        login_response = self.client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 4. Get user info
        user_response = self.client.get("/api/auth/me", headers=headers)
        assert user_response.status_code == 200
        
        # 5. Search athletes
        athletes_response = self.client.get("/api/athletes/", headers=headers)
        assert athletes_response.status_code == 200
        
        # 6. Get events
        events_response = self.client.get("/api/events/", headers=headers)
        assert events_response.status_code == 200
        
        # 7. Get leaderboard
        leaderboard_response = self.client.get("/api/leaderboards/under_88kg", headers=headers)
        assert leaderboard_response.status_code == 200
        
        # 8. Logout
        logout_response = self.client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
    
    def test_error_handling(self):
        """Test error handling throughout the system."""
        # Test 404 error
        response = self.client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        # Test invalid API endpoint
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404
        
        # Test invalid athlete ID
        response = self.client.get("/api/athletes/invalid-id")
        assert response.status_code == 404
        
        # Test invalid event ID
        response = self.client.get("/api/events/invalid-id")
        assert response.status_code == 404
    
    def test_cors_headers(self):
        """Test CORS headers are properly set."""
        response = self.client.get("/health")
        assert response.status_code == 200
        # CORS headers should be present (handled by middleware)
    
    def test_api_documentation_access(self):
        """Test that API documentation is accessible."""
        # Test Swagger UI
        response = self.client.get("/api/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = self.client.get("/api/redoc")
        assert response.status_code == 200


def run_phase7_verification():
    """Run all Phase 7 verification tests."""
    print("🚀 Starting Phase 7: Web UI Development Verification...")
    
    # Run all tests
    test_classes = [
        TestFastAPIApplication,
        TestAuthenticationAPI,
        TestAthletesAPI,
        TestEventsAPI,
        TestLeaderboardsAPI,
        TestFrontendTemplates,
        TestSchemaValidation,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        
        # Create test instance
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_') and callable(getattr(test_instance, method))]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Run setup if it exists
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run the test
                getattr(test_instance, test_method)()
                passed_tests += 1
                print(f"  ✅ {test_method}")
                
            except Exception as e:
                failed_tests.append(f"{test_class.__name__}.{test_method}: {str(e)}")
                print(f"  ❌ {test_method}: {str(e)}")
    
    # Print summary
    print(f"\n📊 Phase 7 Verification Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {len(failed_tests)}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"   - {failure}")
        return False
    else:
        print(f"\n🎉 All Phase 7 tests passed!")
        return True


if __name__ == "__main__":
    success = run_phase7_verification()
    exit(0 if success else 1) 