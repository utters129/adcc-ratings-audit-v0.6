"""
ADCC Analysis Engine v0.6 - Phase 4 Data Storage Tests
Tests for Parquet file processing, JSON dictionary creation, and state management.
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

from src.utils.file_handler import (
    save_parquet_file, load_parquet_file, save_json_file, load_json_file,
    ensure_directory_exists, backup_file, get_file_size_mb
)
from src.core.constants import PROCESSED_DATA_DIR, DATASTORE_DIR


class TestParquetFileProcessing:
    """Test enhanced Parquet file processing functionality."""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'athlete_id': ['A001', 'A002', 'A003'],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'division': ['Adult Male Black Belt', 'Adult Female Purple Belt', 'Master 1 Male Blue Belt'],
            'club': ['Team Alpha', 'Team Beta', 'Team Gamma'],
            'matches_played': [5, 3, 7],
            'wins': [4, 2, 5],
            'losses': [1, 1, 2]
        })
    
    @pytest.fixture
    def test_parquet_path(self, tmp_path):
        """Create a test Parquet file path."""
        return tmp_path / "test_data.parquet"
    
    def test_save_parquet_file_success(self, sample_dataframe, test_parquet_path):
        """Test successful Parquet file saving."""
        result = save_parquet_file(sample_dataframe, test_parquet_path)
        
        assert result is True
        assert test_parquet_path.exists()
        assert test_parquet_path.stat().st_size > 0
    
    def test_save_parquet_file_with_compression(self, sample_dataframe, test_parquet_path):
        """Test Parquet file saving with different compression methods."""
        result = save_parquet_file(sample_dataframe, test_parquet_path, compression='gzip')
        
        assert result is True
        assert test_parquet_path.exists()
    
    def test_save_parquet_file_creates_directory(self, sample_dataframe, tmp_path):
        """Test that save_parquet_file creates parent directory if it doesn't exist."""
        test_path = tmp_path / "new_dir" / "test_data.parquet"
        
        result = save_parquet_file(sample_dataframe, test_path)
        
        assert result is True
        assert test_path.parent.exists()
        assert test_path.exists()
    
    def test_load_parquet_file_success(self, sample_dataframe, test_parquet_path):
        """Test successful Parquet file loading."""
        # First save the file
        save_parquet_file(sample_dataframe, test_parquet_path)
        
        # Then load it
        loaded_df = load_parquet_file(test_parquet_path)
        
        assert loaded_df is not None
        assert len(loaded_df) == len(sample_dataframe)
        assert list(loaded_df.columns) == list(sample_dataframe.columns)
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)
    
    def test_load_parquet_file_not_found(self, tmp_path):
        """Test loading non-existent Parquet file."""
        test_path = tmp_path / "nonexistent.parquet"
        
        result = load_parquet_file(test_path)
        
        assert result is None
    
    def test_parquet_file_integrity(self, sample_dataframe, test_parquet_path):
        """Test Parquet file data integrity."""
        # Save with specific data types
        sample_dataframe['matches_played'] = sample_dataframe['matches_played'].astype('int32')
        sample_dataframe['wins'] = sample_dataframe['wins'].astype('int32')
        sample_dataframe['losses'] = sample_dataframe['losses'].astype('int32')
        
        save_parquet_file(sample_dataframe, test_parquet_path)
        loaded_df = load_parquet_file(test_parquet_path)
        
        assert loaded_df is not None
        assert loaded_df.dtypes['matches_played'] == 'int32'
        assert loaded_df.dtypes['wins'] == 'int32'
        assert loaded_df.dtypes['losses'] == 'int32'
    
    def test_parquet_file_performance(self, sample_dataframe, test_parquet_path):
        """Test Parquet file performance with larger datasets."""
        # Create larger dataset
        large_df = pd.concat([sample_dataframe] * 1000, ignore_index=True)
        
        save_parquet_file(large_df, test_parquet_path)
        loaded_df = load_parquet_file(test_parquet_path)
        
        assert loaded_df is not None
        assert len(loaded_df) == len(large_df)
        assert get_file_size_mb(test_parquet_path) > 0


class TestJSONDictionaryCreation:
    """Test JSON dictionary creation and management."""
    
    @pytest.fixture
    def sample_athlete_data(self):
        """Create sample athlete data for testing."""
        return {
            'athlete_id': 'A001',
            'name': 'John Doe',
            'club': 'Team Alpha',
            'divisions': ['Adult Male Black Belt'],
            'total_matches': 15,
            'wins': 12,
            'losses': 3,
            'rating': 1500.0,
            'rating_deviation': 350.0,
            'last_updated': '2024-01-15T10:30:00Z'
        }
    
    @pytest.fixture
    def sample_division_data(self):
        """Create sample division data for testing."""
        return {
            'division_id': 'D001',
            'name': 'Adult Male Black Belt',
            'age_class': 'Adult',
            'gender': 'Male',
            'skill_level': 'Black Belt',
            'gi_status': 'Gi',
            'athletes': ['A001', 'A002', 'A003'],
            'total_athletes': 3
        }
    
    @pytest.fixture
    def test_json_path(self, tmp_path):
        """Create a test JSON file path."""
        return tmp_path / "test_data.json"
    
    def test_save_json_file_success(self, sample_athlete_data, test_json_path):
        """Test successful JSON file saving."""
        result = save_json_file(sample_athlete_data, test_json_path)
        
        assert result is True
        assert test_json_path.exists()
        assert test_json_path.stat().st_size > 0
    
    def test_save_json_file_creates_directory(self, sample_athlete_data, tmp_path):
        """Test that save_json_file creates parent directory if it doesn't exist."""
        test_path = tmp_path / "new_dir" / "test_data.json"
        
        result = save_json_file(sample_athlete_data, test_path)
        
        assert result is True
        assert test_path.parent.exists()
        assert test_path.exists()
    
    def test_load_json_file_success(self, sample_athlete_data, test_json_path):
        """Test successful JSON file loading."""
        # First save the file
        save_json_file(sample_athlete_data, test_json_path)
        
        # Then load it
        loaded_data = load_json_file(test_json_path)
        
        assert loaded_data is not None
        assert loaded_data == sample_athlete_data
    
    def test_load_json_file_not_found(self, tmp_path):
        """Test loading non-existent JSON file."""
        test_path = tmp_path / "nonexistent.json"
        
        result = load_json_file(test_path)
        
        assert result == {}
    
    def test_json_file_integrity(self, sample_athlete_data, test_json_path):
        """Test JSON file data integrity with complex nested structures."""
        complex_data = {
            'athletes': {
                'A001': sample_athlete_data,
                'A002': {**sample_athlete_data, 'athlete_id': 'A002', 'name': 'Jane Smith'}
            },
            'metadata': {
                'total_athletes': 2,
                'last_updated': '2024-01-15T10:30:00Z',
                'version': '1.0'
            }
        }
        
        save_json_file(complex_data, test_json_path)
        loaded_data = load_json_file(test_json_path)
        
        assert loaded_data == complex_data
        assert 'athletes' in loaded_data
        assert 'metadata' in loaded_data
        assert len(loaded_data['athletes']) == 2


class TestStateManagement:
    """Test state management and snapshot functionality."""
    
    @pytest.fixture
    def sample_state_data(self):
        """Create sample state data for testing."""
        return {
            'state_id': 'S001',
            'timestamp': '2024-01-15T10:30:00Z',
            'version': '1.0',
            'data_sources': {
                'events_processed': 5,
                'athletes_processed': 150,
                'matches_processed': 300
            },
            'checksums': {
                'athletes_file': 'abc123',
                'divisions_file': 'def456',
                'matches_file': 'ghi789'
            }
        }
    
    @pytest.fixture
    def test_state_path(self, tmp_path):
        """Create a test state file path."""
        return tmp_path / "state" / "test_state.json"
    
    def test_state_snapshot_creation(self, sample_state_data, test_state_path):
        """Test creating state snapshots."""
        result = save_json_file(sample_state_data, test_state_path)
        
        assert result is True
        assert test_state_path.exists()
        
        loaded_state = load_json_file(test_state_path)
        assert loaded_state == sample_state_data
    
    def test_state_validation(self, sample_state_data, test_state_path):
        """Test state data validation."""
        # Test valid state
        result = save_json_file(sample_state_data, test_state_path)
        assert result is True
        
        # Test invalid state (missing required fields)
        invalid_state = {'timestamp': '2024-01-15T10:30:00Z'}
        result = save_json_file(invalid_state, test_state_path)
        assert result is True  # Should still save, validation happens elsewhere
    
    def test_state_rollback_preparation(self, sample_state_data, test_state_path):
        """Test preparing state for rollback functionality."""
        # Create multiple state snapshots
        states = []
        for i in range(3):
            state = {**sample_state_data, 'state_id': f'S00{i+1}', 'sequence': i}
            state_path = test_state_path.parent / f"state_{i}.json"
            save_json_file(state, state_path)
            states.append(state_path)
        
        # Verify all states exist
        for state_path in states:
            assert state_path.exists()
            loaded_state = load_json_file(state_path)
            assert loaded_state is not None


class TestDataStorageIntegration:
    """Test integration between different data storage components."""
    
    @pytest.fixture
    def sample_integration_data(self):
        """Create sample data for integration testing."""
        return {
            'athletes_df': pd.DataFrame({
                'athlete_id': ['A001', 'A002'],
                'name': ['John Doe', 'Jane Smith'],
                'rating': [1500.0, 1450.0]
            }),
            'athletes_dict': {
                'A001': {'name': 'John Doe', 'rating': 1500.0},
                'A002': {'name': 'Jane Smith', 'rating': 1450.0}
            },
            'state_data': {
                'timestamp': '2024-01-15T10:30:00Z',
                'athletes_processed': 2
            }
        }
    
    def test_parquet_json_integration(self, sample_integration_data, tmp_path):
        """Test integration between Parquet and JSON storage."""
        # Save DataFrame to Parquet
        parquet_path = tmp_path / "athletes.parquet"
        save_parquet_file(sample_integration_data['athletes_df'], parquet_path)
        
        # Save dictionary to JSON
        json_path = tmp_path / "athletes.json"
        save_json_file(sample_integration_data['athletes_dict'], json_path)
        
        # Verify both files exist and contain correct data
        assert parquet_path.exists()
        assert json_path.exists()
        
        loaded_df = load_parquet_file(parquet_path)
        loaded_dict = load_json_file(json_path)
        
        assert loaded_df is not None
        assert loaded_dict is not None
        assert len(loaded_df) == len(sample_integration_data['athletes_df'])
        assert len(loaded_dict) == len(sample_integration_data['athletes_dict'])
    
    def test_file_size_optimization(self, sample_integration_data, tmp_path):
        """Test file size optimization with different compression methods."""
        df = sample_integration_data['athletes_df']
        
        # Test different compression methods
        compressions = ['snappy', 'gzip', 'brotli']
        file_sizes = {}
        
        for compression in compressions:
            file_path = tmp_path / f"test_{compression}.parquet"
            save_parquet_file(df, file_path, compression=compression)
            file_sizes[compression] = get_file_size_mb(file_path)
        
        # All files should exist and have reasonable sizes
        for compression, size in file_sizes.items():
            assert size > 0
            assert size < 1.0  # Should be small for this test data


class TestErrorHandling:
    """Test error handling in data storage components."""
    
    def test_parquet_save_error_handling(self, tmp_path):
        """Test error handling when saving Parquet files."""
        # Test with invalid DataFrame
        with pytest.raises(Exception):
            save_parquet_file(None, tmp_path / "test.parquet")
    
    def test_json_save_error_handling(self, tmp_path):
        """Test error handling when saving JSON files."""
        # Test with non-serializable data
        non_serializable = {'data': lambda x: x}
        
        # Should handle gracefully
        result = save_json_file(non_serializable, tmp_path / "test.json")
        assert result is False
    
    def test_file_permission_errors(self, tmp_path):
        """Test handling of file permission errors."""
        # Create a read-only directory
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir()
        read_only_dir.chmod(0o444)  # Read-only
        
        with pytest.raises(Exception):
            save_json_file({'test': 'data'}, read_only_dir / "test.json")


class TestPerformance:
    """Test performance characteristics of data storage components."""
    
    def test_large_dataset_handling(self, tmp_path):
        """Test handling of large datasets."""
        # Create large DataFrame
        large_df = pd.DataFrame({
            'athlete_id': [f'A{i:06d}' for i in range(10000)],
            'name': [f'Athlete {i}' for i in range(10000)],
            'rating': [1500.0 + (i % 500) for i in range(10000)]
        })
        
        parquet_path = tmp_path / "large_dataset.parquet"
        
        # Test save performance
        save_parquet_file(large_df, parquet_path)
        
        # Test load performance
        loaded_df = load_parquet_file(parquet_path)
        
        assert loaded_df is not None
        assert len(loaded_df) == 10000
        assert get_file_size_mb(parquet_path) > 0
    
    def test_concurrent_access_simulation(self, tmp_path):
        """Test simulation of concurrent file access."""
        # Create multiple files simultaneously
        files = []
        for i in range(10):
            df = pd.DataFrame({'id': [i], 'data': [f'test_{i}']})
            file_path = tmp_path / f"concurrent_{i}.parquet"
            save_parquet_file(df, file_path)
            files.append(file_path)
        
        # Verify all files were created successfully
        for file_path in files:
            assert file_path.exists()
            loaded_df = load_parquet_file(file_path)
            assert loaded_df is not None 