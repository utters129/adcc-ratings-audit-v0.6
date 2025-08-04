"""
ADCC Analysis Engine v0.6 - File Handler Utilities
Common file operations for the ADCC analysis system.
"""

import json
import gzip
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import pandas as pd
import logging

from src.core.constants import (
    PROCESSED_DATA_DIR, DATASTORE_DIR, LOGS_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Constants for file operations
ALLOWED_FILE_TYPES = ['json', 'csv', 'xlsx', 'parquet', 'txt']
BACKUP_FILES = True


def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Path to the directory
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {directory}")
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        raise


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception as e:
        logger.error(f"Failed to get file size for {file_path}: {e}")
        return 0.0


def validate_file_type(file_path: Path) -> bool:
    """
    Validate if file type is supported.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file type is supported
    """
    file_extension = file_path.suffix.lower().lstrip('.')
    return file_extension in ALLOWED_FILE_TYPES


def backup_file(file_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Create a backup of a file.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory for backup (defaults to same directory)
        
    Returns:
        Path to the backup file
    """
    if not BACKUP_FILES:
        return file_path
        
    try:
        backup_dir = backup_dir or file_path.parent
        ensure_directory_exists(backup_dir)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Failed to create backup for {file_path}: {e}")
        return file_path


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
    """
    try:
        if not file_path.exists():
            logger.warning(f"JSON file not found: {file_path}")
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        logger.debug(f"Loaded JSON file: {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        return {}


def save_json_file(data: Dict[str, Any], file_path: Path, indent: int = 2) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path to save the file
        indent: JSON indentation
        
    Returns:
        True if successful
    """
    try:
        ensure_directory_exists(file_path.parent)
        
        # Create backup if file exists
        if file_path.exists():
            backup_file(file_path)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            
        logger.info(f"Saved JSON file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")
        return False


def load_parquet_file(file_path: Path) -> Optional[pd.DataFrame]:
    """
    Load data from a Parquet file.
    
    Args:
        file_path: Path to the Parquet file
        
    Returns:
        DataFrame containing the data, or None if failed
    """
    try:
        if not file_path.exists():
            logger.warning(f"Parquet file not found: {file_path}")
            return None
            
        df = pd.read_parquet(file_path)
        logger.debug(f"Loaded Parquet file: {file_path}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load Parquet file {file_path}: {e}")
        return None


def save_parquet_file(df: pd.DataFrame, file_path: Path, compression: str = 'snappy') -> bool:
    """
    Save DataFrame to a Parquet file.
    
    Args:
        df: DataFrame to save
        file_path: Path to save the file
        compression: Compression method
        
    Returns:
        True if successful
    """
    try:
        ensure_directory_exists(file_path.parent)
        
        # Create backup if file exists
        if file_path.exists():
            backup_file(file_path)
            
        df.to_parquet(file_path, compression=compression, index=False)
        logger.info(f"Saved Parquet file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save Parquet file {file_path}: {e}")
        return False


def list_files_in_directory(directory: Path, pattern: str = "*") -> List[Path]:
    """
    List files in a directory matching a pattern.
    
    Args:
        directory: Directory to search
        pattern: File pattern to match
        
    Returns:
        List of matching file paths
    """
    try:
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []
            
        files = list(directory.glob(pattern))
        logger.debug(f"Found {len(files)} files in {directory}")
        return files
        
    except Exception as e:
        logger.error(f"Failed to list files in {directory}: {e}")
        return []


def cleanup_old_files(directory: Path, days_old: int = 30) -> int:
    """
    Clean up old files in a directory.
    
    Args:
        directory: Directory to clean
        days_old: Remove files older than this many days
        
    Returns:
        Number of files removed
    """
    try:
        if not directory.exists():
            return 0
            
        cutoff_time = pd.Timestamp.now() - pd.Timedelta(days=days_old)
        removed_count = 0
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_time = pd.Timestamp.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    removed_count += 1
                    logger.debug(f"Removed old file: {file_path}")
                    
        logger.info(f"Cleaned up {removed_count} old files from {directory}")
        return removed_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup old files in {directory}: {e}")
        return 0 