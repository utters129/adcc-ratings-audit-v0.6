#!/usr/bin/env python3
"""
Railway Deployment Helper Script
This script helps prepare the application for Railway deployment.
"""

import os
import sys
import subprocess
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)

def check_railway_cli():
    """Check if Railway CLI is installed."""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Railway CLI is installed")
            return True
        else:
            logger.warning("Railway CLI not found")
            return False
    except FileNotFoundError:
        logger.warning("Railway CLI not found")
        return False

def generate_environment_variables():
    """Generate environment variables for Railway."""
    logger.info("Generating Railway environment variables...")
    
    # Generate secure passwords
    import bcrypt
    
    admin_password = "admin123"  # Change this in production
    developer_password = "dev123"  # Change this in production
    
    admin_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
    developer_hash = bcrypt.hashpw(developer_password.encode(), bcrypt.gensalt()).decode()
    
    env_vars = {
        "SMOOTHCOMP_USERNAME": "your_smoothcomp_username",
        "SMOOTHCOMP_PASSWORD": "your_smoothcomp_password",
        "ADMIN_PASSWORD": admin_hash,
        "DEVELOPER_PASSWORD": developer_hash,
        "LOG_LEVEL": "INFO",
        "WEBHOOK_SECRET": "your_webhook_secret_key_here",
        "JWT_SECRET_KEY": "your_jwt_secret_key_here",
        "ENVIRONMENT": "production",
        "DEBUG": "false"
    }
    
    # Create .env file for Railway
    env_content = "\n".join([f"{key}={value}" for key, value in env_vars.items()])
    
    with open("railway.env", "w") as f:
        f.write(env_content)
    
    logger.info("Created railway.env file with environment variables")
    logger.info("IMPORTANT: Update the placeholder values in railway.env before deployment")
    
    return env_vars

def check_deployment_files():
    """Check if all required deployment files exist."""
    logger.info("Checking deployment files...")
    
    required_files = [
        "railway.json",
        "Procfile", 
        "runtime.txt",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            logger.info(f"✅ {file} exists")
    
    if missing_files:
        logger.error(f"Missing deployment files: {missing_files}")
        return False
    
    logger.info("All deployment files are present")
    return True

def test_local_deployment():
    """Test the application locally to ensure it's ready for deployment."""
    logger.info("Testing local deployment...")
    
    try:
        # Test importing the main app
        from src.web_ui.main import app
        logger.info("✅ FastAPI app imports successfully")
        
        # Test configuration
        from src.config.settings import get_settings
        settings = get_settings()
        logger.info(f"✅ Configuration loaded: environment={settings.environment}")
        
        # Test all major components
        from src.data_acquisition.smoothcomp_client import SmoothcompClient
        from src.analytics.glicko_engine import GlickoEngine
        from src.webhooks import WebhookManager
        
        logger.info("✅ All major components import successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Local deployment test failed: {e}")
        return False

def main():
    """Main deployment preparation function."""
    logger.info("Starting Railway deployment preparation...")
    
    # Check deployment files
    if not check_deployment_files():
        logger.error("Deployment files check failed")
        return False
    
    # Test local deployment
    if not test_local_deployment():
        logger.error("Local deployment test failed")
        return False
    
    # Generate environment variables
    env_vars = generate_environment_variables()
    
    # Check Railway CLI
    if check_railway_cli():
        logger.info("Railway CLI is available for deployment")
    else:
        logger.info("Railway CLI not found - you'll need to deploy via Railway web interface")
    
    logger.info("\n" + "="*60)
    logger.info("DEPLOYMENT PREPARATION COMPLETE")
    logger.info("="*60)
    logger.info("Next steps:")
    logger.info("1. Update railway.env with your actual credentials")
    logger.info("2. Go to https://railway.app/ and create a new project")
    logger.info("3. Connect your GitHub repository")
    logger.info("4. Set the environment variables in Railway dashboard")
    logger.info("5. Deploy the application")
    logger.info("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 