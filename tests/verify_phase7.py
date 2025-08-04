"""
Phase 7: Web UI Development - Comprehensive Verification

This script provides comprehensive verification of all Phase 7 components:
- FastAPI application setup
- Authentication system
- API endpoints (athletes, events, leaderboards)
- Frontend templates and static files
- Integration testing
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_file_exists(file_path, description):
    """Check if a file exists and return status."""
    path = Path(file_path)
    exists = path.exists()
    print(f"  {'✅' if exists else '❌'} {description}: {file_path}")
    return exists

def check_directory_structure():
    """Check the web UI directory structure."""
    print("\n📁 Checking Web UI Directory Structure...")
    
    required_files = [
        ("src/web_ui/main.py", "FastAPI Main Application"),
        ("src/web_ui/models/schemas.py", "Pydantic Schemas"),
        ("src/web_ui/api/auth.py", "Authentication API"),
        ("src/web_ui/api/athletes.py", "Athletes API"),
        ("src/web_ui/api/events.py", "Events API"),
        ("src/web_ui/api/leaderboards.py", "Leaderboards API"),
        ("src/web_ui/templates/base.html", "Base Template"),
        ("src/web_ui/templates/index.html", "Index Template"),
        ("src/web_ui/templates/error.html", "Error Template"),
        ("src/web_ui/static/css/style.css", "Main CSS"),
        ("src/web_ui/static/js/main.js", "Main JavaScript"),
        ("tests/test_phase7_web_ui.py", "Phase 7 Test Suite")
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_imports():
    """Check that all modules can be imported."""
    print("\n📦 Checking Module Imports...")
    
    try:
        from src.web_ui.main import app
        print("  ✅ FastAPI app imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import FastAPI app: {e}")
        return False
    
    try:
        from src.web_ui.models.schemas import (
            LoginRequest, AthleteResponse, EventResponse, 
            LeaderboardResponse, Division, UserRole
        )
        print("  ✅ Pydantic schemas imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import schemas: {e}")
        return False
    
    try:
        from src.web_ui.api.auth import router as auth_router
        from src.web_ui.api.athletes import router as athletes_router
        from src.web_ui.api.events import router as events_router
        from src.web_ui.api.leaderboards import router as leaderboards_router
        print("  ✅ API routers imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import API routers: {e}")
        return False
    
    return True

def check_fastapi_app():
    """Check FastAPI application configuration."""
    print("\n🚀 Checking FastAPI Application...")
    
    try:
        from src.web_ui.main import app
        
        # Check app metadata
        assert app.title == "ADCC Analysis Engine"
        assert app.version == "0.6.0-alpha"
        print("  ✅ App metadata configured correctly")
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/api/docs", "/api/redoc"]
        for route in expected_routes:
            if route in routes:
                print(f"  ✅ Route {route} found")
            else:
                print(f"  ❌ Route {route} missing")
                return False
        
        print("  ✅ FastAPI application configured correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ FastAPI app check failed: {e}")
        return False

def check_authentication_system():
    """Check authentication system."""
    print("\n🔐 Checking Authentication System...")
    
    try:
        from src.web_ui.api.auth import (
            authenticate_user, create_access_token, verify_token,
            get_current_user, get_current_admin_user
        )
        print("  ✅ Authentication functions imported")
        
        # Test user authentication
        from src.web_ui.api.auth import MOCK_USERS
        assert "admin" in MOCK_USERS
        assert "developer" in MOCK_USERS
        print("  ✅ Mock users configured")
        
        # Test password verification
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        test_password = "test123"
        hashed = pwd_context.hash(test_password)
        assert pwd_context.verify(test_password, hashed)
        print("  ✅ Password hashing working")
        
        print("  ✅ Authentication system configured correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Authentication system check failed: {e}")
        return False

def check_api_endpoints():
    """Check API endpoints."""
    print("\n🔗 Checking API Endpoints...")
    
    try:
        from src.web_ui.api.athletes import MOCK_ATHLETES
        from src.web_ui.api.events import MOCK_EVENTS
        from src.web_ui.api.leaderboards import MOCK_LEADERBOARD_DATA
        
        # Check mock data
        assert len(MOCK_ATHLETES) > 0
        assert len(MOCK_EVENTS) > 0
        assert len(MOCK_LEADERBOARD_DATA) > 0
        print("  ✅ Mock data configured")
        
        # Check API functions
        from src.web_ui.api.athletes import search_athletes, get_athlete_by_id
        from src.web_ui.api.events import get_events_by_filters, get_event_by_id
        from src.web_ui.api.leaderboards import generate_leaderboard
        
        print("  ✅ API functions imported")
        
        # Test athlete search
        from src.web_ui.models.schemas import AthleteQuery
        query = AthleteQuery(name="John", limit=10)
        athletes = search_athletes(query)
        assert isinstance(athletes, list)
        print("  ✅ Athlete search working")
        
        # Test event filters
        events = get_events_by_filters(limit=5)
        assert isinstance(events, list)
        print("  ✅ Event filters working")
        
        # Test leaderboard generation
        from src.web_ui.models.schemas import Division
        leaderboard = generate_leaderboard(Division.UNDER_88KG, limit=5)
        assert isinstance(leaderboard, list)
        print("  ✅ Leaderboard generation working")
        
        print("  ✅ API endpoints configured correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ API endpoints check failed: {e}")
        return False

def check_frontend_templates():
    """Check frontend templates."""
    print("\n🎨 Checking Frontend Templates...")
    
    try:
        # Check base template
        base_template = Path("src/web_ui/templates/base.html")
        content = base_template.read_text()
        
        required_elements = [
            "ADCC Analysis Engine",
            "bootstrap",
            "navbar",
            "footer",
            "loginModal"
        ]
        
        for element in required_elements:
            if element.lower() in content.lower():
                print(f"  ✅ Base template contains {element}")
            else:
                print(f"  ❌ Base template missing {element}")
                return False
        
        # Check index template
        index_template = Path("src/web_ui/templates/index.html")
        content = index_template.read_text()
        
        required_elements = [
            "extends",
            "leaderboards",
            "athletes",
            "events"
        ]
        
        for element in required_elements:
            if element.lower() in content.lower():
                print(f"  ✅ Index template contains {element}")
            else:
                print(f"  ❌ Index template missing {element}")
                return False
        
        # Check error template
        error_template = Path("src/web_ui/templates/error.html")
        content = error_template.read_text()
        
        if "error" in content.lower() and "go home" in content.lower():
            print("  ✅ Error template configured")
        else:
            print("  ❌ Error template missing required elements")
            return False
        
        print("  ✅ Frontend templates configured correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Frontend templates check failed: {e}")
        return False

def check_static_files():
    """Check static files."""
    print("\n📄 Checking Static Files...")
    
    try:
        # Check CSS
        css_file = Path("src/web_ui/static/css/style.css")
        css_content = css_file.read_text()
        
        required_css = [
            "ADCC Analysis Engine",
            "primary-color",
            "bootstrap"
        ]
        
        for element in required_css:
            if element.lower() in css_content.lower():
                print(f"  ✅ CSS contains {element}")
            else:
                print(f"  ❌ CSS missing {element}")
                return False
        
        # Check JavaScript
        js_file = Path("src/web_ui/static/js/main.js")
        js_content = js_file.read_text()
        
        required_js = [
            "ADCC Analysis Engine",
            "authentication",
            "api"
        ]
        
        for element in required_js:
            if element.lower() in js_content.lower():
                print(f"  ✅ JavaScript contains {element}")
            else:
                print(f"  ❌ JavaScript missing {element}")
                return False
        
        print("  ✅ Static files configured correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Static files check failed: {e}")
        return False

def check_schema_validation():
    """Check Pydantic schema validation."""
    print("\n📋 Checking Schema Validation...")
    
    try:
        from src.web_ui.models.schemas import (
            LoginRequest, AthleteResponse, Division, UserRole
        )
        
        # Test LoginRequest validation
        valid_login = LoginRequest(username="test", password="password123")
        assert valid_login.username == "test"
        print("  ✅ LoginRequest validation working")
        
        # Test Division enum
        assert Division.ABSOLUTE == "absolute"
        assert Division.UNDER_88KG == "under_88kg"
        print("  ✅ Division enum working")
        
        # Test UserRole enum
        assert UserRole.ADMIN == "admin"
        assert UserRole.DEVELOPER == "developer"
        print("  ✅ UserRole enum working")
        
        # Test AthleteResponse validation
        athlete_data = {
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
        athlete = AthleteResponse(**athlete_data)
        assert athlete.id == "A123456"
        print("  ✅ AthleteResponse validation working")
        
        print("  ✅ Schema validation configured correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Schema validation check failed: {e}")
        return False

def run_unit_tests():
    """Run the unit tests."""
    print("\n🧪 Running Unit Tests...")
    
    try:
        # Import and run test functions
        from tests.test_phase7_web_ui import (
            TestFastAPIApplication, TestAuthenticationAPI,
            TestAthletesAPI, TestEventsAPI, TestLeaderboardsAPI
        )
        
        # Test FastAPI app
        test_app = TestFastAPIApplication()
        test_app.setup_method()
        test_app.test_app_creation()
        test_app.test_health_check()
        print("  ✅ FastAPI application tests passed")
        
        # Test authentication
        test_auth = TestAuthenticationAPI()
        test_auth.setup_method()
        test_auth.test_login_success()
        test_auth.test_login_invalid_credentials()
        print("  ✅ Authentication tests passed")
        
        # Test athletes API
        test_athletes = TestAthletesAPI()
        test_athletes.setup_method()
        test_athletes.test_search_athletes()
        test_athletes.test_get_athlete_by_id()
        print("  ✅ Athletes API tests passed")
        
        # Test events API
        test_events = TestEventsAPI()
        test_events.setup_method()
        test_events.test_get_events()
        test_events.test_get_event_by_id()
        print("  ✅ Events API tests passed")
        
        # Test leaderboards API
        test_leaderboards = TestLeaderboardsAPI()
        test_leaderboards.setup_method()
        test_leaderboards.test_get_leaderboard()
        test_leaderboards.test_get_top_athletes()
        print("  ✅ Leaderboards API tests passed")
        
        print("  ✅ All unit tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Unit tests failed: {e}")
        return False

def generate_report(results):
    """Generate a comprehensive report."""
    print("\n" + "="*60)
    print("📊 PHASE 7: WEB UI DEVELOPMENT - VERIFICATION REPORT")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"\n📈 Summary:")
    print(f"   Total Checks: {total_checks}")
    print(f"   Passed: {passed_checks}")
    print(f"   Failed: {total_checks - passed_checks}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n🎉 Phase 7 VERIFICATION SUCCESSFUL!")
        print(f"   The Web UI Development phase is complete and ready for production.")
    elif success_rate >= 75:
        print(f"\n⚠️  Phase 7 VERIFICATION PARTIAL SUCCESS")
        print(f"   Most components are working, but some issues need attention.")
    else:
        print(f"\n❌ Phase 7 VERIFICATION FAILED")
        print(f"   Multiple issues detected. Review and fix before proceeding.")
    
    print(f"\n📅 Verification completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return success_rate >= 90

def main():
    """Main verification function."""
    print("🚀 Starting Phase 7: Web UI Development Verification...")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run all checks
    results["Directory Structure"] = check_directory_structure()
    results["Module Imports"] = check_imports()
    results["FastAPI Application"] = check_fastapi_app()
    results["Authentication System"] = check_authentication_system()
    results["API Endpoints"] = check_api_endpoints()
    results["Frontend Templates"] = check_frontend_templates()
    results["Static Files"] = check_static_files()
    results["Schema Validation"] = check_schema_validation()
    results["Unit Tests"] = run_unit_tests()
    
    # Generate report
    success = generate_report(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 