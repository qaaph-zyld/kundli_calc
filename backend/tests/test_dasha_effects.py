"""
Tests for Dasha period interpretations
"""
import pytest
from decimal import Decimal
from app.core.interpretations.dasha_effects import DashaEffects

def test_planet_effects():
    # Test getting effects for each planet
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        effects = DashaEffects.get_planet_effects(planet)
        assert isinstance(effects, list)
        assert len(effects) > 0
        
    # Test invalid planet
    effects = DashaEffects.get_planet_effects('Invalid')
    assert effects == []

def test_combination_effects():
    # Test valid combinations
    effects = DashaEffects.get_combination_effects('Sun', 'Moon')
    assert isinstance(effects, list)
    assert len(effects) > 0
    
    # Test reverse order of planets
    effects_reverse = DashaEffects.get_combination_effects('Moon', 'Sun')
    assert effects == effects_reverse
    
    # Test invalid combination
    effects = DashaEffects.get_combination_effects('Sun', 'Invalid')
    assert effects == []

def test_dasha_interpretation():
    # Test mahadasha only
    result = DashaEffects.interpret_dasha_period('Sun')
    assert 'main_effects' in result
    assert len(result['main_effects']) > 0
    assert 'combinations' in result
    assert 'sub_effects' not in result
    
    # Test mahadasha and antardasha
    result = DashaEffects.interpret_dasha_period('Sun', 'Moon')
    assert 'main_effects' in result
    assert 'sub_effects' in result
    assert 'combinations' in result
    assert len(result['combinations']) > 0
    
    # Test all three levels
    result = DashaEffects.interpret_dasha_period('Sun', 'Moon', 'Mars')
    assert 'main_effects' in result
    assert 'sub_effects' in result
    assert 'prat_effects' in result
    assert 'combinations' in result
    assert len(result['combinations']) > 0

def test_strength_factors():
    # Test Sun factors
    factors = DashaEffects.get_strength_factors('Sun')
    assert isinstance(factors, dict)
    assert 'day' in factors
    assert isinstance(factors['day'], Decimal)
    assert factors['day'] > factors['night']
    
    # Test Moon factors
    factors = DashaEffects.get_strength_factors('Moon')
    assert 'phase' in factors
    assert factors['phase']['full'] > factors['phase']['new']
    
    # Test invalid planet
    factors = DashaEffects.get_strength_factors('Invalid')
    assert factors == {}
