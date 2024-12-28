"""
Tests for Ashtakavarga calculations
"""
import pytest
from decimal import Decimal
from app.core.calculations.ashtakavarga import Ashtakavarga

def test_calculate_bindus():
    # Test bindu calculation for Sun
    planet_positions = {
        'Sun': 1,
        'Moon': 4,
        'Mars': 7,
        'Mercury': 2,
        'Jupiter': 5,
        'Venus': 3,
        'Saturn': 8
    }
    
    bindus = Ashtakavarga.calculate_bindus('Sun', 1, planet_positions)
    assert isinstance(bindus, int)
    assert bindus >= 0
    
    # Test with empty planet positions
    bindus = Ashtakavarga.calculate_bindus('Sun', 1, {})
    assert bindus == 1  # Should only count self-contribution
    
    # Test with invalid planet
    bindus = Ashtakavarga.calculate_bindus('Invalid', 1, planet_positions)
    assert bindus == 0

def test_calculate_sarvashtakavarga():
    planet_positions = {
        'Sun': 1,
        'Moon': 4,
        'Mars': 7,
        'Mercury': 2,
        'Jupiter': 5,
        'Venus': 3,
        'Saturn': 8
    }
    
    result = Ashtakavarga.calculate_sarvashtakavarga(planet_positions)
    
    # Verify structure
    assert isinstance(result, dict)
    assert all(planet in result for planet in planet_positions.keys())
    
    # Verify each planet has 12 houses
    for planet, bindus in result.items():
        assert len(bindus) == 12
        assert all(isinstance(b, int) for b in bindus)
        assert all(b >= 0 for b in bindus)
        
    # Test with empty positions
    result = Ashtakavarga.calculate_sarvashtakavarga({})
    assert isinstance(result, dict)
    assert len(result) > 0  # Should still calculate self-contributions

def test_calculate_house_strength():
    sarvashtakavarga = {
        'Sun': [4, 3, 2, 5, 1, 3, 4, 5, 2, 3, 4, 2],
        'Moon': [3, 4, 2, 3, 4, 2, 3, 4, 5, 2, 3, 4]
    }
    
    strength = Ashtakavarga.calculate_house_strength(1, sarvashtakavarga)
    assert isinstance(strength, Decimal)
    assert Decimal('0') <= strength <= Decimal('1')
    
    # Test with empty sarvashtakavarga
    strength = Ashtakavarga.calculate_house_strength(1, {})
    assert strength == Decimal('0')
    
    # Test invalid house number
    with pytest.raises(IndexError):
        Ashtakavarga.calculate_house_strength(13, sarvashtakavarga)

def test_get_strong_houses():
    sarvashtakavarga = {
        'Sun': [4, 3, 2, 5, 1, 3, 4, 5, 2, 3, 4, 2],
        'Moon': [3, 4, 2, 3, 4, 2, 3, 4, 5, 2, 3, 4]
    }
    
    strong_houses = Ashtakavarga.get_strong_houses(sarvashtakavarga)
    assert isinstance(strong_houses, list)
    assert all(1 <= house <= 12 for house in strong_houses)
    
    # Test with different threshold
    strong_houses = Ashtakavarga.get_strong_houses(sarvashtakavarga, Decimal('0.8'))
    assert len(strong_houses) <= len(Ashtakavarga.get_strong_houses(sarvashtakavarga))
    
    # Test with empty sarvashtakavarga
    strong_houses = Ashtakavarga.get_strong_houses({})
    assert len(strong_houses) == 0

def test_analyze_planet_strength():
    sarvashtakavarga = {
        'Sun': [4, 3, 2, 5, 1, 3, 4, 5, 2, 3, 4, 2],
        'Moon': [3, 4, 2, 3, 4, 2, 3, 4, 5, 2, 3, 4]
    }
    
    analysis = Ashtakavarga.analyze_planet_strength('Sun', sarvashtakavarga)
    assert isinstance(analysis, dict)
    assert 'strength' in analysis
    assert 'favorable_houses' in analysis
    assert 'unfavorable_houses' in analysis
    assert 'recommendations' in analysis
    
    # Verify strength is between 0 and 1
    assert Decimal('0') <= analysis['strength'] <= Decimal('1')
    
    # Test invalid planet
    analysis = Ashtakavarga.analyze_planet_strength('Invalid', sarvashtakavarga)
    assert analysis['strength'] == Decimal('0')
    assert len(analysis['favorable_houses']) == 0
    assert len(analysis['unfavorable_houses']) == 0
