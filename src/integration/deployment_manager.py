"""
Deployment Manager for ADCC Analysis Engine

This module handles deployment preparation, configuration, and monitoring
for Railway deployment and production environment management.
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import structlog

from src.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class DeploymentManager:
    """
    Manages deployment preparation, configuration, and monitoring
    for the ADCC Analysis Engine.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the deployment manager.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.deployment_config: Dict[str, Any] = {}
        self.environment_vars: Dict[str, str] = {}
        self.deployment_status: Dict[str, Any] = {}
        
        logger.info("Deployment manager initialized", project_root=str(self.project_root))
    
    def prepare_deployment(self, environment: str = "production") -> Dict[str, Any]:
        """
        Prepare the application for deployment.
        
        Args:
            environment: Deployment environment (production, staging, development)
            
        Returns:
            Dictionary containing deployment preparation results
        """
        logger.info("Preparing deployment", environment=environment)
        
        try:
            # Step 1: Validate project structure
            structure_validation = self._validate_project_structure()
            
            # Step 2: Check dependencies
            dependency_check = self._check_dependencies()
            
            # Step 3: Generate deployment configuration
            config_generation = self._generate_deployment_config(environment)
            
            # Step 4: Prepare environment variables
            env_preparation = self._prepare_environment_variables(environment)
            
            # Step 5: Create deployment files
            file_creation = self._create_deployment_files(environment)
            
            # Step 6: Run pre-deployment tests
            pre_deployment_tests = self._run_pre_deployment_tests()
            
            self.deployment_status = {
                "environment": environment,
                "timestamp": datetime.now().isoformat(),
                "structure_validation": structure_validation,
                "dependency_check": dependency_check,
                "config_generation": config_generation,
                "env_preparation": env_preparation,
                "file_creation": file_creation,
                "pre_deployment_tests": pre_deployment_tests,
                "overall_status": "READY" if all([
                    structure_validation["status"] == "PASS",
                    dependency_check["status"] == "PASS",
                    config_generation["status"] == "PASS",
                    env_preparation["status"] == "PASS",
                    file_creation["status"] == "PASS",
                    pre_deployment_tests["status"] == "PASS"
                ]) else "FAILED"
            }
            
            logger.info("Deployment preparation completed", 
                       environment=environment,
                       status=self.deployment_status["overall_status"])
            
            return self.deployment_status
            
        except Exception as e:
            logger.error("Deployment preparation failed", error=str(e))
            self.deployment_status = {
                "environment": environment,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall_status": "FAILED"
            }
            return self.deployment_status
    
    def _validate_project_structure(self) -> Dict[str, Any]:
        """Validate that all required files and directories exist."""
        logger.info("Validating project structure")
        
        required_files = [
            "requirements.txt",
            "src/web_ui/main.py",
            "src/config/settings.py",
            "src/integration/system_integrator.py",
            "src/integration/performance_monitor.py"
        ]
        
        required_directories = [
            "src/web_ui/templates",
            "src/web_ui/static",
            "src/web_ui/api",
            "tests"
        ]
        
        missing_files = []
        missing_directories = []
        
        # Check files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        # Check directories
        for dir_path in required_directories:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_directories.append(dir_path)
        
        status = "PASS" if not missing_files and not missing_directories else "FAIL"
        
        return {
            "status": status,
            "missing_files": missing_files,
            "missing_directories": missing_directories,
            "total_checked": len(required_files) + len(required_directories)
        }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check that all required dependencies are available."""
        logger.info("Checking dependencies")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "pandas",
            "structlog",
            "pydantic",
            "jinja2",
            "python-jose",
            "passlib",
            "psutil"
        ]
        
        missing_packages = []
        available_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                available_packages.append(package)
            except ImportError:
                missing_packages.append(package)
        
        status = "PASS" if not missing_packages else "FAIL"
        
        return {
            "status": status,
            "missing_packages": missing_packages,
            "available_packages": available_packages,
            "total_required": len(required_packages)
        }
    
    def _generate_deployment_config(self, environment: str) -> Dict[str, Any]:
        """Generate deployment configuration for Railway."""
        logger.info("Generating deployment configuration", environment=environment)
        
        try:
            # Railway configuration
            railway_config = {
                "build": {
                    "builder": "nixpacks",
                    "buildCommand": "pip install -r requirements.txt"
                },
                "deploy": {
                    "startCommand": "uvicorn src.web_ui.main:app --host 0.0.0.0 --port $PORT",
                    "healthcheckPath": "/health",
                    "healthcheckTimeout": 300,
                    "restartPolicyType": "ON_FAILURE"
                }
            }
            
            # Environment-specific configurations
            if environment == "production":
                railway_config["deploy"]["numReplicas"] = 2
                railway_config["deploy"]["restartPolicyType"] = "ON_FAILURE"
            elif environment == "staging":
                railway_config["deploy"]["numReplicas"] = 1
                railway_config["deploy"]["restartPolicyType"] = "ON_FAILURE"
            else:  # development
                railway_config["deploy"]["numReplicas"] = 1
                railway_config["deploy"]["restartPolicyType"] = "NEVER"
            
            self.deployment_config = railway_config
            
            return {
                "status": "PASS",
                "config_generated": True,
                "environment": environment
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def _prepare_environment_variables(self, environment: str) -> Dict[str, Any]:
        """Prepare environment variables for deployment."""
        logger.info("Preparing environment variables", environment=environment)
        
        try:
            # Base environment variables
            base_vars = {
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": environment,
                "PYTHONPATH": "/app",
                "PORT": "8000"
            }
            
            # Environment-specific variables
            if environment == "production":
                env_vars = {
                    **base_vars,
                    "LOG_LEVEL": "WARNING",
                    "DEBUG": "false",
                    "RELOAD": "false"
                }
            elif environment == "staging":
                env_vars = {
                    **base_vars,
                    "LOG_LEVEL": "INFO",
                    "DEBUG": "false",
                    "RELOAD": "false"
                }
            else:  # development
                env_vars = {
                    **base_vars,
                    "LOG_LEVEL": "DEBUG",
                    "DEBUG": "true",
                    "RELOAD": "true"
                }
            
            # Add sensitive variables (these should be set via Railway dashboard)
            sensitive_vars = [
                "SMOOTHCOMP_USERNAME",
                "SMOOTHCOMP_PASSWORD",
                "SECRET_KEY",
                "ADMIN_PASSWORD",
                "DEVELOPER_PASSWORD"
            ]
            
            self.environment_vars = env_vars
            
            return {
                "status": "PASS",
                "base_variables": len(base_vars),
                "sensitive_variables": len(sensitive_vars),
                "total_variables": len(env_vars) + len(sensitive_vars)
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def _create_deployment_files(self, environment: str) -> Dict[str, Any]:
        """Create necessary deployment files."""
        logger.info("Creating deployment files", environment=environment)
        
        try:
            created_files = []
            
            # Create Railway configuration file
            railway_config_path = self.project_root / "railway.json"
            with open(railway_config_path, 'w') as f:
                json.dump(self.deployment_config, f, indent=2)
            created_files.append("railway.json")
            
            # Create Procfile for Railway
            procfile_path = self.project_root / "Procfile"
            with open(procfile_path, 'w') as f:
                f.write("web: uvicorn src.web_ui.main:app --host 0.0.0.0 --port $PORT\n")
            created_files.append("Procfile")
            
            # Create runtime.txt for Python version
            runtime_path = self.project_root / "runtime.txt"
            with open(runtime_path, 'w') as f:
                f.write("python-3.9.18\n")
            created_files.append("runtime.txt")
            
            # Create .dockerignore
            dockerignore_path = self.project_root / ".dockerignore"
            dockerignore_content = [
                "__pycache__",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".Python",
                "env",
                "pip-log.txt",
                "pip-delete-this-directory.txt",
                ".tox",
                ".coverage",
                ".coverage.*",
                ".cache",
                "nosetests.xml",
                "coverage.xml",
                "*.cover",
                "*.log",
                ".git",
                ".mypy_cache",
                ".pytest_cache",
                ".DS_Store",
                "tests/",
                "context/",
                "logs/",
                "data/",
                "downloads/"
            ]
            with open(dockerignore_path, 'w') as f:
                f.write('\n'.join(dockerignore_content))
            created_files.append(".dockerignore")
            
            return {
                "status": "PASS",
                "files_created": created_files,
                "total_files": len(created_files)
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def _run_pre_deployment_tests(self) -> Dict[str, Any]:
        """Run pre-deployment tests to ensure everything works."""
        logger.info("Running pre-deployment tests")
        
        try:
            # Test imports
            import_test = self._test_imports()
            
            # Test configuration loading
            config_test = self._test_configuration()
            
            # Test web application startup
            web_test = self._test_web_application()
            
            # Test API endpoints
            api_test = self._test_api_endpoints()
            
            all_tests_passed = all([
                import_test["status"] == "PASS",
                config_test["status"] == "PASS",
                web_test["status"] == "PASS",
                api_test["status"] == "PASS"
            ])
            
            return {
                "status": "PASS" if all_tests_passed else "FAIL",
                "import_test": import_test,
                "config_test": config_test,
                "web_test": web_test,
                "api_test": api_test,
                "total_tests": 4,
                "passed_tests": sum([
                    1 if import_test["status"] == "PASS" else 0,
                    1 if config_test["status"] == "PASS" else 0,
                    1 if web_test["status"] == "PASS" else 0,
                    1 if api_test["status"] == "PASS" else 0
                ])
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def _test_imports(self) -> Dict[str, Any]:
        """Test that all required modules can be imported."""
        try:
            # Test core imports
            from src.web_ui.main import app
            from src.config.settings import get_settings
            from src.integration.system_integrator import SystemIntegrator
            from src.integration.performance_monitor import PerformanceMonitor
            
            return {
                "status": "PASS",
                "modules_imported": ["app", "settings", "SystemIntegrator", "PerformanceMonitor"]
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def _test_configuration(self) -> Dict[str, Any]:
        """Test configuration loading."""
        try:
            settings = get_settings()
            
            # Check required settings
            required_settings = [
                "secret_key",
                "log_level"
            ]
            
            missing_settings = []
            for setting in required_settings:
                if not hasattr(settings, setting) or getattr(settings, setting) is None:
                    missing_settings.append(setting)
            
            return {
                "status": "PASS" if not missing_settings else "FAIL",
                "missing_settings": missing_settings,
                "settings_loaded": True
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def _test_web_application(self) -> Dict[str, Any]:
        """Test web application startup."""
        try:
            from src.web_ui.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            
            return {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "health_check_status": response.status_code,
                "app_started": True
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def _test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints."""
        try:
            from src.web_ui.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test basic endpoints
            endpoints_to_test = [
                "/api/athletes/",
                "/api/events/",
                "/api/leaderboards/global/top"
            ]
            
            failed_endpoints = []
            successful_endpoints = []
            
            for endpoint in endpoints_to_test:
                try:
                    response = client.get(endpoint)
                    if response.status_code in [200, 401]:  # 401 is expected for unauthenticated requests
                        successful_endpoints.append(endpoint)
                    else:
                        failed_endpoints.append(f"{endpoint}: {response.status_code}")
                except Exception as e:
                    failed_endpoints.append(f"{endpoint}: {str(e)}")
            
            return {
                "status": "PASS" if not failed_endpoints else "FAIL",
                "successful_endpoints": successful_endpoints,
                "failed_endpoints": failed_endpoints,
                "total_endpoints": len(endpoints_to_test)
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def generate_deployment_instructions(self) -> Dict[str, Any]:
        """Generate deployment instructions for Railway."""
        logger.info("Generating deployment instructions")
        
        instructions = {
            "railway_setup": [
                "1. Install Railway CLI: npm install -g @railway/cli",
                "2. Login to Railway: railway login",
                "3. Link project: railway link",
                "4. Set environment variables via Railway dashboard"
            ],
            "environment_variables": {
                "required": [
                    "SMOOTHCOMP_USERNAME",
                    "SMOOTHCOMP_PASSWORD", 
                    "SECRET_KEY",
                    "ADMIN_PASSWORD",
                    "DEVELOPER_PASSWORD"
                ],
                "optional": [
                    "LOG_LEVEL=INFO",
                    "ENVIRONMENT=production",
                    "DEBUG=false"
                ]
            },
            "deployment_commands": [
                "railway up --service production",
                "railway status",
                "railway logs"
            ],
            "monitoring": [
                "Check Railway dashboard for resource usage",
                "Monitor application logs: railway logs",
                "Set up alerts for high resource usage"
            ],
            "rollback": [
                "railway rollback",
                "Check previous deployment status"
            ]
        }
        
        return instructions
    
    def create_deployment_report(self) -> Dict[str, Any]:
        """Create a comprehensive deployment report."""
        logger.info("Creating deployment report")
        
        if not self.deployment_status:
            return {"error": "No deployment status available. Run prepare_deployment() first."}
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "deployment_status": self.deployment_status,
            "instructions": self.generate_deployment_instructions(),
            "recommendations": self._generate_deployment_recommendations(),
            "next_steps": self._generate_next_steps()
        }
        
        return report
    
    def _generate_deployment_recommendations(self) -> List[str]:
        """Generate deployment recommendations based on status."""
        recommendations = []
        
        if not self.deployment_status:
            recommendations.append("Run prepare_deployment() to generate recommendations")
            return recommendations
        
        # Check structure validation
        if self.deployment_status.get("structure_validation", {}).get("status") == "FAIL":
            recommendations.append("Fix missing files and directories before deployment")
        
        # Check dependencies
        if self.deployment_status.get("dependency_check", {}).get("status") == "FAIL":
            recommendations.append("Install missing dependencies before deployment")
        
        # Check pre-deployment tests
        if self.deployment_status.get("pre_deployment_tests", {}).get("status") == "FAIL":
            recommendations.append("Fix failing tests before deployment")
        
        # General recommendations
        if self.deployment_status.get("overall_status") == "READY":
            recommendations.append("System is ready for deployment")
            recommendations.append("Set up monitoring and alerting in Railway")
            recommendations.append("Configure backup strategy for production data")
        else:
            recommendations.append("Fix all issues before attempting deployment")
        
        return recommendations
    
    def _generate_next_steps(self) -> List[str]:
        """Generate next steps for deployment."""
        if self.deployment_status.get("overall_status") == "READY":
            return [
                "1. Set up Railway project and link repository",
                "2. Configure environment variables in Railway dashboard",
                "3. Deploy to staging environment first",
                "4. Run integration tests on staging",
                "5. Deploy to production environment",
                "6. Monitor application performance and logs",
                "7. Set up automated monitoring and alerting"
            ]
        else:
            return [
                "1. Fix all deployment preparation issues",
                "2. Re-run prepare_deployment()",
                "3. Ensure all tests pass",
                "4. Then proceed with Railway deployment"
            ]
    
    def cleanup_deployment_files(self):
        """Clean up deployment files created during preparation."""
        logger.info("Cleaning up deployment files")
        
        files_to_remove = [
            "railway.json",
            "Procfile", 
            "runtime.txt",
            ".dockerignore"
        ]
        
        removed_files = []
        for file_name in files_to_remove:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_path.unlink()
                removed_files.append(file_name)
        
        logger.info("Deployment files cleaned up", removed_files=removed_files)
        return removed_files


def prepare_railway_deployment(environment: str = "production") -> Dict[str, Any]:
    """
    Convenience function to prepare Railway deployment.
    
    Args:
        environment: Deployment environment
        
    Returns:
        Deployment preparation results
    """
    manager = DeploymentManager()
    try:
        results = manager.prepare_deployment(environment)
        report = manager.create_deployment_report()
        return {
            "preparation_results": results,
            "deployment_report": report
        }
    finally:
        # Clean up deployment files after generating report
        manager.cleanup_deployment_files()


if __name__ == "__main__":
    # Prepare deployment
    results = prepare_railway_deployment("production")
    print(json.dumps(results, indent=2)) 