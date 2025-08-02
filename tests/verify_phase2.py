"""
ADCC Analysis Engine v0.6 - Phase 2 Verification Script
Simple script to verify that Phase 2 (Data Models & Validation) is working correctly.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_models():
    """Test core data models."""
    print("🏗️  Testing Core Data Models...")
    
    try:
        from src.core.models import (
            Athlete, Event, Match, Division, Club,
            Gender, SkillLevel, AgeClass, GiStatus
        )
        
        # Test Athlete model
        athlete_data = {
            "id": "A123456",
            "name": "John Doe",
            "age": 25,
            "gender": Gender.MALE,
            "country": "US",
            "skill_level": SkillLevel.ADVANCED
        }
        
        athlete = Athlete(**athlete_data)
        print(f"  ✅ Athlete model: {athlete.name} ({athlete.id})")
        
        # Test Event model
        event_data = {
            "id": "E123456",
            "name": "ADCC World Championship 2024",
            "date": datetime(2024, 6, 15, 9, 0, 0),
            "location": "Las Vegas, NV"
        }
        
        event = Event(**event_data)
        print(f"  ✅ Event model: {event.name} ({event.id})")
        
        # Test Division model
        division_data = {
            "id": "D123456",
            "name": "Adult Male Advanced Gi",
            "age_class": AgeClass.ADULT,
            "gender": Gender.MALE,
            "skill_level": SkillLevel.ADVANCED,
            "gi_status": GiStatus.GI,
            "event_id": "E123456"
        }
        
        division = Division(**division_data)
        print(f"  ✅ Division model: {division.name} ({division.id})")
        
        # Test Club model
        club_data = {
            "id": "C123456",
            "name": "Gracie Academy",
            "country": "US",
            "city": "Los Angeles"
        }
        
        club = Club(**club_data)
        print(f"  ✅ Club model: {club.name} ({club.id})")
        
        # Test Match model
        match_data = {
            "id": "M123456",
            "event_id": "E123456",
            "division_id": "D123456",
            "athlete1_id": "A123456",
            "athlete2_id": "A789012",
            "winner_id": "A123456",
            "win_type": "submission",
            "bracket_round": "final",
            "match_date": datetime(2024, 6, 15, 14, 30, 0)
        }
        
        match = Match(**match_data)
        print(f"  ✅ Match model: {match.id} (Winner: {match.winner_id})")
        
        return True
    except Exception as e:
        print(f"  ❌ Models test failed: {e}")
        return False

def test_validators():
    """Test validation utilities."""
    print("\n🔍 Testing Validation Utilities...")
    
    try:
        from src.utils.validators import (
            normalize_name, validate_age, validate_gender, validate_skill_level,
            parse_division_string, generate_athlete_id, validate_athlete_data
        )
        
        # Test name normalization
        normalized_name = normalize_name("john doe jr")
        print(f"  ✅ Name normalization: 'john doe jr' -> '{normalized_name}'")
        
        # Test age validation
        valid_age = validate_age(25)
        print(f"  ✅ Age validation: 25 -> {valid_age}")
        
        # Test gender validation
        valid_gender = validate_gender("M")
        print(f"  ✅ Gender validation: 'M' -> '{valid_gender}'")
        
        # Test skill level validation
        valid_skill = validate_skill_level("Advanced")
        print(f"  ✅ Skill level validation: 'Advanced' -> '{valid_skill}'")
        
        # Test division string parsing
        division_components = parse_division_string("Adult_Male_Advanced_Gi")
        print(f"  ✅ Division parsing: {division_components}")
        
        # Test athlete ID generation
        athlete_id = generate_athlete_id("John Doe", "US")
        print(f"  ✅ Athlete ID generation: {athlete_id}")
        
        # Test athlete data validation
        athlete_data = {
            "name": "Jane Smith",
            "age": 23,
            "gender": "F",
            "country": "CA",
            "skill_level": "Intermediate"
        }
        
        is_valid, cleaned_data, errors = validate_athlete_data(athlete_data)
        if is_valid:
            print(f"  ✅ Athlete data validation: {cleaned_data['name']} ({cleaned_data['id']})")
        else:
            print(f"  ❌ Athlete data validation failed: {errors}")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Validators test failed: {e}")
        return False

def test_model_integration():
    """Test model integration."""
    print("\n🔗 Testing Model Integration...")
    
    try:
        from src.core.models import Athlete, Event, Division, Match, Gender, SkillLevel, AgeClass, GiStatus
        from src.utils.validators import validate_athlete_data, generate_event_id
        
        # Create a complete tournament scenario
        event_date = datetime(2024, 6, 15, 9, 0, 0)
        event_id = generate_event_id("ADCC World Championship", event_date)
        
        event = Event(
            id=event_id,
            name="ADCC World Championship 2024",
            date=event_date,
            location="Las Vegas, NV"
        )
        
        division = Division(
            id="D123456",
            name="Adult Male Advanced Gi",
            age_class=AgeClass.ADULT,
            gender=Gender.MALE,
            skill_level=SkillLevel.ADVANCED,
            gi_status=GiStatus.GI,
            event_id=event.id
        )
        
        # Validate and create athletes
        athlete1_data = {
            "name": "John Doe",
            "age": 25,
            "gender": "M",
            "country": "US",
            "skill_level": "Advanced"
        }
        
        athlete2_data = {
            "name": "Jane Smith",
            "age": 23,
            "gender": "F",
            "country": "CA",
            "skill_level": "Intermediate"
        }
        
        is_valid1, cleaned1, errors1 = validate_athlete_data(athlete1_data)
        is_valid2, cleaned2, errors2 = validate_athlete_data(athlete2_data)
        
        if is_valid1 and is_valid2:
            athlete1 = Athlete(**cleaned1)
            athlete2 = Athlete(**cleaned2)
            
            match = Match(
                id="M123456",
                event_id=event.id,
                division_id=division.id,
                athlete1_id=athlete1.id,
                athlete2_id=athlete2.id,
                winner_id=athlete1.id,
                win_type="submission",
                bracket_round="final",
                match_date=datetime(2024, 6, 15, 14, 30, 0)
            )
            
            print(f"  ✅ Tournament scenario created:")
            print(f"     Event: {event.name}")
            print(f"     Division: {division.name}")
            print(f"     Athletes: {athlete1.name} vs {athlete2.name}")
            print(f"     Match: {match.id} (Winner: {athlete1.name})")
            
            return True
        else:
            print(f"  ❌ Athlete validation failed: {errors1 + errors2}")
            return False
            
    except Exception as e:
        print(f"  ❌ Model integration test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests."""
    print("🚀 ADCC Analysis Engine v0.6 - Phase 2 Verification")
    print("=" * 60)
    
    tests = [
        test_models,
        test_validators,
        test_model_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Phase 2 Verification Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} Phase 2 tests PASSED!")
        print("✅ Data Models & Validation system is ready for Phase 3")
        return True
    else:
        print(f"⚠️  {passed}/{total} Phase 2 tests passed")
        print("❌ Some Phase 2 components need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 