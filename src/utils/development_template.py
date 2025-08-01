"""
Development Template for ADCC Analysis Engine v0.6
This template ensures all code follows the development roadmap principles.
Use this template when creating new modules or functions.
"""

import logging
import structlog
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import traceback

# Import project-specific modules
from src.config.settings import LOG_LEVEL, LOGS_DIR
from src.config.constants import *

# Set up structured logging
logger = structlog.get_logger(__name__)

class DevelopmentTemplate:
    """
    Template class that enforces development standards.
    All new modules should inherit from this or follow its patterns.
    """
    
    def __init__(self, module_name: str):
        """
        Initialize the development template.
        
        Args:
            module_name: Name of the module for logging purposes
        """
        self.module_name = module_name
        self.logger = structlog.get_logger(f"{__name__}.{module_name}")
        
        # Log module initialization
        self.logger.info(
            "module_initialized",
            module_name=module_name,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_operation_start(self, operation: str, **kwargs) -> None:
        """
        Log the start of an operation for debugging.
        
        Args:
            operation: Name of the operation
            **kwargs: Additional context for logging
        """
        self.logger.info(
            "operation_started",
            operation=operation,
            module=self.module_name,
            **kwargs
        )
    
    def log_operation_success(self, operation: str, **kwargs) -> None:
        """
        Log successful completion of an operation.
        
        Args:
            operation: Name of the operation
            **kwargs: Additional context for logging
        """
        self.logger.info(
            "operation_completed",
            operation=operation,
            module=self.module_name,
            **kwargs
        )
    
    def log_operation_error(self, operation: str, error: Exception, **kwargs) -> None:
        """
        Log errors during operations for debugging.
        
        Args:
            operation: Name of the operation
            error: The exception that occurred
            **kwargs: Additional context for logging
        """
        self.logger.error(
            "operation_failed",
            operation=operation,
            module=self.module_name,
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=traceback.format_exc(),
            **kwargs
        )
    
    def validate_input(self, data: Any, validation_type: str) -> bool:
        """
        Validate input data and log validation results.
        
        Args:
            data: Data to validate
            validation_type: Type of validation being performed
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Add specific validation logic here based on validation_type
            self.logger.debug(
                "input_validation",
                validation_type=validation_type,
                data_type=type(data).__name__,
                data_sample=str(data)[:100] if data else None
            )
            return True
        except Exception as e:
            self.log_operation_error("input_validation", e, validation_type=validation_type)
            return False
    
    def handle_file_operation(self, file_path: Path, operation: str, data: Any = None) -> bool:
        """
        Handle file operations with comprehensive logging and error handling.
        
        Args:
            file_path: Path to the file
            operation: Type of operation (read, write, delete, etc.)
            data: Data to write (for write operations)
            
        Returns:
            True if operation succeeds, False otherwise
        """
        try:
            self.log_operation_start(f"file_{operation}", file_path=str(file_path))
            
            if operation == "read":
                # Add read logic here
                pass
            elif operation == "write":
                # Add write logic here
                pass
            elif operation == "delete":
                # Add delete logic here
                pass
            
            self.log_operation_success(f"file_{operation}", file_path=str(file_path))
            return True
            
        except Exception as e:
            self.log_operation_error(f"file_{operation}", e, file_path=str(file_path))
            return False

def create_module_logger(module_name: str) -> structlog.BoundLogger:
    """
    Create a structured logger for a module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Configured structured logger
    """
    return structlog.get_logger(f"adcc_engine.{module_name}")

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present, False otherwise
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        logger.error(
            "missing_required_fields",
            missing_fields=missing_fields,
            available_fields=list(data.keys())
        )
        return False
    
    return True

def safe_file_operation(operation_func, *args, **kwargs) -> Any:
    """
    Safely execute file operations with error handling and logging.
    
    Args:
        operation_func: Function to execute
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the operation or None if it fails
    """
    try:
        logger.debug(
            "file_operation_start",
            operation=operation_func.__name__,
            args=args,
            kwargs=kwargs
        )
        
        result = operation_func(*args, **kwargs)
        
        logger.debug(
            "file_operation_success",
            operation=operation_func.__name__,
            result_type=type(result).__name__
        )
        
        return result
        
    except FileNotFoundError as e:
        logger.error(
            "file_not_found",
            operation=operation_func.__name__,
            error=str(e),
            file_path=args[0] if args else None
        )
        return None
        
    except PermissionError as e:
        logger.error(
            "permission_error",
            operation=operation_func.__name__,
            error=str(e),
            file_path=args[0] if args else None
        )
        return None
        
    except Exception as e:
        logger.error(
            "file_operation_error",
            operation=operation_func.__name__,
            error_type=type(e).__name__,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return None

def performance_monitor(func):
    """
    Decorator to monitor function performance.
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance monitoring
    """
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                "function_performance",
                function_name=func.__name__,
                execution_time_seconds=execution_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.error(
                "function_performance",
                function_name=func.__name__,
                execution_time_seconds=execution_time,
                success=False,
                error=str(e)
            )
            
            raise
    
    return wrapper

# Example usage of the template
class ExampleModule(DevelopmentTemplate):
    """
    Example module showing how to use the development template.
    """
    
    def __init__(self):
        super().__init__("example_module")
    
    @performance_monitor
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Example data processing function with full logging and error handling.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
            
        Raises:
            ValueError: If data is invalid
        """
        try:
            self.log_operation_start("process_data", data_size=len(data))
            
            # Validate input
            if not self.validate_input(data, "data_processing"):
                raise ValueError("Invalid input data")
            
            # Process data (example)
            processed_data = {
                "processed": True,
                "timestamp": datetime.utcnow().isoformat(),
                "original_data": data
            }
            
            self.log_operation_success("process_data", result_size=len(processed_data))
            
            return processed_data
            
        except Exception as e:
            self.log_operation_error("process_data", e, data_size=len(data))
            raise

# Development checklist reminder
DEVELOPMENT_CHECKLIST = """
Before committing any code, ensure:

1. ✅ All functions have comprehensive docstrings
2. ✅ All functions have type hints
3. ✅ All operations are logged for debugging
4. ✅ All errors are properly handled and logged
5. ✅ Unit tests are written and passing
6. ✅ Code follows PEP 8 standards
7. ✅ Pre-commit hooks pass
8. ✅ Integration with previous phases works
9. ✅ Performance meets requirements
10. ✅ Documentation is updated

Remember: Test early, test often, log everything!
""" 