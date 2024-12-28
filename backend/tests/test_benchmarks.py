"""Test suite for ayanamsa benchmarking system."""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.core.benchmarks.ayanamsa_benchmark import AyanamsaBenchmark, BenchmarkResult

@pytest.fixture
def mock_swe():
    with patch('app.core.calculations.ayanamsa.swe') as mock_swe:
        # Mock all required swe functions
        mock_swe.SIDM_LAHIRI = 1
        mock_swe.SIDM_RAMAN = 2
        mock_swe.SIDM_KRISHNAMURTI = 3
        mock_swe.SIDM_YUKTESHWAR = 4
        mock_swe.set_sid_mode = MagicMock()
        mock_swe.get_ayanamsa_ut = MagicMock(return_value=23.5)
        mock_swe.julday = MagicMock(return_value=2451545.0)
        mock_swe.calc_ut = MagicMock(return_value=[(0, 0, 0), 0])
        yield mock_swe

@pytest.fixture
def ayanamsa_benchmark(mock_swe):
    return AyanamsaBenchmark()

def test_benchmark_initialization(ayanamsa_benchmark):
    """Test benchmark system initialization."""
    assert isinstance(ayanamsa_benchmark, AyanamsaBenchmark)
    assert len(ayanamsa_benchmark._results) == 0

def test_benchmark_execution(ayanamsa_benchmark, mock_swe):
    """Test benchmark execution with small iteration count."""
    result = ayanamsa_benchmark.run_benchmark(iterations=2)
    assert isinstance(result, BenchmarkResult)
    assert result.total_calculations > 0
    assert result.avg_execution_time > 0
    assert result.peak_memory_mb >= 0
    assert 0 <= result.error_rate <= 1
    assert 0 <= result.cache_hit_ratio <= 1

def test_benchmark_metrics_validity(ayanamsa_benchmark, mock_swe):
    """Test validity of benchmark metrics."""
    result = ayanamsa_benchmark.run_benchmark(iterations=2)
    assert result.avg_execution_time >= 0
    assert result.median_execution_time >= 0
    assert result.std_dev >= 0

def test_historical_trends(ayanamsa_benchmark, mock_swe):
    """Test historical trend analysis."""
    # Run multiple benchmarks
    for _ in range(2):
        ayanamsa_benchmark.run_benchmark(iterations=2)
    
    trends = ayanamsa_benchmark.get_historical_trends()
    assert len(trends['execution_time_trend']) == 2
    assert len(trends['memory_usage_trend']) == 2
    assert len(trends['error_rate_trend']) == 2
    assert len(trends['cache_efficiency_trend']) == 2
    assert len(trends['timestamps']) == 2

def test_benchmark_error_handling(ayanamsa_benchmark):
    """Test benchmark error handling with invalid inputs."""
    with pytest.raises(Exception):
        ayanamsa_benchmark.run_benchmark(iterations=0)

def test_performance_thresholds(ayanamsa_benchmark, mock_swe):
    """Test performance threshold monitoring."""
    result = ayanamsa_benchmark.run_benchmark(iterations=2)
    
    # Basic performance assertions
    assert result.avg_execution_time < 1000  # Less than 1 second
    assert result.peak_memory_mb < 1000  # Less than 1GB
    assert result.error_rate < 0.1  # Less than 10% errors
