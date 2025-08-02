"""
ADCC Analysis Engine v0.6 - Phase 5 Verification
Tests the Analytics Engine components.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.models import Athlete, Match, Event, Division, Gender, SkillLevel, AgeClass, GiStatus
from analytics.glicko_engine import GlickoEngine
from analytics.record_calculator import RecordCalculator
from analytics.medal_tracker import MedalTracker
from analytics.report_generator import ReportGenerator


def test_glicko_engine():
    """Test GlickoEngine functionality."""
    print("\n🔍 Testing Glicko-2 Engine...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize engine
            glicko_engine = GlickoEngine(datastore_dir=datastore_path)
            
            # Initialize athletes
            success1 = glicko_engine.initialize_athlete("A001", 1500.0, 350.0, 0.06)
            success2 = glicko_engine.initialize_athlete("A002", 1600.0, 300.0, 0.05)
            
            if not success1 or not success2:
                raise Exception("Failed to initialize athletes")
            
            # Get athlete ratings
            rating1 = glicko_engine.get_athlete_rating("A001")
            rating2 = glicko_engine.get_athlete_rating("A002")
            
            if not rating1 or not rating2:
                raise Exception("Failed to retrieve athlete ratings")
            
            # Test expected score calculation
            expected_score = glicko_engine.calculate_expected_score(
                rating1['rating'], rating1['rating_deviation'],
                rating2['rating'], rating2['rating_deviation']
            )
            
            if not (0 <= expected_score <= 1):
                raise Exception("Invalid expected score")
            
            # Test rating update
            original_rating = rating1['rating']
            success = glicko_engine.update_rating(
                "A001", rating2['rating'], rating2['rating_deviation'], 1.0, "M001"
            )
            
            if not success:
                raise Exception("Failed to update rating")
            
            # Get updated rating
            updated_rating = glicko_engine.get_athlete_rating("A001")
            if updated_rating['rating'] <= original_rating:
                raise Exception(f"Rating should increase after win: {original_rating} -> {updated_rating['rating']}")
            
            # Test rating period management
            success = glicko_engine.start_rating_period("PERIOD001", "Test period")
            if not success:
                raise Exception("Failed to start rating period")
            
            # Get statistics
            stats = glicko_engine.get_rating_statistics()
            if stats['total_athletes'] != 2:
                raise Exception("Incorrect athlete count in statistics")
            
            # Export to DataFrame
            df = glicko_engine.export_ratings_to_dataframe()
            if len(df) != 2:
                raise Exception("Incorrect DataFrame size")
        
        print("✅ Glicko-2 Engine: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Glicko-2 Engine: FAILED - {e}")
        return False


def test_record_calculator():
    """Test RecordCalculator functionality."""
    print("\n🔍 Testing Record Calculator...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize calculator
            record_calc = RecordCalculator(datastore_dir=datastore_path)
            
            # Initialize athletes
            success1 = record_calc.initialize_athlete("A001")
            success2 = record_calc.initialize_athlete("A002")
            
            if not success1 or not success2:
                raise Exception("Failed to initialize athletes")
            
            # Create test match
            match = Match(
                id="M001",
                event_id="EVENT001",
                division_id="D001",
                athlete1_id="A001",
                athlete2_id="A002",
                winner_id="A001",
                win_type="submission",
                bracket_round="final",
                match_date=datetime.now(timezone.utc)
            )
            
            # Process match
            success = record_calc.process_match(match, "A001")
            if not success:
                raise Exception("Failed to process match")
            
            # Get athlete records
            record1 = record_calc.get_athlete_record("A001")
            record2 = record_calc.get_athlete_record("A002")
            
            if not record1 or not record2:
                raise Exception("Failed to retrieve athlete records")
            
            # Check record accuracy
            if record1['wins'] != 1 or record1['losses'] != 0:
                raise Exception("Incorrect win/loss record for A001")
            
            if record2['wins'] != 0 or record2['losses'] != 1:
                raise Exception("Incorrect win/loss record for A002")
            
            # Test win streak calculation
            streak = record_calc.calculate_win_streak("A001")
            if streak != 1:
                raise Exception("Incorrect win streak calculation")
            
            # Get athletes by win rate
            athletes_by_win_rate = record_calc.get_athletes_by_win_rate(min_matches=1)
            if len(athletes_by_win_rate) != 2:
                raise Exception("Incorrect number of athletes by win rate")
            
            # Validate record accuracy
            validation = record_calc.validate_record_accuracy("A001")
            if not validation['valid']:
                raise Exception("Record validation failed")
            
            # Get statistics
            stats = record_calc.get_record_statistics()
            if stats['total_athletes'] != 2:
                raise Exception("Incorrect athlete count in statistics")
            
            # Export to DataFrame
            df = record_calc.export_records_to_dataframe()
            if len(df) != 2:
                raise Exception("Incorrect DataFrame size")
        
        print("✅ Record Calculator: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Record Calculator: FAILED - {e}")
        return False


def test_medal_tracker():
    """Test MedalTracker functionality."""
    print("\n🔍 Testing Medal Tracker...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize tracker
            medal_tracker = MedalTracker(datastore_dir=datastore_path)
            
            # Initialize athletes
            success1 = medal_tracker.initialize_athlete("A001")
            success2 = medal_tracker.initialize_athlete("A002")
            success3 = medal_tracker.initialize_athlete("A003")
            
            if not success1 or not success2 or not success3:
                raise Exception("Failed to initialize athletes")
            
            # Award medals
            event_date = datetime.now(timezone.utc)
            
            success1 = medal_tracker.award_medal("A001", "EVENT001", "D001", 
                                               MedalTracker.GOLD, 1, 8, event_date)
            success2 = medal_tracker.award_medal("A002", "EVENT001", "D001", 
                                               MedalTracker.SILVER, 2, 8, event_date)
            success3 = medal_tracker.award_medal("A003", "EVENT001", "D001", 
                                               MedalTracker.BRONZE, 3, 8, event_date)
            
            if not success1 or not success2 or not success3:
                raise Exception("Failed to award medals")
            
            # Get athlete medals
            medals1 = medal_tracker.get_athlete_medals("A001")
            medals2 = medal_tracker.get_athlete_medals("A002")
            medals3 = medal_tracker.get_athlete_medals("A003")
            
            if not medals1 or not medals2 or not medals3:
                raise Exception("Failed to retrieve athlete medals")
            
            # Check medal counts
            if medals1['gold'] != 1 or medals1['total_medals'] != 1:
                raise Exception("Incorrect medal count for A001")
            
            if medals2['silver'] != 1 or medals2['total_medals'] != 1:
                raise Exception("Incorrect medal count for A002")
            
            if medals3['bronze'] != 1 or medals3['total_medals'] != 1:
                raise Exception("Incorrect medal count for A003")
            
            # Test tournament results processing
            results = [
                {'athlete_id': 'A001', 'placement': 1, 'total_participants': 8},
                {'athlete_id': 'A002', 'placement': 2, 'total_participants': 8},
                {'athlete_id': 'A003', 'placement': 3, 'total_participants': 8}
            ]
            
            success = medal_tracker.process_tournament_results("EVENT002", "D002", results, event_date)
            if not success:
                raise Exception("Failed to process tournament results")
            
            # Get most decorated athletes
            decorated = medal_tracker.get_most_decorated_athletes(3)
            if len(decorated) != 3:
                raise Exception("Incorrect number of decorated athletes")
            
            # Get athletes by medal type
            gold_athletes = medal_tracker.get_athletes_by_medal_type(MedalTracker.GOLD, 3)
            if len(gold_athletes) != 1:
                raise Exception("Incorrect number of gold medalists")
            
            # Validate medal accuracy
            validation = medal_tracker.validate_medal_accuracy("A001")
            if not validation['valid']:
                raise Exception("Medal validation failed")
            
            # Get statistics
            stats = medal_tracker.get_medal_statistics()
            if stats['total_athletes'] != 3:
                raise Exception("Incorrect athlete count in statistics")
            
            # Export to DataFrame
            df = medal_tracker.export_medals_to_dataframe()
            if len(df) != 3:
                raise Exception("Incorrect DataFrame size")
        
        print("✅ Medal Tracker: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Medal Tracker: FAILED - {e}")
        return False


def test_report_generator():
    """Test ReportGenerator functionality."""
    print("\n🔍 Testing Report Generator...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize generator
            report_gen = ReportGenerator(datastore_dir=datastore_path)
            
            # Test data
            athlete_data = {
                'id': 'A001',
                'name': 'John Doe',
                'age': 25,
                'gender': 'M',
                'country': 'USA',
                'club_id': 'C001',
                'skill_level': 'Expert'
            }
            
            rating_data = {
                'rating': 1550.0,
                'rating_deviation': 300.0,
                'volatility': 0.05,
                'matches_played': 10
            }
            
            record_data = {
                'wins': 8,
                'losses': 2,
                'draws': 0,
                'total_matches': 10,
                'win_rate': 0.8,
                'current_streak': 3
            }
            
            medal_data = {
                'gold': 2,
                'silver': 1,
                'bronze': 0,
                'total_medals': 3
            }
            
            # Generate athlete report
            report_path = report_gen.generate_athlete_report(
                athlete_data, rating_data, record_data, medal_data
            )
            
            if not report_path or not report_path.exists():
                raise Exception("Failed to generate athlete report")
            
            # Test tournament report
            event_data = {
                'id': 'EVENT001',
                'name': 'ADCC Championship',
                'date': '2024-01-15',
                'location': 'Las Vegas, NV'
            }
            
            results_data = [
                {'athlete_id': 'A001', 'placement': 1, 'medal': 'gold'},
                {'athlete_id': 'A002', 'placement': 2, 'medal': 'silver'},
                {'athlete_id': 'A003', 'placement': 3, 'medal': 'bronze'}
            ]
            
            tournament_report = report_gen.generate_tournament_report(event_data, results_data)
            
            if not tournament_report or not tournament_report.exists():
                raise Exception("Failed to generate tournament report")
            
            # List reports
            reports = report_gen.list_reports()
            if len(reports) != 2:
                raise Exception("Incorrect number of reports")
        
        print("✅ Report Generator: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Report Generator: FAILED - {e}")
        return False


def test_analytics_integration():
    """Test integration between all analytics components."""
    print("\n🔍 Testing Analytics Integration...")
    
    try:
        import tempfile
        
        # Create temporary datastore
        with tempfile.TemporaryDirectory() as tmp_dir:
            datastore_path = Path(tmp_dir)
            
            # Initialize all components
            glicko_engine = GlickoEngine(datastore_dir=datastore_path)
            record_calc = RecordCalculator(datastore_dir=datastore_path)
            medal_tracker = MedalTracker(datastore_dir=datastore_path)
            report_gen = ReportGenerator(datastore_dir=datastore_path)
            
            # Initialize athlete in all systems
            athlete_id = "A001"
            
            glicko_engine.initialize_athlete(athlete_id, 1500.0, 350.0, 0.06)
            record_calc.initialize_athlete(athlete_id)
            medal_tracker.initialize_athlete(athlete_id)
            
            # Also initialize A002 for the match
            glicko_engine.initialize_athlete("A002", 1600.0, 300.0, 0.05)
            record_calc.initialize_athlete("A002")
            
            # Create test match
            match = Match(
                id="M001",
                event_id="EVENT001",
                division_id="D001",
                athlete1_id="A001",
                athlete2_id="A002",
                winner_id="A001",
                win_type="submission",
                bracket_round="final",
                match_date=datetime.now(timezone.utc)
            )
            
            # Process match in all systems
            glicko_engine.process_match(match, "A001")
            record_calc.process_match(match, "A001")
            
            # Award medal
            medal_tracker.award_medal(athlete_id, "EVENT001", "D001", 
                                    MedalTracker.GOLD, 1, 8, datetime.now(timezone.utc))
            
            # Get data from all systems
            rating_data = glicko_engine.get_athlete_rating(athlete_id)
            record_data = record_calc.get_athlete_record(athlete_id)
            medal_data = medal_tracker.get_athlete_medals(athlete_id)
            
            # Verify data consistency
            if not rating_data or not record_data or not medal_data:
                raise Exception("Failed to retrieve data from all systems")
            
            if record_data['wins'] != 1:
                raise Exception("Record not updated correctly")
            
            if medal_data['gold'] != 1:
                raise Exception("Medal not awarded correctly")
            
            # Generate comprehensive report
            athlete_data = {
                'id': athlete_id,
                'name': 'John Doe',
                'age': 25,
                'gender': 'M',
                'country': 'USA',
                'club_id': 'C001',
                'skill_level': 'Expert'
            }
            
            report_path = report_gen.generate_athlete_report(
                athlete_data, rating_data, record_data, medal_data
            )
            
            if not report_path or not report_path.exists():
                raise Exception("Failed to generate integrated report")
            
            # Get statistics from all systems
            rating_stats = glicko_engine.get_rating_statistics()
            record_stats = record_calc.get_record_statistics()
            medal_stats = medal_tracker.get_medal_statistics()
            
            # Verify statistics
            if rating_stats['total_athletes'] != 2:
                raise Exception("Incorrect rating statistics")
            
            if record_stats['total_athletes'] != 2:
                raise Exception("Incorrect record statistics")
            
            if medal_stats['total_athletes'] != 1:
                raise Exception("Incorrect medal statistics")
        
        print("✅ Analytics Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Analytics Integration: FAILED - {e}")
        return False


def main():
    """Run all Phase 5 verification tests."""
    print("🚀 ADCC Analysis Engine v0.6 - Phase 5 Verification")
    print("=" * 60)
    
    tests = [
        ("Glicko-2 Engine", test_glicko_engine),
        ("Record Calculator", test_record_calculator),
        ("Medal Tracker", test_medal_tracker),
        ("Report Generator", test_report_generator),
        ("Analytics Integration", test_analytics_integration)
    ]
    
    results = []
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print("📊 PHASE 5 VERIFICATION SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
    print()
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 5 verification completed successfully!")
        print("✅ All analytics engine components are working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 