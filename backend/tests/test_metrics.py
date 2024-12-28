"""Tests for performance metrics functionality"""
import pytest
from datetime import datetime, timedelta
import time
from app.core.metrics import metrics
from app.core.metrics.performance_metrics import MetricPoint, MetricsTimer

def test_metrics_initialization():
    """Test metrics initialization"""
    assert metrics is not None
    assert metrics.retention_hours == 24

def test_record_and_get_metrics():
    """Test recording and retrieving metrics"""
    category = "test_metric"
    value = 42.0
    metadata = {"test_key": "test_value"}
    
    metrics.record_metric(category, value, metadata)
    results = metrics.get_metrics(category)
    
    assert len(results) == 1
    assert results[0].value == value
    assert results[0].metadata == metadata
    assert isinstance(results[0].timestamp, datetime)

def test_metrics_retention():
    """Test metrics retention period"""
    category = "retention_test"
    
    # Record old metric
    old_time = datetime.now() - timedelta(hours=25)
    metrics._metrics[category].append(
        MetricPoint(
            timestamp=old_time,
            value=1.0,
            metadata={}
        )
    )
    
    # Record new metric
    metrics.record_metric(category, 2.0)
    
    # Old metric should be cleaned up
    results = metrics.get_metrics(category)
    assert len(results) == 1
    assert results[0].value == 2.0

def test_average_calculation():
    """Test metric average calculation"""
    category = "avg_test"
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    for value in values:
        metrics.record_metric(category, value)
    
    avg = metrics.get_average(category)
    assert avg == 3.0

def test_metrics_timer():
    """Test metrics timer context manager"""
    category = "timer_test"
    sleep_time = 0.1
    
    with MetricsTimer(metrics, category):
        time.sleep(sleep_time)
    
    results = metrics.get_metrics(category)
    assert len(results) == 1
    assert results[0].value >= sleep_time

def test_time_range_filtering():
    """Test metric filtering by time range"""
    category = "time_range_test"
    
    # Record metrics at different times
    start_time = datetime.now() - timedelta(hours=2)
    mid_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now()
    
    metrics._metrics[category] = [
        MetricPoint(timestamp=start_time, value=1.0),
        MetricPoint(timestamp=mid_time, value=2.0),
        MetricPoint(timestamp=end_time, value=3.0)
    ]
    
    # Test filtering
    results = metrics.get_metrics(
        category,
        start_time=mid_time,
        end_time=end_time
    )
    
    assert len(results) == 2
    assert [r.value for r in results] == [2.0, 3.0]

def test_empty_metrics():
    """Test handling of empty metrics"""
    category = "empty_test"
    
    results = metrics.get_metrics(category)
    assert len(results) == 0
    
    avg = metrics.get_average(category)
    assert avg == 0.0

def test_metrics_cleanup():
    """Test automatic cleanup of old metrics"""
    category = "cleanup_test"
    
    # Add metrics with different timestamps
    now = datetime.now()
    old_metrics = [
        MetricPoint(
            timestamp=now - timedelta(hours=x),
            value=float(x)
        )
        for x in range(30)  # 30 hours of data
    ]
    
    # Add old metrics
    for metric in old_metrics:
        metrics.record_metric(category, metric.value, timestamp=metric.timestamp)
    
    # Record new metric to trigger cleanup
    metrics.record_metric(category, 0.0)
    metrics._cleanup_old_metrics()  # Force cleanup
    
    # Only metrics within retention period should remain
    results = metrics.get_metrics(category)
    assert len(results) == 25  # 24 hours + 1 new metric
