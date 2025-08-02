"""
ADCC Analysis Engine v0.6 - ID Generator
Handles unique ID generation for all entities in the system.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import json

from src.core.constants import (
    ATHLETE_ID_PREFIX, EVENT_ID_PREFIX, DIVISION_ID_PREFIX,
    MATCH_ID_PREFIX, CLUB_ID_PREFIX
)
from src.utils.validators import normalize_name
from src.utils.file_handler import load_json_file, save_json_file
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IDGenerator:
    """Handles unique ID generation for all entities in the system."""
    
    def __init__(self, id_registry_path: Optional[Path] = None):
        """
        Initialize ID generator with optional registry file.
        
        Args:
            id_registry_path: Path to store ID registry for persistence
        """
        self.id_registry_path = id_registry_path or Path("data/datastore/id_registry.json")
        self.id_registry = self._load_id_registry()
        self.generated_ids = {
            'athletes': set(),
            'events': set(),
            'divisions': set(),
            'matches': set(),
            'clubs': set()
        }
        self._load_existing_ids()
    
    def _load_id_registry(self) -> Dict[str, Any]:
        """Load existing ID registry from file."""
        try:
            if self.id_registry_path.exists():
                registry = load_json_file(self.id_registry_path)
                logger.info(f"Loaded ID registry from {self.id_registry_path}")
                return registry
            else:
                logger.info("No existing ID registry found, creating new one")
                return {
                    'athletes': {},
                    'events': {},
                    'divisions': {},
                    'matches': {},
                    'clubs': {},
                    'metadata': {
                        'created_at': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat()
                    }
                }
        except Exception as e:
            logger.error(f"Error loading ID registry: {e}")
            return {
                'athletes': {},
                'events': {},
                'divisions': {},
                'matches': {},
                'clubs': {},
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
            }
    
    def _load_existing_ids(self):
        """Load existing IDs into memory for uniqueness checking."""
        for entity_type in self.generated_ids.keys():
            if entity_type in self.id_registry:
                self.generated_ids[entity_type] = set(self.id_registry[entity_type].keys())
        
        total_ids = sum(len(ids) for ids in self.generated_ids.values())
        logger.info(f"Loaded {total_ids} existing IDs into memory")
    
    def _save_id_registry(self) -> bool:
        """Save ID registry to file."""
        try:
            self.id_registry['metadata']['last_updated'] = datetime.now().isoformat()
            self.id_registry_path.parent.mkdir(parents=True, exist_ok=True)
            save_json_file(self.id_registry, self.id_registry_path)
            logger.info(f"Saved ID registry to {self.id_registry_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving ID registry: {e}")
            return False
    
    def _generate_hash_id(self, data: str, prefix: str, max_length: int = 8) -> str:
        """
        Generate a hash-based ID from input data.
        
        Args:
            data: Input data to hash
            prefix: ID prefix
            max_length: Maximum length of hash part
            
        Returns:
            Generated ID with prefix
        """
        # Create hash from normalized data
        normalized_data = data.lower().strip()
        hash_object = hashlib.md5(normalized_data.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # Take first max_length characters
        hash_part = hash_hex[:max_length].upper()
        
        return f"{prefix}{hash_part}"
    
    def _generate_sequential_id(self, prefix: str, entity_type: str) -> str:
        """
        Generate a sequential ID with prefix.
        
        Args:
            prefix: ID prefix
            entity_type: Type of entity for tracking
            
        Returns:
            Generated sequential ID
        """
        # Get current count for this entity type
        current_count = len(self.generated_ids[entity_type]) + 1
        
        # Generate ID with zero-padding
        id_part = f"{current_count:06d}"
        
        return f"{prefix}{id_part}"
    
    def generate_athlete_id(self, name: str, country: str, birth_year: Optional[int] = None) -> str:
        """
        Generate unique athlete ID.
        
        Args:
            name: Athlete name
            country: Athlete country
            birth_year: Optional birth year for additional uniqueness
            
        Returns:
            Unique athlete ID
        """
        try:
            # Normalize name
            normalized_name = normalize_name(name)
            
            # Create unique identifier
            if birth_year:
                unique_data = f"{normalized_name}_{country}_{birth_year}"
            else:
                unique_data = f"{normalized_name}_{country}"
            
            # Try hash-based ID first
            athlete_id = self._generate_hash_id(unique_data, ATHLETE_ID_PREFIX)
            
            # Check if ID already exists
            if athlete_id in self.generated_ids['athletes']:
                # Use sequential ID as fallback
                athlete_id = self._generate_sequential_id(ATHLETE_ID_PREFIX, 'athletes')
            
            # Register the ID
            self.generated_ids['athletes'].add(athlete_id)
            self.id_registry['athletes'][athlete_id] = {
                'name': normalized_name,
                'country': country,
                'birth_year': birth_year,
                'created_at': datetime.now().isoformat()
            }
            
            logger.debug(f"Generated athlete ID: {athlete_id} for {normalized_name}")
            return athlete_id
            
        except Exception as e:
            logger.error(f"Error generating athlete ID: {e}")
            # Fallback to sequential ID
            return self._generate_sequential_id(ATHLETE_ID_PREFIX, 'athletes')
    
    def generate_event_id(self, name: str, date: datetime) -> str:
        """
        Generate unique event ID.
        
        Args:
            name: Event name
            date: Event date
            
        Returns:
            Unique event ID
        """
        try:
            # Normalize name
            normalized_name = normalize_name(name)
            date_str = date.strftime("%Y%m%d")
            
            # Create unique identifier
            unique_data = f"{normalized_name}_{date_str}"
            
            # Generate hash-based ID
            event_id = self._generate_hash_id(unique_data, EVENT_ID_PREFIX)
            
            # Check if ID already exists
            if event_id in self.generated_ids['events']:
                # Use sequential ID as fallback
                event_id = self._generate_sequential_id(EVENT_ID_PREFIX, 'events')
            
            # Register the ID
            self.generated_ids['events'].add(event_id)
            self.id_registry['events'][event_id] = {
                'name': normalized_name,
                'date': date.isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            logger.debug(f"Generated event ID: {event_id} for {normalized_name}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error generating event ID: {e}")
            # Fallback to sequential ID
            return self._generate_sequential_id(EVENT_ID_PREFIX, 'events')
    
    def generate_division_id(self, age_class: str, gender: str, skill_level: str, gi_status: str) -> str:
        """
        Generate unique division ID.
        
        Args:
            age_class: Age class (youth, adult, masters)
            gender: Gender (M, F)
            skill_level: Skill level
            gi_status: Gi status (gi, no-gi)
            
        Returns:
            Unique division ID
        """
        try:
            # Normalize inputs
            age_class = age_class.lower().strip()
            gender = gender.upper().strip()
            skill_level = skill_level.lower().strip()
            gi_status = gi_status.lower().strip()
            
            # Create unique identifier
            unique_data = f"{age_class}_{gender}_{skill_level}_{gi_status}"
            
            # Generate hash-based ID
            division_id = self._generate_hash_id(unique_data, DIVISION_ID_PREFIX)
            
            # Check if ID already exists
            if division_id in self.generated_ids['divisions']:
                # Use sequential ID as fallback
                division_id = self._generate_sequential_id(DIVISION_ID_PREFIX, 'divisions')
            
            # Register the ID
            self.generated_ids['divisions'].add(division_id)
            self.id_registry['divisions'][division_id] = {
                'age_class': age_class,
                'gender': gender,
                'skill_level': skill_level,
                'gi_status': gi_status,
                'created_at': datetime.now().isoformat()
            }
            
            logger.debug(f"Generated division ID: {division_id} for {unique_data}")
            return division_id
            
        except Exception as e:
            logger.error(f"Error generating division ID: {e}")
            # Fallback to sequential ID
            return self._generate_sequential_id(DIVISION_ID_PREFIX, 'divisions')
    
    def generate_match_id(self, winner_id: str, loser_id: str, event_id: str, division_id: str) -> str:
        """
        Generate unique match ID.
        
        Args:
            winner_id: Winner athlete ID
            loser_id: Loser athlete ID
            event_id: Event ID
            division_id: Division ID
            
        Returns:
            Unique match ID
        """
        try:
            # Create unique identifier
            unique_data = f"{winner_id}_{loser_id}_{event_id}_{division_id}"
            
            # Generate hash-based ID
            match_id = self._generate_hash_id(unique_data, MATCH_ID_PREFIX)
            
            # Check if ID already exists
            if match_id in self.generated_ids['matches']:
                # Use sequential ID as fallback
                match_id = self._generate_sequential_id(MATCH_ID_PREFIX, 'matches')
            
            # Register the ID
            self.generated_ids['matches'].add(match_id)
            self.id_registry['matches'][match_id] = {
                'winner_id': winner_id,
                'loser_id': loser_id,
                'event_id': event_id,
                'division_id': division_id,
                'created_at': datetime.now().isoformat()
            }
            
            logger.debug(f"Generated match ID: {match_id}")
            return match_id
            
        except Exception as e:
            logger.error(f"Error generating match ID: {e}")
            # Fallback to sequential ID
            return self._generate_sequential_id(MATCH_ID_PREFIX, 'matches')
    
    def generate_club_id(self, club_name: str, country: str) -> str:
        """
        Generate unique club ID.
        
        Args:
            club_name: Club name
            country: Club country
            
        Returns:
            Unique club ID
        """
        try:
            # Normalize club name
            normalized_name = normalize_name(club_name)
            
            # Create unique identifier
            unique_data = f"{normalized_name}_{country}"
            
            # Generate hash-based ID
            club_id = self._generate_hash_id(unique_data, CLUB_ID_PREFIX)
            
            # Check if ID already exists
            if club_id in self.generated_ids['clubs']:
                # Use sequential ID as fallback
                club_id = self._generate_sequential_id(CLUB_ID_PREFIX, 'clubs')
            
            # Register the ID
            self.generated_ids['clubs'].add(club_id)
            self.id_registry['clubs'][club_id] = {
                'name': normalized_name,
                'country': country,
                'created_at': datetime.now().isoformat()
            }
            
            logger.debug(f"Generated club ID: {club_id} for {normalized_name}")
            return club_id
            
        except Exception as e:
            logger.error(f"Error generating club ID: {e}")
            # Fallback to sequential ID
            return self._generate_sequential_id(CLUB_ID_PREFIX, 'clubs')
    
    def get_id_info(self, entity_id: str, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific ID.
        
        Args:
            entity_id: The ID to look up
            entity_type: Type of entity
            
        Returns:
            ID information or None if not found
        """
        try:
            if entity_type in self.id_registry and entity_id in self.id_registry[entity_type]:
                return self.id_registry[entity_type][entity_id]
            return None
        except Exception as e:
            logger.error(f"Error getting ID info: {e}")
            return None
    
    def is_id_exists(self, entity_id: str, entity_type: str) -> bool:
        """
        Check if an ID already exists.
        
        Args:
            entity_id: The ID to check
            entity_type: Type of entity
            
        Returns:
            True if ID exists, False otherwise
        """
        return entity_id in self.generated_ids.get(entity_type, set())
    
    def get_all_ids(self, entity_type: str) -> Set[str]:
        """
        Get all IDs for a specific entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Set of all IDs for the entity type
        """
        return self.generated_ids.get(entity_type, set()).copy()
    
    def get_id_statistics(self) -> Dict[str, int]:
        """
        Get statistics about generated IDs.
        
        Returns:
            Dictionary with ID counts by entity type
        """
        return {
            entity_type: len(ids) 
            for entity_type, ids in self.generated_ids.items()
        }
    
    def save_registry(self) -> bool:
        """
        Save the current ID registry to file.
        
        Returns:
            True if save was successful, False otherwise
        """
        return self._save_id_registry()
    
    def reset(self):
        """Reset the ID generator (for testing purposes)."""
        self.generated_ids = {
            'athletes': set(),
            'events': set(),
            'divisions': set(),
            'matches': set(),
            'clubs': set()
        }
        self.id_registry = {
            'athletes': {},
            'events': {},
            'divisions': {},
            'matches': {},
            'clubs': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        }
        logger.info("IDGenerator state reset")
    
    def cleanup_unused_ids(self) -> int:
        """
        Clean up IDs that are no longer referenced.
        This is a maintenance function that should be run periodically.
        
        Returns:
            Number of IDs cleaned up
        """
        # This would require additional logic to track ID usage
        # For now, we'll just return 0 as a placeholder
        logger.info("ID cleanup not implemented yet")
        return 0 