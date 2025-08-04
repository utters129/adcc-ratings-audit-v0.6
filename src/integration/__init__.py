"""
Integration Package for ADCC Analysis Engine

This package contains components for system integration, performance monitoring,
and deployment preparation for Phase 8 of the ADCC Analysis Engine.
"""

from .system_integrator import SystemIntegrator, run_integration_test
from .performance_monitor import (
    PerformanceMonitor, PerformanceMetric, 
    get_performance_monitor, monitor_performance, monitor_async_performance
)
from .deployment_manager import DeploymentManager, prepare_railway_deployment

__all__ = [
    # System Integration
    'SystemIntegrator',
    'run_integration_test',
    
    # Performance Monitoring
    'PerformanceMonitor',
    'PerformanceMetric',
    'get_performance_monitor',
    'monitor_performance',
    'monitor_async_performance',
    
    # Deployment Management
    'DeploymentManager',
    'prepare_railway_deployment'
]

__version__ = "0.6.0-alpha.8"
__author__ = "ADCC Analysis Engine Team"
__description__ = "Integration & Testing components for ADCC Analysis Engine" 