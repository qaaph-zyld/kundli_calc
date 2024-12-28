"""Tests for the calculation caching system"""
import pytest
from datetime import datetime
from app.core.cache import calculation_cache
from app.core.calculations.astronomical import AstronomicalCalculator
from app.api.models import Location

@pytest.fixture
def calculator():
    return AstronomicalCalculator()

@pytest.fixture
def test_date():
    return datetime(2024, 1, 1, 0, 0)

@pytest.fixture
def test_location():
    return Location(latitude=28.6139, longitude=77.2090, altitude=0)

def test_cache_initialization():
    """Test cache initialization"""
    assert calculation_cache is not None
    assert calculation_cache.max_size == 1000
    assert calculation_cache.ttl_hours == 24

def test_planetary_positions_caching(calculator, test_date, test_location, mocker):
    """Test caching of planetary positions"""
    # Mock swisseph calls
    mocker.patch('swisseph.calc_ut', return_value=((120.5, 23.4, 0.9), 0))
    mocker.patch('swisseph.get_ayanamsa_ut', return_value=24.13)
    mocker.patch('swisseph.set_topo')
    
    # First call - should calculate
    result1 = calculator.calculate_planetary_positions(test_date, test_location)
    
    # Second call - should use cache
    result2 = calculator.calculate_planetary_positions(test_date, test_location)
    
    assert result1 == result2
    
def test_house_cusps_caching(calculator, test_date, mocker):
    """Test caching of house cusps calculations"""
    mock_cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
    mock_ascmc = [83.5, 173.2, 263.1, 353.0]
    mocker.patch('swisseph.houses_ex', return_value=(mock_cusps, mock_ascmc))
    
    # First call - should calculate
    result1 = calculator.calculate_house_cusps(test_date, 28.6139, 77.2090)
    
    # Second call - should use cache
    result2 = calculator.calculate_house_cusps(test_date, 28.6139, 77.2090)
    
    assert result1 == result2
    assert len(result1['cusps']) == 12
    assert len(result1['ascmc']) == 4

def test_cache_invalidation(calculator, test_date, test_location, mocker):
    """Test cache invalidation"""
    # Mock swisseph calls
    mocker.patch('swisseph.calc_ut', return_value=((120.5, 23.4, 0.9), 0))
    mocker.patch('swisseph.get_ayanamsa_ut', return_value=24.13)
    mocker.patch('swisseph.set_topo')
    mocker.patch('swisseph.houses_ex', return_value=([0.0] * 12, [0.0] * 4))
    
    # Calculate and cache some values
    calculator.calculate_planetary_positions(test_date, test_location)
    calculator.calculate_house_cusps(test_date, 28.6139, 77.2090)
    
    # Get cache keys
    date_key, location_key = calculation_cache._make_cache_key(test_date, test_location)
    house_key = f"{date_key}_{28.6139:.4f}_{77.2090:.4f}"
    
    # Verify values are cached
    assert calculation_cache._planetary_positions_cache[f"{date_key}_{location_key}"] is not None
    assert calculation_cache._house_cusps_cache[house_key] is not None
    
    # Invalidate cache
    calculation_cache.invalidate_cache()
    
    # Verify caches are empty
    assert len(calculation_cache._planetary_positions_cache) == 0
    assert len(calculation_cache._house_cusps_cache) == 0
    assert len(calculation_cache._ayanamsa_cache) == 0
