"""
Test Suite for Yoga Calculator
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""

import pytest
from app.core.calculations.yoga_calculator import (
    YogaCalculator,
    YogaType,
    YogaResult
)

@pytest.fixture
def yoga_calculator():
    return YogaCalculator()

@pytest.fixture
def sample_planet_positions():
    """Sample planet positions for testing"""
    return {
        "Sun": {
            "longitude": 120.0,  # In Leo (5th house)
            "latitude": 0.0,
            "dignity": "own"
        },
        "Moon": {
            "longitude": 90.0,   # In Cancer (4th house)
            "latitude": 0.0,
            "dignity": "own"
        },
        "Mars": {
            "longitude": 30.0,   # In Taurus (2nd house)
            "latitude": 0.0,
            "dignity": "neutral"
        },
        "Mercury": {
            "longitude": 150.0,  # In Virgo (6th house)
            "latitude": 0.0,
            "dignity": "own"
        },
        "Jupiter": {
            "longitude": 270.0,  # In Capricorn (10th house)
            "latitude": 0.0,
            "dignity": "exalted"
        },
        "Venus": {
            "longitude": 210.0,  # In Libra (7th house)
            "latitude": 0.0,
            "dignity": "own"
        },
        "Saturn": {
            "longitude": 300.0,  # In Aquarius (11th house)
            "latitude": 0.0,
            "dignity": "own"
        }
    }

@pytest.fixture
def sample_house_positions(sample_planet_positions):
    """Generate house positions from planet positions"""
    houses = {i: [] for i in range(1, 13)}
    for planet, data in sample_planet_positions.items():
        house = int(data['longitude'] / 30) + 1
        houses[house].append(planet)
    return houses

def test_raj_yoga_calculation(yoga_calculator, sample_planet_positions, sample_house_positions):
    """Test Raj Yoga calculation"""
    yogas = yoga_calculator.calculate_raj_yoga(
        sample_planet_positions,
        sample_house_positions
    )
    
    # Verify results
    assert len(yogas) > 0
    for yoga in yogas:
        assert isinstance(yoga, YogaResult)
        assert yoga.yoga_type == YogaType.RAJ
        assert len(yoga.planets_involved) > 0
        assert len(yoga.houses_involved) == 2
        assert 0 <= yoga.strength <= 100
        assert yoga.is_complete

def test_dhana_yoga_calculation(yoga_calculator, sample_planet_positions, sample_house_positions):
    """Test Dhana Yoga calculation"""
    yogas = yoga_calculator.calculate_dhana_yoga(
        sample_planet_positions,
        sample_house_positions
    )
    
    # Verify results
    assert len(yogas) > 0
    for yoga in yogas:
        assert isinstance(yoga, YogaResult)
        assert yoga.yoga_type == YogaType.DHANA
        assert len(yoga.planets_involved) > 0
        assert len(yoga.houses_involved) == 2
        assert 0 <= yoga.strength <= 100
        assert yoga.is_complete

def test_mahapurusha_yoga_calculation(yoga_calculator, sample_planet_positions):
    """Test Pancha Mahapurusha Yoga calculation"""
    yogas = yoga_calculator.calculate_mahapurusha_yoga(sample_planet_positions)
    
    # Verify results
    assert len(yogas) > 0
    for yoga in yogas:
        assert isinstance(yoga, YogaResult)
        assert yoga.yoga_type == YogaType.MAHAPURUSHA
        assert len(yoga.planets_involved) == 1
        assert len(yoga.houses_involved) == 1
        assert 0 <= yoga.strength <= 100
        assert yoga.is_complete
        
        # Verify planet is in appropriate house
        planet = yoga.planets_involved[0]
        house = yoga.houses_involved[0]
        assert house in yoga_calculator.mahapurusha_conditions[planet]

def test_yoga_strength_calculation(yoga_calculator, sample_planet_positions):
    """Test yoga strength calculation"""
    # Test exalted planet in kendra
    strength = yoga_calculator._calculate_yoga_strength(
        "Jupiter",
        10,  # Kendra house
        sample_planet_positions
    )
    assert 80 < strength <= 100
    
    # Test debilitated planet in dusthana
    debilitated_positions = sample_planet_positions.copy()
    debilitated_positions["Mars"] = {
        "longitude": 180.0,  # In Libra
        "latitude": 0.0,
        "dignity": "debilitated"
    }
    strength = yoga_calculator._calculate_yoga_strength(
        "Mars",
        12,  # Dusthana house
        debilitated_positions
    )
    assert strength < 60

def test_planet_dignity_determination(yoga_calculator, sample_planet_positions):
    """Test planet dignity determination"""
    # Test own sign
    assert yoga_calculator._get_planet_dignity("Sun", sample_planet_positions) == "own"
    
    # Test exaltation
    assert yoga_calculator._get_planet_dignity("Jupiter", sample_planet_positions) == "exalted"
    
    # Test neutral
    assert yoga_calculator._get_planet_dignity("Mars", sample_planet_positions) == "neutral"

def test_planet_house_determination(yoga_calculator, sample_planet_positions):
    """Test determination of planet's house position"""
    assert yoga_calculator._get_planet_house("Sun", sample_planet_positions) == 5  # Leo
    assert yoga_calculator._get_planet_house("Moon", sample_planet_positions) == 4  # Cancer
    assert yoga_calculator._get_planet_house("Jupiter", sample_planet_positions) == 10  # Capricorn
