"""
File Monitor for ADCC Analysis Engine v0.6
Handles file monitoring and management for downloaded data files.
"""

import structlog
from pathlib import Path
from typing import Dict, List, Optional, Any
import time
import shutil
from datetime import datetime
import fnmatch

logger = structlog.get_logger(__name__)


class FileMonitor:
    """
    File monitoring and management system.
    
    Monitors directories for new files, validates file formats,
    and manages file movement and organization.
    """
    
    def __init__(self, watch_directory: Path, file_patterns: List[str]):
        """
        Initialize file monitor.
        
        Args:
            watch_directory: Directory to monitor for new files
            file_patterns: List of file patterns to watch (e.g., ["*.csv", "*.xlsx"])
        """
        self.watch_directory = Path(watch_directory)
        self.file_patterns = file_patterns
        self.detected_files = []
        self.is_monitoring = False
        self.known_files = set()
        
        # Ensure watch directory exists
        self.watch_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize known files
        self._update_known_files()
        
        logger.info("FileMonitor initialized", 
                   watch_directory=str(watch_directory), 
                   file_patterns=file_patterns)
    
    def start_monitoring(self) -> bool:
        """
        Start file monitoring.
        
        Returns:
            bool: True if monitoring started successfully
        """
        try:
            self.is_monitoring = True
            self._update_known_files()
            logger.info("File monitoring started", watch_directory=str(self.watch_directory))
            return True
        except Exception as e:
            logger.error("Failed to start file monitoring", error=str(e))
            return False
    
    def stop_monitoring(self):
        """Stop file monitoring."""
        self.is_monitoring = False
        logger.info("File monitoring stopped")
    
    def _update_known_files(self):
        """Update the set of known files in the watch directory."""
        if not self.watch_directory.exists():
            self.known_files = set()
            return
        
        current_files = set()
        for pattern in self.file_patterns:
            files = list(self.watch_directory.glob(pattern))
            current_files.update(f.name for f in files)
        
        self.known_files = current_files
    
    def detect_new_files(self) -> List[Path]:
        """
        Detect new files in the watch directory.
        
        Returns:
            List of new file paths
        """
        if not self.is_monitoring:
            logger.warning("File monitoring not active")
            return []
        
        try:
            new_files = []
            current_files = set()
            
            # Check for files matching patterns
            for pattern in self.file_patterns:
                files = list(self.watch_directory.glob(pattern))
                for file_path in files:
                    if file_path.is_file():
                        current_files.add(file_path.name)
                        if file_path.name not in self.known_files:
                            new_files.append(file_path)
            
            # Update known files
            self.known_files = current_files
            
            if new_files:
                logger.info("New files detected", 
                           count=len(new_files), 
                           files=[f.name for f in new_files])
            
            return new_files
            
        except Exception as e:
            logger.error("Error detecting new files", error=str(e))
            return []
    
    def validate_file_format(self, filename: str) -> bool:
        """
        Validate if a file matches expected formats.
        
        Args:
            filename: Filename to validate
            
        Returns:
            bool: True if file format is valid
        """
        return any(fnmatch.fnmatch(filename, pattern) for pattern in self.file_patterns)
    
    def get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Get metadata for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file metadata
        """
        try:
            stat = file_path.stat()
            
            metadata = {
                "name": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(file_path),
                "valid_format": self.validate_file_format(file_path.name)
            }
            
            return metadata
            
        except Exception as e:
            logger.error("Error getting file metadata", 
                        file_path=str(file_path), error=str(e))
            return {
                "name": file_path.name,
                "error": str(e)
            }
    
    def move_file_to_processed(self, file_path: Path, processed_dir: Path) -> bool:
        """
        Move a file to the processed directory.
        
        Args:
            file_path: Path to the file to move
            processed_dir: Directory to move the file to
            
        Returns:
            bool: True if move successful
        """
        try:
            # Ensure processed directory exists
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate destination path
            dest_path = processed_dir / file_path.name
            
            # Check if destination file already exists
            if dest_path.exists():
                # Generate unique filename
                counter = 1
                while dest_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    dest_path = processed_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            # Move the file
            shutil.move(str(file_path), str(dest_path))
            
            logger.info("File moved to processed directory", 
                       source=str(file_path), 
                       destination=str(dest_path))
            
            return True
            
        except Exception as e:
            logger.error("Error moving file to processed directory", 
                        file_path=str(file_path), 
                        processed_dir=str(processed_dir), 
                        error=str(e))
            return False
    
    def copy_file_to_processed(self, file_path: Path, processed_dir: Path) -> bool:
        """
        Copy a file to the processed directory.
        
        Args:
            file_path: Path to the file to copy
            processed_dir: Directory to copy the file to
            
        Returns:
            bool: True if copy successful
        """
        try:
            # Ensure processed directory exists
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate destination path
            dest_path = processed_dir / file_path.name
            
            # Check if destination file already exists
            if dest_path.exists():
                # Generate unique filename
                counter = 1
                while dest_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    dest_path = processed_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            # Copy the file
            shutil.copy2(str(file_path), str(dest_path))
            
            logger.info("File copied to processed directory", 
                       source=str(file_path), 
                       destination=str(dest_path))
            
            return True
            
        except Exception as e:
            logger.error("Error copying file to processed directory", 
                        file_path=str(file_path), 
                        processed_dir=str(processed_dir), 
                        error=str(e))
            return False
    
    def rename_file(self, file_path: Path, new_name: str) -> bool:
        """
        Rename a file.
        
        Args:
            file_path: Path to the file to rename
            new_name: New filename
            
        Returns:
            bool: True if rename successful
        """
        try:
            new_path = file_path.parent / new_name
            
            # Check if destination file already exists
            if new_path.exists():
                logger.warning("Destination file already exists", 
                              destination=str(new_path))
                return False
            
            # Rename the file
            file_path.rename(new_path)
            
            logger.info("File renamed", 
                       old_name=file_path.name, 
                       new_name=new_name)
            
            return True
            
        except Exception as e:
            logger.error("Error renaming file", 
                        file_path=str(file_path), 
                        new_name=new_name, 
                        error=str(e))
            return False
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            file_path.unlink()
            
            logger.info("File deleted", file_path=str(file_path))
            
            # Update known files if monitoring
            if self.is_monitoring:
                self._update_known_files()
            
            return True
            
        except Exception as e:
            logger.error("Error deleting file", 
                        file_path=str(file_path), 
                        error=str(e))
            return False
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the watch directory.
        
        Returns:
            Dict containing directory statistics
        """
        try:
            if not self.watch_directory.exists():
                return {
                    "directory": str(self.watch_directory),
                    "exists": False,
                    "total_files": 0,
                    "matching_files": 0
                }
            
            total_files = len(list(self.watch_directory.glob("*")))
            matching_files = len(list(self.watch_directory.glob("*.csv"))) + \
                           len(list(self.watch_directory.glob("*.xlsx")))
            
            stats = {
                "directory": str(self.watch_directory),
                "exists": True,
                "total_files": total_files,
                "matching_files": matching_files,
                "patterns": self.file_patterns,
                "monitoring": self.is_monitoring
            }
            
            return stats
            
        except Exception as e:
            logger.error("Error getting directory stats", error=str(e))
            return {
                "directory": str(self.watch_directory),
                "error": str(e)
            }
    
    def wait_for_file(self, filename: str, timeout: int = 30) -> Optional[Path]:
        """
        Wait for a specific file to appear.
        
        Args:
            filename: Expected filename
            timeout: Timeout in seconds
            
        Returns:
            Path to the file if found, None if timeout
        """
        logger.info("Waiting for file", filename=filename, timeout=timeout)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            file_path = self.watch_directory / filename
            
            if file_path.exists():
                logger.info("File found", filename=filename)
                return file_path
            
            time.sleep(1)
        
        logger.warning("File not found within timeout", filename=filename, timeout=timeout)
        return None
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old files from the watch directory.
        
        Args:
            max_age_hours: Maximum age of files in hours
            
        Returns:
            Number of files cleaned up
        """
        try:
            if not self.watch_directory.exists():
                return 0
            
            cutoff_time = time.time() - (max_age_hours * 3600)
            cleaned_count = 0
            
            for file_path in self.watch_directory.iterdir():
                if file_path.is_file():
                    file_age = file_path.stat().st_mtime
                    if file_age < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug("Cleaned up old file", filename=file_path.name)
                        except Exception as e:
                            logger.error("Error cleaning up old file", 
                                        filename=file_path.name, error=str(e))
            
            if cleaned_count > 0:
                logger.info("Cleanup completed", 
                           files_cleaned=cleaned_count, 
                           max_age_hours=max_age_hours)
            
            return cleaned_count
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
            return 0 