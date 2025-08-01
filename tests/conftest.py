"""
Pytest configuration for ADCC Analysis Engine v0.6
Shared fixtures and test configuration.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

# Import test template
from tests.fixtures.test_template import TestTemplate


@pytest.fixture(scope="session")
def test_root() -> Generator[Path, None, None]:
    """
    Create a temporary test root directory for the entire test session.
    
    Returns:
        Path to the test root directory
    """
    test_dir = Path(tempfile.mkdtemp(prefix="adcc_test_session_"))
    
    # Create test directory structure
    (test_dir / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (test_dir / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (test_dir / "data" / "datastore").mkdir(parents=True, exist_ok=True)
    (test_dir / "logs").mkdir(exist_ok=True)
    
    yield test_dir
    
    # Cleanup
    shutil.rmtree(test_dir)


@pytest.fixture(scope="function")
def test_environment(test_root: Path) -> Generator[Path, None, None]:
    """
    Create a clean test environment for each test function.
    
    Args:
        test_root: Session-level test root directory
        
    Returns:
        Path to the test environment directory
    """
    # Create a unique subdirectory for this test
    test_env = test_root / f"test_{pytest.current_test_name()}"
    test_env.mkdir(exist_ok=True)
    
    # Create test-specific directories
    (test_env / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (test_env / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (test_env / "data" / "datastore").mkdir(parents=True, exist_ok=True)
    (test_env / "logs").mkdir(exist_ok=True)
    
    yield test_env
    
    # Cleanup test environment
    if test_env.exists():
        shutil.rmtree(test_env)


@pytest.fixture(scope="function")
def test_template(test_environment: Path) -> TestTemplate:
    """
    Create a test template instance for each test.
    
    Args:
        test_environment: Test environment directory
        
    Returns:
        Configured TestTemplate instance
    """
    return TestTemplate("test_function")


@pytest.fixture(scope="session")
def sample_csv_data() -> str:
    """
    Sample CSV registration data for testing.
    
    Returns:
        CSV string with sample registration data
    """
    return """id,user_id,club_id,event_id,name,age,gender,country,team,skill_level
3236294,56825,32158,E12692,John Doe,25,M,US,Test Team,Advanced
3236295,56826,32159,E12692,Jane Smith,23,F,US,Test Team,Intermediate
3236296,56827,32160,E12692,Bob Johnson,30,M,US,Test Team,Beginner"""


@pytest.fixture(scope="session")
def sample_json_data() -> dict:
    """
    Sample JSON registration data for testing.
    
    Returns:
        Dictionary with sample registration data
    """
    return {
        "registrations": [
            {
                "id": 3236294,
                "user_id": 56825,
                "club_id": 32158,
                "event_id": "E12692",
                "name": "John Doe",
                "age": 25,
                "gender": "M",
                "country": "US",
                "team": "Test Team",
                "skill_level": "Advanced"
            },
            {
                "id": 3236295,
                "user_id": 56826,
                "club_id": 32159,
                "event_id": "E12692",
                "name": "Jane Smith",
                "age": 23,
                "gender": "F",
                "country": "US",
                "team": "Test Team",
                "skill_level": "Intermediate"
            }
        ]
    }


@pytest.fixture(scope="session")
def sample_excel_data() -> dict:
    """
    Sample Excel match data for testing.
    
    Returns:
        Dictionary with sample match data
    """
    return {
        "matches": [
            {
                "match_id": "M001",
                "event_id": "E12692",
                "division_id": "D001",
                "athlete1_id": "A123456",
                "athlete2_id": "A789012",
                "winner_id": "A123456",
                "win_type": "submission",
                "bracket_round": "final"
            },
            {
                "match_id": "M002",
                "event_id": "E12692",
                "division_id": "D001",
                "athlete1_id": "A345678",
                "athlete2_id": "A901234",
                "winner_id": "A345678",
                "win_type": "points",
                "bracket_round": "semi-final"
            }
        ]
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow) 