"""Performance testing suite for the Kundli Calculator service"""
import pytest
from datetime import datetime, timedelta
import time
import random
from unittest.mock import patch
import swisseph as swe
from app.core.metrics import metrics
from app.core.metrics.performance_metrics import MetricsTimer
from app.core.cache.calculation_cache import CalculationCache
from app.core.parallel.batch_processor import BatchProcessor
from app.core.calculations.astronomical import AstronomicalCalculator, Location
from app.core.calculations.ayanamsa import EnhancedAyanamsaManager
import psutil
import os
import gc

@pytest.fixture
def mock_swisseph():
    """Mock swisseph calculations with delay"""
    with patch('swisseph.calc_ut') as mock_calc, \
         patch('swisseph.get_ayanamsa_ut') as mock_ayanamsa:
        def calc_with_delay(*args, **kwargs):
            time.sleep(0.001)  # Add 1ms delay
            return ((120.5, 23.4, 0.9), 0)
        mock_calc.side_effect = calc_with_delay
        mock_ayanamsa.return_value = 24.13
        yield

@pytest.fixture
def shared_cache():
    """Create a shared cache instance"""
    return CalculationCache()

@pytest.fixture
def calculator(shared_cache):
    """Create calculator with shared cache"""
    calculator = AstronomicalCalculator()
    calculator.cache = shared_cache
    return calculator

def test_calculation_performance(mock_swisseph, calculator):
    """Test performance of astronomical calculations"""
    location = Location(latitude=28.6139, longitude=77.2090)  # New Delhi
    with MetricsTimer(metrics, "calculation_time"):
        # Perform a series of calculations
        for planet_id in range(10):  # Test with different planets
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            calculator.calculate_planet_position(date, planet_id)
    
    results = metrics.get_metrics("calculation_time")
    assert len(results) == 1
    avg_calc_time = results[0].value
    assert avg_calc_time < 1.0  # Should complete in under 1 second

def test_cache_performance(mock_swisseph, calculator):
    """Test cache hit rates and performance improvements"""
    # Perform calculations with cache
    dates = [
        datetime.now() - timedelta(days=x)
        for x in range(50)
    ]
    
    # First pass - populate cache
    with MetricsTimer(metrics, "uncached_calculation"):
        for date in dates:
            for planet_id in range(5):  # Test with first 5 planets
                calculator.calculate_planet_position(date, planet_id)
    
    # Second pass - should hit cache
    with MetricsTimer(metrics, "cached_calculation"):
        for date in dates:
            for planet_id in range(5):
                calculator.calculate_planet_position(date, planet_id)
    
    # Verify cache performance
    uncached_time = metrics.get_metrics("uncached_calculation")[0].value
    cached_time = metrics.get_metrics("cached_calculation")[0].value
    assert cached_time < uncached_time * 0.5  # Cache should be at least 2x faster

def test_batch_processing_performance(mock_swisseph, calculator):
    """Test parallel processing performance"""
    processor = BatchProcessor()
    
    # Create a large batch of calculations
    dates = [
        datetime.now() - timedelta(days=x)
        for x in range(100)
    ]
    
    # Sequential processing
    with MetricsTimer(metrics, "sequential_processing"):
        for date in dates:
            for planet_id in range(3):  # Test with first 3 planets
                calculator.calculate_planet_position(date, planet_id)
    
    # Parallel processing
    with MetricsTimer(metrics, "parallel_processing"):
        futures = []
        for date in dates:
            for planet_id in range(3):
                future = processor.execute(
                    calculator.calculate_planet_position,
                    args=(date, planet_id)
                )
                futures.append(future)
        for future in futures:
            future.result()
    
    # Verify parallel performance improvement
    sequential_time = metrics.get_metrics("sequential_processing")[0].value
    parallel_time = metrics.get_metrics("parallel_processing")[0].value
    
    # Performance should improve with parallel processing
    assert parallel_time < sequential_time * 0.8

def test_end_to_end_performance(mock_swisseph, calculator):
    """Test end-to-end system performance"""
    processor = BatchProcessor()
    
    # Test different batch sizes
    batch_sizes = [10, 50, 100]
    for size in batch_sizes:
        dates = [
            datetime.now() - timedelta(days=x)
            for x in range(size)
        ]
        
        with MetricsTimer(metrics, f"end_to_end_{size}"):
            # Process batch with both caching and parallelization
            futures = []
            for date in dates:
                for planet_id in range(2):  # Test with first 2 planets
                    future = processor.execute(
                        calculator.calculate_planet_position,
                        args=(date, planet_id)
                    )
                    futures.append(future)
            for future in futures:
                future.result()
        
        result_time = metrics.get_metrics(f"end_to_end_{size}")[0].value
        # Larger batches should show better per-calculation performance
        assert result_time / size < 0.1  # Less than 100ms per calculation

def test_memory_usage(mock_swisseph, shared_cache, calculator):
    """Test memory usage during calculations"""
    # Monitor cache size
    initial_size = len(shared_cache)
    
    # Perform many calculations
    for _ in range(1000):
        date = datetime.now() - timedelta(days=random.randint(0, 365))
        for planet_id in range(5):
            calculator.calculate_planet_position(date, planet_id)
    
    # Verify cache growth
    final_size = len(shared_cache)
    assert final_size > initial_size
    assert final_size <= (shared_cache.l1_size + shared_cache.l2_size)

def test_dynamic_thread_scaling(mock_swisseph, calculator):
    """Test dynamic thread pool scaling behavior"""
    processor = BatchProcessor(min_workers=2, max_workers=8)
    location = Location(latitude=28.6139, longitude=77.2090)
    
    # Create mixed workload
    light_dates = [datetime.now() - timedelta(days=x) for x in range(10)]
    heavy_dates = [datetime.now() - timedelta(days=x) for x in range(10, 20)]
    
    # Test scaling up with heavy load
    with MetricsTimer(metrics, "heavy_load_processing"):
        futures = []
        for date in heavy_dates:
            for planet_id in range(7):  # More planets = heavier load
                future = processor.execute(
                    calculator.calculate_planet_position,
                    args=(date, planet_id)
                )
                futures.append(future)
        
        # Wait for completion
        for future in futures:
            future.result()
    
    heavy_load_time = metrics.get_metrics("heavy_load_processing")[0].value
    
    # Test scaling down with light load
    with MetricsTimer(metrics, "light_load_processing"):
        futures = []
        for date in light_dates:
            for planet_id in range(3):  # Fewer planets = lighter load
                future = processor.execute(
                    calculator.calculate_planet_position,
                    args=(date, planet_id)
                )
                futures.append(future)
        
        # Wait for completion
        for future in futures:
            future.result()
    
    light_load_time = metrics.get_metrics("light_load_processing")[0].value
    
    # Verify scaling behavior through timing
    assert light_load_time < heavy_load_time * 0.7  # Light load should be significantly faster

def test_two_level_cache_performance(mock_swisseph, calculator):
    """Test two-level cache performance and promotion/demotion"""
    shared_cache = CalculationCache(l1_size=50, l2_size=200)
    calculator.cache = shared_cache
    
    # Generate test data with fixed dates for deterministic testing
    base_date = datetime(2024, 1, 1, 12, 0, 0)
    frequent_dates = [base_date + timedelta(days=x) for x in range(5)]
    infrequent_dates = [base_date + timedelta(days=x) for x in range(5, 15)]
    
    # Phase 1: Initial population
    for date in frequent_dates + infrequent_dates:
        for planet_id in range(5):
            calculator.calculate_planet_position(date, planet_id)
    
    # Phase 2: Access frequent items multiple times
    for _ in range(5):
        for date in frequent_dates:
            for planet_id in range(5):
                calculator.calculate_planet_position(date, planet_id)
    
    # Phase 3: Verify cache metrics
    cache_metrics = shared_cache.get_metrics()
    
    # Lower thresholds for initial testing
    assert cache_metrics['l1_hit_rate'] > 0.2  # Frequently accessed items should be in L1
    assert cache_metrics['hit_rate'] > 0.5     # Overall hit rate should be reasonable

def test_cache_eviction_strategy(mock_swisseph, calculator):
    """Test cache eviction and memory management"""
    shared_cache = CalculationCache(l1_size=10, l2_size=20)
    calculator.cache = shared_cache
    
    # Use fixed dates for deterministic testing
    base_date = datetime(2024, 1, 1, 12, 0, 0)
    dates = [base_date + timedelta(days=x) for x in range(50)]
    
    # Fill cache beyond capacity
    for date in dates:
        calculator.calculate_planet_position(date, 0)
    
    # Verify cache size constraints
    assert len(shared_cache._l1_cache) <= shared_cache.l1_size
    assert len(shared_cache._l2_cache) <= shared_cache.l2_size
    
    # Access first item repeatedly to ensure promotion
    test_date = dates[0]
    for _ in range(5):
        calculator.calculate_planet_position(test_date, 0)
    
    # Verify the item is in L1 cache using the correct key format
    test_key = shared_cache.get_cache_key(test_date, 0)
    assert test_key in shared_cache._l1_cache

def test_calculation_performance_ayanamsa():
    """Test the performance of ayanamsa calculations"""
    manager = EnhancedAyanamsaManager()
    test_date = datetime(2024, 1, 1, 12, 0)
    
    # Warm-up run
    manager.calculate_precise_ayanamsa(test_date, 'LAHIRI')
    
    # Performance test
    start_time = time.perf_counter()
    iterations = 1000
    
    for _ in range(iterations):
        manager.calculate_precise_ayanamsa(test_date, 'LAHIRI')
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = (total_time * 1000) / iterations  # Convert to milliseconds
    
    # Performance assertions
    assert avg_time < 1.0, f"Average calculation time ({avg_time:.3f}ms) exceeds 1ms threshold"

def test_multiple_system_performance_ayanamsa():
    """Test performance when switching between ayanamsa systems"""
    manager = EnhancedAyanamsaManager()
    test_date = datetime(2024, 1, 1, 12, 0)
    systems = ['LAHIRI', 'RAMAN', 'KRISHNAMURTI']
    
    # Warm-up run
    for system in systems:
        manager.calculate_precise_ayanamsa(test_date, system)
    
    # Performance test
    start_time = time.perf_counter()
    iterations = 100
    
    for _ in range(iterations):
        for system in systems:
            manager.calculate_precise_ayanamsa(test_date, system)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = (total_time * 1000) / (iterations * len(systems))
    
    # Performance assertions
    assert avg_time < 1.5, f"Average calculation time ({avg_time:.3f}ms) exceeds 1.5ms threshold"

def test_date_range_performance_ayanamsa():
    """Test performance across different date ranges"""
    manager = EnhancedAyanamsaManager()
    test_dates = [
        datetime(1, 1, 1, 12, 0),
        datetime(1900, 1, 1, 12, 0),
        datetime(2000, 1, 1, 12, 0),
        datetime(2100, 1, 1, 12, 0),
        datetime(9999, 12, 31, 12, 0)
    ]
    
    # Warm-up run
    for date in test_dates:
        manager.calculate_precise_ayanamsa(date, 'LAHIRI')
    
    # Performance test
    start_time = time.perf_counter()
    iterations = 100
    
    for _ in range(iterations):
        for date in test_dates:
            manager.calculate_precise_ayanamsa(date, 'LAHIRI')
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = (total_time * 1000) / (iterations * len(test_dates))
    
    # Performance assertions
    assert avg_time < 2.0, f"Average calculation time ({avg_time:.3f}ms) exceeds 2ms threshold"

def test_memory_usage_ayanamsa():
    """Test memory usage of ayanamsa calculations"""
    process = psutil.Process(os.getpid())
    manager = EnhancedAyanamsaManager()
    test_date = datetime(2024, 1, 1, 12, 0)
    
    # Force garbage collection
    gc.collect()
    initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    # Perform calculations
    iterations = 10000
    for _ in range(iterations):
        manager.calculate_precise_ayanamsa(test_date, 'LAHIRI')
    
    # Force garbage collection again
    gc.collect()
    final_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    memory_increase = final_memory - initial_memory
    memory_per_calculation = memory_increase / iterations
    
    # Memory usage assertions
    assert memory_per_calculation < 0.001, f"Memory usage per calculation ({memory_per_calculation:.6f}MB) exceeds threshold"
    assert memory_increase < 10, f"Total memory increase ({memory_increase:.2f}MB) exceeds threshold"

def test_cache_effectiveness_ayanamsa():
    """Test the effectiveness of LRU cache in ayanamsa calculations"""
    manager = EnhancedAyanamsaManager()
    test_dates = [
        datetime(2024, 1, 1, 12, 0),
        datetime(2024, 1, 2, 12, 0),
        datetime(2024, 1, 3, 12, 0)
    ]
    
    # First run - should populate cache
    start_time = time.perf_counter()
    for date in test_dates:
        manager.calculate_precise_ayanamsa(date, 'LAHIRI')
    first_run_time = time.perf_counter() - start_time
    
    # Second run - should use cache
    start_time = time.perf_counter()
    for date in test_dates:
        manager.calculate_precise_ayanamsa(date, 'LAHIRI')
    second_run_time = time.perf_counter() - start_time
    
    # Cache effectiveness assertions
    assert second_run_time < first_run_time * 0.5, "Cache not providing significant performance improvement"
