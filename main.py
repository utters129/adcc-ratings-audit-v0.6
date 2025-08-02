"""
ADCC Analysis Engine v0.6 - Main Orchestrator
Main entry point for the ADCC Analysis Engine application.
"""

import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import get_settings
from src.utils.logger import setup_logging


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load settings
        settings = get_settings()
        logger.info("ADCC Analysis Engine v0.6 starting...")
        logger.info(f"Environment: {settings.environment}")
        
        # TODO: Initialize components
        # TODO: Start web server
        # TODO: Start data processing pipeline
        
        logger.info("ADCC Analysis Engine started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start ADCC Analysis Engine: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 