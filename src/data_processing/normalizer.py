"""
ADCC Analysis Engine v0.6 - Data Normalizer
Handles raw file processing, data cleaning, and normalization.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

from src.core.constants import (
    MIN_AGE, MAX_AGE, VALID_GENDERS, VALID_SKILL_LEVELS,
    RAW_DATA_DIR, PROCESSED_DATA_DIR
)
from src.utils.validators import (
    normalize_name, validate_age, validate_gender, validate_skill_level,
    validate_date, validate_csv_data
)
from src.utils.file_handler import (
    load_json_file, save_json_file, load_parquet_file, save_parquet_file
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataNormalizer:
    """Handles raw file processing, data cleaning, and normalization."""
    
    def __init__(self):
        self.processed_data = {
            'athletes': [],
            'events': [],
            'matches': [],
            'divisions': []
        }
        self.validation_errors = []
        self.processing_stats = {
            'files_processed': 0,
            'records_processed': 0,
            'records_validated': 0,
            'records_failed': 0
        }
    
    def process_csv_registration_file(self, file_path: Path) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Process CSV registration file and return normalized athlete data.
        
        Args:
            file_path: Path to CSV registration file
            
        Returns:
            Tuple of (success, normalized_athletes)
        """
        try:
            logger.info(f"Processing CSV registration file: {file_path}")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records from CSV")
            
            # Expected columns for registration data
            expected_columns = [
                'Name', 'Age', 'Gender', 'Country', 'Club', 'Skill Level'
            ]
            
            # Validate CSV structure
            is_valid, cleaned_df, errors = validate_csv_data(df, expected_columns)
            if not is_valid:
                logger.error(f"CSV validation failed: {errors}")
                self.validation_errors.extend(errors)
                return False, []
            
            # Process each athlete record
            normalized_athletes = []
            for index, row in cleaned_df.iterrows():
                try:
                    athlete = self._normalize_athlete_record(row)
                    if athlete:
                        normalized_athletes.append(athlete)
                        self.processing_stats['records_validated'] += 1
                    else:
                        self.processing_stats['records_failed'] += 1
                except Exception as e:
                    logger.warning(f"Failed to process athlete record {index}: {e}")
                    self.processing_stats['records_failed'] += 1
                    self.validation_errors.append(f"Row {index}: {str(e)}")
            
            self.processing_stats['records_processed'] += len(df)
            logger.info(f"Successfully processed {len(normalized_athletes)} athletes from CSV")
            
            return True, normalized_athletes
            
        except Exception as e:
            logger.error(f"Failed to process CSV file {file_path}: {e}")
            self.validation_errors.append(f"CSV processing error: {str(e)}")
            return False, []
    
    def process_excel_match_file(self, file_path: Path) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Process Excel match results file and return normalized match data.
        
        Args:
            file_path: Path to Excel match file
            
        Returns:
            Tuple of (success, normalized_matches)
        """
        try:
            logger.info(f"Processing Excel match file: {file_path}")
            
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name='Match_Results')
            logger.info(f"Loaded {len(df)} match records from Excel")
            
            # Expected columns for match data
            expected_columns = [
                'Division', 'Winner_ID', 'Loser_ID', 'Winner_Name', 'Loser_Name', 'Outcome'
            ]
            
            # Validate Excel structure
            is_valid, cleaned_df, errors = validate_csv_data(df, expected_columns)
            if not is_valid:
                logger.error(f"Excel validation failed: {errors}")
                self.validation_errors.extend(errors)
                return False, []
            
            # Process each match record
            normalized_matches = []
            for index, row in cleaned_df.iterrows():
                try:
                    match = self._normalize_match_record(row)
                    if match:
                        normalized_matches.append(match)
                        self.processing_stats['records_validated'] += 1
                    else:
                        self.processing_stats['records_failed'] += 1
                except Exception as e:
                    logger.warning(f"Failed to process match record {index}: {e}")
                    self.processing_stats['records_failed'] += 1
                    self.validation_errors.append(f"Row {index}: {str(e)}")
            
            self.processing_stats['records_processed'] += len(df)
            logger.info(f"Successfully processed {len(normalized_matches)} matches from Excel")
            
            return True, normalized_matches
            
        except Exception as e:
            logger.error(f"Failed to process Excel file {file_path}: {e}")
            self.validation_errors.append(f"Excel processing error: {str(e)}")
            return False, []
    
    def process_json_api_file(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """
        Process JSON API response file and return normalized data.
        
        Args:
            file_path: Path to JSON API file
            
        Returns:
            Tuple of (success, normalized_data)
        """
        try:
            logger.info(f"Processing JSON API file: {file_path}")
            
            # Load JSON data
            api_data = load_json_file(file_path)
            if not api_data:
                logger.error(f"Failed to load JSON data from {file_path}")
                return False, {}
            
            # Extract and normalize data
            normalized_data = {
                'event': self._normalize_event_data(api_data.get('event', {})),
                'athletes': [],
                'divisions': []
            }
            
            # Process athletes
            athletes = api_data.get('athletes', [])
            for athlete_data in athletes:
                try:
                    athlete = self._normalize_athlete_record(athlete_data)
                    if athlete:
                        normalized_data['athletes'].append(athlete)
                        self.processing_stats['records_validated'] += 1
                    else:
                        self.processing_stats['records_failed'] += 1
                except Exception as e:
                    logger.warning(f"Failed to process athlete from JSON: {e}")
                    self.processing_stats['records_failed'] += 1
            
            # Process divisions
            divisions = api_data.get('divisions', [])
            for division_data in divisions:
                try:
                    division = self._normalize_division_data(division_data)
                    if division:
                        normalized_data['divisions'].append(division)
                except Exception as e:
                    logger.warning(f"Failed to process division from JSON: {e}")
            
            self.processing_stats['records_processed'] += len(athletes)
            logger.info(f"Successfully processed JSON API data: {len(normalized_data['athletes'])} athletes")
            
            return True, normalized_data
            
        except Exception as e:
            logger.error(f"Failed to process JSON file {file_path}: {e}")
            self.validation_errors.append(f"JSON processing error: {str(e)}")
            return False, {}
    
    def _normalize_athlete_record(self, row: Union[pd.Series, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Normalize a single athlete record."""
        try:
            # Convert pandas Series to dict if needed
            if isinstance(row, pd.Series):
                row = row.to_dict()
            
            # Extract and validate basic fields
            name = normalize_name(str(row.get('Name', '')))
            if not name:
                logger.warning("Athlete name is empty or invalid")
                return None
            
            age = validate_age(row.get('Age'))
            if age is None:
                logger.warning(f"Invalid age for athlete {name}")
                return None
            
            gender = validate_gender(row.get('Gender'))
            if gender is None:
                logger.warning(f"Invalid gender for athlete {name}")
                return None
            
            skill_level = validate_skill_level(row.get('Skill Level'))
            if skill_level is None:
                logger.warning(f"Invalid skill level for athlete {name}")
                return None
            
            # Create normalized athlete record
            athlete = {
                'name': name,
                'age': age,
                'gender': gender,
                'country': str(row.get('Country', '')).strip(),
                'club': str(row.get('Club', '')).strip(),
                'skill_level': skill_level,
                'weight': str(row.get('Weight', '')).strip(),
                'belt': str(row.get('Belt', '')).strip(),
                'email': str(row.get('Email', '')).strip(),
                'phone': str(row.get('Phone', '')).strip(),
                'raw_data': row  # Keep original data for reference
            }
            
            return athlete
            
        except Exception as e:
            logger.error(f"Error normalizing athlete record: {e}")
            return None
    
    def _normalize_match_record(self, row: Union[pd.Series, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Normalize a single match record."""
        try:
            # Convert pandas Series to dict if needed
            if isinstance(row, pd.Series):
                row = row.to_dict()
            
            # Extract and validate basic fields
            division = str(row.get('Division', '')).strip()
            if not division:
                logger.warning("Match division is empty")
                return None
            
            winner_id = str(row.get('Winner_ID', '')).strip()
            loser_id = str(row.get('Loser_ID', '')).strip()
            if not winner_id or not loser_id:
                logger.warning("Match missing winner or loser ID")
                return None
            
            outcome = str(row.get('Outcome', '')).strip()
            if not outcome:
                logger.warning("Match outcome is empty")
                return None
            
            # Create normalized match record
            match = {
                'division': division,
                'winner_id': winner_id,
                'loser_id': loser_id,
                'winner_name': str(row.get('Winner_Name', '')).strip(),
                'loser_name': str(row.get('Loser_Name', '')).strip(),
                'outcome': outcome,
                'method': str(row.get('Method', '')).strip(),
                'time': str(row.get('Time', '')).strip(),
                'round': int(row.get('Round', 1)),
                'points_winner': int(row.get('Points_Winner', 0)),
                'points_loser': int(row.get('Points_Loser', 0)),
                'raw_data': row  # Keep original data for reference
            }
            
            return match
            
        except Exception as e:
            logger.error(f"Error normalizing match record: {e}")
            return None
    
    def _normalize_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event data."""
        try:
            event = {
                'name': str(event_data.get('Event_Name', '')).strip(),
                'date': validate_date(event_data.get('Event_Date')),
                'location': str(event_data.get('Location', '')).strip(),
                'organizer': str(event_data.get('Organizer', '')).strip(),
                'total_participants': int(event_data.get('Total_Participants', 0)),
                'divisions': int(event_data.get('Divisions', 0)),
                'status': str(event_data.get('Status', '')).strip(),
                'raw_data': event_data
            }
            return event
        except Exception as e:
            logger.error(f"Error normalizing event data: {e}")
            return {}
    
    def _normalize_division_data(self, division_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize division data."""
        try:
            division = {
                'name': str(division_data.get('name', '')).strip(),
                'participants': int(division_data.get('participants', 0)),
                'status': str(division_data.get('status', '')).strip(),
                'raw_data': division_data
            }
            return division
        except Exception as e:
            logger.error(f"Error normalizing division data: {e}")
            return None
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process a single file based on its type and extension.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.csv':
                success, data = self.process_csv_registration_file(file_path)
                if success:
                    self.processed_data['athletes'].extend(data)
                    self.processing_stats['files_processed'] += 1
                return success
                
            elif file_extension == '.xlsx':
                success, data = self.process_excel_match_file(file_path)
                if success:
                    self.processed_data['matches'].extend(data)
                    self.processing_stats['files_processed'] += 1
                return success
                
            elif file_extension == '.json':
                success, data = self.process_json_api_file(file_path)
                if success:
                    if 'event' in data:
                        self.processed_data['events'].append(data['event'])
                    if 'athletes' in data:
                        self.processed_data['athletes'].extend(data['athletes'])
                    if 'divisions' in data:
                        self.processed_data['divisions'].extend(data['divisions'])
                    self.processing_stats['files_processed'] += 1
                return success
                
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return False
    
    def process_directory(self, directory: Path) -> bool:
        """
        Process all supported files in a directory.
        
        Args:
            directory: Directory containing files to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            if not directory.exists():
                logger.error(f"Directory does not exist: {directory}")
                return False
            
            supported_extensions = ['.csv', '.xlsx', '.json']
            files_processed = 0
            total_files = 0
            
            for file_path in directory.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    total_files += 1
                    if self.process_file(file_path):
                        files_processed += 1
            
            logger.info(f"Processed {files_processed}/{total_files} files in {directory}")
            return files_processed > 0
            
        except Exception as e:
            logger.error(f"Error processing directory {directory}: {e}")
            return False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            **self.processing_stats,
            'validation_errors': len(self.validation_errors),
            'processed_athletes': len(self.processed_data['athletes']),
            'processed_matches': len(self.processed_data['matches']),
            'processed_events': len(self.processed_data['events']),
            'processed_divisions': len(self.processed_data['divisions'])
        }
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors."""
        return self.validation_errors.copy()
    
    def save_processed_data(self, output_dir: Path) -> bool:
        """
        Save processed data to output directory.
        
        Args:
            output_dir: Directory to save processed data
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save athletes data
            if self.processed_data['athletes']:
                athletes_df = pd.DataFrame(self.processed_data['athletes'])
                athletes_path = output_dir / "processed_athletes.parquet"
                save_parquet_file(athletes_df, athletes_path)
                logger.info(f"Saved {len(self.processed_data['athletes'])} athletes to {athletes_path}")
            
            # Save matches data
            if self.processed_data['matches']:
                matches_df = pd.DataFrame(self.processed_data['matches'])
                matches_path = output_dir / "processed_matches.parquet"
                save_parquet_file(matches_df, matches_path)
                logger.info(f"Saved {len(self.processed_data['matches'])} matches to {matches_path}")
            
            # Save events data
            if self.processed_data['events']:
                events_path = output_dir / "processed_events.json"
                save_json_file(self.processed_data['events'], events_path)
                logger.info(f"Saved {len(self.processed_data['events'])} events to {events_path}")
            
            # Save divisions data
            if self.processed_data['divisions']:
                divisions_path = output_dir / "processed_divisions.json"
                save_json_file(self.processed_data['divisions'], divisions_path)
                logger.info(f"Saved {len(self.processed_data['divisions'])} divisions to {divisions_path}")
            
            # Save processing stats
            stats_path = output_dir / "processing_stats.json"
            save_json_file(self.get_processing_stats(), stats_path)
            
            # Save validation errors
            if self.validation_errors:
                errors_path = output_dir / "validation_errors.json"
                save_json_file(self.validation_errors, errors_path)
                logger.warning(f"Saved {len(self.validation_errors)} validation errors to {errors_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            return False
    
    def reset(self):
        """Reset the normalizer state."""
        self.processed_data = {
            'athletes': [],
            'events': [],
            'matches': [],
            'divisions': []
        }
        self.validation_errors = []
        self.processing_stats = {
            'files_processed': 0,
            'records_processed': 0,
            'records_validated': 0,
            'records_failed': 0
        }
        logger.info("DataNormalizer state reset") 