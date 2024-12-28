"""Monitoring system for ayanamsa calculations."""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager

@dataclass
class CalculationMetrics:
    """Metrics for a single calculation"""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    success: bool = False
    error_message: str = ""
    
    @property
    def duration(self) -> float:
        """Calculate duration in seconds"""
        if not self.end_time:
            return 0.0
        return self.end_time - self.start_time

class AyanamsaMonitor:
    """Monitor for Ayanamsa calculations with performance tracking"""
    
    def __init__(self):
        """Initialize the monitor"""
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, CalculationMetrics] = {}
        self.total_calculations = 0
        self.successful_calculations = 0
        self.failed_calculations = 0
        self.total_duration = 0.0
        self.last_calculation_time = None
        
    @contextmanager
    def track_calculation(self):
        """Context manager to track a calculation's performance"""
        calc_id = str(time.time())
        metrics = CalculationMetrics()
        self.metrics[calc_id] = metrics
        
        try:
            yield
            metrics.success = True
            self.successful_calculations += 1
            
        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            self.failed_calculations += 1
            raise
            
        finally:
            metrics.end_time = time.time()
            self.total_calculations += 1
            self.total_duration += metrics.duration
            self.last_calculation_time = datetime.now()
            
            # Log performance metrics
            self.logger.debug(
                f"Calculation completed in {metrics.duration:.3f}s "
                f"(success={metrics.success})"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics"""
        avg_duration = (
            self.total_duration / self.total_calculations 
            if self.total_calculations > 0 else 0.0
        )
        
        success_rate = (
            self.successful_calculations / self.total_calculations * 100
            if self.total_calculations > 0 else 0.0
        )
        
        return {
            'total_calculations': self.total_calculations,
            'successful_calculations': self.successful_calculations,
            'failed_calculations': self.failed_calculations,
            'success_rate': success_rate,
            'average_duration': avg_duration,
            'total_duration': self.total_duration,
            'last_calculation_time': self.last_calculation_time
        }
    
    def reset_metrics(self):
        """Reset all metrics to initial state"""
        self.metrics.clear()
        self.total_calculations = 0
        self.successful_calculations = 0
        self.failed_calculations = 0
        self.total_duration = 0.0
        self.last_calculation_time = None
