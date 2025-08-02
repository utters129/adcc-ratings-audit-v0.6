"""
ADCC Analysis Engine v0.6 - Foundation Verification Script
Simple script to verify that all foundation components are working correctly.
"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Test configuration system."""
    print("🔧 Testing Configuration System...")
    
    try:
        from src.config.settings import get_settings
        from src.core.constants import PROJECT_ROOT, DATA_DIR, LOGS_DIR
        
        settings = get_settings()
        print(f"  ✅ Settings loaded successfully")
        print(f"  ✅ Environment: {settings.environment}")
        print(f"  ✅ Admin username: {settings.admin_username}")
        print(f"  ✅ Project root: {PROJECT_ROOT}")
        print(f"  ✅ Data directory: {DATA_DIR}")
        print(f"  ✅ Logs directory: {LOGS_DIR}")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_logging():
    """Test logging infrastructure."""
    print("\n📝 Testing Logging Infrastructure...")
    
    try:
        from src.utils.logger import setup_logging, get_logger
        from src.core.constants import LOGS_DIR
        
        # Setup logging
        setup_logging()
        print(f"  ✅ Logging setup successful")
        
        # Test logger
        logger = get_logger("verification_test")
        logger.info("Test log message")
        print(f"  ✅ Logger created and working")
        
        # Check log directory
        if LOGS_DIR.exists():
            print(f"  ✅ Log directory exists: {LOGS_DIR}")
        else:
            print(f"  ⚠️  Log directory does not exist: {LOGS_DIR}")
        
        return True
    except Exception as e:
        print(f"  ❌ Logging test failed: {e}")
        return False

def test_file_operations():
    """Test file operations."""
    print("\n📁 Testing File Operations...")
    
    try:
        from src.utils.file_handler import (
            ensure_directory_exists, save_json_file, load_json_file,
            save_parquet_file, load_parquet_file, list_files_in_directory
        )
        import pandas as pd
        import tempfile
        
        # Test directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_subdir"
            ensure_directory_exists(test_dir)
            print(f"  ✅ Directory creation: {test_dir}")
            
            # Test JSON operations
            test_data = {"test": "data", "number": 42}
            json_file = test_dir / "test.json"
            success = save_json_file(test_data, json_file)
            if success:
                print(f"  ✅ JSON save successful")
                
                loaded_data = load_json_file(json_file)
                if loaded_data == test_data:
                    print(f"  ✅ JSON load successful")
                else:
                    print(f"  ❌ JSON load failed - data mismatch")
                    return False
            else:
                print(f"  ❌ JSON save failed")
                return False
            
            # Test Parquet operations
            test_df = pd.DataFrame({
                'name': ['Alice', 'Bob'],
                'age': [25, 30]
            })
            parquet_file = test_dir / "test.parquet"
            success = save_parquet_file(test_df, parquet_file)
            if success:
                print(f"  ✅ Parquet save successful")
                
                loaded_df = load_parquet_file(parquet_file)
                if loaded_df is not None and len(loaded_df) == len(test_df):
                    print(f"  ✅ Parquet load successful")
                else:
                    print(f"  ❌ Parquet load failed")
                    return False
            else:
                print(f"  ❌ Parquet save failed")
                return False
            
            # Test file listing
            files = list_files_in_directory(test_dir)
            if len(files) == 2:  # JSON and Parquet files
                print(f"  ✅ File listing successful: {len(files)} files found")
            else:
                print(f"  ❌ File listing failed: expected 2 files, got {len(files)}")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ File operations test failed: {e}")
        return False

def test_data_directories():
    """Test data directory structure."""
    print("\n📂 Testing Data Directory Structure...")
    
    try:
        from src.core.constants import (
            DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, DATASTORE_DIR
        )
        from src.utils.file_handler import ensure_directory_exists
        
        # Ensure all directories exist
        directories = [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, DATASTORE_DIR]
        
        for directory in directories:
            ensure_directory_exists(directory)
            if directory.exists():
                print(f"  ✅ Directory exists: {directory}")
            else:
                print(f"  ❌ Directory missing: {directory}")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Data directories test failed: {e}")
        return False

def main():
    """Run all foundation tests."""
    print("🚀 ADCC Analysis Engine v0.6 - Foundation Verification")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_logging,
        test_file_operations,
        test_data_directories
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
    print("📊 Foundation Verification Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} foundation tests PASSED!")
        print("✅ Foundation is ready for Phase 2 development")
        return True
    else:
        print(f"⚠️  {passed}/{total} foundation tests passed")
        print("❌ Some foundation components need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 