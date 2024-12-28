"""
Test Suite for Aspect Analysis System
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""

import pytest
from app.core.calculations.aspect_analysis import (
    AspectAnalyzer,
    AspectType,
    AspectInfluence
)

@pytest.fixture
def aspect_analyzer():
    return AspectAnalyzer()

def test_aspect_type_determination(aspect_analyzer):
    """Test aspect type determination"""
    # Test 7th house aspect (full)
    assert aspect_analyzer._determine_aspect_type('Sun', 7) == AspectType.FULL
    
    # Test Jupiter's special aspects
    assert aspect_analyzer._determine_aspect_type('Jupiter', 5) == AspectType.THREE_QUARTER
    assert aspect_analyzer._determine_aspect_type('Jupiter', 9) == AspectType.THREE_QUARTER
    
    # Test Mars' special aspects
    assert aspect_analyzer._determine_aspect_type('Mars', 4) == AspectType.HALF
    assert aspect_analyzer._determine_aspect_type('Mars', 8) == AspectType.HALF

def test_relationship_factor(aspect_analyzer):
    """Test planetary relationship factors"""
    # Test friendly relationship
    assert aspect_analyzer._calculate_relationship_factor('Sun', 'Moon') == 1.1
    
    # Test enemy relationship
    assert aspect_analyzer._calculate_relationship_factor('Sun', 'Saturn') == 0.9
    
    # Test neutral relationship
    assert aspect_analyzer._calculate_relationship_factor('Sun', 'Mercury') == 1.0

def test_aspect_influence_calculation(aspect_analyzer):
    """Test calculation of aspect influence"""
    # Test Sun's aspect on Moon in 7th house
    influence = aspect_analyzer.calculate_aspect_influence('Sun', 'Moon', 7)
    assert influence is not None
    assert influence.aspect_type == AspectType.FULL
    assert influence.strength == pytest.approx(1.1, 0.01)  # Full strength * friendly factor
    
    # Test Jupiter's aspect on Venus in 5th house
    influence = aspect_analyzer.calculate_aspect_influence('Jupiter', 'Venus', 5)
    assert influence is not None
    assert influence.aspect_type == AspectType.THREE_QUARTER
    assert influence.strength == pytest.approx(0.75, 0.01)
    
    # Test non-existent aspect
    influence = aspect_analyzer.calculate_aspect_influence('Sun', 'Moon', 2)
    assert influence is None

def test_special_effects(aspect_analyzer):
    """Test special aspect effects"""
    # Test Gaja-Kesari Yoga
    effects = aspect_analyzer._check_special_effects('Jupiter', 'Moon', 7)
    assert effects is not None
    assert 'Gaja-Kesari Yoga' in effects
    
    # Test no special effects
    effects = aspect_analyzer._check_special_effects('Mars', 'Saturn', 7)
    assert effects is None

def test_calculate_all_aspects(aspect_analyzer):
    """Test calculation of all aspects between planets"""
    planet_positions = {
        'Sun': 0.0,      # In Aries
        'Moon': 180.0,   # In Libra (7th house from Sun)
        'Jupiter': 120.0  # In Leo (5th house from Sun)
    }
    
    aspects = aspect_analyzer.calculate_all_aspects(planet_positions)
    
    # Check Sun-Moon mutual aspect
    assert ('Sun', 'Moon') in aspects
    assert ('Moon', 'Sun') in aspects
    assert aspects[('Sun', 'Moon')].aspect_type == AspectType.FULL
    
    # Check Jupiter's aspect on Sun
    assert ('Jupiter', 'Sun') in aspects
    assert aspects[('Jupiter', 'Sun')].aspect_type == AspectType.THREE_QUARTER

def test_houses_between_calculation(aspect_analyzer):
    """Test calculation of houses between planets"""
    # Test regular cases
    assert aspect_analyzer._calculate_houses_between(0.0, 180.0) == 7  # Opposite houses
    assert aspect_analyzer._calculate_houses_between(0.0, 90.0) == 4   # Square aspect
    
    # Test wrap-around case
    assert aspect_analyzer._calculate_houses_between(330.0, 30.0) == 3  # Across 0°
