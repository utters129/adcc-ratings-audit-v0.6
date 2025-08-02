"""
ADCC Analysis Engine v0.6 - Data Processing Unit Tests
Tests for Phase 3: File Processing Pipeline components.
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from src.data_processing.normalizer import DataNormalizer
from src.data_processing.id_generator import IDGenerator
from src.data_processing.classifier import DivisionClassifier
from tests.fixtures.mock_data_generator import MockDataGenerator


class TestDataNormalizer:
    """Test the DataNormalizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = DataNormalizer()
        self.mock_generator = MockDataGenerator()
        self.test_dir = Path("tests/data/phase3_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.normalizer.reset()
        # Clean up test files
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_normalizer_initialization(self):
        """Test DataNormalizer initialization."""
        assert self.normalizer.processed_data['athletes'] == []
        assert self.normalizer.processed_data['matches'] == []
        assert self.normalizer.processed_data['events'] == []
        assert self.normalizer.processed_data['divisions'] == []
        assert self.normalizer.validation_errors == []
        assert self.normalizer.processing_stats['files_processed'] == 0
    
    def test_process_csv_registration_file_success(self):
        """Test successful CSV registration file processing."""
        # Create test CSV file
        athletes = self.mock_generator.generate_athlete_data(5)
        df = pd.DataFrame(athletes)
        csv_path = self.test_dir / "test_registration.csv"
        df.to_csv(csv_path, index=False)
        
        # Process the file
        success, data = self.normalizer.process_csv_registration_file(csv_path)
        
        assert success is True
        assert len(data) == 5
        assert all('name' in athlete for athlete in data)
        assert all('age' in athlete for athlete in data)
        assert all('gender' in athlete for athlete in data)
        assert self.normalizer.processing_stats['records_validated'] == 5
    
    def test_process_csv_registration_file_invalid_data(self):
        """Test CSV processing with invalid data."""
        # Create CSV with invalid data
        invalid_athletes = [
            {"Name": "John Smith", "Age": 25, "Gender": "M", "Country": "USA", "Club": "Gracie", "Skill Level": "Advanced"},
            {"Name": "", "Age": None, "Gender": "X", "Country": "", "Club": "Alliance", "Skill Level": "Invalid"}
        ]
        df = pd.DataFrame(invalid_athletes)
        csv_path = self.test_dir / "invalid_registration.csv"
        df.to_csv(csv_path, index=False)
        
        # Process the file
        success, data = self.normalizer.process_csv_registration_file(csv_path)
        
        assert success is True  # File processed, but some records failed
        assert len(data) == 1  # Only valid record processed
        assert self.normalizer.processing_stats['records_failed'] >= 1
    
    def test_process_excel_match_file_success(self):
        """Test successful Excel match file processing."""
        # Create test Excel file
        matches = self.mock_generator.generate_match_data(10)
        df = pd.DataFrame(matches)
        excel_path = self.test_dir / "test_matches.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Match_Results', index=False)
        
        # Process the file
        success, data = self.normalizer.process_excel_match_file(excel_path)
        
        assert success is True
        assert len(data) == 10
        assert all('division' in match for match in data)
        assert all('winner_id' in match for match in data)
        assert all('loser_id' in match for match in data)
    
    def test_process_json_api_file_success(self):
        """Test successful JSON API file processing."""
        # Create test JSON file
        api_data = self.mock_generator.generate_json_api_data(5)
        json_path = self.test_dir / "test_api.json"
        import json
        with open(json_path, 'w') as f:
            json.dump(api_data, f)
        
        # Process the file
        success, data = self.normalizer.process_json_api_file(json_path)
        
        assert success is True
        assert 'event' in data
        assert 'athletes' in data
        assert len(data['athletes']) == 5
    
    def test_normalize_athlete_record(self):
        """Test athlete record normalization."""
        athlete_data = {
            'Name': 'John Smith',
            'Age': 25,
            'Gender': 'M',
            'Country': 'USA',
            'Club': 'Gracie Academy',
            'Skill Level': 'Advanced',
            'Weight': '80kg',
            'Belt': 'Purple',
            'Email': 'john.smith@example.com',
            'Phone': '+1-555-123-4567'
        }
        
        normalized = self.normalizer._normalize_athlete_record(athlete_data)
        
        assert normalized is not None
        assert normalized['name'] == 'John Smith'
        assert normalized['age'] == 25
        assert normalized['gender'] == 'M'
        assert normalized['skill_level'] == 'Advanced'
    
    def test_normalize_athlete_record_invalid(self):
        """Test athlete record normalization with invalid data."""
        invalid_data = {
            'Name': '',
            'Age': 999,
            'Gender': 'X',
            'Country': 'USA',
            'Club': 'Gracie',
            'Skill Level': 'Invalid'
        }
        
        normalized = self.normalizer._normalize_athlete_record(invalid_data)
        
        assert normalized is None
    
    def test_process_file_csv(self):
        """Test processing CSV file through main interface."""
        # Create test CSV file
        athletes = self.mock_generator.generate_athlete_data(3)
        df = pd.DataFrame(athletes)
        csv_path = self.test_dir / "test.csv"
        df.to_csv(csv_path, index=False)
        
        # Process the file
        success = self.normalizer.process_file(csv_path)
        
        assert success is True
        assert len(self.normalizer.processed_data['athletes']) == 3
        assert self.normalizer.processing_stats['files_processed'] == 1
    
    def test_process_file_unsupported(self):
        """Test processing unsupported file type."""
        # Create unsupported file
        unsupported_path = self.test_dir / "test.txt"
        unsupported_path.write_text("test data")
        
        # Process the file
        success = self.normalizer.process_file(unsupported_path)
        
        assert success is False
    
    def test_get_processing_stats(self):
        """Test getting processing statistics."""
        stats = self.normalizer.get_processing_stats()
        
        assert 'files_processed' in stats
        assert 'records_processed' in stats
        assert 'records_validated' in stats
        assert 'records_failed' in stats
        assert 'validation_errors' in stats
    
    def test_reset(self):
        """Test normalizer reset."""
        # Add some data
        self.normalizer.processed_data['athletes'] = [{'name': 'test'}]
        self.normalizer.validation_errors = ['test error']
        self.normalizer.processing_stats['files_processed'] = 1
        
        # Reset
        self.normalizer.reset()
        
        assert self.normalizer.processed_data['athletes'] == []
        assert self.normalizer.validation_errors == []
        assert self.normalizer.processing_stats['files_processed'] == 0


class TestIDGenerator:
    """Test the IDGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_registry_path = Path("tests/data/phase3_test/id_registry.json")
        self.id_generator = IDGenerator(self.test_registry_path)
        self.test_dir = self.test_registry_path.parent
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.id_generator.reset()
        # Clean up test files
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_id_generator_initialization(self):
        """Test IDGenerator initialization."""
        assert self.id_generator.id_registry_path == self.test_registry_path
        assert 'athletes' in self.id_generator.id_registry
        assert 'events' in self.id_generator.id_registry
        assert 'divisions' in self.id_generator.id_registry
        assert 'matches' in self.id_generator.id_registry
        assert 'clubs' in self.id_generator.id_registry
    
    def test_generate_athlete_id(self):
        """Test athlete ID generation."""
        athlete_id = self.id_generator.generate_athlete_id("John Smith", "USA")
        
        assert athlete_id.startswith('A')
        assert len(athlete_id) > 1
        assert self.id_generator.is_id_exists(athlete_id, 'athletes')
    
    def test_generate_athlete_id_with_birth_year(self):
        """Test athlete ID generation with birth year."""
        athlete_id = self.id_generator.generate_athlete_id("John Smith", "USA", 1990)
        
        assert athlete_id.startswith('A')
        assert self.id_generator.is_id_exists(athlete_id, 'athletes')
    
    def test_generate_event_id(self):
        """Test event ID generation."""
        event_date = datetime(2024, 6, 15)
        event_id = self.id_generator.generate_event_id("ADCC Championship 2024", event_date)
        
        assert event_id.startswith('E')
        assert self.id_generator.is_id_exists(event_id, 'events')
    
    def test_generate_division_id(self):
        """Test division ID generation."""
        division_id = self.id_generator.generate_division_id("adult", "M", "advanced", "gi")
        
        assert division_id.startswith('D')
        assert self.id_generator.is_id_exists(division_id, 'divisions')
    
    def test_generate_match_id(self):
        """Test match ID generation."""
        winner_id = "A12345"
        loser_id = "A67890"
        event_id = "E20240615"
        division_id = "D12345"
        
        match_id = self.id_generator.generate_match_id(winner_id, loser_id, event_id, division_id)
        
        assert match_id.startswith('M')
        assert self.id_generator.is_id_exists(match_id, 'matches')
    
    def test_generate_club_id(self):
        """Test club ID generation."""
        club_id = self.id_generator.generate_club_id("Gracie Academy", "USA")
        
        assert club_id.startswith('C')
        assert self.id_generator.is_id_exists(club_id, 'clubs')
    
    def test_id_uniqueness(self):
        """Test that generated IDs are unique."""
        # Generate multiple athlete IDs
        athlete_ids = set()
        for i in range(10):
            athlete_id = self.id_generator.generate_athlete_id(f"Athlete {i}", "USA")
            athlete_ids.add(athlete_id)
        
        assert len(athlete_ids) == 10  # All IDs should be unique
    
    def test_get_id_info(self):
        """Test getting ID information."""
        athlete_id = self.id_generator.generate_athlete_id("John Smith", "USA")
        info = self.id_generator.get_id_info(athlete_id, 'athletes')
        
        assert info is not None
        assert info['name'] == 'John Smith'
        assert info['country'] == 'USA'
    
    def test_get_all_ids(self):
        """Test getting all IDs for an entity type."""
        # Generate some IDs
        self.id_generator.generate_athlete_id("Athlete 1", "USA")
        self.id_generator.generate_athlete_id("Athlete 2", "Canada")
        
        all_athlete_ids = self.id_generator.get_all_ids('athletes')
        
        assert len(all_athlete_ids) >= 2
    
    def test_get_id_statistics(self):
        """Test getting ID statistics."""
        # Generate some IDs
        self.id_generator.generate_athlete_id("Athlete 1", "USA")
        self.id_generator.generate_event_id("Event 1", datetime.now())
        
        stats = self.id_generator.get_id_statistics()
        
        assert 'athletes' in stats
        assert 'events' in stats
        assert stats['athletes'] >= 1
        assert stats['events'] >= 1
    
    def test_save_registry(self):
        """Test saving ID registry."""
        # Generate some IDs
        self.id_generator.generate_athlete_id("Test Athlete", "USA")
        
        # Save registry
        success = self.id_generator.save_registry()
        
        assert success is True
        assert self.test_registry_path.exists()


class TestDivisionClassifier:
    """Test the DivisionClassifier class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = DivisionClassifier()
    
    def test_classifier_initialization(self):
        """Test DivisionClassifier initialization."""
        assert hasattr(self.classifier, 'age_patterns')
        assert hasattr(self.classifier, 'gender_patterns')
        assert hasattr(self.classifier, 'skill_patterns')
        assert hasattr(self.classifier, 'gi_patterns')
    
    def test_parse_division_string_valid(self):
        """Test parsing valid division string."""
        division_str = "Adult Male Black Belt -88kg Gi"
        parsed = self.classifier.parse_division_string(division_str)
        
        assert parsed['age_class'] == 'adult'
        assert parsed['gender'] == 'M'
        assert parsed['skill_level'] == 'expert'
        assert parsed['gi_status'] == 'gi'
        assert parsed['confidence'] > 0.5
    
    def test_parse_division_string_no_gi(self):
        """Test parsing no-gi division string."""
        division_str = "Adult Female Purple Belt No-Gi -64kg"
        parsed = self.classifier.parse_division_string(division_str)
        
        assert parsed['age_class'] == 'adult'
        assert parsed['gender'] == 'F'
        assert parsed['skill_level'] == 'advanced'
        assert parsed['gi_status'] == 'no-gi'
    
    def test_parse_division_string_youth(self):
        """Test parsing youth division string."""
        division_str = "Youth Male Blue Belt Gi U16"
        parsed = self.classifier.parse_division_string(division_str)
        
        assert parsed['age_class'] == 'youth'
        assert parsed['gender'] == 'M'
        assert parsed['skill_level'] == 'intermediate'
        assert parsed['gi_status'] == 'gi'
    
    def test_parse_division_string_masters(self):
        """Test parsing masters division string."""
        division_str = "Masters Female Brown Belt No-Gi 30+"
        parsed = self.classifier.parse_division_string(division_str)
        
        assert parsed['age_class'] == 'masters'
        assert parsed['gender'] == 'F'
        assert parsed['skill_level'] == 'expert'
        assert parsed['gi_status'] == 'no-gi'
    
    def test_parse_division_string_invalid(self):
        """Test parsing invalid division string."""
        division_str = "Invalid Division String"
        parsed = self.classifier.parse_division_string(division_str)
        
        assert parsed['age_class'] == 'adult'  # Default
        assert parsed['gender'] == 'unknown'
        assert parsed['skill_level'] == 'unknown'
        assert parsed['confidence'] < 0.5
    
    def test_classify_division(self):
        """Test division classification."""
        division_str = "Adult Male Black Belt -88kg Gi"
        classification = self.classifier.classify_division(division_str)
        
        assert classification['is_valid'] is True
        assert 'suggestions' in classification
        assert 'normalized_division' in classification
        assert classification['parsed_components']['confidence'] > 0.5
    
    def test_validate_division(self):
        """Test division validation."""
        # Valid division
        is_valid, errors = self.classifier.validate_division("Adult Male Black Belt Gi")
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid division
        is_valid, errors = self.classifier.validate_division("Invalid Division")
        assert is_valid is False
        assert len(errors) > 0
    
    def test_get_division_mapping(self):
        """Test getting division mapping."""
        division_str = "Adult Female Purple Belt No-Gi -64kg"
        mapping = self.classifier.get_division_mapping(division_str)
        
        assert mapping['original'] == division_str
        assert mapping['age_class'] == 'adult'
        assert mapping['gender'] == 'F'
        assert mapping['skill_level'] == 'advanced'
        assert mapping['gi_status'] == 'no-gi'
        assert 'normalized' in mapping
    
    def test_batch_classify_divisions(self):
        """Test batch division classification."""
        division_strings = [
            "Adult Male Black Belt Gi",
            "Adult Female Purple Belt No-Gi",
            "Youth Male Blue Belt Gi"
        ]
        
        results = self.classifier.batch_classify_divisions(division_strings)
        
        assert len(results) == 3
        assert all(result['is_valid'] for result in results.values())
    
    def test_get_division_statistics(self):
        """Test getting division statistics."""
        division_strings = [
            "Adult Male Black Belt Gi",
            "Adult Female Purple Belt No-Gi",
            "Youth Male Blue Belt Gi",
            "Invalid Division"
        ]
        
        stats = self.classifier.get_division_statistics(division_strings)
        
        assert stats['total_divisions'] == 4
        assert stats['valid_divisions'] >= 3
        assert stats['invalid_divisions'] >= 1
        assert 'age_class_distribution' in stats
        assert 'gender_distribution' in stats
        assert 'skill_level_distribution' in stats
        assert 'gi_status_distribution' in stats


class TestDataProcessingIntegration:
    """Integration tests for data processing components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_generator = MockDataGenerator()
        self.normalizer = DataNormalizer()
        self.id_generator = IDGenerator()
        self.classifier = DivisionClassifier()
        self.test_dir = Path("tests/data/phase3_integration_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.normalizer.reset()
        self.id_generator.reset()
        # Clean up test files
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_full_pipeline_integration(self):
        """Test full data processing pipeline integration."""
        # Create test dataset
        test_files = self.mock_generator.create_test_dataset(self.test_dir)
        
        # Process files with normalizer
        for file_path in test_files.values():
            success = self.normalizer.process_file(file_path)
            assert success is True
        
        # Generate IDs for processed data
        for athlete in self.normalizer.processed_data['athletes']:
            athlete_id = self.id_generator.generate_athlete_id(
                athlete['name'], 
                athlete['country']
            )
            assert athlete_id.startswith('A')
        
        # Classify divisions
        divisions = [match['division'] for match in self.normalizer.processed_data['matches']]
        classifications = self.classifier.batch_classify_divisions(divisions)
        
        assert len(classifications) == len(divisions)
        assert all('is_valid' in classification for classification in classifications.values())
        
        # Verify processing stats
        stats = self.normalizer.get_processing_stats()
        assert stats['files_processed'] >= 3  # CSV, Excel, JSON
        assert stats['processed_athletes'] > 0
        assert stats['processed_matches'] > 0
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Create problematic dataset
        problematic_files = self.mock_generator.create_problematic_dataset(self.test_dir)
        
        # Process files - should handle errors gracefully
        for file_path in problematic_files.values():
            if file_path.suffix in ['.csv', '.xlsx', '.json']:
                success = self.normalizer.process_file(file_path)
                # Should not crash, even with problematic data
                assert isinstance(success, bool)
        
        # Verify error handling
        errors = self.normalizer.get_validation_errors()
        assert isinstance(errors, list) 