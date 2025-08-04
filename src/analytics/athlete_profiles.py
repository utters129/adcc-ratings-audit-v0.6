"""
ADCC Analysis Engine v0.6 - Athlete Profiles Management
Manages athlete profiles as JSON dictionaries with ratings, history, and metadata.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd

from src.core.constants import DATASTORE_DIR
from src.core.models import Athlete, Division, Match
from src.utils.file_handler import save_json_file, load_json_file, ensure_directory_exists
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AthleteProfileManager:
    """
    Manages athlete profiles stored as JSON dictionaries.
    
    Each athlete profile contains:
    - Basic information (name, club, etc.)
    - Division history
    - Match history
    - Rating information
    - Performance statistics
    - Metadata (last updated, version, etc.)
    """
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the athlete profile manager.
        
        Args:
            datastore_dir: Directory for storing athlete profiles
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.athletes_file = self.datastore_dir / "athletes.json"
        self.profiles_dir = self.datastore_dir / "athlete_profiles"
        
        # Ensure directories exist
        ensure_directory_exists(self.datastore_dir)
        ensure_directory_exists(self.profiles_dir)
        
        # Load existing athlete registry
        self.athletes_registry = self._load_athletes_registry()
        
        logger.info(f"AthleteProfileManager initialized with datastore: {self.datastore_dir}")
    
    def _load_athletes_registry(self) -> Dict[str, Any]:
        """Load the athletes registry from JSON file."""
        try:
            if self.athletes_file.exists():
                registry = load_json_file(self.athletes_file)
                logger.debug(f"Loaded athletes registry with {len(registry.get('athletes', {}))} athletes")
                return registry
            else:
                # Create new registry
                registry = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_athletes': 0
                    },
                    'athletes': {}
                }
                self._save_athletes_registry(registry)
                logger.info("Created new athletes registry")
                return registry
        except Exception as e:
            logger.error(f"Failed to load athletes registry: {e}")
            return {'metadata': {}, 'athletes': {}}
    
    def _save_athletes_registry(self, registry: Dict[str, Any]) -> bool:
        """Save the athletes registry to JSON file."""
        try:
            return save_json_file(registry, self.athletes_file)
        except Exception as e:
            logger.error(f"Failed to save athletes registry: {e}")
            return False
    
    def create_athlete_profile(self, athlete: Athlete) -> Dict[str, Any]:
        """
        Create a new athlete profile.
        
        Args:
            athlete: Athlete model instance
            
        Returns:
            Created athlete profile dictionary
        """
        try:
            profile = {
                'athlete_id': athlete.id,
                'name': athlete.name,
                'club_id': athlete.club_id,
                'divisions': [],
                'matches': [],
                'statistics': {
                    'total_matches': 0,
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'win_rate': 0.0
                },
                'ratings': {
                    'current_rating': 1500.0,
                    'rating_deviation': 350.0,
                    'volatility': 0.06,
                    'last_updated': None
                },
                'metadata': {
                    'created': datetime.now(timezone.utc).isoformat(),
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'version': '1.0'
                }
            }
            
            # Save individual profile
            profile_file = self.profiles_dir / f"{athlete.id}.json"
            save_json_file(profile, profile_file)
            
            # Update registry
            self.athletes_registry['athletes'][athlete.id] = {
                'name': athlete.name,
                'club_id': athlete.club_id,
                'profile_file': f"{athlete.id}.json",
                'created': profile['metadata']['created']
            }
            self.athletes_registry['metadata']['total_athletes'] = len(self.athletes_registry['athletes'])
            self._save_athletes_registry(self.athletes_registry)
            
            logger.info(f"Created athlete profile for {athlete.name} ({athlete.id})")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create athlete profile for {athlete.id}: {e}")
            return {}
    
    def get_athlete_profile(self, athlete_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an athlete profile by ID.
        
        Args:
            athlete_id: Athlete ID
            
        Returns:
            Athlete profile dictionary or None if not found
        """
        try:
            profile_file = self.profiles_dir / f"{athlete_id}.json"
            if profile_file.exists():
                profile = load_json_file(profile_file)
                logger.debug(f"Loaded athlete profile for {athlete_id}")
                return profile
            else:
                logger.warning(f"Athlete profile not found: {athlete_id}")
                return None
        except Exception as e:
            logger.error(f"Failed to load athlete profile for {athlete_id}: {e}")
            return None
    
    def update_athlete_profile(self, athlete_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an athlete profile with new data.
        
        Args:
            athlete_id: Athlete ID
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful
        """
        try:
            profile = self.get_athlete_profile(athlete_id)
            if not profile:
                logger.warning(f"Cannot update non-existent athlete profile: {athlete_id}")
                return False
            
            # Apply updates
            for key, value in updates.items():
                if key in profile:
                    if isinstance(profile[key], dict) and isinstance(value, dict):
                        profile[key].update(value)
                    else:
                        profile[key] = value
                else:
                    profile[key] = value
            
            # Update metadata
            profile['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save updated profile
            profile_file = self.profiles_dir / f"{athlete_id}.json"
            success = save_json_file(profile, profile_file)
            
            if success:
                logger.info(f"Updated athlete profile for {athlete_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update athlete profile for {athlete_id}: {e}")
            return False
    
    def add_division_to_athlete(self, athlete_id: str, division: Division) -> bool:
        """
        Add a division to an athlete's profile.
        
        Args:
            athlete_id: Athlete ID
            division: Division model instance
            
        Returns:
            True if successful
        """
        try:
            division_data = {
                'division_id': division.division_id,
                'name': division.name,
                'age_class': division.age_class.value,
                'gender': division.gender.value,
                'skill_level': division.skill_level.value,
                'gi_status': division.gi_status.value,
                'added': datetime.now(timezone.utc).isoformat()
            }
            
            updates = {
                'divisions': [division_data]
            }
            
            return self.update_athlete_profile(athlete_id, updates)
            
        except Exception as e:
            logger.error(f"Failed to add division to athlete {athlete_id}: {e}")
            return False
    
    def add_match_to_athlete(self, athlete_id: str, match: Match, is_winner: bool) -> bool:
        """
        Add a match result to an athlete's profile.
        
        Args:
            athlete_id: Athlete ID
            match: Match model instance
            is_winner: Whether the athlete won the match
            
        Returns:
            True if successful
        """
        try:
            match_data = {
                'match_id': match.match_id,
                'event_id': match.event_id,
                'opponent_id': match.athlete2_id if match.athlete1_id == athlete_id else match.athlete1_id,
                'result': 'win' if is_winner else 'loss',
                'method': match.method,
                'date': match.date.isoformat() if match.date else None,
                'division': match.division
            }
            
            # Get current profile
            profile = self.get_athlete_profile(athlete_id)
            if not profile:
                return False
            
            # Add match to history
            if 'matches' not in profile:
                profile['matches'] = []
            profile['matches'].append(match_data)
            
            # Update statistics
            stats = profile.get('statistics', {})
            stats['total_matches'] = len(profile['matches'])
            stats['wins'] = sum(1 for m in profile['matches'] if m['result'] == 'win')
            stats['losses'] = sum(1 for m in profile['matches'] if m['result'] == 'loss')
            stats['draws'] = sum(1 for m in profile['matches'] if m['result'] == 'draw')
            stats['win_rate'] = stats['wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0.0
            
            updates = {
                'matches': profile['matches'],
                'statistics': stats
            }
            
            return self.update_athlete_profile(athlete_id, updates)
            
        except Exception as e:
            logger.error(f"Failed to add match to athlete {athlete_id}: {e}")
            return False
    
    def update_athlete_rating(self, athlete_id: str, rating: float, 
                            deviation: float, volatility: float) -> bool:
        """
        Update an athlete's rating information.
        
        Args:
            athlete_id: Athlete ID
            rating: New rating value
            deviation: New rating deviation
            volatility: New volatility value
            
        Returns:
            True if successful
        """
        try:
            rating_data = {
                'current_rating': rating,
                'rating_deviation': deviation,
                'volatility': volatility,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            updates = {
                'ratings': rating_data
            }
            
            return self.update_athlete_profile(athlete_id, updates)
            
        except Exception as e:
            logger.error(f"Failed to update rating for athlete {athlete_id}: {e}")
            return False
    
    def get_all_athlete_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all athlete profiles.
        
        Returns:
            Dictionary of all athlete profiles
        """
        try:
            profiles = {}
            for athlete_id in self.athletes_registry['athletes']:
                profile = self.get_athlete_profile(athlete_id)
                if profile:
                    profiles[athlete_id] = profile
            
            logger.debug(f"Loaded {len(profiles)} athlete profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"Failed to load all athlete profiles: {e}")
            return {}
    
    def search_athletes(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search athletes by name or club.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching athlete profiles
        """
        try:
            results = []
            search_term_lower = search_term.lower()
            
            for athlete_id, athlete_info in self.athletes_registry['athletes'].items():
                if (search_term_lower in athlete_info['name'].lower() or 
                    search_term_lower in athlete_info['club'].lower()):
                    profile = self.get_athlete_profile(athlete_id)
                    if profile:
                        results.append(profile)
            
            logger.debug(f"Found {len(results)} athletes matching '{search_term}'")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search athletes: {e}")
            return []
    
    def get_athlete_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics about all athletes.
        
        Returns:
            Dictionary of statistics
        """
        try:
            profiles = self.get_all_athlete_profiles()
            
            if not profiles:
                return {
                    'total_athletes': 0,
                    'total_matches': 0,
                    'average_rating': 0.0,
                    'rating_distribution': {}
                }
            
            total_matches = sum(p.get('statistics', {}).get('total_matches', 0) for p in profiles.values())
            total_rating = sum(p.get('ratings', {}).get('current_rating', 1500.0) for p in profiles.values())
            average_rating = total_rating / len(profiles) if profiles else 0.0
            
            # Rating distribution
            rating_ranges = {
                '1500-1600': 0,
                '1600-1700': 0,
                '1700-1800': 0,
                '1800+': 0
            }
            
            for profile in profiles.values():
                rating = profile.get('ratings', {}).get('current_rating', 1500.0)
                if 1500 <= rating < 1600:
                    rating_ranges['1500-1600'] += 1
                elif 1600 <= rating < 1700:
                    rating_ranges['1600-1700'] += 1
                elif 1700 <= rating < 1800:
                    rating_ranges['1700-1800'] += 1
                else:
                    rating_ranges['1800+'] += 1
            
            stats = {
                'total_athletes': len(profiles),
                'total_matches': total_matches,
                'average_rating': round(average_rating, 2),
                'rating_distribution': rating_ranges,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            logger.debug(f"Generated athlete statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate athlete statistics: {e}")
            return {}
    
    def export_athletes_to_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Export all athlete profiles to a pandas DataFrame.
        
        Returns:
            DataFrame with athlete data or None if failed
        """
        try:
            profiles = self.get_all_athlete_profiles()
            
            if not profiles:
                return pd.DataFrame()
            
            data = []
            for athlete_id, profile in profiles.items():
                row = {
                    'athlete_id': athlete_id,
                    'name': profile.get('name', ''),
                    'club': profile.get('club', ''),
                    'total_matches': profile.get('statistics', {}).get('total_matches', 0),
                    'wins': profile.get('statistics', {}).get('wins', 0),
                    'losses': profile.get('statistics', {}).get('losses', 0),
                    'win_rate': profile.get('statistics', {}).get('win_rate', 0.0),
                    'current_rating': profile.get('ratings', {}).get('current_rating', 1500.0),
                    'rating_deviation': profile.get('ratings', {}).get('rating_deviation', 350.0),
                    'divisions_count': len(profile.get('divisions', [])),
                    'last_updated': profile.get('metadata', {}).get('last_updated', '')
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            logger.info(f"Exported {len(df)} athletes to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Failed to export athletes to DataFrame: {e}")
            return None 