"""
Performance metrics collection and monitoring module.
Implements metrics tracking for astronomical calculations and caching.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric measurement point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceMetrics:
    """Collects and manages performance metrics"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self._metrics = defaultdict(list)
        self._lock = Lock()
        
        # Metric categories
        self.CALCULATION_TIME = "calculation_time"
        self.CACHE_HIT_RATE = "cache_hit_rate"
        self.BATCH_PROCESSING_TIME = "batch_processing_time"
        self.PARALLEL_EFFICIENCY = "parallel_efficiency"
    
    def record_metric(
        self,
        category: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Record a new metric value"""
        with self._lock:
            if category not in self._metrics:
                self._metrics[category] = []
            
            self._metrics[category].append(
                MetricPoint(
                    timestamp=timestamp or datetime.now(),
                    value=value,
                    metadata=metadata or {}
                )
            )
            self._cleanup_old_metrics()
    
    def record_timing(self, name: str, duration: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a timing measurement"""
        self.record_metric(name, duration, metadata)
    
    def timer(self, category: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations"""
        return MetricsTimer(self, category, metadata)
    
    def get_metrics(
        self,
        category: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list[MetricPoint]:
        """Get metrics for a category within time range"""
        with self._lock:
            metrics = self._metrics[category]
            if not metrics:
                return []
            
            if start_time is None:
                start_time = datetime.now() - timedelta(hours=self.retention_hours)
            if end_time is None:
                end_time = datetime.now()
                
            return [
                m for m in metrics
                if start_time <= m.timestamp <= end_time
            ]
    
    def get_average(
        self,
        category: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> float:
        """Calculate average value for a metric category"""
        metrics = self.get_metrics(category, start_time, end_time)
        if not metrics:
            return 0.0
        return sum(m.value for m in metrics) / len(metrics)
    
    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        for category in list(self._metrics.keys()):
            self._metrics[category] = [
                m for m in self._metrics[category]
                if m.timestamp >= cutoff_time
            ]
            # Remove empty categories
            if not self._metrics[category]:
                del self._metrics[category]

class MetricsTimer:
    """Context manager for timing operations"""
    
    def __init__(
        self,
        metrics: PerformanceMetrics,
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.metrics = metrics
        self.category = category
        self.metadata = metadata or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        self.metrics.record_timing(self.category, duration, self.metadata)

# Global metrics instance
metrics = PerformanceMetrics()

"""
Performance Metrics Module
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""
