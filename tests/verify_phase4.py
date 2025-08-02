#!/usr/bin/env python3
"""
ADCC Analysis Engine v0.6 - Phase 4 Verification Script
Tests all Phase 4 components: data storage and state management.
"""

import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analytics.athlete_profiles import AthleteProfileManager
from analytics.division_mapper import DivisionMapper
from analytics.club_tracker import ClubTracker
from state_management.save_states import StateManager
from state_management.rollback import StateRollback
from core.models import Athlete, Division, Club, Match, AgeClass, Gender, SkillLevel, GiStatus
from utils.file_handler import save_parquet_file, load_parquet_file, save_json_file, load_json_file
from utils.logger import get_logger

logger = get_logger(__name__)


def test_parquet_file_processing():
    """Test Parquet file processing functionality."""
    print("\n🔍 Testing Parquet File Processing...")
    
    try:
        import pandas as pd
        import tempfile
        
        # Create test data
        test_data = pd.DataFrame({
            'athlete_id': ['A001', 'A002', 'A003'],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'rating': [1500.0, 1450.0, 1600.0],
            'matches_played': [10, 8, 15]
        })
        
        # Test save and load
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
            test_path = Path(tmp_file.name)
        
        # Save to Parquet
        success = save_parquet_file(test_data, test_path)
        if not success:
            raise Exception("Failed to save Parquet file")
        
        # Load from Parquet
        loaded_data = load_parquet_file(test_path)
        if loaded_data is None:
            raise Exception("Failed to load Parquet file")
        
        # Verify data integrity
        if not test_data.equals(loaded_data):
            raise Exception("Data integrity check failed")
        
        # Cleanup
        test_path.unlink()
        
        print("✅ Parquet file processing: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Parquet file processing: FAILED - {e}")
        return False


def test_json_dictionary_creation():
    """Test JSON dictionary creation and management."""
    print("\n🔍 Testing JSON Dictionary Creation...")
    
    try:
        import tempfile
        
        # Test data
        test_data = {
            'athletes': {
                'A001': {'name': 'John Doe', 'rating': 1500.0},
                'A002': {'name': 'Jane Smith', 'rating': 1450.0}
            },
            'metadata': {
                'total_athletes': 2,
                'version': '1.0'
            }
        }
        
        # Test save and load
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            test_path = Path(tmp_file.name)
        
        # Save to JSON
        success = save_json_file(test_data, test_path)
        if not success:
            raise Exception("Failed to save JSON file")
        
        # Load from JSON
        loaded_data = load_json_file(test_path)
        if loaded_data != test_data:
            raise Exception("Data integrity check failed")
        
        # Cleanup
        test_path.unlink()
        
        print("✅ JSON dictionary creation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ JSON dictionary creation: FAILED - {e}")
        return False


def test_athlete_profile_manager():
    """Test AthleteProfileManager functionality."""
    print("\n🔍 Testing Athlete Profile Manager...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize manager
            profile_manager = AthleteProfileManager(datastore_dir=datastore_path)
            
            # Create test athlete
            athlete = Athlete(
                id="A001",
                name="John Doe",
                age=25,
                gender=Gender.MALE,
                country="USA",
                skill_level=SkillLevel.EXPERT
            )
            
            # Create athlete profile
            profile = profile_manager.create_athlete_profile(athlete)
            if not profile:
                raise Exception("Failed to create athlete profile")
            
            # Get athlete profile
            retrieved_profile = profile_manager.get_athlete_profile("A001")
            if not retrieved_profile:
                raise Exception("Failed to retrieve athlete profile")
            
            # Update athlete profile
            updates = {'statistics': {'total_matches': 15, 'wins': 12}}
            success = profile_manager.update_athlete_profile("A001", updates)
            if not success:
                raise Exception("Failed to update athlete profile")
            
            # Get all profiles
            all_profiles = profile_manager.get_all_athlete_profiles()
            if len(all_profiles) != 1:
                raise Exception("Incorrect number of profiles")
            
            # Get statistics
            stats = profile_manager.get_athlete_statistics()
            if stats['total_athletes'] != 1:
                raise Exception("Incorrect athlete count in statistics")
        
        print("✅ Athlete Profile Manager: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Athlete Profile Manager: FAILED - {e}")
        return False


def test_division_mapper():
    """Test DivisionMapper functionality."""
    print("\n🔍 Testing Division Mapper...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize mapper
            division_mapper = DivisionMapper(datastore_dir=datastore_path)
            
            # Create test division
            division = Division(
                id="D001",
                name="Adult Male Expert",
                age_class=AgeClass.ADULT,
                gender=Gender.MALE,
                skill_level=SkillLevel.EXPERT,
                gi_status=GiStatus.GI,
                event_id="EVENT001"
            )
            
            # Register division
            success = division_mapper.register_division(division)
            if not success:
                raise Exception("Failed to register division")
            
            # Get division
            retrieved_division = division_mapper.get_division("D001")
            if not retrieved_division:
                raise Exception("Failed to retrieve division")
            
            # Parse division string
            parsed = division_mapper.parse_division_string("Adult Male Black Belt")
            if not parsed:
                raise Exception("Failed to parse division string")
            
            # Add athlete to division
            success = division_mapper.add_athlete_to_division("D001", "A001")
            if not success:
                raise Exception("Failed to add athlete to division")
            
            # Get divisions by criteria
            divisions = division_mapper.get_divisions_by_criteria(
                age_class="adult",
                gender="M"
            )
            if len(divisions) != 1:
                raise Exception("Incorrect number of divisions found")
            
            # Get statistics
            stats = division_mapper.get_division_statistics()
            if stats['total_divisions'] != 1:
                raise Exception("Incorrect division count in statistics")
        
        print("✅ Division Mapper: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Division Mapper: FAILED - {e}")
        return False


def test_club_tracker():
    """Test ClubTracker functionality."""
    print("\n🔍 Testing Club Tracker...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize tracker
            club_tracker = ClubTracker(datastore_dir=datastore_path)
            
            # Create test club
            club = Club(
                id="C001",
                name="Team Alpha",
                country="USA",
                city="New York"
            )
            
            # Register club
            success = club_tracker.register_club(club)
            if not success:
                raise Exception("Failed to register club")
            
            # Get club
            retrieved_club = club_tracker.get_club("C001")
            if not retrieved_club:
                raise Exception("Failed to retrieve club")
            
            # Add athlete to club
            success = club_tracker.add_athlete_to_club("C001", "A001")
            if not success:
                raise Exception("Failed to add athlete to club")
            
            # Update club performance
            match_result = {'result': 'win', 'method': 'submission'}
            success = club_tracker.update_club_performance("C001", match_result)
            if not success:
                raise Exception("Failed to update club performance")
            
            # Get club rankings
            rankings = club_tracker.get_club_rankings('win_rate')
            if len(rankings) != 1:
                raise Exception("Incorrect number of clubs in rankings")
            
            # Get statistics
            stats = club_tracker.calculate_club_statistics()
            if stats['total_clubs'] != 1:
                raise Exception("Incorrect club count in statistics")
        
        print("✅ Club Tracker: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Club Tracker: FAILED - {e}")
        return False


def test_state_manager():
    """Test StateManager functionality."""
    print("\n🔍 Testing State Manager...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize state manager
            state_manager = StateManager(datastore_dir=datastore_path)
            
            # Test data
            test_data = {
                'athletes': {'A001': {'name': 'John Doe'}},
                'divisions': {'D001': {'name': 'Adult Male Black Belt'}},
                'metadata': {'version': '1.0'}
            }
            
            # Create state snapshot
            state_id = state_manager.create_state_snapshot(
                "Test state snapshot",
                test_data,
                {'test_metadata': 'value'}
            )
            if not state_id:
                raise Exception("Failed to create state snapshot")
            
            # Get state
            retrieved_state = state_manager.get_state(state_id)
            if not retrieved_state:
                raise Exception("Failed to retrieve state")
            
            # Get latest state
            latest_state = state_manager.get_latest_state()
            if not latest_state:
                raise Exception("Failed to get latest state")
            
            # List states
            states = state_manager.list_states()
            if len(states) != 1:
                raise Exception("Incorrect number of states")
            
            # Validate state integrity
            is_valid = state_manager.validate_state_integrity(state_id)
            if not is_valid:
                raise Exception("State integrity validation failed")
            
            # Get state statistics
            stats = state_manager.get_state_statistics()
            if stats['total_states'] != 1:
                raise Exception("Incorrect state count in statistics")
        
        print("✅ State Manager: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ State Manager: FAILED - {e}")
        return False


def test_state_rollback():
    """Test StateRollback functionality."""
    print("\n🔍 Testing State Rollback...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize state manager and rollback
            state_manager = StateManager(datastore_dir=datastore_path)
            state_rollback = StateRollback(state_manager, datastore_dir=datastore_path)
            
            # Create test state
            test_data = {'athletes': {'A001': {'name': 'John Doe'}}}
            state_id = state_manager.create_state_snapshot("Test state", test_data)
            
            # Create rollback point
            rollback_id = state_rollback.create_rollback_point(
                "Test rollback point",
                state_id
            )
            if not rollback_id:
                raise Exception("Failed to create rollback point")
            
            # Get rollback
            rollback_data = state_rollback.get_rollback(rollback_id)
            if not rollback_data:
                raise Exception("Failed to retrieve rollback data")
            
            # Get rollback history
            history = state_rollback.get_rollback_history()
            if len(history) != 1:
                raise Exception("Incorrect number of rollbacks in history")
            
            # Validate rollback safety
            safety = state_rollback.validate_rollback_safety(rollback_id)
            if not safety['safe']:
                raise Exception("Rollback safety validation failed")
            
            # Execute rollback
            success = state_rollback.execute_rollback(rollback_id)
            if not success:
                raise Exception("Failed to execute rollback")
            
            # Get rollback statistics
            stats = state_rollback.get_rollback_statistics()
            if stats['total_rollbacks'] != 2:  # Original + backup rollback
                raise Exception("Incorrect rollback count in statistics")
        
        print("✅ State Rollback: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ State Rollback: FAILED - {e}")
        return False


def test_integration():
    """Test integration between all Phase 4 components."""
    print("\n🔍 Testing Component Integration...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize all components
            profile_manager = AthleteProfileManager(datastore_dir=datastore_path)
            division_mapper = DivisionMapper(datastore_dir=datastore_path)
            club_tracker = ClubTracker(datastore_dir=datastore_path)
            state_manager = StateManager(datastore_dir=datastore_path)
            state_rollback = StateRollback(state_manager, datastore_dir=datastore_path)
            
            # Create test data
            athlete = Athlete(
                id="A001",
                name="John Doe",
                age=25,
                gender=Gender.MALE,
                country="USA",
                skill_level=SkillLevel.EXPERT
            )
            
            division = Division(
                id="D001",
                name="Adult Male Expert",
                age_class=AgeClass.ADULT,
                gender=Gender.MALE,
                skill_level=SkillLevel.EXPERT,
                gi_status=GiStatus.GI,
                event_id="EVENT001"
            )
            
            club = Club(
                id="C001",
                name="Team Alpha",
                country="USA",
                city="New York"
            )
            
            # Create profiles and registrations
            profile_manager.create_athlete_profile(athlete)
            division_mapper.register_division(division)
            club_tracker.register_club(club)
            
            # Add relationships
            division_mapper.add_athlete_to_division("D001", "A001")
            club_tracker.add_athlete_to_club("C001", "A001")
            
            # Create state snapshot
            state_data = {
                'athletes': profile_manager.get_all_athlete_profiles(),
                'divisions': division_mapper.get_all_divisions(),
                'clubs': club_tracker.get_all_clubs()
            }
            
            state_id = state_manager.create_state_snapshot("Integration test state", state_data)
            
            # Create rollback point
            rollback_id = state_rollback.create_rollback_point("Integration rollback", state_id)
            
            # Verify all components work together
            assert len(profile_manager.get_all_athlete_profiles()) == 1
            assert len(division_mapper.get_all_divisions()) == 1
            assert len(club_tracker.get_all_clubs()) == 1
            assert state_manager.get_state(state_id) is not None
            assert state_rollback.get_rollback(rollback_id) is not None
        
        print("✅ Component Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Component Integration: FAILED - {e}")
        return False


def main():
    """Run all Phase 4 verification tests."""
    print("🚀 ADCC Analysis Engine v0.6 - Phase 4 Verification")
    print("=" * 60)
    
    tests = [
        ("Parquet File Processing", test_parquet_file_processing),
        ("JSON Dictionary Creation", test_json_dictionary_creation),
        ("Athlete Profile Manager", test_athlete_profile_manager),
        ("Division Mapper", test_division_mapper),
        ("Club Tracker", test_club_tracker),
        ("State Manager", test_state_manager),
        ("State Rollback", test_state_rollback),
        ("Component Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: FAILED - Unexpected error: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PHASE 4 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 4 verification completed successfully!")
        print("✅ All data storage and state management components are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 