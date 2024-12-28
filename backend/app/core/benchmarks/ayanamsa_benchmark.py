"""Benchmarking system for ayanamsa calculations."""
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from statistics import mean, median, stdev
from app.core.calculations.ayanamsa import EnhancedAyanamsaManager

@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    avg_execution_time: float
    median_execution_time: float
    std_dev: float
    peak_memory_mb: float
    total_calculations: int
    cache_hit_ratio: float
    error_rate: float
    timestamp: datetime

class AyanamsaBenchmark:
    """Benchmark suite for ayanamsa calculations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.manager = EnhancedAyanamsaManager()
        self._results: List[BenchmarkResult] = []
    
    def run_benchmark(self, iterations: int = 1000) -> BenchmarkResult:
        """Run a comprehensive benchmark of the ayanamsa calculation system."""
        execution_times = []
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        errors = 0
        
        # Generate test dates spanning different eras
        test_dates = [
            datetime(1, 1, 1),  # Ancient
            datetime(500, 6, 15),  # Medieval
            datetime(1000, 12, 31),  # Middle Ages
            datetime(1500, 3, 21),  # Renaissance
            datetime(1900, 1, 1),  # Modern
            datetime(2000, 1, 1),  # Contemporary
            datetime(2024, 12, 26),  # Current
            datetime(3000, 12, 31),  # Future
        ]
        
        # Test different ayanamsa systems
        systems = ['LAHIRI', 'RAMAN', 'KRISHNAMURTI', 'YUKTESHWAR']
        
        self.logger.info(f"Starting benchmark with {iterations} iterations...")
        
        try:
            for _ in range(iterations):
                for date in test_dates:
                    for system in systems:
                        try:
                            start_time = time.perf_counter()
                            self.manager.calculate_precise_ayanamsa(
                                date=date,
                                system=system,
                                apply_nutation=True
                            )
                            execution_time = (time.perf_counter() - start_time) * 1000
                            execution_times.append(execution_time)
                        except Exception as e:
                            errors += 1
                            self.logger.error(f"Benchmark error: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Benchmark suite error: {str(e)}")
            raise
        
        # Calculate metrics
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_used = peak_memory - start_memory
        
        # Get monitoring metrics
        monitoring_metrics = self.manager.get_monitoring_metrics()
        
        result = BenchmarkResult(
            avg_execution_time=mean(execution_times),
            median_execution_time=median(execution_times),
            std_dev=stdev(execution_times) if len(execution_times) > 1 else 0,
            peak_memory_mb=memory_used,
            total_calculations=len(execution_times),
            cache_hit_ratio=monitoring_metrics['cache_hit_ratio'],
            error_rate=errors / max(1, len(execution_times)),
            timestamp=datetime.now()
        )
        
        self._results.append(result)
        self._log_benchmark_results(result)
        
        return result
    
    def _log_benchmark_results(self, result: BenchmarkResult) -> None:
        """Log benchmark results with analysis."""
        self.logger.info("=== Ayanamsa Calculation Benchmark Results ===")
        self.logger.info(f"Average Execution Time: {result.avg_execution_time:.3f}ms")
        self.logger.info(f"Median Execution Time: {result.median_execution_time:.3f}ms")
        self.logger.info(f"Standard Deviation: {result.std_dev:.3f}ms")
        self.logger.info(f"Peak Memory Usage: {result.peak_memory_mb:.2f}MB")
        self.logger.info(f"Total Calculations: {result.total_calculations}")
        self.logger.info(f"Cache Hit Ratio: {result.cache_hit_ratio:.2%}")
        self.logger.info(f"Error Rate: {result.error_rate:.2%}")
        
        # Performance analysis
        if result.avg_execution_time > 5.0:
            self.logger.warning("High average execution time detected")
        if result.error_rate > 0.01:
            self.logger.warning("High error rate detected")
        if result.peak_memory_mb > 100:
            self.logger.warning("High memory usage detected")
    
    def get_historical_trends(self) -> Dict[str, Any]:
        """Analyze historical benchmark trends."""
        if not self._results:
            return {}
        
        return {
            'execution_time_trend': [r.avg_execution_time for r in self._results],
            'memory_usage_trend': [r.peak_memory_mb for r in self._results],
            'error_rate_trend': [r.error_rate for r in self._results],
            'cache_efficiency_trend': [r.cache_hit_ratio for r in self._results],
            'timestamps': [r.timestamp for r in self._results]
        }
