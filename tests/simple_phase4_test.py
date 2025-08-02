#!/usr/bin/env python3
"""
Simple Phase 4 Test - Tests basic functionality without complex imports
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_basic_imports():
    """Test that we can import basic modules."""
    print("🔍 Testing basic imports...")
    
    try:
        # Test core imports
        from core.models import Athlete, Division, Club
        from core.constants import DATASTORE_DIR
        print("✅ Core models imported successfully")
        
        # Test utils imports
        from utils.file_handler import save_json_file, load_json_file
        print("✅ File handler imported successfully")
        
        # Test logger
        from utils.logger import get_logger
        logger = get_logger(__name__)
        print("✅ Logger imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_file_operations():
    """Test basic file operations."""
    print("\n🔍 Testing file operations...")
    
    try:
        from utils.file_handler import save_json_file, load_json_file
        
        # Test data
        test_data = {
            'test': 'data',
            'number': 42,
            'list': [1, 2, 3]
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            test_path = Path(tmp_file.name)
        
        # Save and load
        success = save_json_file(test_data, test_path)
        if not success:
            raise Exception("Failed to save JSON file")
        
        loaded_data = load_json_file(test_path)
        if loaded_data != test_data:
            raise Exception("Data integrity check failed")
        
        # Cleanup
        test_path.unlink()
        
        print("✅ File operations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def test_models():
    """Test model creation."""
    print("\n🔍 Testing models...")
    
    try:
        from core.models import Athlete, Division, Club, Gender, SkillLevel, AgeClass, GiStatus
        
        # Create test athlete
        athlete = Athlete(
            id="TEST001",
            name="Test Athlete",
            age=25,
            gender=Gender.MALE,
            country="USA",
            skill_level=SkillLevel.EXPERT
        )
        
        # Create test division
        division = Division(
            id="TEST001",
            name="Test Division",
            age_class=AgeClass.ADULT,
            gender=Gender.MALE,
            skill_level=SkillLevel.EXPERT,
            gi_status=GiStatus.GI,
            event_id="EVENT001"
        )
        
        # Create test club
        club = Club(
            id="TEST001",
            name="Test Club",
            country="USA",
            city="Test City"
        )
        
        print("✅ Models created successfully")
        print(f"   Athlete: {athlete.name}")
        print(f"   Division: {division.name}")
        print(f"   Club: {club.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def main():
    """Run simple Phase 4 tests."""
    print("🚀 Simple Phase 4 Test")
    print("=" * 40)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("File Operations", test_file_operations),
        ("Models", test_models)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: FAILED - Unexpected error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SIMPLE PHASE 4 TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Basic Phase 4 functionality is working!")
        return True
    else:
        print("⚠️  Some basic tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 