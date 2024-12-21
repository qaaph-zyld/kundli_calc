import pytest
from datetime import datetime
from app.core.calculations.astronomical import AstronomicalCalculator, Location
from app.core.calculations.houses import HouseCalculator

def test_planetary_positions():
    calculator = AstronomicalCalculator()
    test_date = datetime(2024, 1, 1, 12, 0)
    test_location = Location(13.0827, 80.2707)  # Chennai coordinates
    
    positions = calculator.calculate_planetary_positions(test_date, test_location)
    
    assert positions is not None
    assert "Sun" in positions
    assert "Moon" in positions
    assert isinstance(positions["Sun"]["longitude"], float)
    assert 0 <= positions["Sun"]["longitude"] <= 360

def test_house_calculations():
    calculator = HouseCalculator()
    test_date = datetime(2024, 1, 1, 12, 0)
    test_location = Location(13.0827, 80.2707)
    
    houses = calculator.calculate_houses(test_date, test_location)
    
    assert houses is not None
    assert "cusps" in houses
    assert "ascendant" in houses
    assert len(houses["cusps"]) == 12  # Should have 12 house cusps
    assert 0 <= houses["ascendant"] <= 360
