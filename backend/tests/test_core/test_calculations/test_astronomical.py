"""Test astronomical calculations."""
import pytest
from datetime import datetime
from app.core.calculations.astronomical import AstronomicalCalculator
from app.models.enums import Planet
from app.models.location import Location


@pytest.fixture
def calculator():
    """Get calculator instance."""
    return AstronomicalCalculator()


def test_julian_day(calculator):
    """Test Julian day calculation."""
    # Test case: January 1, 2000, 12:00 UTC
    dt = datetime(2000, 1, 1, 12, 0)
    jd = calculator._julian_day(dt)
    assert isinstance(jd, float)
    assert abs(jd - 2451545.0) < 0.001  # Standard J2000.0 epoch


def test_calculate_planet_position(calculator):
    """Test planet position calculation."""
    # Test case: Sun's position at J2000.0
    dt = datetime(2000, 1, 1, 12, 0)
    location = Location(latitude=0.0, longitude=0.0)
    
    position = calculator.calculate_planet_position(dt, Planet.SUN, location)
    assert isinstance(position, dict)
    assert "longitude" in position
    assert "speed" in position
    assert "is_retrograde" in position


def test_calculate_house_cusps(calculator):
    """Test house cusps calculation."""
    # Test case: Greenwich at J2000.0
    dt = datetime(2000, 1, 1, 12, 0)
    location = Location(latitude=51.4777, longitude=0.0)  # Greenwich
    
    cusps = calculator.calculate_house_cusps(dt, location)
    assert isinstance(cusps, list)
    assert len(cusps) == 12  # 12 houses
