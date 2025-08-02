"""
ADCC Analysis Engine v0.6 - Division Classifier
Handles division string parsing, age class separation, and gi/no-gi classification.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json

from src.core.constants import AGE_CLASSES, VALID_GENDERS, VALID_SKILL_LEVELS, EVENT_MASTER_LIST_FILE, DATASTORE_DIR
from src.utils.validators import normalize_name
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DivisionClassifier:
    """Handles division string parsing, age class separation, and gi/no-gi classification."""
    
    def __init__(self, event_master_list_path: Optional[Path] = None):
        """
        Initialize the division classifier.
        
        Args:
            event_master_list_path: Optional path to event master list file
        """
        # Age class patterns
        self.age_patterns = {
            'youth': [r'\byouth\b', r'\bu\d+\b', r'\bjuvenile\b', r'\bteen\b'],
            'adult': [r'\badult\b', r'\bopen\b'],
            'masters': [r'\bmasters?\b', r'\b30\+\b', r'\b40\+\b', r'\b50\+\b', r'\bsenior\b']
        }
        
        # Gender patterns
        self.gender_patterns = {
            'M': [r'\bmale\b', r'\bmen\b', r'\bm\b'],
            'F': [r'\bfemale\b', r'\bwomen\b', r'\bf\b', r'\bladies\b']
        }
        
        # Skill level patterns
        self.skill_patterns = {
            'white': [r'\bwhite\b', r'\bwhite belt\b'],
            'blue': [r'\bblue\b', r'\bblue belt\b'],
            'purple': [r'\bpurple\b', r'\bpurple belt\b'],
            'brown': [r'\bbrown\b', r'\bbrown belt\b'],
            'black': [r'\bblack\b', r'\bblack belt\b'],
            'beginner': [r'\bbeginner\b', r'\bnovice\b'],
            'intermediate': [r'\bintermediate\b'],
            'advanced': [r'\badvanced\b', r'\bexpert\b']
        }
        
        # Gi status patterns (order matters - check no-gi first to avoid matching 'gi' in 'no-gi')
        self.gi_patterns = {
            'no-gi': [r'\bno-gi\b', r'\bnogi\b', r'\bno gi\b', r'\bwithout gi\b', r'\bgrappling\b'],
            'gi': [r'\bgi\b', r'\bwith gi\b', r'\bkimono\b']
        }
        
        # Weight class patterns
        self.weight_patterns = [
            r'\b\d+kg\b',
            r'\b\d+\.\d+kg\b',
            r'\b\d+-\d+kg\b',
            r'\b\d+\.\d+-\d+\.\d+kg\b',
            r'\b\+\d+kg\b',
            r'\b\d+\.\d+\+kg\b',
            r'\b\d+-\d+\.\d+kg\b',
            r'\b\d+\.\d+-\d+kg\b'
        ]
        
        # Common division mappings
        self.division_mappings = {
            'adult_male_black_gi': 'Adult Male Black Belt Gi',
            'adult_female_black_gi': 'Adult Female Black Belt Gi',
            'adult_male_black_nogi': 'Adult Male Black Belt No-Gi',
            'adult_female_black_nogi': 'Adult Female Black Belt No-Gi',
            'masters_male_brown_gi': 'Masters Male Brown Belt Gi',
            'masters_female_brown_gi': 'Masters Female Brown Belt Gi'
        }
        
        # Load event master list
        self.event_master_list_path = event_master_list_path or DATASTORE_DIR / EVENT_MASTER_LIST_FILE
        self.event_master_list = self._load_event_master_list()
    
    def _load_event_master_list(self) -> Dict[str, Any]:
        """Load the event master list from file."""
        try:
            if self.event_master_list_path.exists():
                with open(self.event_master_list_path, 'r', encoding='utf-8') as f:
                    event_master_list = json.load(f)
                logger.info(f"Loaded event master list from {self.event_master_list_path}")
                return event_master_list
            else:
                logger.warning(f"Event master list not found at {self.event_master_list_path}")
                return {"events": []}
        except Exception as e:
            logger.error(f"Error loading event master list: {e}")
            return {"events": []}
    
    def _get_event_gi_status(self, event_id: Optional[str] = None, event_name: Optional[str] = None) -> Optional[str]:
        """
        Get gi status from event master list.
        
        Args:
            event_id: Event ID to look up
            event_name: Event name to look up (fallback)
            
        Returns:
            'gi', 'no-gi', or None if not found
        """
        try:
            if not self.event_master_list or 'events' not in self.event_master_list:
                return None
            
            for event in self.event_master_list['events']:
                # Check by event ID first
                if event_id and event.get('id') == event_id:
                    if event.get('gi_event') and not event.get('no_gi_event'):
                        return 'gi'
                    elif event.get('no_gi_event') and not event.get('gi_event'):
                        return 'no-gi'
                    elif event.get('gi_event') and event.get('no_gi_event'):
                        logger.warning(f"Event {event_id} has both gi and no-gi events")
                        return None
                    else:
                        logger.warning(f"Event {event_id} has no gi status specified")
                        return None
                
                # Check by event name as fallback
                if event_name and event.get('name') and event_name.lower() in event.get('name', '').lower():
                    if event.get('gi_event') and not event.get('no_gi_event'):
                        return 'gi'
                    elif event.get('no_gi_event') and not event.get('gi_event'):
                        return 'no-gi'
                    elif event.get('gi_event') and event.get('no_gi_event'):
                        logger.warning(f"Event {event.get('name')} has both gi and no-gi events")
                        return None
                    else:
                        logger.warning(f"Event {event.get('name')} has no gi status specified")
                        return None
            
            logger.warning(f"Event not found in master list: ID={event_id}, Name={event_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting event gi status: {e}")
            return None
    
    def parse_division_string(self, division_str: str, event_id: Optional[str] = None, event_name: Optional[str] = None) -> Dict[str, str]:
        """
        Parse a division string and extract all components.
        
        Args:
            division_str: Raw division string
            event_id: Optional event ID for gi status lookup
            event_name: Optional event name for gi status lookup
            
        Returns:
            Dictionary with parsed components
        """
        try:
            if not division_str or not isinstance(division_str, str):
                logger.warning(f"Invalid division string: {division_str}")
                return {}
            
            # Normalize the string
            normalized_str = division_str.lower().strip()
            logger.debug(f"Parsing division string: '{division_str}' -> '{normalized_str}'")
            
            # Extract components
            result = {
                'original': division_str,
                'normalized': normalized_str,
                'age_class': self._extract_age_class(normalized_str),
                'gender': self._extract_gender(normalized_str),
                'skill_level': self._extract_skill_level(normalized_str),
                'gi_status': self._extract_gi_status(normalized_str, event_id, event_name),
                'weight_class': self._extract_weight_class(normalized_str),
                'confidence': 0.0
            }
            
            # Calculate confidence score
            result['confidence'] = self._calculate_confidence(result)
            
            logger.debug(f"Parsed division: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing division string '{division_str}': {e}")
            return {
                'original': division_str,
                'normalized': str(division_str).lower().strip() if division_str else '',
                'age_class': 'unknown',
                'gender': 'unknown',
                'skill_level': 'unknown',
                'gi_status': 'unknown',
                'weight_class': 'unknown',
                'confidence': 0.0
            }
    
    def _extract_age_class(self, text: str) -> str:
        """Extract age class from text."""
        try:
            for age_class, patterns in self.age_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        return age_class
            
            # Default to adult if no specific age class found
            return 'adult'
            
        except Exception as e:
            logger.error(f"Error extracting age class: {e}")
            return 'unknown'
    
    def _extract_gender(self, text: str) -> str:
        """Extract gender from text."""
        try:
            for gender, patterns in self.gender_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        return gender
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error extracting gender: {e}")
            return 'unknown'
    
    def _extract_skill_level(self, text: str) -> str:
        """Extract skill level from text."""
        try:
            for skill_level, patterns in self.skill_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        return skill_level
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error extracting skill level: {e}")
            return 'unknown'
    
    def _extract_gi_status(self, text: str, event_id: Optional[str] = None, event_name: Optional[str] = None) -> str:
        """
        Extract gi status from text, with fallback to event master list.
        
        Args:
            text: Division string text
            event_id: Optional event ID for master list lookup
            event_name: Optional event name for master list lookup
            
        Returns:
            'gi', 'no-gi', or 'unknown'
        """
        try:
            # First, try to extract gi status from the division text
            for gi_status, patterns in self.gi_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        return gi_status
            
            # If no gi status found in text, check event master list
            if event_id or event_name:
                event_gi_status = self._get_event_gi_status(event_id, event_name)
                if event_gi_status:
                    logger.info(f"Using event master list gi status '{event_gi_status}' for division '{text}'")
                    return event_gi_status
            
            # Default to gi if no specific gi status found and no event info available
            logger.warning(f"No gi status found in division '{text}' and no event info available, defaulting to 'gi'")
            return 'gi'
            
        except Exception as e:
            logger.error(f"Error extracting gi status: {e}")
            return 'unknown'
    
    def _extract_weight_class(self, text: str) -> str:
        """Extract weight class from text."""
        try:
            for pattern in self.weight_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(0)
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error extracting weight class: {e}")
            return 'unknown'
    
    def _calculate_confidence(self, parsed_result: Dict[str, str]) -> float:
        """Calculate confidence score for the parsing result."""
        try:
            confidence = 0.0
            total_components = 4  # age_class, gender, skill_level, gi_status
            
            # Check if each component was successfully extracted
            if parsed_result['age_class'] != 'unknown':
                confidence += 0.25
            if parsed_result['gender'] != 'unknown':
                confidence += 0.25
            if parsed_result['skill_level'] != 'unknown':
                confidence += 0.25
            if parsed_result['gi_status'] != 'unknown':
                confidence += 0.25
            
            # Bonus for weight class
            if parsed_result['weight_class'] != 'unknown':
                confidence += 0.1
            
            # Cap at 1.0
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0
    
    def classify_division(self, division_str: str, event_id: Optional[str] = None, event_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify a division string and return structured information.
        
        Args:
            division_str: Raw division string
            event_id: Optional event ID for gi status lookup
            event_name: Optional event name for gi status lookup
            
        Returns:
            Dictionary with classification results
        """
        try:
            # Parse the division string
            parsed = self.parse_division_string(division_str, event_id, event_name)
            
            # Create classification result
            classification = {
                'division_string': division_str,
                'parsed_components': parsed,
                'is_valid': parsed['confidence'] >= 0.5,
                'suggestions': self._generate_suggestions(parsed),
                'normalized_division': self._create_normalized_division(parsed)
            }
            
            logger.info(f"Classified division '{division_str}' with confidence {parsed['confidence']:.2f}")
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying division '{division_str}': {e}")
            return {
                'division_string': division_str,
                'parsed_components': {},
                'is_valid': False,
                'suggestions': [],
                'normalized_division': '',
                'error': str(e)
            }
    
    def _generate_suggestions(self, parsed: Dict[str, str]) -> List[str]:
        """Generate suggestions for improving the division classification."""
        suggestions = []
        
        if parsed['age_class'] == 'unknown':
            suggestions.append("Age class not detected. Consider adding 'youth', 'adult', or 'masters'")
        
        if parsed['gender'] == 'unknown':
            suggestions.append("Gender not detected. Consider adding 'male' or 'female'")
        
        if parsed['skill_level'] == 'unknown':
            suggestions.append("Skill level not detected. Consider adding belt color or skill level")
        
        if parsed['gi_status'] == 'unknown':
            suggestions.append("Gi status not detected. Consider adding 'gi' or 'no-gi'")
        
        if parsed['weight_class'] == 'unknown':
            suggestions.append("Weight class not detected. Consider adding weight range or category")
        
        return suggestions
    
    def _create_normalized_division(self, parsed: Dict[str, str]) -> str:
        """Create a normalized division string from parsed components."""
        try:
            components = []
            
            # Add age class
            if parsed['age_class'] != 'unknown':
                components.append(parsed['age_class'].title())
            
            # Add gender
            if parsed['gender'] != 'unknown':
                gender_map = {'M': 'Male', 'F': 'Female'}
                components.append(gender_map.get(parsed['gender'], parsed['gender'].title()))
            
            # Add skill level
            if parsed['skill_level'] != 'unknown':
                components.append(parsed['skill_level'].title())
            
            # Add weight class
            if parsed['weight_class'] != 'unknown':
                components.append(parsed['weight_class'])
            
            # Add gi status
            if parsed['gi_status'] != 'unknown':
                gi_map = {'gi': 'Gi', 'no-gi': 'No-Gi'}
                components.append(gi_map.get(parsed['gi_status'], parsed['gi_status'].title()))
            
            return ' '.join(components) if components else 'Unknown Division'
            
        except Exception as e:
            logger.error(f"Error creating normalized division: {e}")
            return 'Unknown Division'
    
    def validate_division(self, division_str: str, event_id: Optional[str] = None, event_name: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Validate a division string and return validation results.
        
        Args:
            division_str: Division string to validate
            event_id: Optional event ID for gi status lookup
            event_name: Optional event name for gi status lookup
            
        Returns:
            Tuple of (is_valid, validation_errors)
        """
        try:
            classification = self.classify_division(division_str, event_id, event_name)
            errors = []
            
            if not classification['is_valid']:
                errors.append("Division string has low confidence score")
            
            if classification['parsed_components']['age_class'] == 'unknown':
                errors.append("Age class not detected")
            
            if classification['parsed_components']['gender'] == 'unknown':
                errors.append("Gender not detected")
            
            if classification['parsed_components']['skill_level'] == 'unknown':
                errors.append("Skill level not detected")
            
            if classification['parsed_components']['gi_status'] == 'unknown':
                errors.append("Gi status not detected")
            
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Error validating division '{division_str}': {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def get_division_mapping(self, division_str: str, event_id: Optional[str] = None, event_name: Optional[str] = None) -> Dict[str, str]:
        """
        Get standardized mapping for a division string.
        
        Args:
            division_str: Division string to map
            event_id: Optional event ID for gi status lookup
            event_name: Optional event name for gi status lookup
            
        Returns:
            Dictionary with standardized mapping
        """
        try:
            parsed = self.parse_division_string(division_str, event_id, event_name)
            
            mapping = {
                'original': division_str,
                'age_class': parsed['age_class'],
                'gender': parsed['gender'],
                'skill_level': parsed['skill_level'],
                'gi_status': parsed['gi_status'],
                'weight_class': parsed['weight_class'],
                'normalized': self._create_normalized_division(parsed)
            }
            
            return mapping
            
        except Exception as e:
            logger.error(f"Error getting division mapping for '{division_str}': {e}")
            return {
                'original': division_str,
                'age_class': 'unknown',
                'gender': 'unknown',
                'skill_level': 'unknown',
                'gi_status': 'unknown',
                'weight_class': 'unknown',
                'normalized': 'Unknown Division'
            }
    
    def batch_classify_divisions(self, division_strings: List[str], event_id: Optional[str] = None, event_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Classify multiple division strings in batch.
        
        Args:
            division_strings: List of division strings to classify
            event_id: Optional event ID for gi status lookup
            event_name: Optional event name for gi status lookup
            
        Returns:
            Dictionary mapping original strings to classification results
        """
        try:
            results = {}
            
            for division_str in division_strings:
                results[division_str] = self.classify_division(division_str, event_id, event_name)
            
            # Calculate batch statistics based on actual results (not input count)
            total = len(results)
            valid = sum(1 for result in results.values() if result['is_valid'])
            avg_confidence = sum(result['parsed_components']['confidence'] for result in results.values()) / total if total > 0 else 0
            
            logger.info(f"Batch classified {len(division_strings)} divisions: {valid} valid, avg confidence {avg_confidence:.2f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch classification: {e}")
            return {}
    
    def get_division_statistics(self, division_strings: List[str], event_id: Optional[str] = None, event_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about division classifications.
        
        Args:
            division_strings: List of division strings to analyze
            event_id: Optional event ID for gi status lookup
            event_name: Optional event name for gi status lookup
            
        Returns:
            Dictionary with classification statistics
        """
        try:
            classifications = self.batch_classify_divisions(division_strings, event_id, event_name)
            
            stats = {
                'total_divisions': len(division_strings),
                'valid_divisions': 0,
                'invalid_divisions': 0,
                'avg_confidence': 0.0,
                'age_class_distribution': {},
                'gender_distribution': {},
                'skill_level_distribution': {},
                'gi_status_distribution': {},
                'common_issues': []
            }
            
            total_confidence = 0.0
            
            for division_str, classification in classifications.items():
                parsed = classification['parsed_components']
                
                if classification['is_valid']:
                    stats['valid_divisions'] += 1
                else:
                    stats['invalid_divisions'] += 1
                
                total_confidence += parsed['confidence']
                
                # Count distributions
                for component in ['age_class', 'gender', 'skill_level', 'gi_status']:
                    value = parsed[component]
                    distribution_key = f"{component}_distribution"
                    if distribution_key in stats:
                        stats[distribution_key][value] = stats[distribution_key].get(value, 0) + 1
            
            if stats['total_divisions'] > 0:
                stats['avg_confidence'] = total_confidence / stats['total_divisions']
            
            # Identify common issues
            if stats['invalid_divisions'] > 0:
                stats['common_issues'].append(f"{stats['invalid_divisions']} divisions have low confidence scores")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting division statistics: {e}")
            return {} 