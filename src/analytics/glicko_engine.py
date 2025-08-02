"""
ADCC Analysis Engine v0.6 - Glicko-2 Rating Engine
Implements the Glicko-2 rating system for ADCC athletes.
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import pandas as pd

from core.constants import DATASTORE_DIR
from core.models import Athlete, Match
from utils.file_handler import save_json_file, load_json_file, save_parquet_file, load_parquet_file
from utils.logger import get_logger

logger = get_logger(__name__)


class GlickoEngine:
    """
    Glicko-2 rating system implementation for ADCC athletes.
    
    Features:
    - Glicko-2 rating calculations
    - Rating period management
    - Rating deviation and volatility tracking
    - Match outcome processing
    - Rating history tracking
    """
    
    # Glicko-2 constants
    TAU = 0.5  # System constant for volatility
    EPSILON = 0.000001  # Convergence tolerance
    
    def __init__(self, datastore_dir: Optional[Path] = None):
        """
        Initialize the Glicko-2 rating engine.
        
        Args:
            datastore_dir: Directory for storing rating data
        """
        self.datastore_dir = datastore_dir or DATASTORE_DIR
        self.ratings_file = self.datastore_dir / "athlete_ratings.json"
        self.rating_history_file = self.datastore_dir / "rating_history.parquet"
        self.periods_file = self.datastore_dir / "rating_periods.json"
        
        # Load existing rating data
        self.athlete_ratings = self._load_athlete_ratings()
        self.rating_history = self._load_rating_history()
        self.rating_periods = self._load_rating_periods()
        
        logger.info(f"GlickoEngine initialized with datastore: {self.datastore_dir}")
    
    def _load_athlete_ratings(self) -> Dict[str, Dict[str, Any]]:
        """Load athlete ratings from JSON file."""
        try:
            if self.ratings_file.exists():
                ratings = load_json_file(self.ratings_file)
                logger.debug(f"Loaded ratings for {len(ratings.get('athletes', {}))} athletes")
                return ratings
            else:
                # Create new ratings registry
                ratings = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'total_athletes': 0
                    },
                    'athletes': {}
                }
                self._save_athlete_ratings(ratings)
                logger.info("Created new athlete ratings registry")
                return ratings
        except Exception as e:
            logger.error(f"Failed to load athlete ratings: {e}")
            return {'metadata': {}, 'athletes': {}}
    
    def _save_athlete_ratings(self, ratings: Dict[str, Any]) -> bool:
        """Save athlete ratings to JSON file."""
        try:
            return save_json_file(ratings, self.ratings_file)
        except Exception as e:
            logger.error(f"Failed to save athlete ratings: {e}")
            return False
    
    def _load_rating_history(self) -> pd.DataFrame:
        """Load rating history from Parquet file."""
        try:
            if self.rating_history_file.exists():
                history = load_parquet_file(self.rating_history_file)
                logger.debug(f"Loaded rating history with {len(history)} records")
                return history
            else:
                # Create new rating history
                history = pd.DataFrame(columns=[
                    'athlete_id', 'rating', 'rating_deviation', 'volatility',
                    'period_id', 'match_id', 'timestamp', 'change'
                ])
                self._save_rating_history(history)
                logger.info("Created new rating history")
                return history
        except Exception as e:
            logger.error(f"Failed to load rating history: {e}")
            return pd.DataFrame()
    
    def _save_rating_history(self, history: pd.DataFrame) -> bool:
        """Save rating history to Parquet file."""
        try:
            return save_parquet_file(history, self.rating_history_file)
        except Exception as e:
            logger.error(f"Failed to save rating history: {e}")
            return False
    
    def _load_rating_periods(self) -> Dict[str, Any]:
        """Load rating periods from JSON file."""
        try:
            if self.periods_file.exists():
                periods = load_json_file(self.periods_file)
                logger.debug(f"Loaded {len(periods.get('periods', []))} rating periods")
                return periods
            else:
                # Create new periods registry
                periods = {
                    'metadata': {
                        'created': datetime.now(timezone.utc).isoformat(),
                        'version': '1.0',
                        'current_period': None
                    },
                    'periods': []
                }
                self._save_rating_periods(periods)
                logger.info("Created new rating periods registry")
                return periods
        except Exception as e:
            logger.error(f"Failed to load rating periods: {e}")
            return {'metadata': {}, 'periods': []}
    
    def _save_rating_periods(self, periods: Dict[str, Any]) -> bool:
        """Save rating periods to JSON file."""
        try:
            return save_json_file(periods, self.periods_file)
        except Exception as e:
            logger.error(f"Failed to save rating periods: {e}")
            return False
    
    def initialize_athlete(self, athlete_id: str, initial_rating: float = 1500.0,
                          initial_deviation: float = 350.0, initial_volatility: float = 0.06) -> bool:
        """
        Initialize an athlete's rating.
        
        Args:
            athlete_id: Unique athlete ID
            initial_rating: Starting rating (default: 1500)
            initial_deviation: Starting rating deviation (default: 350)
            initial_volatility: Starting volatility (default: 0.06)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if athlete_id in self.athlete_ratings['athletes']:
                logger.warning(f"Athlete {athlete_id} already has ratings")
                return True
            
            # Create athlete rating entry
            self.athlete_ratings['athletes'][athlete_id] = {
                'rating': initial_rating,
                'rating_deviation': initial_deviation,
                'volatility': initial_volatility,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'matches_played': 0,
                'period_id': None
            }
            
            # Update metadata
            self.athlete_ratings['metadata']['total_athletes'] = len(self.athlete_ratings['athletes'])
            self.athlete_ratings['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save ratings
            success = self._save_athlete_ratings(self.athlete_ratings)
            
            if success:
                logger.info(f"Initialized ratings for athlete {athlete_id}: {initial_rating}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize athlete {athlete_id}: {e}")
            return False
    
    def get_athlete_rating(self, athlete_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an athlete's current rating.
        
        Args:
            athlete_id: Unique athlete ID
            
        Returns:
            Rating data or None if not found
        """
        try:
            return self.athlete_ratings['athletes'].get(athlete_id)
        except Exception as e:
            logger.error(f"Failed to get rating for athlete {athlete_id}: {e}")
            return None
    
    def calculate_expected_score(self, rating1: float, deviation1: float,
                               rating2: float, deviation2: float) -> float:
        """
        Calculate expected score between two athletes.
        
        Args:
            rating1: First athlete's rating
            deviation1: First athlete's rating deviation
            rating2: Second athlete's rating
            deviation2: Second athlete's rating deviation
            
        Returns:
            Expected score for first athlete (0-1)
        """
        try:
            # Convert to Glicko-2 scale
            mu1 = (rating1 - 1500) / 173.7178
            phi1 = deviation1 / 173.7178
            mu2 = (rating2 - 1500) / 173.7178
            phi2 = deviation2 / 173.7178
            
            # Calculate expected score
            g_phi = 1 / math.sqrt(1 + 3 * phi2**2 / math.pi**2)
            E = 1 / (1 + math.exp(-g_phi * (mu1 - mu2)))
            
            return E
            
        except Exception as e:
            logger.error(f"Failed to calculate expected score: {e}")
            return 0.5
    
    def update_rating(self, athlete_id: str, opponent_rating: float, opponent_deviation: float,
                     actual_score: float, match_id: Optional[str] = None) -> bool:
        """
        Update an athlete's rating after a match.
        
        Args:
            athlete_id: Athlete ID to update
            opponent_rating: Opponent's rating
            opponent_deviation: Opponent's rating deviation
            actual_score: Actual match result (1 for win, 0.5 for draw, 0 for loss)
            match_id: Optional match ID for tracking
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if athlete_id not in self.athlete_ratings['athletes']:
                logger.error(f"Athlete {athlete_id} not found in ratings")
                return False
            
            # Get current rating
            current = self.athlete_ratings['athletes'][athlete_id]
            mu = (current['rating'] - 1500) / 173.7178
            phi = current['rating_deviation'] / 173.7178
            sigma = current['volatility']
            
            # Convert opponent to Glicko-2 scale
            mu_j = (opponent_rating - 1500) / 173.7178
            phi_j = opponent_deviation / 173.7178
            
            # Calculate g and E
            g_phi_j = 1 / math.sqrt(1 + 3 * phi_j**2 / math.pi**2)
            E = 1 / (1 + math.exp(-g_phi_j * (mu - mu_j)))
            
            # Calculate v and delta
            v = 1 / (g_phi_j**2 * E * (1 - E))
            delta = v * g_phi_j * (actual_score - E)
            
            # Update volatility using iterative algorithm
            a = math.log(sigma**2)
            A = a
            B = 0
            
            if delta**2 > phi**2 + v:
                B = math.log(delta**2 - phi**2 - v)
            else:
                k = 1
                max_k = 100  # Prevent infinite loop
                while k <= max_k and self._f(a + k * self.TAU, delta, phi, v, a) < 0:
                    k += 1
                if k > max_k:
                    # Fallback: use current volatility
                    new_sigma = sigma
                else:
                    B = a + k * self.TAU
            
            # Only proceed with iterative calculation if B was set
            if B != 0:
                f_A = self._f(A, delta, phi, v, a)
                f_B = self._f(B, delta, phi, v, a)
                
                # Check for valid function values
                if math.isnan(f_A) or math.isnan(f_B) or math.isinf(f_A) or math.isinf(f_B):
                    new_sigma = sigma  # Fallback to current volatility
                else:
                    iteration_count = 0
                    max_iterations = 100  # Prevent infinite loop
                    
                    while abs(B - A) > self.EPSILON and iteration_count < max_iterations:
                        # Check for division by zero
                        if abs(f_B - f_A) < 1e-10:
                            break
                            
                        C = A + (A - B) * f_A / (f_B - f_A)
                        f_C = self._f(C, delta, phi, v, a)
                        
                        # Check for valid function value
                        if math.isnan(f_C) or math.isinf(f_C):
                            break
                        
                        if f_C * f_B < 0:
                            A = B
                            f_A = f_B
                        else:
                            f_A = f_A / 2
                        
                        B = C
                        f_B = f_C
                        iteration_count += 1
                    
                    if iteration_count >= max_iterations:
                        # Fallback: use current volatility
                        new_sigma = sigma
                    else:
                        new_sigma = math.exp(A / 2)
            else:
                new_sigma = sigma  # Fallback to current volatility
            
            # Update rating and deviation
            phi_star = math.sqrt(phi**2 + new_sigma**2)
            new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
            new_mu = mu + new_phi**2 * g_phi_j * (actual_score - E)
            
            # Convert back to Glicko scale
            new_rating = 173.7178 * new_mu + 1500
            new_deviation = 173.7178 * new_phi
            
            # Update athlete rating
            old_rating = current['rating']
            current['rating'] = new_rating
            current['rating_deviation'] = new_deviation
            current['volatility'] = new_sigma
            current['matches_played'] += 1
            current['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save updated ratings
            success = self._save_athlete_ratings(self.athlete_ratings)
            
            if success:
                # Add to rating history
                history_entry = {
                    'athlete_id': athlete_id,
                    'rating': new_rating,
                    'rating_deviation': new_deviation,
                    'volatility': new_sigma,
                    'period_id': current.get('period_id'),
                    'match_id': match_id,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'change': new_rating - old_rating
                }
                
                new_row = pd.DataFrame([history_entry])
                self.rating_history = pd.concat([self.rating_history, new_row], ignore_index=True)
                self._save_rating_history(self.rating_history)
                
                logger.info(f"Updated rating for {athlete_id}: {old_rating:.1f} → {new_rating:.1f} (Δ{new_rating - old_rating:+.1f})")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update rating for athlete {athlete_id}: {e}")
            return False
    
    def _f(self, x: float, delta: float, phi: float, v: float, a: float) -> float:
        """Helper function for volatility calculation."""
        try:
            # Add comprehensive bounds checking to prevent overflow
            if x > 700:  # Prevent exp(x) overflow
                x = 700
            elif x < -700:  # Prevent exp(-x) overflow
                x = -700
                
            # Check for division by zero
            if abs(phi**2 + v) < 1e-10:
                return 0
                
            ex = math.exp(x)
            
            # Check for potential overflow in calculations
            if ex > 1e300:
                return 0
                
            denominator = 2 * (phi**2 + v + ex)**2
            if abs(denominator) < 1e-10:
                return 0
                
            result = (ex * (delta**2 - phi**2 - v - ex)) / denominator - (x - a) / self.TAU**2
            
            # Check for NaN or infinite results
            if math.isnan(result) or math.isinf(result):
                return 0
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate f(x): {e}")
            return 0
    
    def process_match(self, match: Match, winner_id: str) -> bool:
        """
        Process a match and update both athletes' ratings.
        
        Args:
            match: Match data
            winner_id: ID of the winning athlete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get athlete ratings
            athlete1_rating = self.get_athlete_rating(match.athlete1_id)
            athlete2_rating = self.get_athlete_rating(match.athlete2_id)
            
            if not athlete1_rating or not athlete2_rating:
                logger.error(f"Missing ratings for athletes in match {match.id}")
                return False
            
            # Determine scores
            if winner_id == match.athlete1_id:
                score1, score2 = 1.0, 0.0
            elif winner_id == match.athlete2_id:
                score1, score2 = 0.0, 1.0
            else:
                # Draw (shouldn't happen in ADCC but handle it)
                score1, score2 = 0.5, 0.5
            
            # Update both athletes
            success1 = self.update_rating(
                match.athlete1_id,
                athlete2_rating['rating'],
                athlete2_rating['rating_deviation'],
                score1,
                match.id
            )
            
            success2 = self.update_rating(
                match.athlete2_id,
                athlete1_rating['rating'],
                athlete1_rating['rating_deviation'],
                score2,
                match.id
            )
            
            return success1 and success2
            
        except Exception as e:
            logger.error(f"Failed to process match {match.id}: {e}")
            return False
    
    def start_rating_period(self, period_id: str, description: str = "") -> bool:
        """
        Start a new rating period.
        
        Args:
            period_id: Unique period identifier
            description: Period description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if period already exists
            for period in self.rating_periods['periods']:
                if period['period_id'] == period_id:
                    logger.warning(f"Rating period {period_id} already exists")
                    return True
            
            # Create new period
            new_period = {
                'period_id': period_id,
                'description': description,
                'start_date': datetime.now(timezone.utc).isoformat(),
                'end_date': None,
                'total_matches': 0,
                'total_athletes': len(self.athlete_ratings['athletes'])
            }
            
            self.rating_periods['periods'].append(new_period)
            self.rating_periods['metadata']['current_period'] = period_id
            self.rating_periods['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Update all athletes to new period
            for athlete_id in self.athlete_ratings['athletes']:
                self.athlete_ratings['athletes'][athlete_id]['period_id'] = period_id
            
            # Save both files
            success1 = self._save_rating_periods(self.rating_periods)
            success2 = self._save_athlete_ratings(self.athlete_ratings)
            
            if success1 and success2:
                logger.info(f"Started rating period: {period_id}")
            
            return success1 and success2
            
        except Exception as e:
            logger.error(f"Failed to start rating period {period_id}: {e}")
            return False
    
    def end_rating_period(self, period_id: str) -> bool:
        """
        End a rating period and finalize ratings.
        
        Args:
            period_id: Period identifier to end
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find and update period
            for period in self.rating_periods['periods']:
                if period['period_id'] == period_id:
                    period['end_date'] = datetime.now(timezone.utc).isoformat()
                    break
            else:
                logger.error(f"Rating period {period_id} not found")
                return False
            
            # Update metadata
            self.rating_periods['metadata']['current_period'] = None
            self.rating_periods['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save periods
            success = self._save_rating_periods(self.rating_periods)
            
            if success:
                logger.info(f"Ended rating period: {period_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to end rating period {period_id}: {e}")
            return False
    
    def get_rating_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all ratings.
        
        Returns:
            Dictionary of rating statistics
        """
        try:
            athletes = self.athlete_ratings['athletes']
            
            if not athletes:
                return {
                    'total_athletes': 0,
                    'average_rating': 0,
                    'rating_distribution': {},
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            
            ratings = [athlete['rating'] for athlete in athletes.values()]
            
            # Calculate statistics
            avg_rating = sum(ratings) / len(ratings)
            min_rating = min(ratings)
            max_rating = max(ratings)
            
            # Rating distribution
            distribution = {
                '1500-1600': len([r for r in ratings if 1500 <= r < 1600]),
                '1600-1700': len([r for r in ratings if 1600 <= r < 1700]),
                '1700-1800': len([r for r in ratings if 1700 <= r < 1800]),
                '1800+': len([r for r in ratings if r >= 1800])
            }
            
            stats = {
                'total_athletes': len(athletes),
                'average_rating': avg_rating,
                'min_rating': min_rating,
                'max_rating': max_rating,
                'rating_distribution': distribution,
                'total_matches': sum(athlete['matches_played'] for athlete in athletes.values()),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            logger.debug(f"Generated rating statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate rating statistics: {e}")
            return {}
    
    def export_ratings_to_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Export all ratings to a pandas DataFrame.
        
        Returns:
            DataFrame with rating data or None if failed
        """
        try:
            athletes = self.athlete_ratings['athletes']
            
            if not athletes:
                return pd.DataFrame()
            
            data = []
            for athlete_id, rating_data in athletes.items():
                data.append({
                    'athlete_id': athlete_id,
                    'rating': rating_data['rating'],
                    'rating_deviation': rating_data['rating_deviation'],
                    'volatility': rating_data['volatility'],
                    'matches_played': rating_data['matches_played'],
                    'period_id': rating_data.get('period_id'),
                    'last_updated': rating_data['last_updated']
                })
            
            df = pd.DataFrame(data)
            logger.debug(f"Exported {len(df)} athlete ratings to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Failed to export ratings to DataFrame: {e}")
            return None 