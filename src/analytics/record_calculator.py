"""
ADCC Analysis Engine v0.6 - Record Calculator
Tracks win/loss records and match history for athletes.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pandas as pd

from core.constants import DATASTORE_DIR
from core.models import Athlete, Match
from utils.file_handler import save_json_file, load_json_file, save_parquet_file, load_parquet_file
from utils.logger import get_logger

logger = get_logger(__name__)


class RecordCalculator:
    """
    Calculates and tracks win/loss records for ADCC athletes.
    
    Features:
    - Win/loss record calculation
    - Match history tracking
    - Performance statistics
    - Record accuracy validation
    - Historical trend analysis
    """
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the record calculator.
        
        Args:
            datastore_dir: Directory for storing record data
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.records_file = self.datastore_dir / "athlete_records.json"
        self.match_history_file = self.datastore_dir / "match_history.parquet"
        self.statistics_file = self.datastore_dir / "record_statistics.json"
        
        # Load existing record data
        self.athlete_records = self._load_athlete_records()
        self.match_history = self._load_match_history()
        self.record_statistics = self._load_record_statistics()
        
        logger.info(f"RecordCalculator initialized with datastore: {self.datastore_dir}")
    
    def _load_athlete_records(self) -> Dict[str, Dict[str, Any]]:
        """Load athlete records from JSON file."""
        try:
            if self.records_file.exists():
                records = load_json_file(self.records_file)
                logger.debug(f"Loaded records for {len(records.get('athletes', {}))} athletes")
                return records
            else:
                # Create new records registry
                records = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_athletes': 0
                    },
                    'athletes': {}
                }
                self._save_athlete_records(records)
                logger.info("Created new athlete records registry")
                return records
        except Exception as e:
            logger.error(f"Failed to load athlete records: {e}")
            return {'metadata': {}, 'athletes': {}}
    
    def _save_athlete_records(self, records: Dict[str, Any]) -> bool:
        """Save athlete records to JSON file."""
        try:
            return save_json_file(records, self.records_file)
        except Exception as e:
            logger.error(f"Failed to save athlete records: {e}")
            return False
    
    def _load_match_history(self) -> pd.DataFrame:
        """Load match history from Parquet file."""
        try:
            if self.match_history_file.exists():
                history = load_parquet_file(self.match_history_file)
                logger.debug(f"Loaded match history with {len(history)} records")
                return history
            else:
                # Create new match history
                history = pd.DataFrame(columns=[
                    'match_id', 'event_id', 'division_id', 'athlete1_id', 'athlete2_id',
                    'winner_id', 'win_type', 'bracket_round', 'match_date', 'timestamp'
                ])
                self._save_match_history(history)
                logger.info("Created new match history")
                return history
        except Exception as e:
            logger.error(f"Failed to load match history: {e}")
            return pd.DataFrame()
    
    def _save_match_history(self, history: pd.DataFrame) -> bool:
        """Save match history to Parquet file."""
        try:
            return save_parquet_file(history, self.match_history_file)
        except Exception as e:
            logger.error(f"Failed to save match history: {e}")
            return False
    
    def _load_record_statistics(self) -> Dict[str, Any]:
        """Load record statistics from JSON file."""
        try:
            if self.statistics_file.exists():
                stats = load_json_file(self.statistics_file)
                logger.debug("Loaded record statistics")
                return stats
            else:
                # Create new statistics
                stats = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'last_updated': datetime.now(timezone.utc).isoformat()
                    },
                    'total_matches': 0,
                    'total_athletes': 0,
                    'average_win_rate': 0.0,
                    'win_rate_distribution': {},
                    'most_active_athletes': [],
                    'longest_win_streaks': [],
                    'longest_lose_streaks': []
                }
                self._save_record_statistics(stats)
                logger.info("Created new record statistics")
                return stats
        except Exception as e:
            logger.error(f"Failed to load record statistics: {e}")
            return {}
    
    def _save_record_statistics(self, stats: Dict[str, Any]) -> bool:
        """Save record statistics to JSON file."""
        try:
            return save_json_file(stats, self.statistics_file)
        except Exception as e:
            logger.error(f"Failed to save record statistics: {e}")
            return False
    
    def initialize_athlete(self, athlete_id: str) -> bool:
        """
        Initialize an athlete's record.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if athlete_id in self.athlete_records['athletes']:
                logger.warning(f"Athlete {athlete_id} already has records")
                return True
            
            # Create athlete record entry
            self.athlete_records['athletes'][athlete_id] = {
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'total_matches': 0,
                'win_rate': 0.0,
                'current_streak': 0,
                'longest_win_streak': 0,
                'longest_lose_streak': 0,
                'last_match_date': None,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'match_history': []
            }
            
            # Update metadata
            self.athlete_records['metadata']['total_athletes'] = len(self.athlete_records['athletes'])
            self.athlete_records['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save records
            success = self._save_athlete_records(self.athlete_records)
            
            if success:
                logger.info(f"Initialized records for athlete {athlete_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize athlete {athlete_id}: {e}")
            return False
    
    def get_athlete_record(self, athlete_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an athlete's current record.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            Record data or None if not found
        """
        try:
            return self.athlete_records['athletes'].get(athlete_id)
        except Exception as e:
            logger.error(f"Failed to get record for athlete {athlete_id}: {e}")
            return None
    
    def process_match(self, match: Match, winner_id: str) -> bool:
        """
        Process a match and update both athletes' records.
        
        Args:
            match: Match data
            winner_id: ID of the winning athlete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize athletes if needed
            if match.athlete1_id not in self.athlete_records['athletes']:
                self.initialize_athlete(match.athlete1_id)
            
            if match.athlete2_id not in self.athlete_records['athletes']:
                self.initialize_athlete(match.athlete2_id)
            
            # Determine match outcome
            if winner_id == match.athlete1_id:
                outcome1, outcome2 = 'win', 'loss'
            elif winner_id == match.athlete2_id:
                outcome1, outcome2 = 'loss', 'win'
            else:
                # Draw (shouldn't happen in ADCC but handle it)
                outcome1, outcome2 = 'draw', 'draw'
            
            # Update both athletes
            success1 = self._update_athlete_record(match.athlete1_id, outcome1, match)
            success2 = self._update_athlete_record(match.athlete2_id, outcome2, match)
            
            if success1 and success2:
                # Add to match history
                history_entry = {
                    'match_id': match.id,
                    'event_id': match.event_id,
                    'division_id': match.division_id,
                    'athlete1_id': match.athlete1_id,
                    'athlete2_id': match.athlete2_id,
                    'winner_id': winner_id,
                    'win_type': match.win_type,
                    'bracket_round': match.bracket_round,
                    'match_date': match.match_date.isoformat(),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                new_row = pd.DataFrame([history_entry])
                self.match_history = pd.concat([self.match_history, new_row], ignore_index=True)
                self._save_match_history(self.match_history)
                
                logger.info(f"Processed match {match.id}: {match.athlete1_id} vs {match.athlete2_id}, winner: {winner_id}")
            
            return success1 and success2
            
        except Exception as e:
            logger.error(f"Failed to process match {match.id}: {e}")
            return False
    
    def _update_athlete_record(self, athlete_id: str, outcome: str, match: Match) -> bool:
        """
        Update an athlete's record after a match.
        
        Args:
            athlete_id: Athlete ID to update
            outcome: Match outcome ('win', 'loss', or 'draw')
            match: Match data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if athlete_id not in self.athlete_records['athletes']:
                logger.error(f"Athlete {athlete_id} not found in records")
                return False
            
            record = self.athlete_records['athletes'][athlete_id]
            
            # Update match counts
            record['total_matches'] += 1
            
            if outcome == 'win':
                record['wins'] += 1
                if record['current_streak'] >= 0:
                    record['current_streak'] += 1
                else:
                    record['current_streak'] = 1
                record['longest_win_streak'] = max(record['longest_win_streak'], record['current_streak'])
            elif outcome == 'loss':
                record['losses'] += 1
                if record['current_streak'] <= 0:
                    record['current_streak'] -= 1
                else:
                    record['current_streak'] = -1
                record['longest_lose_streak'] = max(record['longest_lose_streak'], abs(record['current_streak']))
            else:  # draw
                record['draws'] += 1
                record['current_streak'] = 0
            
            # Calculate win rate
            if record['total_matches'] > 0:
                record['win_rate'] = record['wins'] / record['total_matches']
            else:
                record['win_rate'] = 0.0
            
            # Update last match date
            record['last_match_date'] = match.match_date.isoformat()
            record['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Add to match history
            match_summary = {
                'match_id': match.id,
                'event_id': match.event_id,
                'division_id': match.division_id,
                'opponent_id': match.athlete2_id if athlete_id == match.athlete1_id else match.athlete1_id,
                'outcome': outcome,
                'win_type': match.win_type,
                'bracket_round': match.bracket_round,
                'match_date': match.match_date.isoformat()
            }
            record['match_history'].append(match_summary)
            
            # Keep only last 50 matches in memory
            if len(record['match_history']) > 50:
                record['match_history'] = record['match_history'][-50:]
            
            # Save updated records
            success = self._save_athlete_records(self.athlete_records)
            
            if success:
                logger.debug(f"Updated record for {athlete_id}: {outcome} (W:{record['wins']} L:{record['losses']} D:{record['draws']})")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update record for athlete {athlete_id}: {e}")
            return False
    
    def get_athlete_match_history(self, athlete_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get an athlete's match history.
        
        Args:
            athlete_id: Unique athlete ID
            limit: Maximum number of matches to return
            
        Returns:
            List of match records
        """
        try:
            record = self.get_athlete_record(athlete_id)
            if not record:
                return []
            
            history = record.get('match_history', [])
            
            if limit:
                history = history[-limit:]
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get match history for athlete {athlete_id}: {e}")
            return []
    
    def calculate_win_streak(self, athlete_id: str) -> int:
        """
        Calculate an athlete's current win streak.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            Current win streak (positive) or lose streak (negative)
        """
        try:
            record = self.get_athlete_record(athlete_id)
            if not record:
                return 0
            
            return record.get('current_streak', 0)
            
        except Exception as e:
            logger.error(f"Failed to calculate win streak for athlete {athlete_id}: {e}")
            return 0
    
    def get_athletes_by_win_rate(self, min_matches: int = 5) -> List[Tuple[str, float]]:
        """
        Get athletes sorted by win rate.
        
        Args:
            min_matches: Minimum number of matches required
            
        Returns:
            List of (athlete_id, win_rate) tuples sorted by win rate
        """
        try:
            athletes = []
            
            for athlete_id, record in self.athlete_records['athletes'].items():
                if record['total_matches'] >= min_matches:
                    athletes.append((athlete_id, record['win_rate']))
            
            # Sort by win rate (descending)
            athletes.sort(key=lambda x: x[1], reverse=True)
            
            logger.debug(f"Found {len(athletes)} athletes with {min_matches}+ matches")
            return athletes
            
        except Exception as e:
            logger.error(f"Failed to get athletes by win rate: {e}")
            return []
    
    def get_most_active_athletes(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most active athletes by total matches.
        
        Args:
            limit: Maximum number of athletes to return
            
        Returns:
            List of (athlete_id, total_matches) tuples sorted by matches
        """
        try:
            athletes = []
            
            for athlete_id, record in self.athlete_records['athletes'].items():
                athletes.append((athlete_id, record['total_matches']))
            
            # Sort by total matches (descending)
            athletes.sort(key=lambda x: x[1], reverse=True)
            
            return athletes[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get most active athletes: {e}")
            return []
    
    def validate_record_accuracy(self, athlete_id: str) -> Dict[str, Any]:
        """
        Validate the accuracy of an athlete's record.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            Dictionary with validation results
        """
        try:
            record = self.get_athlete_record(athlete_id)
            if not record:
                return {
                    'valid': False,
                    'reason': 'Athlete not found',
                    'discrepancies': []
                }
            
            # Check if totals match
            calculated_total = record['wins'] + record['losses'] + record['draws']
            stored_total = record['total_matches']
            
            discrepancies = []
            
            if calculated_total != stored_total:
                discrepancies.append(f"Total mismatch: calculated={calculated_total}, stored={stored_total}")
            
            # Check win rate calculation
            if stored_total > 0:
                calculated_win_rate = record['wins'] / stored_total
                if abs(calculated_win_rate - record['win_rate']) > 0.001:
                    discrepancies.append(f"Win rate mismatch: calculated={calculated_win_rate:.3f}, stored={record['win_rate']:.3f}")
            
            # Check streak consistency
            if record['current_streak'] > record['longest_win_streak']:
                discrepancies.append(f"Current streak ({record['current_streak']}) exceeds longest win streak ({record['longest_win_streak']})")
            
            if record['current_streak'] < 0 and abs(record['current_streak']) > record['longest_lose_streak']:
                discrepancies.append(f"Current streak ({abs(record['current_streak'])}) exceeds longest lose streak ({record['longest_lose_streak']})")
            
            validation = {
                'valid': len(discrepancies) == 0,
                'reason': 'Record is accurate' if len(discrepancies) == 0 else 'Found discrepancies',
                'discrepancies': discrepancies,
                'total_matches': stored_total,
                'wins': record['wins'],
                'losses': record['losses'],
                'draws': record['draws'],
                'win_rate': record['win_rate']
            }
            
            logger.debug(f"Validated record for {athlete_id}: {validation['valid']}")
            return validation
            
        except Exception as e:
            logger.error(f"Failed to validate record for athlete {athlete_id}: {e}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'discrepancies': []
            }
    
    def update_record_statistics(self) -> bool:
        """
        Update overall record statistics.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            athletes = self.athlete_records['athletes']
            
            if not athletes:
                self.record_statistics.update({
                    'total_matches': 0,
                    'total_athletes': 0,
                    'average_win_rate': 0.0,
                    'win_rate_distribution': {},
                    'most_active_athletes': [],
                    'longest_win_streaks': [],
                    'longest_lose_streaks': []
                })
            else:
                # Calculate statistics
                total_matches = sum(athlete['total_matches'] for athlete in athletes.values())
                total_athletes = len(athletes)
                
                # Average win rate (only for athletes with matches)
                athletes_with_matches = [a for a in athletes.values() if a['total_matches'] > 0]
                if athletes_with_matches:
                    average_win_rate = sum(a['win_rate'] for a in athletes_with_matches) / len(athletes_with_matches)
                else:
                    average_win_rate = 0.0
                
                # Win rate distribution
                win_rate_distribution = {
                    '0.0-0.2': len([a for a in athletes_with_matches if 0.0 <= a['win_rate'] < 0.2]),
                    '0.2-0.4': len([a for a in athletes_with_matches if 0.2 <= a['win_rate'] < 0.4]),
                    '0.4-0.6': len([a for a in athletes_with_matches if 0.4 <= a['win_rate'] < 0.6]),
                    '0.6-0.8': len([a for a in athletes_with_matches if 0.6 <= a['win_rate'] < 0.8]),
                    '0.8-1.0': len([a for a in athletes_with_matches if 0.8 <= a['win_rate'] <= 1.0])
                }
                
                # Most active athletes
                most_active = self.get_most_active_athletes(10)
                
                # Longest streaks
                longest_win_streaks = sorted(
                    [(aid, athlete['longest_win_streak']) for aid, athlete in athletes.items()],
                    key=lambda x: x[1], reverse=True
                )[:10]
                
                longest_lose_streaks = sorted(
                    [(aid, athlete['longest_lose_streak']) for aid, athlete in athletes.items()],
                    key=lambda x: x[1], reverse=True
                )[:10]
                
                self.record_statistics.update({
                    'total_matches': total_matches,
                    'total_athletes': total_athletes,
                    'average_win_rate': average_win_rate,
                    'win_rate_distribution': win_rate_distribution,
                    'most_active_athletes': most_active,
                    'longest_win_streaks': longest_win_streaks,
                    'longest_lose_streaks': longest_lose_streaks
                })
            
            # Update metadata
            self.record_statistics['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save statistics
            success = self._save_record_statistics(self.record_statistics)
            
            if success:
                logger.debug(f"Updated record statistics: {self.record_statistics['total_athletes']} athletes, {self.record_statistics['total_matches']} matches")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update record statistics: {e}")
            return False
    
    def get_record_statistics(self) -> Dict[str, Any]:
        """
        Get current record statistics.
        
        Returns:
            Dictionary of record statistics
        """
        try:
            # Update statistics first
            self.update_record_statistics()
            return self.record_statistics
            
        except Exception as e:
            logger.error(f"Failed to get record statistics: {e}")
            return {}
    
    def export_records_to_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Export all records to a pandas DataFrame.
        
        Returns:
            DataFrame with record data or None if failed
        """
        try:
            athletes = self.athlete_records['athletes']
            
            if not athletes:
                return pd.DataFrame()
            
            data = []
            for athlete_id, record_data in athletes.items():
                data.append({
                    'athlete_id': athlete_id,
                    'wins': record_data['wins'],
                    'losses': record_data['losses'],
                    'draws': record_data['draws'],
                    'total_matches': record_data['total_matches'],
                    'win_rate': record_data['win_rate'],
                    'current_streak': record_data['current_streak'],
                    'longest_win_streak': record_data['longest_win_streak'],
                    'longest_lose_streak': record_data['longest_lose_streak'],
                    'last_match_date': record_data.get('last_match_date'),
                    'last_updated': record_data['last_updated']
                })
            
            df = pd.DataFrame(data)
            logger.debug(f"Exported {len(df)} athlete records to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Failed to export records to DataFrame: {e}")
            return None 