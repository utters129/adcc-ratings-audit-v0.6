"""
Performance Monitor for ADCC Analysis Engine

This module provides comprehensive performance monitoring and analysis
for the entire system, including memory usage, execution times, and bottlenecks.
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class PerformanceMetric:
    """Data class for storing performance metrics."""
    timestamp: datetime
    component: str
    operation: str
    duration: float
    memory_usage: float
    cpu_usage: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for tracking
    system performance across all components.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics: deque = deque(maxlen=max_history)
        self.component_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.active_monitors: Dict[str, Any] = {}
        self.monitoring_enabled = True
        self._lock = threading.Lock()
        
        # Initialize baseline metrics
        self._baseline_memory = psutil.virtual_memory().used
        self._baseline_cpu = psutil.cpu_percent()
        
        logger.info("Performance monitor initialized", 
                   max_history=max_history,
                   baseline_memory=self._baseline_memory,
                   baseline_cpu=self._baseline_cpu)
    
    def start_monitoring(self, component: str, operation: str) -> str:
        """
        Start monitoring a specific operation.
        
        Args:
            component: Component name (e.g., 'data_acquisition', 'analytics')
            operation: Operation name (e.g., 'download_files', 'calculate_ratings')
            
        Returns:
            Monitor ID for stopping the monitor
        """
        if not self.monitoring_enabled:
            return ""
        
        monitor_id = f"{component}_{operation}_{int(time.time())}"
        
        with self._lock:
            self.active_monitors[monitor_id] = {
                "component": component,
                "operation": operation,
                "start_time": time.time(),
                "start_memory": psutil.virtual_memory().used,
                "start_cpu": psutil.cpu_percent()
            }
        
        logger.debug("Started performance monitoring", 
                    monitor_id=monitor_id,
                    component=component,
                    operation=operation)
        
        return monitor_id
    
    def stop_monitoring(self, monitor_id: str, success: bool = True, 
                       error_message: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[PerformanceMetric]:
        """
        Stop monitoring and record the performance metric.
        
        Args:
            monitor_id: Monitor ID returned from start_monitoring
            success: Whether the operation was successful
            error_message: Error message if operation failed
            metadata: Additional metadata about the operation
            
        Returns:
            PerformanceMetric object or None if monitor not found
        """
        if not self.monitoring_enabled or not monitor_id:
            return None
        
        with self._lock:
            if monitor_id not in self.active_monitors:
                logger.warning("Monitor not found", monitor_id=monitor_id)
                return None
            
            monitor_data = self.active_monitors.pop(monitor_id)
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        end_cpu = psutil.cpu_percent()
        
        duration = end_time - monitor_data["start_time"]
        memory_usage = end_memory - monitor_data["start_memory"]
        cpu_usage = (end_cpu + monitor_data["start_cpu"]) / 2
        
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            component=monitor_data["component"],
            operation=monitor_data["operation"],
            duration=duration,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        self._record_metric(metric)
        
        logger.debug("Stopped performance monitoring", 
                    monitor_id=monitor_id,
                    duration=duration,
                    memory_usage=memory_usage,
                    success=success)
        
        return metric
    
    def _record_metric(self, metric: PerformanceMetric):
        """Record a performance metric and update statistics."""
        with self._lock:
            self.metrics.append(metric)
            
            # Update component statistics
            component = metric.component
            if component not in self.component_stats:
                self.component_stats[component] = {
                    "total_operations": 0,
                    "successful_operations": 0,
                    "failed_operations": 0,
                    "total_duration": 0.0,
                    "total_memory": 0.0,
                    "total_cpu": 0.0,
                    "min_duration": float('inf'),
                    "max_duration": 0.0,
                    "avg_duration": 0.0,
                    "operations": defaultdict(int)
                }
            
            stats = self.component_stats[component]
            stats["total_operations"] += 1
            stats["total_duration"] += metric.duration
            stats["total_memory"] += metric.memory_usage
            stats["total_cpu"] += metric.cpu_usage
            stats["operations"][metric.operation] += 1
            
            if metric.success:
                stats["successful_operations"] += 1
            else:
                stats["failed_operations"] += 1
            
            # Update min/max duration
            if metric.duration < stats["min_duration"]:
                stats["min_duration"] = metric.duration
            if metric.duration > stats["max_duration"]:
                stats["max_duration"] = metric.duration
            
            # Update average duration
            stats["avg_duration"] = stats["total_duration"] / stats["total_operations"]
    
    def get_component_stats(self, component: str) -> Dict[str, Any]:
        """
        Get performance statistics for a specific component.
        
        Args:
            component: Component name
            
        Returns:
            Dictionary containing performance statistics
        """
        with self._lock:
            if component not in self.component_stats:
                return {}
            
            stats = self.component_stats[component].copy()
            
            # Calculate success rate
            total_ops = stats["total_operations"]
            if total_ops > 0:
                stats["success_rate"] = stats["successful_operations"] / total_ops
                stats["failure_rate"] = stats["failed_operations"] / total_ops
            else:
                stats["success_rate"] = 0.0
                stats["failure_rate"] = 0.0
            
            return stats
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """
        Get overall performance statistics across all components.
        
        Returns:
            Dictionary containing overall performance statistics
        """
        with self._lock:
            total_operations = sum(stats["total_operations"] for stats in self.component_stats.values())
            total_duration = sum(stats["total_duration"] for stats in self.component_stats.values())
            total_memory = sum(stats["total_memory"] for stats in self.component_stats.values())
            total_cpu = sum(stats["total_cpu"] for stats in self.component_stats.values())
            
            successful_operations = sum(stats["successful_operations"] for stats in self.component_stats.values())
            failed_operations = sum(stats["failed_operations"] for stats in self.component_stats.values())
            
            return {
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "total_duration": total_duration,
                "total_memory_usage": total_memory,
                "total_cpu_usage": total_cpu,
                "success_rate": successful_operations / total_operations if total_operations > 0 else 0.0,
                "failure_rate": failed_operations / total_operations if total_operations > 0 else 0.0,
                "avg_duration": total_duration / total_operations if total_operations > 0 else 0.0,
                "component_count": len(self.component_stats),
                "monitoring_enabled": self.monitoring_enabled,
                "active_monitors": len(self.active_monitors)
            }
    
    def get_recent_metrics(self, minutes: int = 60) -> List[PerformanceMetric]:
        """
        Get performance metrics from the last N minutes.
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List of recent performance metrics
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            recent_metrics = [
                metric for metric in self.metrics
                if metric.timestamp >= cutoff_time
            ]
        
        return recent_metrics
    
    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest operations across all components.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of slowest operations with details
        """
        with self._lock:
            all_metrics = list(self.metrics)
        
        # Sort by duration (descending)
        sorted_metrics = sorted(all_metrics, key=lambda x: x.duration, reverse=True)
        
        slowest_operations = []
        for metric in sorted_metrics[:limit]:
            slowest_operations.append({
                "component": metric.component,
                "operation": metric.operation,
                "duration": metric.duration,
                "timestamp": metric.timestamp.isoformat(),
                "success": metric.success,
                "memory_usage": metric.memory_usage,
                "cpu_usage": metric.cpu_usage
            })
        
        return slowest_operations
    
    def get_memory_usage_trend(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Get memory usage trend over time.
        
        Args:
            minutes: Number of minutes to analyze
            
        Returns:
            List of memory usage data points
        """
        recent_metrics = self.get_recent_metrics(minutes)
        
        # Group by minute and calculate average memory usage
        memory_trend = defaultdict(list)
        for metric in recent_metrics:
            minute_key = metric.timestamp.replace(second=0, microsecond=0)
            memory_trend[minute_key].append(metric.memory_usage)
        
        trend_data = []
        for timestamp, memory_values in sorted(memory_trend.items()):
            trend_data.append({
                "timestamp": timestamp.isoformat(),
                "avg_memory_usage": sum(memory_values) / len(memory_values),
                "max_memory_usage": max(memory_values),
                "min_memory_usage": min(memory_values),
                "operation_count": len(memory_values)
            })
        
        return trend_data
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """
        Generate performance alerts based on thresholds.
        
        Returns:
            List of performance alerts
        """
        alerts = []
        
        # Check for slow operations (>30 seconds)
        slow_operations = [m for m in self.metrics if m.duration > 30]
        if slow_operations:
            alerts.append({
                "type": "slow_operation",
                "severity": "warning",
                "message": f"Found {len(slow_operations)} operations taking longer than 30 seconds",
                "details": [f"{m.component}.{m.operation}: {m.duration:.2f}s" for m in slow_operations[-5:]]
            })
        
        # Check for high memory usage (>500MB)
        high_memory_ops = [m for m in self.metrics if m.memory_usage > 500 * 1024 * 1024]  # 500MB
        if high_memory_ops:
            alerts.append({
                "type": "high_memory_usage",
                "severity": "warning",
                "message": f"Found {len(high_memory_ops)} operations using more than 500MB",
                "details": [f"{m.component}.{m.operation}: {m.memory_usage / (1024*1024):.2f}MB" for m in high_memory_ops[-5:]]
            })
        
        # Check for high failure rate (>10%)
        overall_stats = self.get_overall_stats()
        if overall_stats.get("failure_rate", 0) > 0.1:
            alerts.append({
                "type": "high_failure_rate",
                "severity": "error",
                "message": f"High failure rate detected: {overall_stats['failure_rate']:.2%}",
                "details": [f"Total operations: {overall_stats['total_operations']}, Failed: {overall_stats['failed_operations']}"]
            })
        
        # Check for active monitors (potential hanging operations)
        if len(self.active_monitors) > 0:
            alerts.append({
                "type": "active_monitors",
                "severity": "info",
                "message": f"Found {len(self.active_monitors)} active performance monitors",
                "details": list(self.active_monitors.keys())
            })
        
        return alerts
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dictionary containing performance report
        """
        overall_stats = self.get_overall_stats()
        alerts = self.get_performance_alerts()
        slowest_ops = self.get_slowest_operations(5)
        memory_trend = self.get_memory_usage_trend(60)
        
        # Component breakdown
        component_breakdown = {}
        for component in self.component_stats.keys():
            component_breakdown[component] = self.get_component_stats(component)
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "overall_stats": overall_stats,
            "component_breakdown": component_breakdown,
            "alerts": alerts,
            "slowest_operations": slowest_ops,
            "memory_trend": memory_trend,
            "recommendations": self._generate_performance_recommendations(overall_stats, alerts)
        }
    
    def _generate_performance_recommendations(self, stats: Dict[str, Any], 
                                            alerts: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations based on statistics and alerts."""
        recommendations = []
        
        # Check overall performance
        if stats.get("avg_duration", 0) > 10:
            recommendations.append("Consider optimizing slow operations to improve average response time")
        
        if stats.get("failure_rate", 0) > 0.05:
            recommendations.append("High failure rate detected - investigate and fix failing operations")
        
        # Check memory usage
        if stats.get("total_memory_usage", 0) > 1024 * 1024 * 1024:  # 1GB
            recommendations.append("High memory usage detected - consider implementing memory optimization")
        
        # Check for specific alerts
        for alert in alerts:
            if alert["type"] == "slow_operation":
                recommendations.append("Optimize slow operations to improve user experience")
            elif alert["type"] == "high_memory_usage":
                recommendations.append("Implement memory cleanup and optimization strategies")
        
        if not recommendations:
            recommendations.append("Performance is within acceptable ranges")
        
        return recommendations
    
    def reset_stats(self):
        """Reset all performance statistics."""
        with self._lock:
            self.metrics.clear()
            self.component_stats.clear()
            self.active_monitors.clear()
        
        logger.info("Performance statistics reset")
    
    def enable_monitoring(self):
        """Enable performance monitoring."""
        self.monitoring_enabled = True
        logger.info("Performance monitoring enabled")
    
    def disable_monitoring(self):
        """Disable performance monitoring."""
        self.monitoring_enabled = False
        logger.info("Performance monitoring disabled")
    
    def cleanup(self):
        """Clean up resources and stop all active monitors."""
        with self._lock:
            self.active_monitors.clear()
        
        logger.info("Performance monitor cleanup completed")


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def monitor_performance(component: str, operation: str):
    """
    Decorator for monitoring function performance.
    
    Args:
        component: Component name
        operation: Operation name
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            monitor_id = monitor.start_monitoring(component, operation)
            
            try:
                result = func(*args, **kwargs)
                monitor.stop_monitoring(monitor_id, success=True)
                return result
            except Exception as e:
                monitor.stop_monitoring(monitor_id, success=False, error_message=str(e))
                raise
        
        return wrapper
    return decorator


def monitor_async_performance(component: str, operation: str):
    """
    Decorator for monitoring async function performance.
    
    Args:
        component: Component name
        operation: Operation name
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            monitor_id = monitor.start_monitoring(component, operation)
            
            try:
                result = await func(*args, **kwargs)
                monitor.stop_monitoring(monitor_id, success=True)
                return result
            except Exception as e:
                monitor.stop_monitoring(monitor_id, success=False, error_message=str(e))
                raise
        
        return wrapper
    return decorator 