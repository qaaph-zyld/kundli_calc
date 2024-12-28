"""
Tests for Shadbala calculations
"""
import pytest
from decimal import Decimal
from app.core.calculations.shadbala import ShadbalaSystem

def test_shadbala_calculation():
    # Test data
    planet = "jupiter"
    position = 95.0  # Exaltation point
    house = 4
    is_day = True
    aspects = [
        {'type': 'trine', 'angle': 120},
        {'type': 'square', 'angle': 90}
    ]
    planet_positions = {
        'sun': 30.0,
        'moon': 60.0,
        'mars': 90.0,
        'mercury': 120.0,
        'jupiter': 95.0,
        'venus': 150.0,
        'saturn': 180.0
    }
    
    result = ShadbalaSystem.calculate_shadbala(
        planet,
        position,
        house,
        is_day,
        aspects,
        planet_positions
    )
    
    # Verify result structure
    assert isinstance(result, dict)
    assert 'planet' in result
    assert 'total_strength' in result
    assert 'components' in result
    assert 'interpretation' in result
    
    # Verify components
    components = result['components']
    assert 'sthana_bala' in components
    assert 'dig_bala' in components
    assert 'kala_bala' in components
    assert 'chesta_bala' in components
    assert 'naisargika_bala' in components
    assert 'drik_bala' in components
    
    # Verify strength calculations
    assert 0 <= result['total_strength'] <= 100
    for strength in components.values():
        assert isinstance(strength, float)
        assert strength >= 0
    
    # Test interpretation
    interpretation = result['interpretation']
    assert 'status' in interpretation
    assert 'effect' in interpretation
    assert isinstance(interpretation['status'], str)
    assert isinstance(interpretation['effect'], str)

def test_positional_strength():
    # Test exaltation point
    strength = ShadbalaSystem._calculate_positional_strength(
        'jupiter',
        95.0,  # Exaltation point
        4
    )
    assert isinstance(strength, Decimal)
    assert strength > Decimal('0')
    
    # Test debilitation point
    strength = ShadbalaSystem._calculate_positional_strength(
        'jupiter',
        275.0,  # Opposite to exaltation
        10
    )
    assert isinstance(strength, Decimal)
    assert strength < Decimal('50')

def test_directional_strength():
    # Test optimal position
    strength = ShadbalaSystem._calculate_directional_strength(
        'jupiter',
        0.0  # Strongest in 1st house
    )
    assert isinstance(strength, Decimal)
    assert strength > Decimal('0')
    
    # Test weakest position
    strength = ShadbalaSystem._calculate_directional_strength(
        'jupiter',
        180.0  # Weakest position
    )
    assert isinstance(strength, Decimal)
    assert strength < Decimal('60')

def test_temporal_strength():
    # Test day strength
    strength = ShadbalaSystem._calculate_temporal_strength(
        'sun',
        True,  # Day
        30.0
    )
    assert isinstance(strength, Decimal)
    assert strength == Decimal('60')
    
    # Test night strength
    strength = ShadbalaSystem._calculate_temporal_strength(
        'moon',
        False,  # Night
        60.0
    )
    assert isinstance(strength, Decimal)
    assert strength == Decimal('60')

def test_natural_strength():
    # Test known natural strengths
    for planet, expected in ShadbalaSystem.natural_strengths.items():
        strength = ShadbalaSystem._calculate_natural_strength(planet)
        assert strength == Decimal(str(expected))

def test_aspect_strength():
    # Test beneficial aspects
    aspects = [
        {'type': 'trine', 'angle': 120},
        {'type': 'sextile', 'angle': 60}
    ]
    strength = ShadbalaSystem._calculate_aspect_strength('jupiter', aspects)
    assert isinstance(strength, Decimal)
    assert strength > Decimal('50')  # Should be strengthened
    
    # Test challenging aspects
    aspects = [
        {'type': 'square', 'angle': 90},
        {'type': 'opposition', 'angle': 180}
    ]
    strength = ShadbalaSystem._calculate_aspect_strength('jupiter', aspects)
    assert isinstance(strength, Decimal)
    assert strength < Decimal('50')  # Should be weakened

def test_strength_interpretation():
    # Test excellent strength
    interpretation = ShadbalaSystem._interpret_strength(90.0)
    assert interpretation['status'] == "Excellent"
    
    # Test strong strength
    interpretation = ShadbalaSystem._interpret_strength(75.0)
    assert interpretation['status'] == "Strong"
    
    # Test moderate strength
    interpretation = ShadbalaSystem._interpret_strength(60.0)
    assert interpretation['status'] == "Moderate"
    
    # Test weak strength
    interpretation = ShadbalaSystem._interpret_strength(40.0)
    assert interpretation['status'] == "Weak"
    
    # Test very weak strength
    interpretation = ShadbalaSystem._interpret_strength(20.0)
    assert interpretation['status'] == "Very Weak"

def test_invalid_inputs():
    # Test invalid planet
    with pytest.raises(ValueError):
        ShadbalaSystem.calculate_shadbala(
            "invalid_planet",
            0.0,
            1,
            True,
            [],
            {}
        )
    
    # Test invalid position
    with pytest.raises(ValueError):
        ShadbalaSystem.calculate_shadbala(
            "jupiter",
            -1.0,  # Invalid position
            1,
            True,
            [],
            {}
        )
