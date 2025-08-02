"""
ADCC Analysis Engine v0.6 - Phase 4 State Management Tests
Tests for state management and rollback functionality.
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

from src.state_management.save_states import StateManager
from src.state_management.rollback import StateRollback
from src.utils.file_handler import save_json_file, load_json_file


class TestStateManager:
    """Test StateManager functionality."""
    
    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create a StateManager instance for testing."""
        datastore_dir = tmp_path / "datastore"
        return StateManager(datastore_dir=datastore_dir)
    
    @pytest.fixture
    def sample_state_data(self):
        """Create sample state data for testing."""
        return {
            'athletes': {
                'A001': {'name': 'John Doe', 'rating': 1500.0},
                'A002': {'name': 'Jane Smith', 'rating': 1450.0}
            },
            'divisions': {
                'D001': {'name': 'Adult Male Black Belt', 'athletes': ['A001']}
            },
            'metadata': {
                'total_athletes': 2,
                'total_divisions': 1,
                'version': '1.0'
            }
        }
    
    def test_state_manager_initialization(self, state_manager):
        """Test StateManager initialization."""
        assert state_manager.datastore_dir.exists()
        assert state_manager.states_dir.exists()
        assert state_manager.state_index_file.exists()
        assert 'metadata' in state_manager.state_index
        assert 'states' in state_manager.state_index
    
    def test_create_state_snapshot(self, state_manager, sample_state_data):
        """Test creating a state snapshot."""
        state_id = state_manager.create_state_snapshot(
            "Test state snapshot",
            sample_state_data,
            {'test_metadata': 'value'}
        )
        
        assert state_id is not None
        assert state_id.startswith('STATE_')
        
        # Verify state was added to index
        assert state_id in state_manager.state_index['states']
        assert state_manager.state_index['metadata']['total_states'] == 1
    
    def test_get_state(self, state_manager, sample_state_data):
        """Test retrieving a state snapshot."""
        # Create a state first
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        
        # Retrieve the state
        retrieved_state = state_manager.get_state(state_id)
        
        assert retrieved_state is not None
        assert retrieved_state['state_name'] == "Test state"
        assert retrieved_state['data'] == sample_state_data
        assert 'checksum' in retrieved_state
    
    def test_get_latest_state(self, state_manager, sample_state_data):
        """Test getting the latest state."""
        # Create multiple states
        state_manager.create_state_snapshot("First state", {'data': 'first'})
        state_manager.create_state_snapshot("Second state", {'data': 'second'})
        latest_id = state_manager.create_state_snapshot("Latest state", sample_state_data)
        
        # Get latest state
        latest_state = state_manager.get_latest_state()
        
        assert latest_state is not None
        assert latest_state['state_id'] == latest_id
        assert latest_state['state_name'] == "Latest state"
    
    def test_get_state_sequence(self, state_manager, sample_state_data):
        """Test getting a sequence of states."""
        # Create multiple states
        state_ids = []
        for i in range(3):
            state_id = state_manager.create_state_snapshot(
                f"State {i+1}", 
                {f'data_{i+1}': f'value_{i+1}'}
            )
            state_ids.append(state_id)
        
        # Get sequence
        sequence = state_manager.get_state_sequence(state_ids[0], state_ids[2])
        
        assert len(sequence) == 3
        assert sequence[0]['state_id'] == state_ids[0]
        assert sequence[2]['state_id'] == state_ids[2]
    
    def test_list_states(self, state_manager, sample_state_data):
        """Test listing states."""
        # Create multiple states
        for i in range(5):
            state_manager.create_state_snapshot(f"State {i+1}", {f'data': i+1})
        
        # List all states
        states = state_manager.list_states()
        assert len(states) == 5
        
        # List with limit
        limited_states = state_manager.list_states(limit=3)
        assert len(limited_states) == 3
    
    def test_validate_state_integrity(self, state_manager, sample_state_data):
        """Test state integrity validation."""
        # Create a state
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        
        # Validate integrity
        is_valid = state_manager.validate_state_integrity(state_id)
        assert is_valid is True
        
        # Test with non-existent state
        is_valid = state_manager.validate_state_integrity("NONEXISTENT")
        assert is_valid is False
    
    def test_cleanup_old_states(self, state_manager, sample_state_data):
        """Test cleaning up old states."""
        # Create multiple states
        for i in range(10):
            state_manager.create_state_snapshot(f"State {i+1}", {f'data': i+1})
        
        # Cleanup old states
        removed_count = state_manager.cleanup_old_states(keep_count=5)
        
        assert removed_count == 5
        assert state_manager.state_index['metadata']['total_states'] == 5
    
    def test_get_state_statistics(self, state_manager, sample_state_data):
        """Test getting state statistics."""
        # Create some states
        for i in range(3):
            state_manager.create_state_snapshot(f"State {i+1}", {f'data': i+1})
        
        # Get statistics
        stats = state_manager.get_state_statistics()
        
        assert stats['total_states'] == 3
        assert 'oldest_state' in stats
        assert 'newest_state' in stats
        assert 'state_types' in stats
        assert stats['total_size_mb'] > 0
    
    def test_export_state_to_parquet(self, state_manager, sample_state_data, tmp_path):
        """Test exporting state to Parquet format."""
        # Create a state
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        
        # Export to Parquet
        output_path = tmp_path / "exported_state.parquet"
        success = state_manager.export_state_to_parquet(state_id, output_path)
        
        assert success is True
        assert output_path.exists()
        
        # Verify Parquet file can be read
        df = pd.read_parquet(output_path)
        assert len(df) > 0


class TestStateRollback:
    """Test StateRollback functionality."""
    
    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create a StateManager instance for testing."""
        datastore_dir = tmp_path / "datastore"
        return StateManager(datastore_dir=datastore_dir)
    
    @pytest.fixture
    def state_rollback(self, state_manager, tmp_path):
        """Create a StateRollback instance for testing."""
        datastore_dir = tmp_path / "datastore"
        return StateRollback(state_manager, datastore_dir=datastore_dir)
    
    @pytest.fixture
    def sample_state_data(self):
        """Create sample state data for testing."""
        return {
            'athletes': {
                'A001': {'name': 'John Doe', 'rating': 1500.0},
                'A002': {'name': 'Jane Smith', 'rating': 1450.0}
            },
            'metadata': {
                'total_athletes': 2,
                'version': '1.0'
            }
        }
    
    def test_state_rollback_initialization(self, state_rollback):
        """Test StateRollback initialization."""
        assert state_rollback.datastore_dir.exists()
        assert state_rollback.rollback_dir.exists()
        assert state_rollback.rollback_history_file.exists()
        assert 'metadata' in state_rollback.rollback_history
        assert 'rollbacks' in state_rollback.rollback_history
    
    def test_create_rollback_point(self, state_rollback, state_manager, sample_state_data):
        """Test creating a rollback point."""
        # Create a state first
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        
        # Create rollback point
        rollback_id = state_rollback.create_rollback_point(
            "Test rollback point",
            state_id
        )
        
        assert rollback_id is not None
        assert rollback_id.startswith('ROLLBACK_')
        
        # Verify rollback was added to history
        assert len(state_rollback.rollback_history['rollbacks']) == 1
        assert state_rollback.rollback_history['metadata']['total_rollbacks'] == 1
    
    def test_get_rollback(self, state_rollback, state_manager, sample_state_data):
        """Test retrieving rollback data."""
        # Create a state and rollback point
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        rollback_id = state_rollback.create_rollback_point("Test rollback", state_id)
        
        # Get rollback data
        rollback_data = state_rollback.get_rollback(rollback_id)
        
        assert rollback_data is not None
        assert rollback_data['rollback_id'] == rollback_id
        assert rollback_data['target_state_id'] == state_id
        assert rollback_data['state_data']['state_id'] == state_id
    
    def test_get_rollback_history(self, state_rollback, state_manager, sample_state_data):
        """Test getting rollback history."""
        # Create multiple rollback points
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        for i in range(3):
            state_rollback.create_rollback_point(f"Rollback {i+1}", state_id)
        
        # Get history
        history = state_rollback.get_rollback_history()
        assert len(history) == 3
        
        # Get history with limit
        limited_history = state_rollback.get_rollback_history(limit=2)
        assert len(limited_history) == 2
    
    def test_validate_rollback_safety(self, state_rollback, state_manager, sample_state_data):
        """Test rollback safety validation."""
        # Create a state and rollback point
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        rollback_id = state_rollback.create_rollback_point("Test rollback", state_id)
        
        # Validate safety
        safety = state_rollback.validate_rollback_safety(rollback_id)
        
        assert 'safe' in safety
        assert 'reason' in safety
        assert 'warnings' in safety
        assert isinstance(safety['safe'], bool)
    
    def test_compare_states(self, state_rollback, state_manager):
        """Test state comparison."""
        # Create two different states
        state_1_id = state_manager.create_state_snapshot("State 1", {'data': 'value1'})
        state_2_id = state_manager.create_state_snapshot("State 2", {'data': 'value2'})
        
        # Compare states
        comparison = state_rollback.compare_states(state_1_id, state_2_id)
        
        assert 'state_1' in comparison
        assert 'state_2' in comparison
        assert 'differences' in comparison
        assert comparison['differences']['data_changed'] is True
    
    def test_cleanup_old_rollbacks(self, state_rollback, state_manager, sample_state_data):
        """Test cleaning up old rollbacks."""
        # Create multiple rollback points
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        for i in range(10):
            state_rollback.create_rollback_point(f"Rollback {i+1}", state_id)
        
        # Cleanup old rollbacks
        removed_count = state_rollback.cleanup_old_rollbacks(keep_count=5)
        
        assert removed_count == 5
        assert state_rollback.rollback_history['metadata']['total_rollbacks'] == 5
    
    def test_get_rollback_statistics(self, state_rollback, state_manager, sample_state_data):
        """Test getting rollback statistics."""
        # Create some rollback points
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        for i in range(3):
            state_rollback.create_rollback_point(f"Rollback {i+1}", state_id)
        
        # Get statistics
        stats = state_rollback.get_rollback_statistics()
        
        assert stats['total_rollbacks'] == 3
        assert 'executed_rollbacks' in stats
        assert 'successful_rollbacks' in stats
        assert 'oldest_rollback' in stats
        assert 'newest_rollback' in stats
    
    def test_execute_rollback(self, state_rollback, state_manager, sample_state_data):
        """Test executing a rollback."""
        # Create a state and rollback point
        state_id = state_manager.create_state_snapshot("Test state", sample_state_data)
        rollback_id = state_rollback.create_rollback_point("Test rollback", state_id)
        
        # Execute rollback
        success = state_rollback.execute_rollback(rollback_id)
        
        assert success is True
        
        # Verify rollback status was updated
        rollback_data = state_rollback.get_rollback(rollback_id)
        assert rollback_data is not None  # Rollback data should still exist
    
    def test_execute_rollback_with_backup(self, state_rollback, state_manager, sample_state_data):
        """Test executing a rollback with backup."""
        # Create initial state and rollback point
        state_id = state_manager.create_state_snapshot("Initial state", sample_state_data)
        rollback_id = state_rollback.create_rollback_point("Initial rollback", state_id)
        
        # Create a new state (simulating changes)
        new_state_id = state_manager.create_state_snapshot("New state", {'data': 'new_value'})
        
        # Execute rollback with backup
        success = state_rollback.execute_rollback(rollback_id, backup_current=True)
        
        assert success is True
        
        # Verify backup was created
        history = state_rollback.get_rollback_history()
        backup_rollbacks = [r for r in history if 'Pre-rollback backup' in r['description']]
        assert len(backup_rollbacks) == 1


class TestStateManagementIntegration:
    """Test integration between StateManager and StateRollback."""
    
    @pytest.fixture
    def integrated_system(self, tmp_path):
        """Create an integrated state management system for testing."""
        datastore_dir = tmp_path / "datastore"
        state_manager = StateManager(datastore_dir=datastore_dir)
        state_rollback = StateRollback(state_manager, datastore_dir=datastore_dir)
        return state_manager, state_rollback
    
    def test_full_workflow(self, integrated_system):
        """Test a complete state management workflow."""
        state_manager, state_rollback = integrated_system
        
        # Step 1: Create initial state
        initial_data = {'athletes': {'A001': {'name': 'John Doe'}}}
        state_1_id = state_manager.create_state_snapshot("Initial state", initial_data)
        
        # Step 2: Create rollback point
        rollback_1_id = state_rollback.create_rollback_point("Initial rollback", state_1_id)
        
        # Step 3: Make changes and create new state
        updated_data = {'athletes': {'A001': {'name': 'John Doe'}, 'A002': {'name': 'Jane Smith'}}}
        state_2_id = state_manager.create_state_snapshot("Updated state", updated_data)
        
        # Step 4: Create another rollback point
        rollback_2_id = state_rollback.create_rollback_point("Updated rollback", state_2_id)
        
        # Step 5: Execute rollback to initial state
        success = state_rollback.execute_rollback(rollback_1_id)
        
        assert success is True
        
        # Verify system state
        assert state_manager.state_index['metadata']['total_states'] == 2
        assert state_rollback.rollback_history['metadata']['total_rollbacks'] == 2
    
    def test_state_sequence_tracking(self, integrated_system):
        """Test state sequence tracking through multiple operations."""
        state_manager, state_rollback = integrated_system
        
        # Create a sequence of states
        state_ids = []
        for i in range(5):
            data = {'step': i, 'data': f'value_{i}'}
            state_id = state_manager.create_state_snapshot(f"Step {i+1}", data)
            state_ids.append(state_id)
            
            # Create rollback point for each state
            state_rollback.create_rollback_point(f"Rollback step {i+1}", state_id)
        
        # Verify sequence
        sequence = state_manager.get_state_sequence()
        assert len(sequence) == 5
        
        # Verify rollback history
        history = state_rollback.get_rollback_history()
        assert len(history) == 5
        
        # Test rollback to middle state
        middle_rollback = history[2]['rollback_id']
        success = state_rollback.execute_rollback(middle_rollback)
        assert success is True
    
    def test_data_integrity_validation(self, integrated_system):
        """Test data integrity validation throughout the workflow."""
        state_manager, state_rollback = integrated_system
        
        # Create state with complex data
        complex_data = {
            'athletes': {
                'A001': {'name': 'John Doe', 'rating': 1500.0, 'matches': [1, 2, 3]},
                'A002': {'name': 'Jane Smith', 'rating': 1450.0, 'matches': [4, 5]}
            },
            'divisions': {
                'D001': {'name': 'Adult Male Black Belt', 'athletes': ['A001']}
            },
            'metadata': {
                'total_athletes': 2,
                'total_divisions': 1,
                'checksum': 'abc123'
            }
        }
        
        # Create state and rollback point
        state_id = state_manager.create_state_snapshot("Complex state", complex_data)
        rollback_id = state_rollback.create_rollback_point("Complex rollback", state_id)
        
        # Validate integrity
        assert state_manager.validate_state_integrity(state_id) is True
        
        # Validate rollback safety
        safety = state_rollback.validate_rollback_safety(rollback_id)
        assert safety['safe'] is True
        
        # Execute rollback
        success = state_rollback.execute_rollback(rollback_id)
        assert success is True
    
    def test_error_handling(self, integrated_system):
        """Test error handling in state management."""
        state_manager, state_rollback = integrated_system
        
        # Test with invalid state ID
        invalid_state = state_manager.get_state("INVALID_ID")
        assert invalid_state is None
        
        # Test with invalid rollback ID
        invalid_rollback = state_rollback.get_rollback("INVALID_ID")
        assert invalid_rollback is None
        
        # Test rollback safety with invalid ID
        safety = state_rollback.validate_rollback_safety("INVALID_ID")
        assert safety['safe'] is False
        assert 'not found' in safety['reason']
        
        # Test executing invalid rollback
        success = state_rollback.execute_rollback("INVALID_ID")
        assert success is False
    
    def test_performance_with_large_data(self, integrated_system):
        """Test performance with larger datasets."""
        state_manager, state_rollback = integrated_system
        
        # Create large dataset
        large_data = {
            'athletes': {
                f'A{i:03d}': {
                    'name': f'Athlete {i}',
                    'rating': 1500.0 + (i % 500),
                    'matches': list(range(i % 10 + 1))
                }
                for i in range(100)
            },
            'metadata': {
                'total_athletes': 100,
                'version': '1.0'
            }
        }
        
        # Create state and rollback point
        state_id = state_manager.create_state_snapshot("Large state", large_data)
        rollback_id = state_rollback.create_rollback_point("Large rollback", state_id)
        
        # Validate integrity
        assert state_manager.validate_state_integrity(state_id) is True
        
        # Execute rollback
        success = state_rollback.execute_rollback(rollback_id)
        assert success is True
        
        # Verify data integrity after rollback
        retrieved_state = state_manager.get_state(state_id)
        assert retrieved_state is not None
        assert len(retrieved_state['data']['athletes']) == 100 