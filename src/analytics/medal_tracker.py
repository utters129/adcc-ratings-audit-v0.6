"""
ADCC Analysis Engine v0.6 - Medal Tracker
Tracks tournament results and medal counts for athletes.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pandas as pd

from core.constants import DATASTORE_DIR
from core.models import Athlete, Match, Event
from utils.file_handler import save_json_file, load_json_file, save_parquet_file, load_parquet_file
from utils.logger import get_logger

logger = get_logger(__name__)


class MedalTracker:
    """
    Tracks tournament results and medal counts for ADCC athletes.
    
    Features:
    - Medal counting and tracking
    - Tournament result analysis
    - Performance statistics
    - Medal history tracking
    - Achievement validation
    """
    
    # Medal types
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the medal tracker.
        
        Args:
            datastore_dir: Directory for storing medal data
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.medals_file = self.datastore_dir / "athlete_medals.json"
        self.tournament_results_file = self.datastore_dir / "tournament_results.parquet"
        self.statistics_file = self.datastore_dir / "medal_statistics.json"
        
        # Load existing medal data
        self.athlete_medals = self._load_athlete_medals()
        self.tournament_results = self._load_tournament_results()
        self.medal_statistics = self._load_medal_statistics()
        
        logger.info(f"MedalTracker initialized with datastore: {self.datastore_dir}")
    
    def _load_athlete_medals(self) -> Dict[str, Dict[str, Any]]:
        """Load athlete medals from JSON file."""
        try:
            if self.medals_file.exists():
                medals = load_json_file(self.medals_file)
                logger.debug(f"Loaded medals for {len(medals.get('athletes', {}))} athletes")
                return medals
            else:
                # Create new medals registry
                medals = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_athletes': 0
                    },
                    'athletes': {}
                }
                self._save_athlete_medals(medals)
                logger.info("Created new athlete medals registry")
                return medals
        except Exception as e:
            logger.error(f"Failed to load athlete medals: {e}")
            return {'metadata': {}, 'athletes': {}}
    
    def _save_athlete_medals(self, medals: Dict[str, Any]) -> bool:
        """Save athlete medals to JSON file."""
        try:
            return save_json_file(medals, self.medals_file)
        except Exception as e:
            logger.error(f"Failed to save athlete medals: {e}")
            return False
    
    def _load_tournament_results(self) -> pd.DataFrame:
        """Load tournament results from Parquet file."""
        try:
            if self.tournament_results_file.exists():
                results = load_parquet_file(self.tournament_results_file)
                logger.debug(f"Loaded tournament results with {len(results)} records")
                return results
            else:
                # Create new tournament results
                results = pd.DataFrame(columns=[
                    'event_id', 'division_id', 'athlete_id', 'medal_type', 'placement',
                    'total_participants', 'event_date', 'timestamp'
                ])
                self._save_tournament_results(results)
                logger.info("Created new tournament results")
                return results
        except Exception as e:
            logger.error(f"Failed to load tournament results: {e}")
            return pd.DataFrame()
    
    def _save_tournament_results(self, results: pd.DataFrame) -> bool:
        """Save tournament results to Parquet file."""
        try:
            return save_parquet_file(results, self.tournament_results_file)
        except Exception as e:
            logger.error(f"Failed to save tournament results: {e}")
            return False
    
    def _load_medal_statistics(self) -> Dict[str, Any]:
        """Load medal statistics from JSON file."""
        try:
            if self.statistics_file.exists():
                stats = load_json_file(self.statistics_file)
                logger.debug("Loaded medal statistics")
                return stats
            else:
                # Create new statistics
                stats = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'last_updated': datetime.now(timezone.utc).isoformat()
                    },
                    'total_medals': 0,
                    'total_athletes': 0,
                    'medal_distribution': {
                        'gold': 0,
                        'silver': 0,
                        'bronze': 0
                    },
                    'most_decorated_athletes': [],
                    'recent_medals': [],
                    'tournament_summary': {}
                }
                self._save_medal_statistics(stats)
                logger.info("Created new medal statistics")
                return stats
        except Exception as e:
            logger.error(f"Failed to load medal statistics: {e}")
            return {}
    
    def _save_medal_statistics(self, stats: Dict[str, Any]) -> bool:
        """Save medal statistics to JSON file."""
        try:
            return save_json_file(stats, self.statistics_file)
        except Exception as e:
            logger.error(f"Failed to save medal statistics: {e}")
            return False
    
    def initialize_athlete(self, athlete_id: str) -> bool:
        """
        Initialize an athlete's medal tracking.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if athlete_id in self.athlete_medals['athletes']:
                logger.warning(f"Athlete {athlete_id} already has medal tracking")
                return True
            
            # Create athlete medal entry
            self.athlete_medals['athletes'][athlete_id] = {
                'gold': 0,
                'silver': 0,
                'bronze': 0,
                'total_medals': 0,
                'total_tournaments': 0,
                'first_medal_date': None,
                'last_medal_date': None,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'medal_history': []
            }
            
            # Update metadata
            self.athlete_medals['metadata']['total_athletes'] = len(self.athlete_medals['athletes'])
            self.athlete_medals['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save medals
            success = self._save_athlete_medals(self.athlete_medals)
            
            if success:
                logger.info(f"Initialized medal tracking for athlete {athlete_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize athlete {athlete_id}: {e}")
            return False
    
    def get_athlete_medals(self, athlete_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an athlete's current medal count.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            Medal data or None if not found
        """
        try:
            return self.athlete_medals['athletes'].get(athlete_id)
        except Exception as e:
            logger.error(f"Failed to get medals for athlete {athlete_id}: {e}")
            return None
    
    def award_medal(self, athlete_id: str, event_id: str, division_id: str,
                   medal_type: str, placement: int, total_participants: int,
                   event_date: datetime) -> bool:
        """
        Award a medal to an athlete.
        
        Args:
            athlete_id: Athlete ID to award medal to
            event_id: Event ID where medal was won
            division_id: Division ID where medal was won
            medal_type: Type of medal (gold, silver, bronze)
            placement: Placement in tournament (1, 2, 3)
            total_participants: Total number of participants
            event_date: Date of the event
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate medal type
            if medal_type not in [self.GOLD, self.SILVER, self.BRONZE]:
                logger.error(f"Invalid medal type: {medal_type}")
                return False
            
            # Initialize athlete if needed
            if athlete_id not in self.athlete_medals['athletes']:
                self.initialize_athlete(athlete_id)
            
            # Update athlete medals
            athlete_data = self.athlete_medals['athletes'][athlete_id]
            athlete_data[medal_type] += 1
            athlete_data['total_medals'] += 1
            athlete_data['total_tournaments'] += 1
            
            # Update dates
            event_date_str = event_date.isoformat()
            if not athlete_data['first_medal_date']:
                athlete_data['first_medal_date'] = event_date_str
            athlete_data['last_medal_date'] = event_date_str
            athlete_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Add to medal history
            medal_entry = {
                'event_id': event_id,
                'division_id': division_id,
                'medal_type': medal_type,
                'placement': placement,
                'total_participants': total_participants,
                'event_date': event_date_str
            }
            athlete_data['medal_history'].append(medal_entry)
            
            # Keep only last 50 medals in memory
            if len(athlete_data['medal_history']) > 50:
                athlete_data['medal_history'] = athlete_data['medal_history'][-50:]
            
            # Save updated medals
            success1 = self._save_athlete_medals(self.athlete_medals)
            
            if success1:
                # Add to tournament results
                result_entry = {
                    'event_id': event_id,
                    'division_id': division_id,
                    'athlete_id': athlete_id,
                    'medal_type': medal_type,
                    'placement': placement,
                    'total_participants': total_participants,
                    'event_date': event_date_str,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                new_row = pd.DataFrame([result_entry])
                self.tournament_results = pd.concat([self.tournament_results, new_row], ignore_index=True)
                success2 = self._save_tournament_results(self.tournament_results)
                
                if success2:
                    logger.info(f"Awarded {medal_type} medal to {athlete_id} at event {event_id} (placement: {placement})")
                
                return success2
            
            return success1
            
        except Exception as e:
            logger.error(f"Failed to award medal to athlete {athlete_id}: {e}")
            return False
    
    def process_tournament_results(self, event_id: str, division_id: str,
                                 results: List[Dict[str, Any]], event_date: datetime) -> bool:
        """
        Process complete tournament results for a division.
        
        Args:
            event_id: Event ID
            division_id: Division ID
            results: List of results with athlete_id, placement, total_participants
            event_date: Date of the event
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sort results by placement
            sorted_results = sorted(results, key=lambda x: x['placement'])
            
            # Award medals to top 3
            medal_types = [self.GOLD, self.SILVER, self.BRONZE]
            
            for i, result in enumerate(sorted_results[:3]):
                if i < len(medal_types):
                    success = self.award_medal(
                        result['athlete_id'],
                        event_id,
                        division_id,
                        medal_types[i],
                        result['placement'],
                        result['total_participants'],
                        event_date
                    )
                    
                    if not success:
                        logger.error(f"Failed to award {medal_types[i]} medal to {result['athlete_id']}")
                        return False
            
            logger.info(f"Processed tournament results for {event_id}/{division_id}: {len(sorted_results)} participants")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process tournament results for {event_id}/{division_id}: {e}")
            return False
    
    def get_athlete_medal_history(self, athlete_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get an athlete's medal history.
        
        Args:
            athlete_id: Unique athlete ID
            limit: Maximum number of medals to return
            
        Returns:
            List of medal records
        """
        try:
            medals = self.get_athlete_medals(athlete_id)
            if not medals:
                return []
            
            history = medals.get('medal_history', [])
            
            if limit:
                history = history[-limit:]
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get medal history for athlete {athlete_id}: {e}")
            return []
    
    def get_most_decorated_athletes(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most decorated athletes by total medals.
        
        Args:
            limit: Maximum number of athletes to return
            
        Returns:
            List of (athlete_id, total_medals) tuples sorted by medals
        """
        try:
            athletes = []
            
            for athlete_id, medal_data in self.athlete_medals['athletes'].items():
                total_medals = medal_data['total_medals']
                if total_medals > 0:
                    athletes.append((athlete_id, total_medals))
            
            # Sort by total medals (descending)
            athletes.sort(key=lambda x: x[1], reverse=True)
            
            return athletes[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get most decorated athletes: {e}")
            return []
    
    def get_athletes_by_medal_type(self, medal_type: str, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get athletes sorted by specific medal type.
        
        Args:
            medal_type: Type of medal to sort by (gold, silver, bronze)
            limit: Maximum number of athletes to return
            
        Returns:
            List of (athlete_id, medal_count) tuples sorted by medal count
        """
        try:
            if medal_type not in [self.GOLD, self.SILVER, self.BRONZE]:
                logger.error(f"Invalid medal type: {medal_type}")
                return []
            
            athletes = []
            
            for athlete_id, medal_data in self.athlete_medals['athletes'].items():
                medal_count = medal_data[medal_type]
                if medal_count > 0:
                    athletes.append((athlete_id, medal_count))
            
            # Sort by medal count (descending)
            athletes.sort(key=lambda x: x[1], reverse=True)
            
            return athletes[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get athletes by medal type {medal_type}: {e}")
            return []
    
    def validate_medal_accuracy(self, athlete_id: str) -> Dict[str, Any]:
        """
        Validate the accuracy of an athlete's medal count.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            Dictionary with validation results
        """
        try:
            medals = self.get_athlete_medals(athlete_id)
            if not medals:
                return {
                    'valid': False,
                    'reason': 'Athlete not found',
                    'discrepancies': []
                }
            
            # Check if totals match
            calculated_total = medals['gold'] + medals['silver'] + medals['bronze']
            stored_total = medals['total_medals']
            
            discrepancies = []
            
            if calculated_total != stored_total:
                discrepancies.append(f"Total mismatch: calculated={calculated_total}, stored={stored_total}")
            
            # Check history consistency
            history_total = len(medals.get('medal_history', []))
            if history_total != stored_total:
                discrepancies.append(f"History mismatch: history_count={history_total}, stored_total={stored_total}")
            
            # Check date consistency
            if medals['first_medal_date'] and medals['last_medal_date']:
                if medals['first_medal_date'] > medals['last_medal_date']:
                    discrepancies.append("First medal date is after last medal date")
            
            validation = {
                'valid': len(discrepancies) == 0,
                'reason': 'Medal count is accurate' if len(discrepancies) == 0 else 'Found discrepancies',
                'discrepancies': discrepancies,
                'total_medals': stored_total,
                'gold': medals['gold'],
                'silver': medals['silver'],
                'bronze': medals['bronze']
            }
            
            logger.debug(f"Validated medals for {athlete_id}: {validation['valid']}")
            return validation
            
        except Exception as e:
            logger.error(f"Failed to validate medals for athlete {athlete_id}: {e}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'discrepancies': []
            }
    
    def update_medal_statistics(self) -> bool:
        """
        Update overall medal statistics.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            athletes = self.athlete_medals['athletes']
            
            if not athletes:
                self.medal_statistics.update({
                    'total_medals': 0,
                    'total_athletes': 0,
                    'medal_distribution': {'gold': 0, 'silver': 0, 'bronze': 0},
                    'most_decorated_athletes': [],
                    'recent_medals': [],
                    'tournament_summary': {}
                })
            else:
                # Calculate statistics
                total_medals = sum(athlete['total_medals'] for athlete in athletes.values())
                total_athletes = len(athletes)
                
                # Medal distribution
                medal_distribution = {
                    'gold': sum(athlete['gold'] for athlete in athletes.values()),
                    'silver': sum(athlete['silver'] for athlete in athletes.values()),
                    'bronze': sum(athlete['bronze'] for athlete in athletes.values())
                }
                
                # Most decorated athletes
                most_decorated = self.get_most_decorated_athletes(10)
                
                # Recent medals (last 10)
                recent_medals = []
                for athlete_id, athlete_data in athletes.items():
                    for medal in athlete_data.get('medal_history', [])[-3:]:  # Last 3 per athlete
                        recent_medals.append({
                            'athlete_id': athlete_id,
                            'event_id': medal['event_id'],
                            'medal_type': medal['medal_type'],
                            'event_date': medal['event_date']
                        })
                
                # Sort by date and take last 10
                recent_medals.sort(key=lambda x: x['event_date'], reverse=True)
                recent_medals = recent_medals[:10]
                
                # Tournament summary
                tournament_summary = {}
                for _, row in self.tournament_results.iterrows():
                    event_id = row['event_id']
                    if event_id not in tournament_summary:
                        tournament_summary[event_id] = {
                            'total_medals': 0,
                            'divisions': set(),
                            'athletes': set()
                        }
                    tournament_summary[event_id]['total_medals'] += 1
                    tournament_summary[event_id]['divisions'].add(row['division_id'])
                    tournament_summary[event_id]['athletes'].add(row['athlete_id'])
                
                # Convert sets to counts
                for event_id, summary in tournament_summary.items():
                    summary['divisions'] = len(summary['divisions'])
                    summary['athletes'] = len(summary['athletes'])
                
                self.medal_statistics.update({
                    'total_medals': total_medals,
                    'total_athletes': total_athletes,
                    'medal_distribution': medal_distribution,
                    'most_decorated_athletes': most_decorated,
                    'recent_medals': recent_medals,
                    'tournament_summary': tournament_summary
                })
            
            # Update metadata
            self.medal_statistics['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save statistics
            success = self._save_medal_statistics(self.medal_statistics)
            
            if success:
                logger.debug(f"Updated medal statistics: {self.medal_statistics['total_athletes']} athletes, {self.medal_statistics['total_medals']} medals")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update medal statistics: {e}")
            return False
    
    def get_medal_statistics(self) -> Dict[str, Any]:
        """
        Get current medal statistics.
        
        Returns:
            Dictionary of medal statistics
        """
        try:
            # Update statistics first
            self.update_medal_statistics()
            return self.medal_statistics
            
        except Exception as e:
            logger.error(f"Failed to get medal statistics: {e}")
            return {}
    
    def export_medals_to_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Export all medals to a pandas DataFrame.
        
        Returns:
            DataFrame with medal data or None if failed
        """
        try:
            athletes = self.athlete_medals['athletes']
            
            if not athletes:
                return pd.DataFrame()
            
            data = []
            for athlete_id, medal_data in athletes.items():
                data.append({
                    'athlete_id': athlete_id,
                    'gold': medal_data['gold'],
                    'silver': medal_data['silver'],
                    'bronze': medal_data['bronze'],
                    'total_medals': medal_data['total_medals'],
                    'total_tournaments': medal_data['total_tournaments'],
                    'first_medal_date': medal_data.get('first_medal_date'),
                    'last_medal_date': medal_data.get('last_medal_date'),
                    'last_updated': medal_data['last_updated']
                })
            
            df = pd.DataFrame(data)
            logger.debug(f"Exported {len(df)} athlete medals to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Failed to export medals to DataFrame: {e}")
            return None 