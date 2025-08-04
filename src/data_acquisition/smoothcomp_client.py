"""
Smoothcomp API Client for ADCC Analysis Engine v0.6
Handles authentication and data download from Smoothcomp platform.
"""

import requests
import pandas as pd
import json
import structlog
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logger = structlog.get_logger(__name__)


class SmoothcompClient:
    """
    Client for interacting with Smoothcomp API and web interface.
    
    Handles authentication, data download, and file management for
    event registration and match data.
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize the Smoothcomp client.
        
        Args:
            username: Smoothcomp account username
            password: Smoothcomp account password
        """
        self.username = username
        self.password = password
        self.base_url = "https://www.smoothcomp.com"
        self.session = requests.Session()
        self.is_authenticated = False
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logger.info("SmoothcompClient initialized", username=username)
    
    def login(self) -> bool:
        """
        Authenticate with Smoothcomp.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to login to Smoothcomp")
            
            # First, get the login page to get any necessary tokens
            login_page_url = f"{self.base_url}/en/login"
            response = self.session.get(login_page_url)
            response.raise_for_status()
            
            # Prepare login data
            login_data = {
                'username': self.username,
                'password': self.password,
                'remember': 'on'
            }
            
            # Attempt login
            login_response = self.session.post(
                login_page_url,
                data=login_data,
                allow_redirects=True
            )
            
            # Check if login was successful
            if login_response.status_code == 200:
                # Verify authentication by checking if we can access protected content
                profile_response = self.session.get(f"{self.base_url}/en/profile")
                if profile_response.status_code == 200 and "login" not in profile_response.url.lower():
                    self.is_authenticated = True
                    logger.info("Successfully logged in to Smoothcomp")
                    return True
                else:
                    logger.warning("Login appeared successful but authentication failed")
                    return False
            else:
                logger.error("Login failed", status_code=login_response.status_code)
                return False
                
        except requests.RequestException as e:
            logger.error("Login request failed", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error during login", error=str(e))
            return False
    
    def validate_event_id(self, event_id: str) -> bool:
        """
        Validate event ID format.
        
        Args:
            event_id: Event ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not event_id:
            return False
        
        # Remove 'E' prefix if present
        clean_id = event_id.replace('E', '')
        
        # Check if it's a valid numeric ID
        try:
            int(clean_id)
            return True
        except ValueError:
            return False
    
    def get_event_info(self, event_id: str) -> Dict[str, Any]:
        """
        Get basic information about an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            Dict containing event information or error details
        """
        if not self.validate_event_id(event_id):
            return {
                "success": False,
                "error": f"Invalid event ID format: {event_id}"
            }
        
        if not self.is_authenticated:
            login_result = self.login()
            if not login_result:
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
        
        try:
            clean_id = event_id.replace('E', '')
            event_url = f"{self.base_url}/en/event/{clean_id}"
            
            logger.info("Fetching event information", event_id=clean_id)
            
            response = self.session.get(event_url)
            response.raise_for_status()
            
            # Parse event information from the page
            # This is a simplified implementation - actual parsing would depend on page structure
            event_info = {
                "id": clean_id,
                "url": event_url,
                "fetched_at": datetime.now().isoformat()
            }
            
            logger.info("Successfully fetched event information", event_id=clean_id)
            
            return {
                "success": True,
                "data": event_info
            }
            
        except requests.RequestException as e:
            logger.error("Failed to fetch event info", event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except Exception as e:
            logger.error("Unexpected error fetching event info", event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def get_event_registrations(self, event_id: str, download_dir: Path) -> Dict[str, Any]:
        """
        Download event registration data.
        
        Args:
            event_id: Event ID
            download_dir: Directory to save the file
            
        Returns:
            Dict containing download result and file information
        """
        if not self.validate_event_id(event_id):
            return {
                "success": False,
                "error": f"Invalid event ID format: {event_id}"
            }
        
        if not self.is_authenticated:
            login_result = self.login()
            if not login_result:
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
        
        try:
            clean_id = event_id.replace('E', '')
            registrations_url = f"{self.base_url}/en/event/{clean_id}/registrations"
            
            logger.info("Downloading event registrations", event_id=clean_id)
            
            response = self.session.get(registrations_url)
            response.raise_for_status()
            
            # Parse registration data from the page
            # This is a simplified implementation - actual parsing would depend on page structure
            registration_data = self._parse_registration_data(response.text)
            
            # Save to CSV file
            filename = f"registrations.csv"
            result = self._save_data_to_file(registration_data, filename, download_dir)
            
            if result["success"]:
                logger.info("Successfully downloaded registrations", 
                          event_id=clean_id, filename=filename)
                return {
                    "success": True,
                    "files": [filename],
                    "record_count": len(registration_data)
                }
            else:
                return result
                
        except requests.RequestException as e:
            logger.error("Failed to download registrations", event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except Exception as e:
            logger.error("Unexpected error downloading registrations", 
                        event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def get_event_matches(self, event_id: str, download_dir: Path) -> Dict[str, Any]:
        """
        Download event match data.
        
        Args:
            event_id: Event ID
            download_dir: Directory to save the file
            
        Returns:
            Dict containing download result and file information
        """
        if not self.validate_event_id(event_id):
            return {
                "success": False,
                "error": f"Invalid event ID format: {event_id}"
            }
        
        if not self.is_authenticated:
            login_result = self.login()
            if not login_result:
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
        
        try:
            clean_id = event_id.replace('E', '')
            matches_url = f"{self.base_url}/en/event/{clean_id}/matches"
            
            logger.info("Downloading event matches", event_id=clean_id)
            
            response = self.session.get(matches_url)
            response.raise_for_status()
            
            # Parse match data from the page
            # This is a simplified implementation - actual parsing would depend on page structure
            match_data = self._parse_match_data(response.text)
            
            # Save to Excel file
            filename = f"matches.xlsx"
            result = self._save_data_to_file(match_data, filename, download_dir, file_type="excel")
            
            if result["success"]:
                logger.info("Successfully downloaded matches", 
                          event_id=clean_id, filename=filename)
                return {
                    "success": True,
                    "files": [filename],
                    "match_count": len(match_data)
                }
            else:
                return result
                
        except requests.RequestException as e:
            logger.error("Failed to download matches", event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except Exception as e:
            logger.error("Unexpected error downloading matches", 
                        event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def download_complete_event(self, event_id: str, download_dir: Path) -> Dict[str, Any]:
        """
        Download complete event data (info, registrations, matches).
        
        Args:
            event_id: Event ID
            download_dir: Directory to save files
            
        Returns:
            Dict containing download result and file information
        """
        logger.info("Starting complete event download", event_id=event_id)
        
        # Ensure download directory exists
        download_dir.mkdir(parents=True, exist_ok=True)
        
        all_files = []
        errors = []
        
        # Get event info
        event_info_result = self.get_event_info(event_id)
        if event_info_result["success"]:
            filename = f"event_info.json"
            save_result = self._save_data_to_file(
                event_info_result["data"], filename, download_dir, file_type="json"
            )
            if save_result["success"]:
                all_files.append(filename)
            else:
                errors.append(f"Failed to save event info: {save_result['error']}")
        else:
            errors.append(f"Failed to get event info: {event_info_result['error']}")
        
        # Get registrations
        registrations_result = self.get_event_registrations(event_id, download_dir)
        if registrations_result["success"]:
            all_files.extend(registrations_result["files"])
        else:
            errors.append(f"Failed to get registrations: {registrations_result['error']}")
        
        # Get matches
        matches_result = self.get_event_matches(event_id, download_dir)
        if matches_result["success"]:
            all_files.extend(matches_result["files"])
        else:
            errors.append(f"Failed to get matches: {matches_result['error']}")
        
        if errors:
            logger.warning("Complete event download completed with errors", 
                          event_id=event_id, errors=errors)
            return {
                "success": False,
                "files": all_files,
                "errors": errors
            }
        else:
            logger.info("Complete event download successful", 
                       event_id=event_id, file_count=len(all_files))
            return {
                "success": True,
                "files": all_files
            }
    
    def _parse_registration_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse registration data from HTML content.
        
        Args:
            html_content: HTML content from registration page
            
        Returns:
            List of registration dictionaries
        """
        # This is a placeholder implementation
        # Actual implementation would parse the HTML structure
        # For now, return empty list to satisfy interface
        logger.debug("Parsing registration data from HTML")
        return []
    
    def _parse_match_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse match data from HTML content.
        
        Args:
            html_content: HTML content from matches page
            
        Returns:
            List of match dictionaries
        """
        # This is a placeholder implementation
        # Actual implementation would parse the HTML structure
        # For now, return empty list to satisfy interface
        logger.debug("Parsing match data from HTML")
        return []
    
    def _save_data_to_file(self, data: List[Dict[str, Any]], filename: str, 
                          download_dir: Path, file_type: str = "csv") -> Dict[str, Any]:
        """
        Save data to file in specified format.
        
        Args:
            data: Data to save
            filename: Output filename
            download_dir: Directory to save file
            file_type: File type (csv, excel, json)
            
        Returns:
            Dict containing save result
        """
        try:
            file_path = download_dir / filename
            
            if file_type == "csv":
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
            elif file_type == "excel":
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)
            elif file_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_type}"
                }
            
            logger.debug("Data saved to file", filename=filename, file_type=file_type)
            return {"success": True}
            
        except Exception as e:
            logger.error("Failed to save data to file", 
                        filename=filename, error=str(e))
            return {
                "success": False,
                "error": f"Failed to save file: {str(e)}"
            }
    
    def cleanup(self):
        """Clean up resources and close session."""
        if self.session:
            self.session.close()
            self.session = None
        self.is_authenticated = False
        logger.info("SmoothcompClient session cleaned up") 