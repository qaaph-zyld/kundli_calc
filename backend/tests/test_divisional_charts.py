"""
Divisional Chart Engine Test Suite
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from app.core.calculations.divisional_charts import DivisionalChartEngine, DivisionalChart
from app.core.cache.calculation_cache import CalculationCache

@pytest.fixture
def mock_swe():
    """Mock Swiss Ephemeris functions"""
    with patch('app.core.calculations.astronomical.swe') as mock_swe:
        # Mock houses_ex to return sample house cusps and ascmc
        mock_swe.houses_ex.return_value = (
            [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],  # cusps
            [0, 90, 180, 270]  # ascmc (Asc, MC, ARMC, Vertex)
        )
        
        # Mock calc_ut to return sample planetary positions
        mock_swe.calc_ut.return_value = ([15.5, 0, 1, 1, 0, 0], 0)  # position data, return flag
        
        # Mock other swe functions
        mock_swe.set_ephe_path = Mock()
        mock_swe.set_topo = Mock()
        mock_swe.get_ayanamsa_ut = Mock(return_value=23.15)
        
        yield mock_swe

@pytest.fixture
def chart_engine(mock_swe):
    """Create a chart engine instance for testing"""
    return DivisionalChartEngine(cache=CalculationCache())

@pytest.fixture
def test_date():
    """Fixed test date for consistent results"""
    return datetime(2024, 1, 1, 12, 0, 0)

@pytest.fixture
def test_location():
    """Test location - New Delhi"""
    return {"lat": 28.6139, "lon": 77.2090, "alt": 0.0}

def test_rashi_chart_calculation(chart_engine, test_date, test_location):
    """Test D1 (Rashi) chart calculation"""
    chart = chart_engine.calculate_chart(test_date, division=1, location=test_location)
    assert isinstance(chart, DivisionalChart)
    assert chart.division == 1
    assert len(chart.planets) > 0
    assert all(0 <= pos < 360 for pos in chart.planets.values())
    assert chart.location == test_location

def test_hora_chart_calculation(chart_engine, test_date, test_location):
    """Test D2 (Hora) chart calculation"""
    chart = chart_engine.calculate_chart(test_date, division=2, location=test_location)
    assert chart.division == 2
    for planet, pos in chart.planets.items():
        assert 0 <= pos < 360
        degree = pos % 30
        assert degree in [0, 15]  # Hora points

def test_drekkana_chart_calculation(chart_engine, test_date, test_location):
    """Test D3 (Drekkana) chart calculation"""
    chart = chart_engine.calculate_chart(test_date, division=3, location=test_location)
    assert chart.division == 3
    for pos in chart.planets.values():
        assert 0 <= pos < 360
        assert pos % 10 == 0  # Drekkana points

def test_navamsa_chart_calculation(chart_engine, test_date, test_location):
    """Test D9 (Navamsa) chart calculation"""
    chart = chart_engine.calculate_chart(test_date, division=9, location=test_location)
    assert chart.division == 9
    for pos in chart.planets.values():
        assert 0 <= pos < 360
        # Each navamsa is 3°20' (10/3 degrees)
        assert abs((pos % 40) - 0) < 0.001

def test_cache_functionality(chart_engine, test_date, test_location):
    """Test caching of divisional chart calculations"""
    # First calculation
    chart1 = chart_engine.calculate_chart(test_date, division=1, location=test_location)
    
    # Second calculation (should hit cache)
    chart2 = chart_engine.calculate_chart(test_date, division=1, location=test_location)
    
    assert chart1.planets == chart2.planets
    assert chart1.timestamp == chart2.timestamp
    assert chart1.location == chart2.location

def test_invalid_division(chart_engine, test_date, test_location):
    """Test handling of invalid division numbers"""
    with pytest.raises(ValueError):
        chart_engine.calculate_chart(test_date, division=61, location=test_location)

def test_all_supported_divisions(chart_engine, test_date, test_location):
    """Test calculation of all supported divisional charts"""
    supported_divisions = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
    
    for division in supported_divisions:
        chart = chart_engine.calculate_chart(test_date, division=division, location=test_location)
        assert chart.division == division
        assert len(chart.planets) > 0
        assert all(0 <= pos < 360 for pos in chart.planets.values())
        assert chart.location == test_location

def test_default_location(chart_engine, test_date):
    """Test chart calculation with default location"""
    chart = chart_engine.calculate_chart(test_date, division=1)
    assert chart.location == chart_engine.default_location
