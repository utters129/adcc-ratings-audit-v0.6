"""
Test Template for ADCC Analysis Engine v0.6
This template ensures all tests follow the development roadmap principles.
Use this template when creating new test files.
"""

import pytest
import structlog
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Import project-specific modules
from src.config.settings import LOG_LEVEL, LOGS_DIR
from src.config.constants import *
from src.utils.development_template import DevelopmentTemplate

# Set up test logging
logger = structlog.get_logger(__name__)

class TestTemplate(DevelopmentTemplate):
    """
    Template class for all test modules.
    Ensures consistent testing patterns and comprehensive coverage.
    """
    
    def __init__(self, test_module_name: str):
        """
        Initialize the test template.
        
        Args:
            test_module_name: Name of the test module
        """
        super().__init__(f"test_{test_module_name}")
        self.test_module_name = test_module_name
        
        # Create temporary test directory
        self.test_dir = Path(tempfile.mkdtemp(prefix=f"adcc_test_{test_module_name}_"))
        self.logger.info(
            "test_environment_created",
            test_dir=str(self.test_dir),
            test_module=test_module_name
        )
    
    def setup_method(self, method):
        """
        Setup method called before each test method.
        
        Args:
            method: The test method being executed
        """
        self.logger.info(
            "test_setup",
            test_method=method.__name__,
            test_module=self.test_module_name
        )
        
        # Create test-specific directories
        self.test_data_dir = self.test_dir / "data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        self.test_raw_dir = self.test_data_dir / "raw"
        self.test_raw_dir.mkdir(exist_ok=True)
        
        self.test_processed_dir = self.test_data_dir / "processed"
        self.test_processed_dir.mkdir(exist_ok=True)
        
        self.test_datastore_dir = self.test_data_dir / "datastore"
        self.test_datastore_dir.mkdir(exist_ok=True)
    
    def teardown_method(self, method):
        """
        Teardown method called after each test method.
        
        Args:
            method: The test method that was executed
        """
        self.logger.info(
            "test_teardown",
            test_method=method.__name__,
            test_module=self.test_module_name
        )
        
        # Clean up test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def create_test_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """
        Create test data for different scenarios.
        
        Args:
            data_type: Type of test data to create
            **kwargs: Additional parameters for data creation
            
        Returns:
            Dictionary containing test data
        """
        self.log_operation_start("create_test_data", data_type=data_type, **kwargs)
        
        try:
            if data_type == "athlete":
                test_data = self._create_athlete_test_data(**kwargs)
            elif data_type == "event":
                test_data = self._create_event_test_data(**kwargs)
            elif data_type == "match":
                test_data = self._create_match_test_data(**kwargs)
            elif data_type == "registration":
                test_data = self._create_registration_test_data(**kwargs)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
            
            self.log_operation_success("create_test_data", data_type=data_type, data_size=len(test_data))
            return test_data
            
        except Exception as e:
            self.log_operation_error("create_test_data", e, data_type=data_type)
            raise
    
    def _create_athlete_test_data(self, **kwargs) -> Dict[str, Any]:
        """Create test athlete data."""
        return {
            "smoothcomp_id": kwargs.get("smoothcomp_id", 123456),
            "name": kwargs.get("name", "John Doe"),
            "team": kwargs.get("team", "Test Team"),
            "age": kwargs.get("age", 25),
            "gender": kwargs.get("gender", "M"),
            "country": kwargs.get("country", "US"),
            "skill_level": kwargs.get("skill_level", "Advanced")
        }
    
    def _create_event_test_data(self, **kwargs) -> Dict[str, Any]:
        """Create test event data."""
        return {
            "event_id": kwargs.get("event_id", "E12692"),
            "name": kwargs.get("name", "Test Event"),
            "date": kwargs.get("date", "2023-09-09"),
            "type": kwargs.get("type", "open"),
            "country": kwargs.get("country", "United States"),
            "multi_day": kwargs.get("multi_day", False),
            "gi_event": kwargs.get("gi_event", False),
            "no_gi_event": kwargs.get("no_gi_event", True)
        }
    
    def _create_match_test_data(self, **kwargs) -> Dict[str, Any]:
        """Create test match data."""
        return {
            "match_id": kwargs.get("match_id", "M001"),
            "event_id": kwargs.get("event_id", "E12692"),
            "division_id": kwargs.get("division_id", "D001"),
            "athlete1_id": kwargs.get("athlete1_id", "A123456"),
            "athlete2_id": kwargs.get("athlete2_id", "A789012"),
            "winner_id": kwargs.get("winner_id", "A123456"),
            "win_type": kwargs.get("win_type", "submission"),
            "bracket_round": kwargs.get("bracket_round", "final")
        }
    
    def _create_registration_test_data(self, **kwargs) -> Dict[str, Any]:
        """Create test registration data."""
        return {
            "registration_id": kwargs.get("registration_id", 3236294),
            "user_id": kwargs.get("user_id", 56825),
            "club_id": kwargs.get("club_id", 32158),
            "event_id": kwargs.get("event_id", "E12692"),
            "divisions": kwargs.get("divisions", ["D001", "D002"]),
            "placement": kwargs.get("placement", 1)
        }
    
    def assert_data_structure(self, data: Dict[str, Any], expected_structure: Dict[str, type]) -> None:
        """
        Assert that data has the expected structure.
        
        Args:
            data: Data to validate
            expected_structure: Dictionary mapping field names to expected types
        """
        self.logger.debug(
            "validating_data_structure",
            expected_fields=list(expected_structure.keys()),
            actual_fields=list(data.keys())
        )
        
        for field_name, expected_type in expected_structure.items():
            assert field_name in data, f"Missing required field: {field_name}"
            assert isinstance(data[field_name], expected_type), \
                f"Field {field_name} has wrong type. Expected {expected_type}, got {type(data[field_name])}"
    
    def assert_file_created(self, file_path: Path) -> None:
        """
        Assert that a file was created successfully.
        
        Args:
            file_path: Path to the file to check
        """
        assert file_path.exists(), f"File was not created: {file_path}"
        assert file_path.is_file(), f"Path exists but is not a file: {file_path}"
        
        self.logger.info(
            "file_creation_verified",
            file_path=str(file_path),
            file_size=file_path.stat().st_size
        )
    
    def assert_file_content(self, file_path: Path, expected_content: Any) -> None:
        """
        Assert that file contains expected content.
        
        Args:
            file_path: Path to the file to check
            expected_content: Expected content to find in the file
        """
        assert file_path.exists(), f"File does not exist: {file_path}"
        
        # Read file content based on file type
        if file_path.suffix == ".json":
            import json
            with open(file_path, 'r') as f:
                actual_content = json.load(f)
        elif file_path.suffix == ".parquet":
            import pandas as pd
            actual_content = pd.read_parquet(file_path)
        else:
            with open(file_path, 'r') as f:
                actual_content = f.read()
        
        assert actual_content == expected_content, \
            f"File content does not match expected content in {file_path}"
        
        self.logger.info(
            "file_content_verified",
            file_path=str(file_path),
            content_type=type(actual_content).__name__
        )

# Example test class using the template
class TestExampleModule(TestTemplate):
    """
    Example test class showing how to use the test template.
    """
    
    def __init__(self):
        super().__init__("example_module")
    
    def test_data_creation(self):
        """Test that test data can be created successfully."""
        # Create test data
        athlete_data = self.create_test_data("athlete", name="Test Athlete")
        
        # Validate data structure
        expected_structure = {
            "smoothcomp_id": int,
            "name": str,
            "team": str,
            "age": int,
            "gender": str,
            "country": str,
            "skill_level": str
        }
        
        self.assert_data_structure(athlete_data, expected_structure)
        
        # Verify specific values
        assert athlete_data["name"] == "Test Athlete"
        assert athlete_data["skill_level"] == "Advanced"
    
    def test_file_operations(self):
        """Test file operations with the template."""
        # Create a test file
        test_file = self.test_data_dir / "test.json"
        test_data = {"test": "data"}
        
        import json
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Assert file was created
        self.assert_file_created(test_file)
        
        # Assert file content
        self.assert_file_content(test_file, test_data)

# Test utilities
def create_test_logger(test_name: str) -> structlog.BoundLogger:
    """
    Create a test-specific logger.
    
    Args:
        test_name: Name of the test
        
    Returns:
        Configured test logger
    """
    return structlog.get_logger(f"adcc_test.{test_name}")

def assert_performance_requirement(func, max_execution_time: float = 30.0):
    """
    Assert that a function meets performance requirements.
    
    Args:
        func: Function to test
        max_execution_time: Maximum allowed execution time in seconds
    """
    import time
    
    start_time = time.time()
    result = func()
    execution_time = time.time() - start_time
    
    assert execution_time < max_execution_time, \
        f"Function execution time ({execution_time:.2f}s) exceeds maximum ({max_execution_time}s)"
    
    return result

def assert_error_handling(func, expected_error_type: type, *args, **kwargs):
    """
    Assert that a function properly handles errors.
    
    Args:
        func: Function to test
        expected_error_type: Type of error expected
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function
    """
    with pytest.raises(expected_error_type):
        func(*args, **kwargs)

# Test configuration
@pytest.fixture(scope="session")
def test_environment():
    """
    Fixture to set up test environment.
    """
    # Create test directories
    test_root = Path(tempfile.mkdtemp(prefix="adcc_test_env_"))
    
    # Create test data directories
    (test_root / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (test_root / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (test_root / "data" / "datastore").mkdir(parents=True, exist_ok=True)
    (test_root / "logs").mkdir(exist_ok=True)
    
    yield test_root
    
    # Cleanup
    shutil.rmtree(test_root)

# Test checklist reminder
TEST_CHECKLIST = """
Before committing any tests, ensure:

1. ✅ All test methods have descriptive names
2. ✅ All test methods have docstrings explaining what they test
3. ✅ Tests cover both success and failure scenarios
4. ✅ Tests validate data structures and content
5. ✅ Tests include performance requirements
6. ✅ Tests include error handling scenarios
7. ✅ Tests clean up after themselves
8. ✅ Tests are independent and can run in any order
9. ✅ Tests provide sufficient logging for debugging
10. ✅ Test coverage meets requirements (target: 80%+)

Remember: Good tests are the foundation of reliable code!
""" 