"""
ADCC Analysis Engine v0.6 - Report Generator
Generates Excel reports from analytics data.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd

from core.constants import DATASTORE_DIR
from utils.file_handler import save_json_file, load_json_file
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    Generates Excel reports from analytics data.
    
    Features:
    - Excel report generation
    - Multiple sheet support
    - Data formatting and styling
    - Chart generation
    - Report templates
    """
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the report generator.
        
        Args:
            datastore_dir: Directory for storing reports
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.reports_dir = self.datastore_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        logger.info(f"ReportGenerator initialized with datastore: {self.datastore_dir}")
    
    def generate_athlete_report(self, athlete_data: Dict[str, Any], 
                              rating_data: Optional[Dict[str, Any]] = None,
                              record_data: Optional[Dict[str, Any]] = None,
                              medal_data: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        """
        Generate a comprehensive athlete report.
        
        Args:
            athlete_data: Basic athlete information
            rating_data: Glicko rating data
            record_data: Win/loss record data
            medal_data: Medal count data
            
        Returns:
            Path to generated report file or None if failed
        """
        try:
            # Create filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"athlete_report_{athlete_data.get('id', 'unknown')}_{timestamp}.xlsx"
            filepath = self.reports_dir / filename
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Basic info sheet
                self._create_athlete_info_sheet(writer, athlete_data)
                
                # Rating sheet
                if rating_data:
                    self._create_rating_sheet(writer, rating_data)
                
                # Record sheet
                if record_data:
                    self._create_record_sheet(writer, record_data)
                
                # Medal sheet
                if medal_data:
                    self._create_medal_sheet(writer, medal_data)
            
            logger.info(f"Generated athlete report: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate athlete report: {e}")
            return None
    
    def generate_tournament_report(self, event_data: Dict[str, Any],
                                 results_data: List[Dict[str, Any]]) -> Optional[Path]:
        """
        Generate a tournament results report.
        
        Args:
            event_data: Event information
            results_data: Tournament results
            
        Returns:
            Path to generated report file or None if failed
        """
        try:
            # Create filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"tournament_report_{event_data.get('id', 'unknown')}_{timestamp}.xlsx"
            filepath = self.reports_dir / filename
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Event info sheet
                self._create_event_info_sheet(writer, event_data)
                
                # Results sheet
                if results_data:
                    self._create_results_sheet(writer, results_data)
            
            logger.info(f"Generated tournament report: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate tournament report: {e}")
            return None
    
    def _create_athlete_info_sheet(self, writer: pd.ExcelWriter, athlete_data: Dict[str, Any]) -> None:
        """Create athlete information sheet."""
        try:
            # Create basic info DataFrame
            info_data = {
                'Field': ['ID', 'Name', 'Age', 'Gender', 'Country', 'Club ID', 'Skill Level'],
                'Value': [
                    athlete_data.get('id', ''),
                    athlete_data.get('name', ''),
                    athlete_data.get('age', ''),
                    athlete_data.get('gender', ''),
                    athlete_data.get('country', ''),
                    athlete_data.get('club_id', ''),
                    athlete_data.get('skill_level', '')
                ]
            }
            
            df = pd.DataFrame(info_data)
            df.to_excel(writer, sheet_name='Athlete Info', index=False)
            
        except Exception as e:
            logger.error(f"Failed to create athlete info sheet: {e}")
    
    def _create_rating_sheet(self, writer: pd.ExcelWriter, rating_data: Dict[str, Any]) -> None:
        """Create rating information sheet."""
        try:
            # Create rating DataFrame
            rating_info = {
                'Field': ['Current Rating', 'Rating Deviation', 'Volatility', 'Matches Played'],
                'Value': [
                    rating_data.get('rating', 0),
                    rating_data.get('rating_deviation', 0),
                    rating_data.get('volatility', 0),
                    rating_data.get('matches_played', 0)
                ]
            }
            
            df = pd.DataFrame(rating_info)
            df.to_excel(writer, sheet_name='Rating Info', index=False)
            
        except Exception as e:
            logger.error(f"Failed to create rating sheet: {e}")
    
    def _create_record_sheet(self, writer: pd.ExcelWriter, record_data: Dict[str, Any]) -> None:
        """Create record information sheet."""
        try:
            # Create record DataFrame
            record_info = {
                'Field': ['Wins', 'Losses', 'Draws', 'Total Matches', 'Win Rate', 'Current Streak'],
                'Value': [
                    record_data.get('wins', 0),
                    record_data.get('losses', 0),
                    record_data.get('draws', 0),
                    record_data.get('total_matches', 0),
                    f"{record_data.get('win_rate', 0):.3f}",
                    record_data.get('current_streak', 0)
                ]
            }
            
            df = pd.DataFrame(record_info)
            df.to_excel(writer, sheet_name='Record Info', index=False)
            
        except Exception as e:
            logger.error(f"Failed to create record sheet: {e}")
    
    def _create_medal_sheet(self, writer: pd.ExcelWriter, medal_data: Dict[str, Any]) -> None:
        """Create medal information sheet."""
        try:
            # Create medal DataFrame
            medal_info = {
                'Medal Type': ['Gold', 'Silver', 'Bronze', 'Total'],
                'Count': [
                    medal_data.get('gold', 0),
                    medal_data.get('silver', 0),
                    medal_data.get('bronze', 0),
                    medal_data.get('total_medals', 0)
                ]
            }
            
            df = pd.DataFrame(medal_info)
            df.to_excel(writer, sheet_name='Medal Info', index=False)
            
        except Exception as e:
            logger.error(f"Failed to create medal sheet: {e}")
    
    def _create_event_info_sheet(self, writer: pd.ExcelWriter, event_data: Dict[str, Any]) -> None:
        """Create event information sheet."""
        try:
            # Create event info DataFrame
            event_info = {
                'Field': ['Event ID', 'Name', 'Date', 'Location'],
                'Value': [
                    event_data.get('id', ''),
                    event_data.get('name', ''),
                    event_data.get('date', ''),
                    event_data.get('location', '')
                ]
            }
            
            df = pd.DataFrame(event_info)
            df.to_excel(writer, sheet_name='Event Info', index=False)
            
        except Exception as e:
            logger.error(f"Failed to create event info sheet: {e}")
    
    def _create_results_sheet(self, writer: pd.ExcelWriter, results_data: List[Dict[str, Any]]) -> None:
        """Create results sheet."""
        try:
            # Convert results to DataFrame
            df = pd.DataFrame(results_data)
            df.to_excel(writer, sheet_name='Results', index=False)
            
        except Exception as e:
            logger.error(f"Failed to create results sheet: {e}")
    
    def list_reports(self) -> List[Path]:
        """
        List all generated reports.
        
        Returns:
            List of report file paths
        """
        try:
            reports = list(self.reports_dir.glob("*.xlsx"))
            logger.debug(f"Found {len(reports)} reports")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return []
    
    def cleanup_old_reports(self, keep_days: int = 30) -> int:
        """
        Clean up old report files.
        
        Args:
            keep_days: Number of days to keep reports
            
        Returns:
            Number of files removed
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - pd.Timedelta(days=keep_days)
            removed_count = 0
            
            for report_file in self.reports_dir.glob("*.xlsx"):
                if report_file.stat().st_mtime < cutoff_date.timestamp():
                    report_file.unlink()
                    removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old reports")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old reports: {e}")
            return 0 