"""
Test Suite for Planetary Strength Calculator
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""

import pytest
from datetime import datetime
from app.core.calculations.planetary_strength import PlanetaryStrengthCalculator, PlanetaryStrength

@pytest.fixture
def strength_calculator():
    return PlanetaryStrengthCalculator()

def test_dignity_calculation(strength_calculator):
    """Test planetary dignity calculations"""
    # Test Sun in Leo (own sign)
    sun_leo = strength_calculator._calculate_dignity('Sun', 125.5)  # Leo
    assert sun_leo == 0.75
    
    # Test Sun in Aries (exaltation)
    sun_aries = strength_calculator._calculate_dignity('Sun', 15.0)  # Aries
    assert sun_aries == 1.0
    
    # Test Sun in Libra (debilitation)
    sun_libra = strength_calculator._calculate_dignity('Sun', 185.0)  # Libra
    assert sun_libra == -0.5

def test_positional_strength(strength_calculator):
    """Test house position strength calculations"""
    # Test angular houses
    kendra = strength_calculator._calculate_positional_strength(1)
    assert kendra == 1.0
    
    # Test succedent houses
    panapara = strength_calculator._calculate_positional_strength(2)
    assert panapara == 0.75
    
    # Test cadent houses
    apoklima = strength_calculator._calculate_positional_strength(3)
    assert apoklima == 0.5

def test_complete_strength_calculation(strength_calculator):
    """Test complete strength calculation for a planet"""
    test_time = datetime(2024, 1, 1, 12, 0)
    
    # Calculate strength for Sun in Leo (own sign)
    strength = strength_calculator.calculate_strength(
        planet='Sun',
        longitude=125.5,  # Leo
        chart_time=test_time,
        house_position=1  # Lagna
    )
    
    assert isinstance(strength, PlanetaryStrength)
    assert 0 <= strength.total_strength <= 1
    assert strength.dignity_score == 0.75  # Own sign
    assert strength.positional_strength == 1.0  # Angular house

def test_shadbala_calculation(strength_calculator):
    """Test Shadbala (six-fold strength) calculation"""
    shadbala = strength_calculator._calculate_shadbala(
        dignity=0.75,  # Own sign
        positional=1.0,  # Angular house
        temporal=0.75,  # Day time
        aspect=0.8  # Beneficial aspects
    )
    
    assert isinstance(shadbala, float)
    assert 0 <= shadbala <= 1
    
    # Test with minimum values
    min_shadbala = strength_calculator._calculate_shadbala(
        dignity=-0.5,  # Debilitation
        positional=0.5,  # Cadent house
        temporal=0.5,  # Weak temporal position
        aspect=0.5  # Weak aspects
    )
    
    assert min_shadbala < shadbala  # Should be weaker

def test_total_strength_calculation(strength_calculator):
    """Test total strength aggregation"""
    components = [0.75, 1.0, 0.8, 0.9, 0.85]
    total = strength_calculator._calculate_total_strength(components)
    
    assert isinstance(total, float)
    assert 0 <= total <= 1
    assert round(total, 2) == round(sum(components) / len(components), 2)
