from typing import Dict, List, Optional
import time
import psutil
import asyncio
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    cpu_usage: float
    memory_usage: float
    execution_time: float
    accuracy: float
    throughput: float

class MetricsFramework:
    def __init__(self):
        self.collectors = {}
        self.analyzers = {}
        self.thresholds = self._initialize_thresholds()
        
    async def measure_execution(
        self,
        operation_name: str,
        execution_func,
        *args,
        **kwargs
    ) -> Dict:
        """Measure execution metrics for an operation"""
        
        start_metrics = self._capture_system_metrics()
        start_time = time.monotonic()
        
        try:
            result = await execution_func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            raise
        finally:
            end_time = time.monotonic()
            end_metrics = self._capture_system_metrics()
            
            execution_metrics = self._calculate_execution_metrics(
                start_time,
                end_time,
                start_metrics,
                end_metrics,
                success
            )
            
            await self._store_metrics(operation_name, execution_metrics)
            await self._analyze_metrics(operation_name, execution_metrics)
            
        return {
            'result': result,
            'metrics': execution_metrics
        }
        
    def _capture_system_metrics(self) -> Dict:
        """Capture current system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters(),
            'network_io': psutil.net_io_counters()
        }
        
    async def _analyze_metrics(self, operation_name: str, metrics: Dict):
        """Analyze metrics and trigger optimizations if needed"""
        analyzer = self.analyzers.get(operation_name)
        if analyzer:
            analysis = await analyzer.analyze(metrics)
            
            if analysis.requires_optimization:
                await self._trigger_optimization(
                    operation_name,
                    analysis
                )
