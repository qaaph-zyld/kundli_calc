"""Test house calculations."""
import pytest
from datetime import datetime
from app.core.calculations.houses import HouseCalculator
from app.models.location import Location


@pytest.fixture
def calculator():
    """Get house calculator instance."""
    return HouseCalculator()


def test_calculate_houses(calculator):
    """Test house cusps calculation."""
    # Test case: Greenwich at J2000.0
    dt = datetime(2000, 1, 1, 12, 0)
    location = Location(latitude=51.4777, longitude=0.0)  # Greenwich
    
    houses = calculator.calculate_houses(dt, location)
    assert isinstance(houses, dict)
    assert "cusps" in houses
    assert "ascendant" in houses
    assert "midheaven" in houses
    assert "armc" in houses
    assert "vertex" in houses
    assert len(houses["cusps"]) == 12  # 12 houses


def test_house_systems(calculator):
    """Test different house systems."""
    dt = datetime(2000, 1, 1, 12, 0)
    location = Location(latitude=51.4777, longitude=0.0)  # Greenwich
    
    # Test Placidus (default)
    houses_p = calculator.calculate_houses(dt, location)
    
    # Test Koch
    calculator.house_system = "K"
    houses_k = calculator.calculate_houses(dt, location)
    
    # Houses should be different between systems
    assert houses_p["cusps"] != houses_k["cusps"]
