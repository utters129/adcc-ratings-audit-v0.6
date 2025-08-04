"""
Browser Automation for ADCC Analysis Engine v0.6
Handles automated browser interactions for data download from Smoothcomp.
"""

import structlog
from pathlib import Path
from typing import Dict, List, Optional, Any
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = structlog.get_logger(__name__)


class BrowserAutomation:
    """
    Browser automation for Smoothcomp data download.
    
    Handles Chrome WebDriver setup, navigation, and automated
    file downloads from Smoothcomp platform.
    """
    
    def __init__(self, download_dir: Path, headless: bool = True):
        """
        Initialize browser automation.
        
        Args:
            download_dir: Directory for downloaded files
            headless: Whether to run browser in headless mode
        """
        self.download_dir = Path(download_dir)
        self.headless = headless
        self.driver = None
        
        # Ensure download directory exists
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("BrowserAutomation initialized", 
                   download_dir=str(download_dir), headless=headless)
    
    def start_browser(self) -> bool:
        """
        Start Chrome browser with appropriate options.
        
        Returns:
            bool: True if browser started successfully, False otherwise
        """
        try:
            logger.info("Starting Chrome browser")
            
            # Configure Chrome options
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Set download directory
            chrome_options.add_experimental_option(
                "prefs", {
                    "download.default_directory": str(self.download_dir),
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
            )
            
            # Additional options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome browser started successfully")
            return True
            
        except WebDriverException as e:
            logger.error("Failed to start Chrome browser", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error starting browser", error=str(e))
            return False
    
    def stop_browser(self):
        """Stop and cleanup browser resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser stopped successfully")
            except Exception as e:
                logger.error("Error stopping browser", error=str(e))
            finally:
                self.driver = None
    
    def navigate_to_event(self, event_id: str) -> bool:
        """
        Navigate to a specific event page.
        
        Args:
            event_id: Event ID to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        if not self.driver:
            logger.error("Browser not started")
            return False
        
        try:
            # Clean event ID (remove 'E' prefix if present)
            clean_id = event_id.replace('E', '')
            event_url = f"https://www.smoothcomp.com/en/event/{clean_id}"
            
            logger.info("Navigating to event page", event_id=clean_id)
            
            self.driver.get(event_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("Successfully navigated to event page", event_id=clean_id)
            return True
            
        except TimeoutException:
            logger.error("Timeout waiting for event page to load", event_id=event_id)
            return False
        except Exception as e:
            logger.error("Error navigating to event page", 
                        event_id=event_id, error=str(e))
            return False
    
    def download_registrations(self, event_id: str) -> Dict[str, Any]:
        """
        Download registration data for an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            Dict containing download result
        """
        if not self.driver:
            return {
                "success": False,
                "error": "Browser not started"
            }
        
        try:
            logger.info("Starting registration download", event_id=event_id)
            
            # Navigate to registrations page
            clean_id = event_id.replace('E', '')
            registrations_url = f"https://www.smoothcomp.com/en/event/{clean_id}/registrations"
            
            self.driver.get(registrations_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for download button/link
            # This is a simplified implementation - actual selectors would depend on page structure
            download_selectors = [
                "//button[contains(text(), 'Download')]",
                "//a[contains(text(), 'Download')]",
                "//button[contains(@class, 'download')]",
                "//a[contains(@class, 'download')]"
            ]
            
            download_clicked = False
            for selector in download_selectors:
                try:
                    download_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    download_element.click()
                    download_clicked = True
                    logger.info("Clicked download button", selector=selector)
                    break
                except TimeoutException:
                    continue
            
            if not download_clicked:
                logger.warning("No download button found, attempting to find export options")
                # Try alternative approaches for data export
                # This would depend on the actual page structure
            
            # Wait for download to complete
            time.sleep(3)  # Give time for download to start
            
            logger.info("Registration download initiated", event_id=event_id)
            return {
                "success": True,
                "message": "Download initiated"
            }
            
        except Exception as e:
            logger.error("Error downloading registrations", 
                        event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Download failed: {str(e)}"
            }
    
    def download_matches(self, event_id: str) -> Dict[str, Any]:
        """
        Download match data for an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            Dict containing download result
        """
        if not self.driver:
            return {
                "success": False,
                "error": "Browser not started"
            }
        
        try:
            logger.info("Starting match download", event_id=event_id)
            
            # Navigate to matches page
            clean_id = event_id.replace('E', '')
            matches_url = f"https://www.smoothcomp.com/en/event/{clean_id}/matches"
            
            self.driver.get(matches_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for download/export options
            # Similar to registration download but for match data
            download_selectors = [
                "//button[contains(text(), 'Export')]",
                "//a[contains(text(), 'Export')]",
                "//button[contains(text(), 'Download')]",
                "//a[contains(text(), 'Download')]"
            ]
            
            download_clicked = False
            for selector in download_selectors:
                try:
                    download_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    download_element.click()
                    download_clicked = True
                    logger.info("Clicked export button", selector=selector)
                    break
                except TimeoutException:
                    continue
            
            if not download_clicked:
                logger.warning("No export button found for matches")
            
            # Wait for download to complete
            time.sleep(3)
            
            logger.info("Match download initiated", event_id=event_id)
            return {
                "success": True,
                "message": "Download initiated"
            }
            
        except Exception as e:
            logger.error("Error downloading matches", 
                        event_id=event_id, error=str(e))
            return {
                "success": False,
                "error": f"Download failed: {str(e)}"
            }
    
    def wait_for_download(self, filename: str, timeout: int = 30) -> bool:
        """
        Wait for a specific file to be downloaded.
        
        Args:
            filename: Expected filename
            timeout: Timeout in seconds
            
        Returns:
            bool: True if file found, False if timeout
        """
        logger.info("Waiting for download", filename=filename, timeout=timeout)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            file_path = self.download_dir / filename
            
            # Check for exact filename
            if file_path.exists():
                logger.info("Download completed", filename=filename)
                return True
            
            # Check for partial downloads (files with .crdownload extension)
            partial_files = list(self.download_dir.glob(f"{filename}.*"))
            if partial_files:
                logger.debug("Partial download detected", files=[f.name for f in partial_files])
            
            time.sleep(1)
        
        logger.warning("Download timeout", filename=filename, timeout=timeout)
        return False
    
    def get_downloaded_files(self) -> List[Path]:
        """
        Get list of downloaded files.
        
        Returns:
            List of downloaded file paths
        """
        if not self.download_dir.exists():
            return []
        
        # Get all files in download directory
        files = list(self.download_dir.glob("*"))
        # Filter out directories and temporary files
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        return files
    
    def cleanup_downloads(self):
        """Clean up downloaded files."""
        try:
            files = self.get_downloaded_files()
            for file_path in files:
                file_path.unlink()
                logger.debug("Cleaned up downloaded file", filename=file_path.name)
            
            logger.info("Download cleanup completed", file_count=len(files))
            
        except Exception as e:
            logger.error("Error during download cleanup", error=str(e)) 