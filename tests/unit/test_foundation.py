"""
ADCC Analysis Engine v0.6 - Foundation Unit Tests
Tests for configuration, logging, and basic utility functions.
"""

import pytest
import tempfile
import json
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.settings import get_settings, Settings
from src.core.constants import (
    PROJECT_ROOT, DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, DATASTORE_DIR,
    LOGS_DIR, HOST, PORT, GLICKO_TAU, GLICKO_DEFAULT_RD
)
from src.utils.logger import setup_logging, get_logger
from src.utils.file_handler import (
    ensure_directory_exists, get_file_size_mb, validate_file_type,
    backup_file, load_json_file, save_json_file, load_parquet_file,
    save_parquet_file, list_files_in_directory, cleanup_old_files
)


class TestConfiguration:
    """Test configuration system."""
    
    def test_settings_loading(self):
        """Test that settings can be loaded."""
        settings = get_settings()
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'environment')
        assert hasattr(settings, 'smoothcomp_username')
        assert hasattr(settings, 'admin_username')
    
    def test_settings_singleton(self):
        """Test that settings is a singleton."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
    
    def test_environment_default(self):
        """Test environment default value."""
        settings = get_settings()
        assert settings.environment in ['development', 'staging', 'production']
    
    def test_admin_credentials_exist(self):
        """Test that admin credentials are defined."""
        settings = get_settings()
        assert settings.admin_username is not None
        assert settings.admin_password is not None


class TestConstants:
    """Test constants are properly defined."""
    
    def test_project_paths(self):
        """Test that project paths are correctly defined."""
        assert PROJECT_ROOT.exists()
        assert DATA_DIR == PROJECT_ROOT / "data"
        assert RAW_DATA_DIR == DATA_DIR / "raw"
        assert PROCESSED_DATA_DIR == DATA_DIR / "processed"
        assert DATASTORE_DIR == DATA_DIR / "datastore"
        assert LOGS_DIR == PROJECT_ROOT / "logs"
    
    def test_server_config(self):
        """Test server configuration constants."""
        assert isinstance(HOST, str)
        assert isinstance(PORT, int)
        assert PORT > 0 and PORT < 65536
    
    def test_glicko_constants(self):
        """Test Glicko rating system constants."""
        assert isinstance(GLICKO_TAU, float)
        assert isinstance(GLICKO_DEFAULT_RD, int)
        assert GLICKO_TAU > 0
        assert GLICKO_DEFAULT_RD > 0


class TestLogging:
    """Test logging infrastructure."""
    
    def test_logger_setup(self):
        """Test that logging can be set up."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            setup_logging(log_dir=log_dir)
            
            # Test that log directory was created
            assert log_dir.exists()
            
            # Test that we can get a logger
            logger = get_logger("test_logger")
            assert logger is not None
    
    def test_logger_functionality(self):
        """Test basic logger functionality."""
        logger = get_logger("test_functionality")
        # This should not raise an exception
        logger.info("Test log message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")
        logger.error("Test error message")


class TestFileHandler:
    """Test file handler utilities."""
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_subdir" / "nested"
            ensure_directory_exists(test_dir)
            assert test_dir.exists()
            assert test_dir.is_dir()
    
    def test_get_file_size_mb(self):
        """Test file size calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            f.flush()
            
            file_path = Path(f.name)
            size_mb = get_file_size_mb(file_path)
            
            assert isinstance(size_mb, float)
            assert size_mb >= 0
            
            # Cleanup
            file_path.unlink()
    
    def test_validate_file_type(self):
        """Test file type validation."""
        # Test valid file types
        assert validate_file_type(Path("test.csv"))
        assert validate_file_type(Path("test.xlsx"))
        assert validate_file_type(Path("test.json"))
        
        # Test invalid file types
        assert not validate_file_type(Path("test.txt"))
        assert not validate_file_type(Path("test.pdf"))
    
    def test_backup_file(self):
        """Test file backup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a test file
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")
            
            # Create backup
            backup_path = backup_file(test_file)
            
            # Check that backup exists and has different name
            assert backup_path.exists()
            assert backup_path != test_file
            assert backup_path.read_text() == "test content"
    
    def test_json_file_operations(self):
        """Test JSON file load and save operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.json"
            
            # Test data
            test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
            
            # Test save
            success = save_json_file(test_data, test_file)
            assert success
            assert test_file.exists()
            
            # Test load
            loaded_data = load_json_file(test_file)
            assert loaded_data == test_data
    
    def test_parquet_file_operations(self):
        """Test Parquet file load and save operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.parquet"
            
            # Test data
            test_df = pd.DataFrame({
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35],
                'score': [85.5, 92.0, 78.5]
            })
            
            # Test save
            success = save_parquet_file(test_df, test_file)
            assert success
            assert test_file.exists()
            
            # Test load
            loaded_df = load_parquet_file(test_file)
            assert loaded_df is not None
            pd.testing.assert_frame_equal(test_df, loaded_df)
    
    def test_list_files_in_directory(self):
        """Test file listing functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some test files
            (temp_path / "test1.txt").touch()
            (temp_path / "test2.csv").touch()
            (temp_path / "test3.json").touch()
            
            # Test listing all files
            files = list_files_in_directory(temp_path)
            assert len(files) == 3
            
            # Test pattern matching
            csv_files = list_files_in_directory(temp_path, "*.csv")
            assert len(csv_files) == 1
            assert csv_files[0].name == "test2.csv"
    
    def test_cleanup_old_files(self):
        """Test old file cleanup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a test file
            test_file = temp_path / "test.txt"
            test_file.touch()
            
            # Test cleanup (should not remove recent file)
            removed_count = cleanup_old_files(temp_path, days_old=1)
            assert removed_count == 0
            assert test_file.exists()


class TestIntegration:
    """Test integration between foundation components."""
    
    def test_configuration_with_logging(self):
        """Test that configuration works with logging."""
        settings = get_settings()
        logger = get_logger("integration_test")
        
        # This should work without errors
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Admin user: {settings.admin_username}")
    
    def test_file_operations_with_logging(self):
        """Test file operations with logging enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "integration_test.json"
            
            test_data = {"test": "integration"}
            
            # This should work and log operations
            success = save_json_file(test_data, test_file)
            assert success
            
            loaded_data = load_json_file(test_file)
            assert loaded_data == test_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 