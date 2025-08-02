#!/usr/bin/env python3
"""
ADCC Analysis Engine v0.6 - Phase 3 Verification Script
Tests the complete File Processing Pipeline implementation.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.normalizer import DataNormalizer
from src.data_processing.id_generator import IDGenerator
from src.data_processing.classifier import DivisionClassifier
from tests.fixtures.mock_data_generator import MockDataGenerator
from src.utils.logger import setup_logging, get_logger


def test_mock_data_generation():
    """Test mock data generation."""
    print("🔧 Testing Mock Data Generation...")
    
    try:
        generator = MockDataGenerator()
        
        # Test athlete data generation
        athletes = generator.generate_athlete_data(10)
        assert len(athletes) == 10
        assert all('Name' in athlete for athlete in athletes)
        print("  ✅ Athlete data generation: PASSED")
        
        # Test match data generation
        matches = generator.generate_match_data(10)
        assert len(matches) == 5  # Half of athlete count
        assert all('Division' in match for match in matches)
        print("  ✅ Match data generation: PASSED")
        
        # Test event data generation
        event = generator.generate_event_data()
        assert 'Event_Name' in event
        assert 'Event_Date' in event
        print("  ✅ Event data generation: PASSED")
        
        # Test API data generation
        api_data = generator.generate_json_api_data(5)
        assert 'event' in api_data
        assert 'athletes' in api_data
        assert len(api_data['athletes']) == 5
        print("  ✅ API data generation: PASSED")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Mock data generation: FAILED - {e}")
        return False


def test_data_normalizer():
    """Test DataNormalizer functionality."""
    print("\n🔧 Testing Data Normalizer...")
    
    try:
        normalizer = DataNormalizer()
        generator = MockDataGenerator()
        test_dir = Path("tests/data/phase3_verification")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        test_files = generator.create_test_dataset(test_dir)
        
        # Process each file
        for file_type, file_path in test_files.items():
            success = normalizer.process_file(file_path)
            assert success is True
            print(f"  ✅ {file_type} processing: PASSED")
        
        # Check processing stats
        stats = normalizer.get_processing_stats()
        assert stats['files_processed'] >= 3
        assert stats['processed_athletes'] > 0
        assert stats['processed_matches'] > 0
        print(f"  ✅ Processing stats: {stats['files_processed']} files, {stats['processed_athletes']} athletes, {stats['processed_matches']} matches")
        
        # Test data normalization
        athlete_data = {
            'Name': 'John Smith',
            'Age': 25,
            'Gender': 'M',
            'Country': 'USA',
            'Club': 'Gracie Academy',
            'Skill Level': 'Advanced'
        }
        
        normalized = normalizer._normalize_athlete_record(athlete_data)
        assert normalized is not None
        assert normalized['name'] == 'John Smith'
        assert normalized['age'] == 25
        print("  ✅ Data normalization: PASSED")
        
        # Clean up
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data normalizer: FAILED - {e}")
        return False


def test_id_generator():
    """Test IDGenerator functionality."""
    print("\n🔧 Testing ID Generator...")
    
    try:
        id_generator = IDGenerator()
        
        # Test athlete ID generation
        athlete_id = id_generator.generate_athlete_id("John Smith", "USA")
        assert athlete_id.startswith('A')
        assert id_generator.is_id_exists(athlete_id, 'athletes')
        print("  ✅ Athlete ID generation: PASSED")
        
        # Test event ID generation
        from datetime import datetime
        event_id = id_generator.generate_event_id("ADCC Championship 2024", datetime(2024, 6, 15))
        assert event_id.startswith('E')
        assert id_generator.is_id_exists(event_id, 'events')
        print("  ✅ Event ID generation: PASSED")
        
        # Test division ID generation
        division_id = id_generator.generate_division_id("adult", "M", "advanced", "gi")
        assert division_id.startswith('D')
        assert id_generator.is_id_exists(division_id, 'divisions')
        print("  ✅ Division ID generation: PASSED")
        
        # Test match ID generation
        match_id = id_generator.generate_match_id("A12345", "A67890", "E20240615", "D12345")
        assert match_id.startswith('M')
        assert id_generator.is_id_exists(match_id, 'matches')
        print("  ✅ Match ID generation: PASSED")
        
        # Test club ID generation
        club_id = id_generator.generate_club_id("Gracie Academy", "USA")
        assert club_id.startswith('C')
        assert id_generator.is_id_exists(club_id, 'clubs')
        print("  ✅ Club ID generation: PASSED")
        
        # Test ID uniqueness
        athlete_ids = set()
        for i in range(10):
            athlete_id = id_generator.generate_athlete_id(f"Athlete {i}", "USA")
            athlete_ids.add(athlete_id)
        assert len(athlete_ids) == 10
        print("  ✅ ID uniqueness: PASSED")
        
        # Test ID statistics
        stats = id_generator.get_id_statistics()
        assert all(count >= 1 for count in stats.values())
        print(f"  ✅ ID statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ID generator: FAILED - {e}")
        return False


def test_division_classifier():
    """Test DivisionClassifier functionality."""
    print("\n🔧 Testing Division Classifier...")
    
    try:
        classifier = DivisionClassifier()
        
        # Test valid division parsing
        test_divisions = [
            "Adult Male Black Belt -88kg Gi",
            "Adult Female Purple Belt No-Gi -64kg",
            "Youth Male Blue Belt Gi U16",
            "Masters Female Brown Belt No-Gi 30+"
        ]
        
        for division_str in test_divisions:
            parsed = classifier.parse_division_string(division_str)
            assert parsed['confidence'] > 0.5
            print(f"  ✅ Division parsing '{division_str}': PASSED (confidence: {parsed['confidence']:.2f})")
        
        # Test division classification
        classification = classifier.classify_division("Adult Male Black Belt -88kg Gi")
        assert classification['is_valid'] is True
        assert 'suggestions' in classification
        assert 'normalized_division' in classification
        print("  ✅ Division classification: PASSED")
        
        # Test division validation
        is_valid, errors = classifier.validate_division("Adult Male Black Belt Gi")
        assert is_valid is True
        assert len(errors) == 0
        print("  ✅ Division validation: PASSED")
        
        # Test batch classification
        results = classifier.batch_classify_divisions(test_divisions)
        assert len(results) == len(test_divisions)
        assert all(result['is_valid'] for result in results.values())
        print("  ✅ Batch classification: PASSED")
        
        # Test division statistics
        stats = classifier.get_division_statistics(test_divisions)
        assert stats['total_divisions'] == len(test_divisions)
        assert stats['valid_divisions'] == len(test_divisions)
        print(f"  ✅ Division statistics: {stats['valid_divisions']}/{stats['total_divisions']} valid")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Division classifier: FAILED - {e}")
        return False


def test_integration():
    """Test integration between all components."""
    print("\n🔧 Testing Component Integration...")
    
    try:
        # Initialize components
        normalizer = DataNormalizer()
        id_generator = IDGenerator()
        classifier = DivisionClassifier()
        generator = MockDataGenerator()
        
        test_dir = Path("tests/data/phase3_integration")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test dataset
        test_files = generator.create_test_dataset(test_dir)
        
        # Process files
        for file_path in test_files.values():
            success = normalizer.process_file(file_path)
            assert success is True
        
        # Generate IDs for athletes
        athlete_ids = []
        for athlete in normalizer.processed_data['athletes']:
            athlete_id = id_generator.generate_athlete_id(
                athlete['name'], 
                athlete['country']
            )
            athlete_ids.append(athlete_id)
        
        assert len(athlete_ids) == len(normalizer.processed_data['athletes'])
        print(f"  ✅ Generated {len(athlete_ids)} athlete IDs")
        
        # Classify divisions
        divisions = [match['division'] for match in normalizer.processed_data['matches']]
        classifications = classifier.batch_classify_divisions(divisions)
        
        # Check that we have classifications for all unique divisions
        unique_divisions = set(divisions)
        assert len(classifications) == len(unique_divisions)
        valid_classifications = sum(1 for c in classifications.values() if c['is_valid'])
        print(f"  ✅ Classified {len(unique_divisions)} unique divisions ({valid_classifications} valid)")
        
        # Generate IDs for divisions (only for valid classifications)
        division_ids = []
        for division_str in divisions:
            parsed = classifier.parse_division_string(division_str)
            if parsed['confidence'] > 0.5:
                division_id = id_generator.generate_division_id(
                    parsed['age_class'],
                    parsed['gender'],
                    parsed['skill_level'],
                    parsed['gi_status']
                )
                division_ids.append(division_id)
        
        print(f"  ✅ Generated {len(division_ids)} division IDs (from {valid_classifications} valid divisions)")
        
        # Verify we have at least some valid divisions
        assert valid_classifications > 0, "No valid divisions found"
        assert len(division_ids) > 0, "No division IDs generated"
        
        # Test data persistence
        output_dir = test_dir / "processed"
        success = normalizer.save_processed_data(output_dir)
        assert success is True
        print("  ✅ Data persistence: PASSED")
        
        # Clean up
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test: FAILED - {e}")
        return False


def main():
    """Main verification function."""
    print("🚀 ADCC Analysis Engine v0.6 - Phase 3 Verification")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Run all tests
    tests = [
        ("Mock Data Generation", test_mock_data_generation),
        ("Data Normalizer", test_data_normalizer),
        ("ID Generator", test_id_generator),
        ("Division Classifier", test_division_classifier),
        ("Component Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED\n")
            else:
                print(f"❌ {test_name}: FAILED\n")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}\n")
    
    # Summary
    print("=" * 60)
    print(f"📊 VERIFICATION SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 3: File Processing Pipeline is COMPLETE!")
        print("\n✅ All components working correctly:")
        print("   • Mock Data Generation")
        print("   • Data Normalizer (CSV, Excel, JSON processing)")
        print("   • ID Generator (unique ID creation)")
        print("   • Division Classifier (division parsing)")
        print("   • Component Integration")
        print("\n🚀 Ready to proceed to Phase 4: Data Storage & State Management")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 