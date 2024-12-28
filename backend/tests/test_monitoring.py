"""Test suite for ayanamsa monitoring system."""
import pytest
from datetime import datetime
from app.core.monitoring.ayanamsa_monitor import AyanamsaMonitor, CalculationMetrics

@pytest.fixture
def monitor():
    return AyanamsaMonitor()

def test_monitor_initialization(monitor):
    """Test monitor initialization."""
    metrics = monitor.get_metrics()
    assert metrics['total_calculations'] == 0
    assert metrics['cache_hit_ratio'] == 0
    assert metrics['avg_execution_time_ms'] == 0
    assert isinstance(metrics['system_usage'], dict)
    assert metrics['error_rate'] == 0

def test_metrics_update(monitor):
    """Test metrics update functionality."""
    # Simulate a calculation
    monitor._update_metrics(
        CalculationMetrics(
            execution_time=1.5,
            system_used='LAHIRI',
            date_calculated=datetime.now(),
            cache_hit=False
        )
    )
    
    metrics = monitor.get_metrics()
    assert metrics['total_calculations'] == 1
    assert metrics['avg_execution_time_ms'] == 1.5
    assert metrics['system_usage']['LAHIRI'] == 1

def test_cache_hit_tracking(monitor):
    """Test cache hit ratio calculation."""
    # Simulate calculations with cache hits
    for _ in range(3):
        monitor._update_metrics(
            CalculationMetrics(
                execution_time=1.0,
                system_used='LAHIRI',
                date_calculated=datetime.now(),
                cache_hit=True
            )
        )
    
    # Simulate calculation without cache hit
    monitor._update_metrics(
        CalculationMetrics(
            execution_time=2.0,
            system_used='LAHIRI',
            date_calculated=datetime.now(),
            cache_hit=False
        )
    )
    
    metrics = monitor.get_metrics()
    assert metrics['cache_hit_ratio'] == 0.75  # 3 out of 4 were cache hits

def test_system_usage_tracking(monitor):
    """Test system usage tracking."""
    systems = ['LAHIRI', 'RAMAN', 'LAHIRI', 'KRISHNAMURTI']
    
    for system in systems:
        monitor._update_metrics(
            CalculationMetrics(
                execution_time=1.0,
                system_used=system,
                date_calculated=datetime.now()
            )
        )
    
    metrics = monitor.get_metrics()
    assert metrics['system_usage']['LAHIRI'] == 2
    assert metrics['system_usage']['RAMAN'] == 1
    assert metrics['system_usage']['KRISHNAMURTI'] == 1

def test_error_rate_calculation(monitor):
    """Test error rate calculation."""
    # Simulate successful calculations
    for _ in range(9):
        monitor._update_metrics(
            CalculationMetrics(
                execution_time=1.0,
                system_used='LAHIRI',
                date_calculated=datetime.now()
            )
        )
    
    # Simulate error
    monitor._metrics['errors'] += 1
    monitor._metrics['total_calculations'] += 1  # Add error to total calculations
    
    metrics = monitor.get_metrics()
    assert metrics['error_rate'] == 0.1  # 1 error out of 10 calculations

def test_average_execution_time(monitor):
    """Test average execution time calculation."""
    times = [1.0, 2.0, 3.0]
    
    for time_value in times:
        monitor._update_metrics(
            CalculationMetrics(
                execution_time=time_value,
                system_used='LAHIRI',
                date_calculated=datetime.now()
            )
        )
    
    metrics = monitor.get_metrics()
    assert metrics['avg_execution_time_ms'] == 2.0  # (1 + 2 + 3) / 3
