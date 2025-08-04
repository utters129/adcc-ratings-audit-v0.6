"""
ADCC Analysis Engine v0.6 - State Management
Manages system state snapshots and persistence.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd

from src.core.constants import DATASTORE_DIR
from src.utils.file_handler import save_json_file, load_json_file, ensure_directory_exists, save_parquet_file
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """
    Manages state snapshots and persistence for the data processing pipeline.
    
    Features:
    - State snapshots with timestamps
    - Data integrity validation
    - Chronological processing tracking
    - State rollback capabilities
    """
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the state manager.
        
        Args:
            datastore_dir: Directory for storing state data
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.states_dir = self.datastore_dir / "states"
        self.state_index_file = self.states_dir / "state_index.json"
        
        # Ensure directories exist
        ensure_directory_exists(self.datastore_dir)
        ensure_directory_exists(self.states_dir)
        
        # Load state index
        self.state_index = self._load_state_index()
        
        logger.info(f"StateManager initialized with datastore: {self.datastore_dir}")
    
    def _load_state_index(self) -> Dict[str, Any]:
        """Load the state index from JSON file."""
        try:
            if self.state_index_file.exists():
                index = load_json_file(self.state_index_file)
                logger.debug(f"Loaded state index with {len(index.get('states', {}))} states")
                return index
            else:
                # Create new index
                index = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_states': 0,
                        'last_state_id': None
                    },
                    'states': {},
                    'processing_sequence': []
                }
                self._save_state_index(index)
                logger.info("Created new state index")
                return index
        except Exception as e:
            logger.error(f"Failed to load state index: {e}")
            return {'metadata': {}, 'states': {}, 'processing_sequence': []}
    
    def _save_state_index(self, index: Dict[str, Any]) -> bool:
        """Save the state index to JSON file."""
        try:
            return save_json_file(index, self.state_index_file)
        except Exception as e:
            logger.error(f"Failed to save state index: {e}")
            return False
    
    def _generate_state_id(self) -> str:
        """Generate a unique state ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return f"STATE_{timestamp.replace(':', '-').replace('.', '-')}"
    
    def _calculate_checksum(self, data: Union[Dict[str, Any], pd.DataFrame]) -> str:
        """Calculate checksum for data integrity validation."""
        try:
            if isinstance(data, pd.DataFrame):
                # Convert DataFrame to string representation for checksum
                data_str = data.to_json(orient='records')
            else:
                data_str = json.dumps(data, sort_keys=True)
            
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return ""
    
    def create_state_snapshot(self, state_name: str, data: Dict[str, Any], 
                            metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create a new state snapshot.
        
        Args:
            state_name: Name/description of the state
            data: Data to snapshot
            metadata: Additional metadata
            
        Returns:
            State ID if successful, None otherwise
        """
        try:
            state_id = self._generate_state_id()
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Calculate checksum for data integrity
            checksum = self._calculate_checksum(data)
            
            # Create state data
            state_data = {
                'state_id': state_id,
                'state_name': state_name,
                'timestamp': timestamp,
                'data': data,
                'checksum': checksum,
                'metadata': metadata or {},
                'version': '1.0'
            }
            
            # Save state file
            state_file = self.states_dir / f"{state_id}.json"
            success = save_json_file(state_data, state_file)
            
            if not success:
                logger.error(f"Failed to save state file for {state_id}")
                return None
            
            # Update state index
            self.state_index['states'][state_id] = {
                'state_name': state_name,
                'timestamp': timestamp,
                'file_path': f"{state_id}.json",
                'checksum': checksum,
                'metadata': metadata or {}
            }
            
            self.state_index['processing_sequence'].append(state_id)
            self.state_index['metadata']['total_states'] = len(self.state_index['states'])
            self.state_index['metadata']['last_state_id'] = state_id
            self.state_index['metadata']['last_updated'] = timestamp
            
            # Save updated index
            index_success = self._save_state_index(self.state_index)
            
            if index_success:
                logger.info(f"Created state snapshot: {state_name} ({state_id})")
                return state_id
            else:
                logger.error(f"Failed to update state index for {state_id}")
                return None
            
        except Exception as e:
            logger.error(f"Failed to create state snapshot: {e}")
            return None
    
    def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a state snapshot by ID.
        
        Args:
            state_id: State ID
            
        Returns:
            State data or None if not found
        """
        try:
            if state_id not in self.state_index['states']:
                logger.warning(f"State not found in index: {state_id}")
                return None
            
            state_info = self.state_index['states'][state_id]
            state_file = self.states_dir / state_info['file_path']
            
            if not state_file.exists():
                logger.warning(f"State file not found: {state_file}")
                return None
            
            state_data = load_json_file(state_file)
            
            # Validate checksum
            if state_data and 'data' in state_data:
                current_checksum = self._calculate_checksum(state_data['data'])
                if current_checksum != state_data.get('checksum', ''):
                    logger.warning(f"Checksum mismatch for state {state_id}")
                    return None
            
            logger.debug(f"Loaded state: {state_id}")
            return state_data
            
        except Exception as e:
            logger.error(f"Failed to get state {state_id}: {e}")
            return None
    
    def get_latest_state(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent state snapshot.
        
        Returns:
            Latest state data or None if no states exist
        """
        try:
            if not self.state_index['states']:
                logger.debug("No states available")
                return None
            
            latest_state_id = self.state_index['metadata']['last_state_id']
            if latest_state_id:
                return self.get_state(latest_state_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest state: {e}")
            return None
    
    def get_state_sequence(self, start_state_id: Optional[str] = None, 
                          end_state_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a sequence of states.
        
        Args:
            start_state_id: Starting state ID (inclusive)
            end_state_id: Ending state ID (inclusive)
            
        Returns:
            List of state data in chronological order
        """
        try:
            sequence = self.state_index['processing_sequence']
            
            if not sequence:
                return []
            
            # Determine start and end indices
            start_idx = 0
            end_idx = len(sequence)
            
            if start_state_id:
                try:
                    start_idx = sequence.index(start_state_id)
                except ValueError:
                    logger.warning(f"Start state ID not found: {start_state_id}")
                    return []
            
            if end_state_id:
                try:
                    end_idx = sequence.index(end_state_id) + 1
                except ValueError:
                    logger.warning(f"End state ID not found: {end_state_id}")
                    return []
            
            # Get states in sequence
            state_sequence = []
            for state_id in sequence[start_idx:end_idx]:
                state_data = self.get_state(state_id)
                if state_data:
                    state_sequence.append(state_data)
            
            logger.debug(f"Retrieved {len(state_sequence)} states in sequence")
            return state_sequence
            
        except Exception as e:
            logger.error(f"Failed to get state sequence: {e}")
            return []
    
    def list_states(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all available states.
        
        Args:
            limit: Maximum number of states to return
            
        Returns:
            List of state information
        """
        try:
            states = []
            for state_id, state_info in self.state_index['states'].items():
                state_summary = {
                    'state_id': state_id,
                    'state_name': state_info['state_name'],
                    'timestamp': state_info['timestamp'],
                    'metadata': state_info.get('metadata', {})
                }
                states.append(state_summary)
            
            # Sort by timestamp (newest first)
            states.sort(key=lambda x: x['timestamp'], reverse=True)
            
            if limit:
                states = states[:limit]
            
            logger.debug(f"Listed {len(states)} states")
            return states
            
        except Exception as e:
            logger.error(f"Failed to list states: {e}")
            return []
    
    def validate_state_integrity(self, state_id: str) -> bool:
        """
        Validate the integrity of a state snapshot.
        
        Args:
            state_id: State ID to validate
            
        Returns:
            True if state is valid
        """
        try:
            state_data = self.get_state(state_id)
            if not state_data:
                return False
            
            # Check if checksum matches
            if 'data' in state_data and 'checksum' in state_data:
                current_checksum = self._calculate_checksum(state_data['data'])
                if current_checksum != state_data['checksum']:
                    logger.warning(f"Checksum validation failed for state {state_id}")
                    return False
            
            # Check if file exists and is readable
            state_info = self.state_index['states'].get(state_id)
            if state_info:
                state_file = self.states_dir / state_info['file_path']
                if not state_file.exists():
                    logger.warning(f"State file missing: {state_file}")
                    return False
            
            logger.debug(f"State integrity validated: {state_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate state integrity for {state_id}: {e}")
            return False
    
    def cleanup_old_states(self, keep_count: int = 10) -> int:
        """
        Clean up old state snapshots, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent states to keep
            
        Returns:
            Number of states removed
        """
        try:
            if keep_count <= 0:
                logger.warning("Invalid keep_count, must be positive")
                return 0
            
            # Get all states sorted by timestamp
            all_states = self.list_states()
            
            if len(all_states) <= keep_count:
                logger.debug("No cleanup needed, states within limit")
                return 0
            
            # States to remove (oldest ones)
            states_to_remove = all_states[keep_count:]
            removed_count = 0
            
            for state_info in states_to_remove:
                state_id = state_info['state_id']
                
                # Remove from index
                if state_id in self.state_index['states']:
                    del self.state_index['states'][state_id]
                
                # Remove from processing sequence
                if state_id in self.state_index['processing_sequence']:
                    self.state_index['processing_sequence'].remove(state_id)
                
                # Remove file
                state_file = self.states_dir / f"{state_id}.json"
                if state_file.exists():
                    state_file.unlink()
                
                removed_count += 1
                logger.debug(f"Removed old state: {state_id}")
            
            # Update index metadata
            self.state_index['metadata']['total_states'] = len(self.state_index['states'])
            self.state_index['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save updated index
            self._save_state_index(self.state_index)
            
            logger.info(f"Cleaned up {removed_count} old states")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old states: {e}")
            return 0
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all states.
        
        Returns:
            Dictionary of state statistics
        """
        try:
            states = self.list_states()
            
            if not states:
                return {
                    'total_states': 0,
                    'oldest_state': None,
                    'newest_state': None,
                    'state_types': {},
                    'total_size_mb': 0.0
                }
            
            # Calculate statistics
            timestamps = [s['timestamp'] for s in states]
            oldest_state = min(timestamps)
            newest_state = max(timestamps)
            
            # Count state types
            state_types = {}
            for state in states:
                state_name = state['state_name']
                state_types[state_name] = state_types.get(state_name, 0) + 1
            
            # Calculate total size
            total_size = 0.0
            for state in states:
                state_file = self.states_dir / f"{state['state_id']}.json"
                if state_file.exists():
                    total_size += state_file.stat().st_size / (1024 * 1024)  # Convert to MB
            
            stats = {
                'total_states': len(states),
                'oldest_state': oldest_state,
                'newest_state': newest_state,
                'state_types': state_types,
                'total_size_mb': round(total_size, 2),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            logger.debug(f"Generated state statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate state statistics: {e}")
            return {}
    
    def export_state_to_parquet(self, state_id: str, output_path: Path) -> bool:
        """
        Export state data to Parquet format.
        
        Args:
            state_id: State ID to export
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            state_data = self.get_state(state_id)
            if not state_data or 'data' not in state_data:
                logger.warning(f"No data found in state {state_id}")
                return False
            
            data = state_data['data']
            
            # Convert to DataFrame if it's a dictionary
            if isinstance(data, dict):
                # Try to convert to DataFrame
                if 'records' in data:
                    df = pd.DataFrame(data['records'])
                else:
                    # Convert dict to DataFrame
                    df = pd.DataFrame([data])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                logger.warning(f"Unsupported data type for Parquet export: {type(data)}")
                return False
            
            # Save to Parquet
            success = save_parquet_file(df, output_path)
            
            if success:
                logger.info(f"Exported state {state_id} to Parquet: {output_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to export state {state_id} to Parquet: {e}")
            return False 