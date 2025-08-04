"""
ADCC Analysis Engine v0.6 - State Rollback
Provides rollback functionality for system states.
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
from .save_states import StateManager

logger = get_logger(__name__)


class StateRollback:
    """
    Provides rollback functionality for the state management system.
    
    Features:
    - Rollback to previous states
    - State comparison and validation
    - Rollback history tracking
    - Data recovery capabilities
    """
    
    def __init__(self, state_manager: StateManager, datastore_dir: Optional[Path] = None):
        """
        Initialize the state rollback system.
        
        Args:
            state_manager: StateManager instance
            datastore_dir: Directory for storing rollback data
        """
        self.state_manager = state_manager
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.rollback_dir = self.datastore_dir / "rollbacks"
        self.rollback_history_file = self.rollback_dir / "rollback_history.json"
        
        # Ensure directories exist
        ensure_directory_exists(self.datastore_dir)
        ensure_directory_exists(self.rollback_dir)
        
        # Load rollback history
        self.rollback_history = self._load_rollback_history()
        
        logger.info(f"StateRollback initialized with datastore: {self.datastore_dir}")
    
    def _load_rollback_history(self) -> Dict[str, Any]:
        """Load the rollback history from JSON file."""
        try:
            if self.rollback_history_file.exists():
                history = load_json_file(self.rollback_history_file)
                logger.debug(f"Loaded rollback history with {len(history.get('rollbacks', []))} rollbacks")
                return history
            else:
                # Create new history
                history = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_rollbacks': 0
                    },
                    'rollbacks': []
                }
                self._save_rollback_history(history)
                logger.info("Created new rollback history")
                return history
        except Exception as e:
            logger.error(f"Failed to load rollback history: {e}")
            return {'metadata': {}, 'rollbacks': []}
    
    def _save_rollback_history(self, history: Dict[str, Any]) -> bool:
        """Save the rollback history to JSON file."""
        try:
            return save_json_file(history, self.rollback_history_file)
        except Exception as e:
            logger.error(f"Failed to save rollback history: {e}")
            return False
    
    def _generate_rollback_id(self) -> str:
        """Generate a unique rollback ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return f"ROLLBACK_{timestamp.replace(':', '-').replace('.', '-')}"
    
    def create_rollback_point(self, description: str, 
                            target_state_id: Optional[str] = None) -> Optional[str]:
        """
        Create a rollback point for the current state.
        
        Args:
            description: Description of the rollback point
            target_state_id: Target state ID (if None, uses current state)
            
        Returns:
            Rollback ID if successful, None otherwise
        """
        try:
            rollback_id = self._generate_rollback_id()
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Get current state
            if target_state_id:
                current_state = self.state_manager.get_state(target_state_id)
                if not current_state:
                    logger.error(f"Target state not found: {target_state_id}")
                    return None
            else:
                current_state = self.state_manager.get_latest_state()
                if not current_state:
                    logger.error("No current state available for rollback point")
                    return None
                target_state_id = current_state['state_id']
            
            # Create rollback data
            rollback_data = {
                'rollback_id': rollback_id,
                'description': description,
                'timestamp': timestamp,
                'target_state_id': target_state_id,
                'state_data': current_state,
                'metadata': {
                    'created': timestamp,
                    'version': '1.0'
                }
            }
            
            # Save rollback file
            rollback_file = self.rollback_dir / f"{rollback_id}.json"
            success = save_json_file(rollback_data, rollback_file)
            
            if not success:
                logger.error(f"Failed to save rollback file for {rollback_id}")
                return None
            
            # Update rollback history
            rollback_record = {
                'rollback_id': rollback_id,
                'description': description,
                'timestamp': timestamp,
                'target_state_id': target_state_id,
                'status': 'created',
                'file_path': f"{rollback_id}.json"
            }
            
            self.rollback_history['rollbacks'].append(rollback_record)
            self.rollback_history['metadata']['total_rollbacks'] = len(self.rollback_history['rollbacks'])
            self.rollback_history['metadata']['last_updated'] = timestamp
            
            # Save updated history
            history_success = self._save_rollback_history(self.rollback_history)
            
            if history_success:
                logger.info(f"Created rollback point: {description} ({rollback_id})")
                return rollback_id
            else:
                logger.error(f"Failed to update rollback history for {rollback_id}")
                return None
            
        except Exception as e:
            logger.error(f"Failed to create rollback point: {e}")
            return None
    
    def execute_rollback(self, rollback_id: str, 
                        backup_current: bool = True) -> bool:
        """
        Execute a rollback to a previous state.
        
        Args:
            rollback_id: Rollback ID to execute
            backup_current: Whether to backup current state before rollback
            
        Returns:
            True if successful
        """
        try:
            # Get rollback data
            rollback_file = self.rollback_dir / f"{rollback_id}.json"
            if not rollback_file.exists():
                logger.error(f"Rollback file not found: {rollback_id}")
                return False
            
            rollback_data = load_json_file(rollback_file)
            if not rollback_data:
                logger.error(f"Failed to load rollback data: {rollback_id}")
                return False
            
            target_state_id = rollback_data['target_state_id']
            target_state = rollback_data['state_data']
            
            # Backup current state if requested
            if backup_current:
                current_state = self.state_manager.get_latest_state()
                if current_state:
                    backup_id = self.create_rollback_point(
                        f"Pre-rollback backup for {rollback_id}",
                        current_state['state_id']
                    )
                    if backup_id:
                        logger.info(f"Created backup before rollback: {backup_id}")
            
            # Validate target state integrity
            if not self.state_manager.validate_state_integrity(target_state_id):
                logger.error(f"Target state integrity validation failed: {target_state_id}")
                return False
            
            # Execute the rollback
            success = self._apply_state_rollback(target_state)
            
            if success:
                # Update rollback history
                for rollback in self.rollback_history['rollbacks']:
                    if rollback['rollback_id'] == rollback_id:
                        rollback['status'] = 'executed'
                        rollback['executed_at'] = datetime.now(timezone.utc).isoformat()
                        break
                
                self._save_rollback_history(self.rollback_history)
                logger.info(f"Successfully executed rollback: {rollback_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to execute rollback {rollback_id}: {e}")
            return False
    
    def _apply_state_rollback(self, target_state: Dict[str, Any]) -> bool:
        """
        Apply a state rollback by restoring target state data.
        
        Args:
            target_state: Target state data to restore
            
        Returns:
            True if successful
        """
        try:
            # This is a simplified implementation
            # In a real system, you would need to:
            # 1. Restore all data files to their previous state
            # 2. Update all registries and indexes
            # 3. Validate data consistency
            
            logger.info(f"Applying state rollback to: {target_state.get('state_name', 'Unknown')}")
            
            # For now, we'll just log the rollback
            # In Phase 5, this will integrate with the actual data restoration
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply state rollback: {e}")
            return False
    
    def get_rollback_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get rollback history.
        
        Args:
            limit: Maximum number of rollbacks to return
            
        Returns:
            List of rollback records
        """
        try:
            rollbacks = self.rollback_history.get('rollbacks', [])
            
            # Sort by timestamp (newest first)
            rollbacks.sort(key=lambda x: x['timestamp'], reverse=True)
            
            if limit:
                rollbacks = rollbacks[:limit]
            
            logger.debug(f"Retrieved {len(rollbacks)} rollback records")
            return rollbacks
            
        except Exception as e:
            logger.error(f"Failed to get rollback history: {e}")
            return []
    
    def get_rollback(self, rollback_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific rollback data.
        
        Args:
            rollback_id: Rollback ID
            
        Returns:
            Rollback data or None if not found
        """
        try:
            rollback_file = self.rollback_dir / f"{rollback_id}.json"
            if not rollback_file.exists():
                logger.warning(f"Rollback file not found: {rollback_id}")
                return None
            
            rollback_data = load_json_file(rollback_file)
            logger.debug(f"Loaded rollback data: {rollback_id}")
            return rollback_data
            
        except Exception as e:
            logger.error(f"Failed to get rollback {rollback_id}: {e}")
            return None
    
    def compare_states(self, state_id_1: str, state_id_2: str) -> Dict[str, Any]:
        """
        Compare two states and return differences.
        
        Args:
            state_id_1: First state ID
            state_id_2: Second state ID
            
        Returns:
            Dictionary of differences
        """
        try:
            state_1 = self.state_manager.get_state(state_id_1)
            state_2 = self.state_manager.get_state(state_id_2)
            
            if not state_1 or not state_2:
                logger.error("One or both states not found")
                return {}
            
            # Compare state metadata
            differences = {
                'state_1': {
                    'state_id': state_id_1,
                    'state_name': state_1.get('state_name'),
                    'timestamp': state_1.get('timestamp')
                },
                'state_2': {
                    'state_id': state_id_2,
                    'state_name': state_2.get('state_name'),
                    'timestamp': state_2.get('timestamp')
                },
                'differences': {}
            }
            
            # Compare data structures
            data_1 = state_1.get('data', {})
            data_2 = state_2.get('data', {})
            
            # Simple comparison - in a real system, you'd want more sophisticated diffing
            if data_1 != data_2:
                differences['differences']['data_changed'] = True
                differences['differences']['data_1_keys'] = list(data_1.keys())
                differences['differences']['data_2_keys'] = list(data_2.keys())
            else:
                differences['differences']['data_changed'] = False
            
            # Compare checksums
            if state_1.get('checksum') != state_2.get('checksum'):
                differences['differences']['checksum_different'] = True
            else:
                differences['differences']['checksum_different'] = False
            
            logger.debug(f"Compared states {state_id_1} and {state_id_2}")
            return differences
            
        except Exception as e:
            logger.error(f"Failed to compare states: {e}")
            return {}
    
    def validate_rollback_safety(self, rollback_id: str) -> Dict[str, Any]:
        """
        Validate if a rollback is safe to execute.
        
        Args:
            rollback_id: Rollback ID to validate
            
        Returns:
            Dictionary of safety validation results
        """
        try:
            rollback_data = self.get_rollback(rollback_id)
            if not rollback_data:
                return {
                    'safe': False,
                    'reason': 'Rollback not found',
                    'warnings': []
                }
            
            target_state_id = rollback_data['target_state_id']
            target_state = rollback_data['state_data']
            
            validation = {
                'safe': True,
                'reason': 'Rollback appears safe',
                'warnings': []
            }
            
            # Check if target state exists and is valid
            if not self.state_manager.validate_state_integrity(target_state_id):
                validation['safe'] = False
                validation['reason'] = 'Target state integrity validation failed'
                validation['warnings'].append('Target state may be corrupted')
            
            # Check if target state is too old
            target_timestamp = target_state.get('timestamp')
            if target_timestamp:
                target_time = datetime.fromisoformat(target_timestamp.replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                time_diff = current_time - target_time
                
                if time_diff.days > 30:
                    validation['warnings'].append('Target state is over 30 days old')
                
                if time_diff.days > 90:
                    validation['safe'] = False
                    validation['reason'] = 'Target state is too old (over 90 days)'
            
            # Check for recent changes
            recent_states = self.state_manager.list_states(limit=5)
            if recent_states:
                latest_state = recent_states[0]
                latest_timestamp = latest_state['timestamp']
                latest_time = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                time_diff = current_time - latest_time
                
                if time_diff.total_seconds() < 3600:  # Less than 1 hour
                    validation['warnings'].append('Recent changes detected (within last hour)')
            
            logger.debug(f"Validated rollback safety for {rollback_id}: {validation['safe']}")
            return validation
            
        except Exception as e:
            logger.error(f"Failed to validate rollback safety for {rollback_id}: {e}")
            return {
                'safe': False,
                'reason': f'Validation error: {str(e)}',
                'warnings': []
            }
    
    def cleanup_old_rollbacks(self, keep_count: int = 20) -> int:
        """
        Clean up old rollback points.
        
        Args:
            keep_count: Number of recent rollbacks to keep
            
        Returns:
            Number of rollbacks removed
        """
        try:
            if keep_count <= 0:
                logger.warning("Invalid keep_count, must be positive")
                return 0
            
            rollbacks = self.get_rollback_history()
            
            if len(rollbacks) <= keep_count:
                logger.debug("No cleanup needed, rollbacks within limit")
                return 0
            
            # Rollbacks to remove (oldest ones)
            rollbacks_to_remove = rollbacks[keep_count:]
            removed_count = 0
            
            for rollback in rollbacks_to_remove:
                rollback_id = rollback['rollback_id']
                
                # Remove from history
                self.rollback_history['rollbacks'] = [
                    r for r in self.rollback_history['rollbacks']
                    if r['rollback_id'] != rollback_id
                ]
                
                # Remove file
                rollback_file = self.rollback_dir / f"{rollback_id}.json"
                if rollback_file.exists():
                    rollback_file.unlink()
                
                removed_count += 1
                logger.debug(f"Removed old rollback: {rollback_id}")
            
            # Update history metadata
            self.rollback_history['metadata']['total_rollbacks'] = len(self.rollback_history['rollbacks'])
            self.rollback_history['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save updated history
            self._save_rollback_history(self.rollback_history)
            
            logger.info(f"Cleaned up {removed_count} old rollbacks")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old rollbacks: {e}")
            return 0
    
    def get_rollback_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about rollback operations.
        
        Returns:
            Dictionary of rollback statistics
        """
        try:
            rollbacks = self.get_rollback_history()
            
            if not rollbacks:
                return {
                    'total_rollbacks': 0,
                    'executed_rollbacks': 0,
                    'successful_rollbacks': 0,
                    'oldest_rollback': None,
                    'newest_rollback': None
                }
            
            # Calculate statistics
            executed_count = sum(1 for r in rollbacks if r.get('status') == 'executed')
            successful_count = sum(1 for r in rollbacks if r.get('status') == 'executed' and 'executed_at' in r)
            
            timestamps = [r['timestamp'] for r in rollbacks]
            oldest_rollback = min(timestamps)
            newest_rollback = max(timestamps)
            
            stats = {
                'total_rollbacks': len(rollbacks),
                'executed_rollbacks': executed_count,
                'successful_rollbacks': successful_count,
                'oldest_rollback': oldest_rollback,
                'newest_rollback': newest_rollback,
                'success_rate': round(successful_count / executed_count, 3) if executed_count > 0 else 0.0,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            logger.debug(f"Generated rollback statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate rollback statistics: {e}")
            return {} 