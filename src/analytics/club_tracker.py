"""
ADCC Analysis Engine v0.6 - Club Tracker
Manages club data and performance tracking.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd

from src.core.constants import DATASTORE_DIR
from src.core.models import Club, Athlete, Match
from src.utils.file_handler import save_json_file, load_json_file, ensure_directory_exists
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ClubTracker:
    """
    Manages club data and tracks club performance and statistics.
    
    Features:
    - Club registry and tracking
    - Club performance analytics
    - Athlete-club relationships
    - Club statistics and rankings
    """
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the club tracker.
        
        Args:
            datastore_dir: Directory for storing club data
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.clubs_file = self.datastore_dir / "clubs.json"
        self.club_stats_file = self.datastore_dir / "club_statistics.json"
        
        # Ensure directories exist
        ensure_directory_exists(self.datastore_dir)
        
        # Load existing club data
        self.clubs_registry = self._load_clubs_registry()
        self.club_statistics = self._load_club_statistics()
        
        logger.info(f"ClubTracker initialized with datastore: {self.datastore_dir}")
    
    def _load_clubs_registry(self) -> Dict[str, Any]:
        """Load the clubs registry from JSON file."""
        try:
            if self.clubs_file.exists():
                registry = load_json_file(self.clubs_file)
                logger.debug(f"Loaded clubs registry with {len(registry.get('clubs', {}))} clubs")
                return registry
            else:
                # Create new registry
                registry = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_clubs': 0
                    },
                    'clubs': {}
                }
                self._save_clubs_registry(registry)
                logger.info("Created new clubs registry")
                return registry
        except Exception as e:
            logger.error(f"Failed to load clubs registry: {e}")
            return {'metadata': {}, 'clubs': {}}
    
    def _save_clubs_registry(self, registry: Dict[str, Any]) -> bool:
        """Save the clubs registry to JSON file."""
        try:
            return save_json_file(registry, self.clubs_file)
        except Exception as e:
            logger.error(f"Failed to save clubs registry: {e}")
            return False
    
    def _load_club_statistics(self) -> Dict[str, Any]:
        """Load the club statistics from JSON file."""
        try:
            if self.club_stats_file.exists():
                stats = load_json_file(self.club_stats_file)
                logger.debug(f"Loaded club statistics for {len(stats.get('statistics', {}))} clubs")
                return stats
            else:
                # Create new statistics
                stats = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'last_updated': datetime.now(timezone.utc).isoformat()
                    },
                    'statistics': {},
                    'rankings': {}
                }
                self._save_club_statistics(stats)
                logger.info("Created new club statistics")
                return stats
        except Exception as e:
            logger.error(f"Failed to load club statistics: {e}")
            return {'metadata': {}, 'statistics': {}, 'rankings': {}}
    
    def _save_club_statistics(self, stats: Dict[str, Any]) -> bool:
        """Save the club statistics to JSON file."""
        try:
            return save_json_file(stats, self.club_stats_file)
        except Exception as e:
            logger.error(f"Failed to save club statistics: {e}")
            return False
    
    def register_club(self, club: Club) -> bool:
        """
        Register a new club in the registry.
        
        Args:
            club: Club model instance
            
        Returns:
            True if successful
        """
        try:
            club_data = {
                'club_id': club.id,
                'name': club.name,
                'country': club.country,
                'city': club.city,
                'athletes': [],
                'total_athletes': 0,
                'total_matches': 0,
                'total_wins': 0,
                'total_losses': 0,
                'win_rate': 0.0,
                'average_rating': 1500.0,
                'metadata': {
                    'created': datetime.now(timezone.utc).isoformat(),
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'version': '1.0'
                }
            }
            
            # Add to registry
            self.clubs_registry['clubs'][club.id] = club_data
            self.clubs_registry['metadata']['total_clubs'] = len(self.clubs_registry['clubs'])
            self.clubs_registry['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save registry
            success = self._save_clubs_registry(self.clubs_registry)
            
            if success:
                logger.info(f"Registered club: {club.name} ({club.id})")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register club {club.id}: {e}")
            return False
    
    def get_club(self, club_id: str) -> Optional[Dict[str, Any]]:
        """
        Get club data by ID.
        
        Args:
            club_id: Club ID
            
        Returns:
            Club data dictionary or None if not found
        """
        try:
            return self.clubs_registry['clubs'].get(club_id)
        except Exception as e:
            logger.error(f"Failed to get club {club_id}: {e}")
            return None
    
    def get_all_clubs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered clubs.
        
        Returns:
            Dictionary of all clubs
        """
        try:
            return self.clubs_registry.get('clubs', {})
        except Exception as e:
            logger.error(f"Failed to get all clubs: {e}")
            return {}
    
    def add_athlete_to_club(self, club_id: str, athlete_id: str) -> bool:
        """
        Add an athlete to a club.
        
        Args:
            club_id: Club ID
            athlete_id: Athlete ID
            
        Returns:
            True if successful
        """
        try:
            if club_id not in self.clubs_registry['clubs']:
                logger.warning(f"Club not found: {club_id}")
                return False
            
            club = self.clubs_registry['clubs'][club_id]
            
            if athlete_id not in club['athletes']:
                club['athletes'].append(athlete_id)
                club['total_athletes'] = len(club['athletes'])
                club['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
                
                success = self._save_clubs_registry(self.clubs_registry)
                
                if success:
                    logger.debug(f"Added athlete {athlete_id} to club {club_id}")
                
                return success
            
            return True  # Athlete already in club
            
        except Exception as e:
            logger.error(f"Failed to add athlete {athlete_id} to club {club_id}: {e}")
            return False
    
    def remove_athlete_from_club(self, club_id: str, athlete_id: str) -> bool:
        """
        Remove an athlete from a club.
        
        Args:
            club_id: Club ID
            athlete_id: Athlete ID
            
        Returns:
            True if successful
        """
        try:
            if club_id not in self.clubs_registry['clubs']:
                logger.warning(f"Club not found: {club_id}")
                return False
            
            club = self.clubs_registry['clubs'][club_id]
            
            if athlete_id in club['athletes']:
                club['athletes'].remove(athlete_id)
                club['total_athletes'] = len(club['athletes'])
                club['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
                
                success = self._save_clubs_registry(self.clubs_registry)
                
                if success:
                    logger.debug(f"Removed athlete {athlete_id} from club {club_id}")
                
                return success
            
            return True  # Athlete not in club
            
        except Exception as e:
            logger.error(f"Failed to remove athlete {athlete_id} from club {club_id}: {e}")
            return False
    
    def update_club_performance(self, club_id: str, match_result: Dict[str, Any]) -> bool:
        """
        Update club performance statistics with match result.
        
        Args:
            club_id: Club ID
            match_result: Match result data
            
        Returns:
            True if successful
        """
        try:
            if club_id not in self.clubs_registry['clubs']:
                logger.warning(f"Club not found: {club_id}")
                return False
            
            club = self.clubs_registry['clubs'][club_id]
            
            # Update match statistics
            club['total_matches'] += 1
            
            if match_result.get('result') == 'win':
                club['total_wins'] += 1
            elif match_result.get('result') == 'loss':
                club['total_losses'] += 1
            
            # Calculate win rate
            if club['total_matches'] > 0:
                club['win_rate'] = club['total_wins'] / club['total_matches']
            
            club['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            success = self._save_clubs_registry(self.clubs_registry)
            
            if success:
                logger.debug(f"Updated performance for club {club_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update club performance for {club_id}: {e}")
            return False
    
    def calculate_club_statistics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for all clubs.
        
        Returns:
            Dictionary of club statistics
        """
        try:
            clubs = self.get_all_clubs()
            
            if not clubs:
                return {
                    'total_clubs': 0,
                    'total_athletes': 0,
                    'total_matches': 0,
                    'average_athletes_per_club': 0.0,
                    'average_win_rate': 0.0,
                    'top_performing_clubs': [],
                    'largest_clubs': [],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate overall statistics
            total_athletes = sum(c.get('total_athletes', 0) for c in clubs.values())
            total_matches = sum(c.get('total_matches', 0) for c in clubs.values())
            total_wins = sum(c.get('total_wins', 0) for c in clubs.values())
            
            average_athletes = total_athletes / len(clubs) if clubs else 0.0
            average_win_rate = total_wins / total_matches if total_matches > 0 else 0.0
            
            # Top performing clubs (by win rate)
            clubs_with_matches = [c for c in clubs.values() if c.get('total_matches', 0) > 0]
            top_performing = sorted(
                clubs_with_matches,
                key=lambda x: x.get('win_rate', 0.0),
                reverse=True
            )[:10]
            
            # Largest clubs (by athlete count)
            largest_clubs = sorted(
                clubs.values(),
                key=lambda x: x.get('total_athletes', 0),
                reverse=True
            )[:10]
            
            stats = {
                'total_clubs': len(clubs),
                'total_athletes': total_athletes,
                'total_matches': total_matches,
                'average_athletes_per_club': round(average_athletes, 2),
                'average_win_rate': round(average_win_rate, 3),
                'top_performing_clubs': [
                    {
                        'club_id': c['club_id'],
                        'name': c['name'],
                        'win_rate': c.get('win_rate', 0.0),
                        'total_matches': c.get('total_matches', 0)
                    }
                    for c in top_performing
                ],
                'largest_clubs': [
                    {
                        'club_id': c['club_id'],
                        'name': c['name'],
                        'total_athletes': c.get('total_athletes', 0)
                    }
                    for c in largest_clubs
                ],
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Save statistics
            self.club_statistics['statistics'] = stats
            self.club_statistics['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            self._save_club_statistics(self.club_statistics)
            
            logger.debug(f"Generated club statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate club statistics: {e}")
            return {}
    
    def get_club_rankings(self, ranking_type: str = 'win_rate') -> List[Dict[str, Any]]:
        """
        Get club rankings by different criteria.
        
        Args:
            ranking_type: Type of ranking ('win_rate', 'athletes', 'matches')
            
        Returns:
            List of ranked clubs
        """
        try:
            clubs = self.get_all_clubs()
            
            if not clubs:
                return []
            
            # Filter clubs based on ranking type
            if ranking_type == 'win_rate':
                # Only include clubs with matches
                eligible_clubs = [c for c in clubs.values() if c.get('total_matches', 0) > 0]
                sorted_clubs = sorted(eligible_clubs, key=lambda x: x.get('win_rate', 0.0), reverse=True)
            elif ranking_type == 'athletes':
                sorted_clubs = sorted(clubs.values(), key=lambda x: x.get('total_athletes', 0), reverse=True)
            elif ranking_type == 'matches':
                sorted_clubs = sorted(clubs.values(), key=lambda x: x.get('total_matches', 0), reverse=True)
            else:
                logger.warning(f"Unknown ranking type: {ranking_type}")
                return []
            
            rankings = []
            for i, club in enumerate(sorted_clubs, 1):
                ranking = {
                    'rank': i,
                    'club_id': club['club_id'],
                    'name': club['name'],
                    'location': club.get('location', ''),
                    'total_athletes': club.get('total_athletes', 0),
                    'total_matches': club.get('total_matches', 0),
                    'win_rate': club.get('win_rate', 0.0),
                    'average_rating': club.get('average_rating', 1500.0)
                }
                rankings.append(ranking)
            
            logger.debug(f"Generated {ranking_type} rankings for {len(rankings)} clubs")
            return rankings
            
        except Exception as e:
            logger.error(f"Failed to generate club rankings: {e}")
            return []
    
    def search_clubs(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search clubs by name or location.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching clubs
        """
        try:
            results = []
            search_term_lower = search_term.lower()
            
            for club in self.clubs_registry['clubs'].values():
                if (search_term_lower in club['name'].lower() or 
                    search_term_lower in club.get('location', '').lower()):
                    results.append(club)
            
            logger.debug(f"Found {len(results)} clubs matching '{search_term}'")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search clubs: {e}")
            return []
    
    def get_club_athletes(self, club_id: str) -> List[str]:
        """
        Get all athletes in a club.
        
        Args:
            club_id: Club ID
            
        Returns:
            List of athlete IDs
        """
        try:
            club = self.get_club(club_id)
            if club:
                return club.get('athletes', [])
            return []
        except Exception as e:
            logger.error(f"Failed to get athletes for club {club_id}: {e}")
            return []
    
    def get_club_performance_history(self, club_id: str) -> List[Dict[str, Any]]:
        """
        Get performance history for a club.
        
        Args:
            club_id: Club ID
            
        Returns:
            List of performance records
        """
        try:
            # This would typically integrate with match data
            # For now, return basic club statistics
            club = self.get_club(club_id)
            if not club:
                return []
            
            return [{
                'date': club['metadata']['last_updated'],
                'total_matches': club.get('total_matches', 0),
                'total_wins': club.get('total_wins', 0),
                'win_rate': club.get('win_rate', 0.0),
                'total_athletes': club.get('total_athletes', 0)
            }]
            
        except Exception as e:
            logger.error(f"Failed to get performance history for club {club_id}: {e}")
            return []
    
    def export_clubs_to_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Export all clubs to a pandas DataFrame.
        
        Returns:
            DataFrame with club data or None if failed
        """
        try:
            clubs = self.get_all_clubs()
            
            if not clubs:
                return pd.DataFrame()
            
            data = []
            for club_id, club in clubs.items():
                row = {
                    'club_id': club_id,
                    'name': club.get('name', ''),
                    'location': club.get('location', ''),
                    'website': club.get('website', ''),
                    'total_athletes': club.get('total_athletes', 0),
                    'total_matches': club.get('total_matches', 0),
                    'total_wins': club.get('total_wins', 0),
                    'win_rate': club.get('win_rate', 0.0),
                    'average_rating': club.get('average_rating', 1500.0),
                    'created': club.get('metadata', {}).get('created', ''),
                    'last_updated': club.get('metadata', {}).get('last_updated', '')
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            logger.info(f"Exported {len(df)} clubs to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Failed to export clubs to DataFrame: {e}")
            return None
    
    def update_club_average_rating(self, club_id: str, new_average: float) -> bool:
        """
        Update the average rating for a club.
        
        Args:
            club_id: Club ID
            new_average: New average rating
            
        Returns:
            True if successful
        """
        try:
            if club_id not in self.clubs_registry['clubs']:
                logger.warning(f"Club not found: {club_id}")
                return False
            
            club = self.clubs_registry['clubs'][club_id]
            club['average_rating'] = new_average
            club['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            success = self._save_clubs_registry(self.clubs_registry)
            
            if success:
                logger.debug(f"Updated average rating for club {club_id}: {new_average}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update average rating for club {club_id}: {e}")
            return False 