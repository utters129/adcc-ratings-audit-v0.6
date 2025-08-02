"""
ADCC Analysis Engine v0.6 - Mock Data Generator
Creates synthetic test data for file processing pipeline testing.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

from src.core.constants import (
    VALID_GENDERS, VALID_SKILL_LEVELS, AGE_CLASSES,
    ATHLETE_ID_PREFIX, EVENT_ID_PREFIX, DIVISION_ID_PREFIX
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MockDataGenerator:
    """Generates synthetic test data for file processing pipeline testing."""
    
    def __init__(self):
        self.athletes = []
        self.events = []
        self.divisions = []
        self.matches = []
        
        # Sample data for realistic generation
        self.countries = ["USA", "Brazil", "Canada", "UK", "Australia", "Japan", "France", "Germany"]
        self.first_names = {
            "M": ["John", "Mike", "David", "Chris", "Alex", "Ryan", "Matt", "Nick"],
            "F": ["Sarah", "Emma", "Jessica", "Ashley", "Rachel", "Amanda", "Nicole", "Stephanie"]
        }
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        self.clubs = ["Gracie Academy", "Alliance", "Atos", "Checkmat", "Art of Jiu-Jitsu", "Marcelo Garcia"]
        
    def generate_athlete_data(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate mock athlete registration data."""
        athletes = []
        
        for i in range(count):
            gender = random.choice(VALID_GENDERS)
            first_name = random.choice(self.first_names[gender])
            last_name = random.choice(self.last_names)
            name = f"{first_name} {last_name}"
            
            age = random.randint(16, 45)
            skill_level = random.choice(VALID_SKILL_LEVELS)
            
            athlete = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Country": random.choice(self.countries),
                "Club": random.choice(self.clubs),
                "Skill Level": skill_level,
                "Weight": f"{random.randint(60, 100)}kg",
                "Belt": random.choice(["White", "Blue", "Purple", "Brown", "Black"]),
                "Email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "Phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            }
            athletes.append(athlete)
            
        return athletes
    
    def generate_match_data(self, athlete_count: int = 50) -> List[Dict[str, Any]]:
        """Generate mock match results data."""
        matches = []
        
        # Create some divisions
        divisions = [
            "Adult Male Black Belt -88kg Gi",
            "Adult Female Purple Belt -64kg No-Gi", 
            "Masters Male Brown Belt +100kg Gi",
            "Adult Male Blue Belt -76kg No-Gi",
            "Adult Female White Belt -55kg Gi"
        ]
        
        for i in range(athlete_count // 2):  # Roughly half the athletes will have matches
            division = random.choice(divisions)
            winner_id = f"{ATHLETE_ID_PREFIX}{random.randint(1000, 9999)}"
            loser_id = f"{ATHLETE_ID_PREFIX}{random.randint(1000, 9999)}"
            
            # Different match outcomes
            outcomes = ["Submission", "Points", "Advantage", "Decision"]
            outcome = random.choice(outcomes)
            
            match = {
                "Division": division,
                "Winner_ID": winner_id,
                "Loser_ID": loser_id,
                "Winner_Name": f"Athlete {winner_id}",
                "Loser_Name": f"Athlete {loser_id}",
                "Outcome": outcome,
                "Method": random.choice(["Armbar", "Triangle", "RNC", "Kimura", "Points", "Advantage"]),
                "Time": f"{random.randint(1, 10)}:{random.randint(0, 59):02d}",
                "Round": random.randint(1, 3),
                "Points_Winner": random.randint(0, 20) if outcome == "Points" else 0,
                "Points_Loser": random.randint(0, 20) if outcome == "Points" else 0
            }
            matches.append(match)
            
        return matches
    
    def generate_event_data(self) -> Dict[str, Any]:
        """Generate mock event data."""
        event_date = datetime.now() + timedelta(days=random.randint(30, 90))
        
        event = {
            "Event_Name": f"ADCC {random.choice(['Open', 'Championship', 'Trial'])} {event_date.year}",
            "Event_Date": event_date.strftime("%Y-%m-%d"),
            "Location": f"{random.choice(['Las Vegas', 'New York', 'Los Angeles', 'Chicago'])}, USA",
            "Organizer": "ADCC Federation",
            "Total_Participants": random.randint(100, 500),
            "Divisions": random.randint(10, 25),
            "Status": random.choice(["Registration Open", "Registration Closed", "In Progress", "Completed"])
        }
        
        return event
    
    def generate_json_api_data(self, athlete_count: int = 30) -> Dict[str, Any]:
        """Generate mock JSON API response data."""
        athletes = self.generate_athlete_data(athlete_count)
        event = self.generate_event_data()
        
        api_response = {
            "event": event,
            "athletes": athletes,
            "divisions": [
                {
                    "name": "Adult Male Black Belt -88kg Gi",
                    "participants": random.randint(8, 32),
                    "status": "Active"
                },
                {
                    "name": "Adult Female Purple Belt -64kg No-Gi", 
                    "participants": random.randint(4, 16),
                    "status": "Active"
                }
            ],
            "metadata": {
                "api_version": "v2.1",
                "timestamp": datetime.now().isoformat(),
                "total_records": len(athletes)
            }
        }
        
        return api_response
    
    def create_csv_registration_file(self, output_path: Path, athlete_count: int = 50) -> Path:
        """Create a mock CSV registration file."""
        athletes = self.generate_athlete_data(athlete_count)
        df = pd.DataFrame(athletes)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Created mock CSV registration file: {output_path}")
        return output_path
    
    def create_excel_match_file(self, output_path: Path, athlete_count: int = 50) -> Path:
        """Create a mock Excel match results file."""
        matches = self.generate_match_data(athlete_count)
        df = pd.DataFrame(matches)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Match_Results', index=False)
            
            # Add a summary sheet
            summary_data = {
                "Total_Matches": [len(matches)],
                "Divisions": [len(df['Division'].unique())],
                "Submission_Rate": [f"{len(df[df['Outcome'] == 'Submission']) / len(df) * 100:.1f}%"]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logger.info(f"Created mock Excel match file: {output_path}")
        return output_path
    
    def create_json_api_file(self, output_path: Path, athlete_count: int = 30) -> Path:
        """Create a mock JSON API response file."""
        api_data = self.generate_json_api_data(athlete_count)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created mock JSON API file: {output_path}")
        return output_path
    
    def create_test_dataset(self, output_dir: Path) -> Dict[str, Path]:
        """Create a complete test dataset with all file types."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Create registration CSV
        csv_path = output_dir / "registration_data.csv"
        files['registration_csv'] = self.create_csv_registration_file(csv_path, 50)
        
        # Create match results Excel
        excel_path = output_dir / "match_results.xlsx"
        files['match_excel'] = self.create_excel_match_file(excel_path, 50)
        
        # Create API response JSON
        json_path = output_dir / "api_response.json"
        files['api_json'] = self.create_json_api_file(json_path, 30)
        
        logger.info(f"Created complete test dataset in: {output_dir}")
        return files
    
    def create_problematic_dataset(self, output_dir: Path) -> Dict[str, Path]:
        """Create test files with data quality issues for edge case testing."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Create CSV with missing data
        problematic_athletes = [
            {"Name": "John Smith", "Age": 25, "Gender": "M", "Country": "USA", "Club": "Gracie", "Skill Level": "Advanced"},
            {"Name": "", "Age": None, "Gender": "F", "Country": "", "Club": "Alliance", "Skill Level": "Beginner"},
            {"Name": "Jane Doe", "Age": 30, "Gender": "X", "Country": "Canada", "Club": None, "Skill Level": "Invalid"},
            {"Name": "Bob Johnson", "Age": 999, "Gender": "M", "Country": "USA", "Club": "Atos", "Skill Level": "Advanced"},
            {"Name": "Alice Brown", "Age": 18, "Gender": "F", "Country": "UK", "Club": "Checkmat", "Skill Level": "Intermediate"}
        ]
        
        df = pd.DataFrame(problematic_athletes)
        problematic_csv_path = output_dir / "problematic_registration.csv"
        df.to_csv(problematic_csv_path, index=False)
        files['problematic_csv'] = problematic_csv_path
        
        # Create empty file
        empty_path = output_dir / "empty_file.csv"
        empty_path.write_text("")
        files['empty_file'] = empty_path
        
        # Create malformed JSON
        malformed_json_path = output_dir / "malformed.json"
        malformed_json_path.write_text('{"invalid": json, "missing": quotes}')
        files['malformed_json'] = malformed_json_path
        
        logger.info(f"Created problematic test dataset in: {output_dir}")
        return files 