"""
ADCC Analysis Engine v0.6 - Division Mapper
Manages division data and mapping functionality.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd

from core.constants import DATASTORE_DIR
from core.models import Division, AgeClass, Gender, SkillLevel, GiStatus
from utils.file_handler import save_json_file, load_json_file, ensure_directory_exists
from utils.logger import get_logger

logger = get_logger(__name__)


class DivisionMapper:
    """
    Manages division data and mapping between different division representations.
    
    Features:
    - Division registry and tracking
    - Division string parsing and classification
    - Division statistics and analytics
    - Cross-reference between divisions and athletes
    """
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the division mapper.
        
        Args:
            datastore_dir: Directory for storing division data
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.divisions_file = self.datastore_dir / "divisions.json"
        self.mapping_file = self.datastore_dir / "division_mapping.json"
        
        # Ensure directories exist
        ensure_directory_exists(self.datastore_dir)
        
        # Load existing division data
        self.divisions_registry = self._load_divisions_registry()
        self.division_mapping = self._load_division_mapping()
        
        logger.info(f"DivisionMapper initialized with datastore: {self.datastore_dir}")
    
    def _load_divisions_registry(self) -> Dict[str, Any]:
        """Load the divisions registry from JSON file."""
        try:
            if self.divisions_file.exists():
                registry = load_json_file(self.divisions_file)
                logger.debug(f"Loaded divisions registry with {len(registry.get('divisions', {}))} divisions")
                return registry
            else:
                # Create new registry
                registry = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_divisions': 0
                    },
                    'divisions': {}
                }
                self._save_divisions_registry(registry)
                logger.info("Created new divisions registry")
                return registry
        except Exception as e:
            logger.error(f"Failed to load divisions registry: {e}")
            return {'metadata': {}, 'divisions': {}}
    
    def _save_divisions_registry(self, registry: Dict[str, Any]) -> bool:
        """Save the divisions registry to JSON file."""
        try:
            return save_json_file(registry, self.divisions_file)
        except Exception as e:
            logger.error(f"Failed to save divisions registry: {e}")
            return False
    
    def _load_division_mapping(self) -> Dict[str, Any]:
        """Load the division mapping from JSON file."""
        try:
            if self.mapping_file.exists():
                mapping = load_json_file(self.mapping_file)
                logger.debug(f"Loaded division mapping with {len(mapping.get('mappings', {}))} mappings")
                return mapping
            else:
                # Create new mapping
                mapping = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0'
                    },
                    'mappings': {},
                    'aliases': {}
                }
                self._save_division_mapping(mapping)
                logger.info("Created new division mapping")
                return mapping
        except Exception as e:
            logger.error(f"Failed to load division mapping: {e}")
            return {'metadata': {}, 'mappings': {}, 'aliases': {}}
    
    def _save_division_mapping(self, mapping: Dict[str, Any]) -> bool:
        """Save the division mapping to JSON file."""
        try:
            return save_json_file(mapping, self.mapping_file)
        except Exception as e:
            logger.error(f"Failed to save division mapping: {e}")
            return False
    
    def register_division(self, division: Division) -> bool:
        """
        Register a new division in the registry.
        
        Args:
            division: Division model instance
            
        Returns:
            True if successful
        """
        try:
            division_data = {
                'division_id': division.id,
                'name': division.name,
                'age_class': division.age_class,
                'gender': division.gender,
                'skill_level': division.skill_level,
                'gi_status': division.gi_status,
                'athletes': [],
                'total_athletes': 0,
                'matches_played': 0,
                'metadata': {
                    'created': datetime.now(timezone.utc).isoformat(),
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'version': '1.0'
                }
            }
            
            # Add to registry
            self.divisions_registry['divisions'][division.id] = division_data
            self.divisions_registry['metadata']['total_divisions'] = len(self.divisions_registry['divisions'])
            self.divisions_registry['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save registry
            success = self._save_divisions_registry(self.divisions_registry)
            
            if success:
                logger.info(f"Registered division: {division.name} ({division.id})")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register division {division.id}: {e}")
            return False
    
    def get_division(self, division_id: str) -> Optional[Dict[str, Any]]:
        """
        Get division data by ID.
        
        Args:
            division_id: Division ID
            
        Returns:
            Division data dictionary or None if not found
        """
        try:
            return self.divisions_registry['divisions'].get(division_id)
        except Exception as e:
            logger.error(f"Failed to get division {division_id}: {e}")
            return None
    
    def get_all_divisions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered divisions.
        
        Returns:
            Dictionary of all divisions
        """
        try:
            return self.divisions_registry.get('divisions', {})
        except Exception as e:
            logger.error(f"Failed to get all divisions: {e}")
            return {}
    
    def add_athlete_to_division(self, division_id: str, athlete_id: str) -> bool:
        """
        Add an athlete to a division.
        
        Args:
            division_id: Division ID
            athlete_id: Athlete ID
            
        Returns:
            True if successful
        """
        try:
            if division_id not in self.divisions_registry['divisions']:
                logger.warning(f"Division not found: {division_id}")
                return False
            
            division = self.divisions_registry['divisions'][division_id]
            
            if athlete_id not in division['athletes']:
                division['athletes'].append(athlete_id)
                division['total_athletes'] = len(division['athletes'])
                division['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
                
                success = self._save_divisions_registry(self.divisions_registry)
                
                if success:
                    logger.debug(f"Added athlete {athlete_id} to division {division_id}")
                
                return success
            
            return True  # Athlete already in division
            
        except Exception as e:
            logger.error(f"Failed to add athlete {athlete_id} to division {division_id}: {e}")
            return False
    
    def remove_athlete_from_division(self, division_id: str, athlete_id: str) -> bool:
        """
        Remove an athlete from a division.
        
        Args:
            division_id: Division ID
            athlete_id: Athlete ID
            
        Returns:
            True if successful
        """
        try:
            if division_id not in self.divisions_registry['divisions']:
                logger.warning(f"Division not found: {division_id}")
                return False
            
            division = self.divisions_registry['divisions'][division_id]
            
            if athlete_id in division['athletes']:
                division['athletes'].remove(athlete_id)
                division['total_athletes'] = len(division['athletes'])
                division['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
                
                success = self._save_divisions_registry(self.divisions_registry)
                
                if success:
                    logger.debug(f"Removed athlete {athlete_id} from division {division_id}")
                
                return success
            
            return True  # Athlete not in division
            
        except Exception as e:
            logger.error(f"Failed to remove athlete {athlete_id} from division {division_id}: {e}")
            return False
    
    def parse_division_string(self, division_string: str) -> Optional[Dict[str, Any]]:
        """
        Parse a division string and return structured data.
        
        Args:
            division_string: Raw division string
            
        Returns:
            Parsed division data or None if parsing failed
        """
        try:
            # Normalize the string
            normalized = division_string.strip().lower()
            
            # Check if we have a mapping for this string
            if normalized in self.division_mapping['mappings']:
                mapping = self.division_mapping['mappings'][normalized]
                logger.debug(f"Found existing mapping for '{division_string}': {mapping}")
                return mapping
            
            # Parse the string manually
            parsed = self._parse_division_components(normalized)
            
            if parsed:
                # Store the mapping for future use
                self.division_mapping['mappings'][normalized] = parsed
                self._save_division_mapping(self.division_mapping)
                logger.debug(f"Created new mapping for '{division_string}': {parsed}")
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse division string '{division_string}': {e}")
            return None
    
    def _parse_division_components(self, division_string: str) -> Optional[Dict[str, Any]]:
        """
        Parse division string into components.
        
        Args:
            division_string: Normalized division string
            
        Returns:
            Parsed components or None if parsing failed
        """
        try:
            # Common patterns
            age_patterns = {
                'adult': AgeClass.ADULT,
                'master': AgeClass.MASTERS,
                'masters': AgeClass.MASTERS,
                'youth': AgeClass.YOUTH
            }
            
            gender_patterns = {
                'male': Gender.MALE,
                'female': Gender.FEMALE
            }
            
            skill_patterns = {
                'beginner': SkillLevel.BEGINNER,
                'intermediate': SkillLevel.INTERMEDIATE,
                'advanced': SkillLevel.ADVANCED,
                'expert': SkillLevel.EXPERT,
                'black': SkillLevel.EXPERT  # Map black belt to expert
            }
            
            gi_patterns = {
                'gi': GiStatus.GI,
                'no-gi': GiStatus.NO_GI,
                'nogi': GiStatus.NO_GI
            }
            
            # Extract components
            age_class = None
            gender = None
            skill_level = None
            gi_status = None
            
            words = division_string.split()
            
            for word in words:
                # Check age class
                for pattern, age in age_patterns.items():
                    if pattern in word:
                        age_class = age
                        break
                
                # Check gender
                for pattern, gen in gender_patterns.items():
                    if pattern in word:
                        gender = gen
                        break
                
                # Check skill level
                for pattern, skill in skill_patterns.items():
                    if pattern in word:
                        skill_level = skill
                        break
                
                # Check gi status
                for pattern, gi in gi_patterns.items():
                    if pattern in word:
                        gi_status = gi
                        break
            
            # Default values if not found
            if not age_class:
                age_class = AgeClass.ADULT
            if not gender:
                gender = Gender.MALE
            if not skill_level:
                skill_level = SkillLevel.BEGINNER
            if not gi_status:
                gi_status = GiStatus.GI
            
            return {
                'age_class': age_class,
                'gender': gender,
                'skill_level': skill_level,
                'gi_status': gi_status,
                'original_string': division_string,
                'confidence': 0.8  # Medium confidence for parsed strings
            }
            
        except Exception as e:
            logger.error(f"Failed to parse division components for '{division_string}': {e}")
            return None
    
    def find_matching_division(self, division_string: str) -> Optional[str]:
        """
        Find a matching division ID for a given division string.
        
        Args:
            division_string: Division string to match
            
        Returns:
            Division ID if found, None otherwise
        """
        try:
            parsed = self.parse_division_string(division_string)
            if not parsed:
                return None
            
            # Look for exact matches
            for division_id, division in self.divisions_registry['divisions'].items():
                if (division['age_class'] == parsed['age_class'] and
                    division['gender'] == parsed['gender'] and
                    division['skill_level'] == parsed['skill_level'] and
                    division['gi_status'] == parsed['gi_status']):
                    return division_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find matching division for '{division_string}': {e}")
            return None
    
    def get_divisions_by_criteria(self, age_class: Optional[str] = None,
                                 gender: Optional[str] = None,
                                 skill_level: Optional[str] = None,
                                 gi_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get divisions matching specific criteria.
        
        Args:
            age_class: Age class filter
            gender: Gender filter
            skill_level: Skill level filter
            gi_status: Gi status filter
            
        Returns:
            List of matching divisions
        """
        try:
            matches = []
            
            for division in self.divisions_registry['divisions'].values():
                if age_class and division['age_class'] != age_class:
                    continue
                if gender and division['gender'] != gender:
                    continue
                if skill_level and division['skill_level'] != skill_level:
                    continue
                if gi_status and division['gi_status'] != gi_status:
                    continue
                
                matches.append(division)
            
            logger.debug(f"Found {len(matches)} divisions matching criteria")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to get divisions by criteria: {e}")
            return []
    
    def get_division_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all divisions.
        
        Returns:
            Dictionary of division statistics
        """
        try:
            divisions = self.get_all_divisions()
            
            if not divisions:
                return {
                    'total_divisions': 0,
                    'total_athletes': 0,
                    'average_athletes_per_division': 0.0,
                    'age_class_distribution': {},
                    'gender_distribution': {},
                    'skill_level_distribution': {},
                    'gi_status_distribution': {}
                }
            
            total_athletes = sum(d.get('total_athletes', 0) for d in divisions.values())
            average_athletes = total_athletes / len(divisions) if divisions else 0.0
            
            # Distribution statistics
            age_dist = {}
            gender_dist = {}
            skill_dist = {}
            gi_dist = {}
            
            for division in divisions.values():
                age = division.get('age_class', 'Unknown')
                gender = division.get('gender', 'Unknown')
                skill = division.get('skill_level', 'Unknown')
                gi = division.get('gi_status', 'Unknown')
                
                age_dist[age] = age_dist.get(age, 0) + 1
                gender_dist[gender] = gender_dist.get(gender, 0) + 1
                skill_dist[skill] = skill_dist.get(skill, 0) + 1
                gi_dist[gi] = gi_dist.get(gi, 0) + 1
            
            stats = {
                'total_divisions': len(divisions),
                'total_athletes': total_athletes,
                'average_athletes_per_division': round(average_athletes, 2),
                'age_class_distribution': age_dist,
                'gender_distribution': gender_dist,
                'skill_level_distribution': skill_dist,
                'gi_status_distribution': gi_dist,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            logger.debug(f"Generated division statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate division statistics: {e}")
            return {}
    
    def export_divisions_to_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Export all divisions to a pandas DataFrame.
        
        Returns:
            DataFrame with division data or None if failed
        """
        try:
            divisions = self.get_all_divisions()
            
            if not divisions:
                return pd.DataFrame()
            
            data = []
            for division_id, division in divisions.items():
                row = {
                    'division_id': division_id,
                    'name': division.get('name', ''),
                    'age_class': division.get('age_class', ''),
                    'gender': division.get('gender', ''),
                    'skill_level': division.get('skill_level', ''),
                    'gi_status': division.get('gi_status', ''),
                    'total_athletes': division.get('total_athletes', 0),
                    'matches_played': division.get('matches_played', 0),
                    'created': division.get('metadata', {}).get('created', ''),
                    'last_updated': division.get('metadata', {}).get('last_updated', '')
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            logger.info(f"Exported {len(df)} divisions to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Failed to export divisions to DataFrame: {e}")
            return None
    
    def add_division_alias(self, original_string: str, alias: str) -> bool:
        """
        Add an alias for a division string.
        
        Args:
            original_string: Original division string
            alias: Alias string
            
        Returns:
            True if successful
        """
        try:
            self.division_mapping['aliases'][alias.lower()] = original_string.lower()
            success = self._save_division_mapping(self.division_mapping)
            
            if success:
                logger.info(f"Added alias '{alias}' for '{original_string}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add division alias: {e}")
            return False
    
    def resolve_division_alias(self, alias: str) -> Optional[str]:
        """
        Resolve a division alias to the original string.
        
        Args:
            alias: Alias string
            
        Returns:
            Original string if found, None otherwise
        """
        try:
            return self.division_mapping['aliases'].get(alias.lower())
        except Exception as e:
            logger.error(f"Failed to resolve division alias '{alias}': {e}")
            return None 