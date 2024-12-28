"""Batch processing module for parallel execution"""
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, List, Tuple, Optional
import multiprocessing
import logging
from functools import partial
import time
from datetime import datetime, timedelta
from app.core.metrics import metrics
from app.api.models import Location
from app.core.calculations.astronomical import AstronomicalCalculator
import threading
from collections import deque

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Enhanced batch processor with dynamic thread pool scaling"""
    
    def __init__(self, num_workers: Optional[int] = None, 
                 min_workers: Optional[int] = None,
                 max_workers: Optional[int] = None):
        """Initialize batch processor with dynamic scaling capabilities"""
        cpu_count = multiprocessing.cpu_count()
        self.min_workers = min_workers or max(1, cpu_count // 4)
        self.max_workers = max_workers or cpu_count * 2
        self.initial_workers = num_workers or cpu_count
        
        # Ensure constraints are met
        self.initial_workers = max(self.min_workers, 
                                 min(self.initial_workers, self.max_workers))
        
        self._executor = ThreadPoolExecutor(max_workers=self.initial_workers)
        self.calculator = AstronomicalCalculator()
        
        # Performance tracking
        self._active_tasks = 0
        self._task_times = deque(maxlen=100)
        self._lock = threading.Lock()
        self._last_scaling_time = time.time()
        self._scaling_cooldown = 5  # seconds
    
    def _track_task_completion(self, duration: float) -> None:
        """Track task completion time for scaling decisions"""
        with self._lock:
            self._task_times.append(duration)
            self._active_tasks -= 1
    
    def _should_scale(self) -> Tuple[bool, int]:
        """Determine if pool should be scaled and target size"""
        if time.time() - self._last_scaling_time < self._scaling_cooldown:
            return False, self._executor._max_workers
        
        with self._lock:
            if not self._task_times:
                return False, self._executor._max_workers
            
            avg_time = sum(self._task_times) / len(self._task_times)
            utilization = self._active_tasks / self._executor._max_workers
            
            if utilization > 0.8 and avg_time > 0.1:
                # High utilization and slow tasks - scale up
                target_size = min(self._executor._max_workers * 2, self.max_workers)
                return True, target_size
            elif utilization < 0.2 and avg_time < 0.05:
                # Low utilization and fast tasks - scale down
                target_size = max(self._executor._max_workers // 2, self.min_workers)
                return True, target_size
            
            return False, self._executor._max_workers
    
    def _scale_pool(self) -> None:
        """Scale the thread pool if needed"""
        should_scale, target_size = self._should_scale()
        if should_scale:
            new_executor = ThreadPoolExecutor(max_workers=target_size)
            old_executor = self._executor
            self._executor = new_executor
            self._last_scaling_time = time.time()
            
            # Gracefully shutdown old executor
            old_executor.shutdown(wait=False)
    
    def execute(self, func: Callable, args: Tuple = None, kwargs: dict = None) -> Future:
        """Execute a function asynchronously with performance tracking"""
        with self._lock:
            self._active_tasks += 1
        
        start_time = time.time()
        
        def wrapped_func(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                self._track_task_completion(duration)
                return result
            except Exception as e:
                self._track_task_completion(time.time() - start_time)
                raise e
        
        self._scale_pool()
        return self._executor.submit(wrapped_func, *(args or ()), **(kwargs or {}))
    
    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Map a function over a list of items in parallel"""
        return list(self._executor.map(func, items))
    
    def shutdown(self):
        """Shutdown the executor"""
        self._executor.shutdown(wait=True)
    
    def process_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        location: Location,
        calculation_func: Callable
    ) -> List[Any]:
        """Process calculations for a date range in parallel
        
        Args:
            start_date: Start date for calculations
            end_date: End date for calculations
            location: Location for calculations
            calculation_func: Function to calculate for each date
            
        Returns:
            List of calculation results
        """
        try:
            # Generate list of dates
            dates = []
            current_date = start_date
            while current_date <= end_date:
                dates.append(current_date)
                current_date += timedelta(days=1)
            
            # Process dates in parallel
            with metrics.timer(
                metrics.BATCH_PROCESSING_TIME,
                {"num_dates": len(dates)}
            ):
                # Create partial function with location
                func = partial(calculation_func, location=location)
                # Execute calculations in parallel and measure time
                start_time = time.perf_counter()
                results = self.map(func, dates)
                end_time = time.perf_counter()
                
                # Calculate and record parallel efficiency
                total_time = end_time - start_time
                avg_time_per_task = total_time / len(dates)
                theoretical_sequential_time = avg_time_per_task * len(dates)
                efficiency = theoretical_sequential_time / total_time
                
                metrics.record_metric(
                    metrics.PARALLEL_EFFICIENCY,
                    efficiency,
                    {
                        "num_dates": len(dates),
                        "total_time": total_time,
                        "avg_time_per_task": avg_time_per_task
                    }
                )
                
            return results
        except Exception as e:
            logger.error(f"Error in parallel processing: {str(e)}")
            raise
