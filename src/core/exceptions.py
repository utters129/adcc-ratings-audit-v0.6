"""
ADCC Analysis Engine v0.6 - Custom Exceptions
Custom exception classes for the application.
"""


class ADCCException(Exception):
    """Base exception for ADCC Analysis Engine."""
    pass


class DataValidationError(ADCCException):
    """Raised when data validation fails."""
    pass


class FileProcessingError(ADCCException):
    """Raised when file processing fails."""
    pass


class GlickoCalculationError(ADCCException):
    """Raised when Glicko calculations fail."""
    pass


class AuthenticationError(ADCCException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(ADCCException):
    """Raised when authorization fails."""
    pass


class SmoothcompAPIError(ADCCException):
    """Raised when Smoothcomp API calls fail."""
    pass


class DatabaseError(ADCCException):
    """Raised when database operations fail."""
    pass


class ConfigurationError(ADCCException):
    """Raised when configuration is invalid."""
    pass


class StateManagementError(ADCCException):
    """Raised when state management operations fail."""
    pass


class WebhookError(ADCCException):
    """Raised when webhook operations fail."""
    pass 