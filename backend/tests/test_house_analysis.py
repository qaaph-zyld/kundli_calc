"""
Test Suite for House Analysis Engine
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""

import pytest
from app.core.calculations.house_analysis import EnhancedHouseAnalysisEngine, HouseStrength

@pytest.fixture
def house_analyzer():
    return EnhancedHouseAnalysisEngine()

def test_natural_strength_calculation(house_analyzer):
    """Test natural strength calculation for different houses"""
    # Test kendra houses (angular houses)
    assert house_analyzer._calculate_natural_strength(1) > 90  # Ascendant
    assert house_analyzer._calculate_natural_strength(4) > 90  # IC
    assert house_analyzer._calculate_natural_strength(7) > 90  # Descendant
    assert house_analyzer._calculate_natural_strength(10) > 90  # MC
    
    # Test trikona houses (trine houses)
    assert house_analyzer._calculate_natural_strength(5) > 70
    assert house_analyzer._calculate_natural_strength(9) > 70
    
    # Test dusthana houses (malefic houses)
    assert house_analyzer._calculate_natural_strength(6) < 60
    assert house_analyzer._calculate_natural_strength(8) < 60
    assert house_analyzer._calculate_natural_strength(12) < 60

def test_occupant_strength_calculation(house_analyzer):
    """Test strength calculation based on planetary occupants"""
    # Test empty house
    assert house_analyzer._calculate_occupant_strength(1, []) == 50
    
    # Test single benefic planet
    jupiter = {
        'name': 'Jupiter',
        'strength': 80,
        'dignity': 'exalted',
        'is_retrograde': False
    }
    strength = house_analyzer._calculate_occupant_strength(1, [jupiter])
    assert 90 < strength <= 100
    
    # Test multiple planets
    mars = {
        'name': 'Mars',
        'strength': 60,
        'dignity': 'debilitated',
        'is_retrograde': True
    }
    strength = house_analyzer._calculate_occupant_strength(1, [jupiter, mars])
    assert 50 < strength < 90

def test_aspect_strength_calculation(house_analyzer):
    """Test strength calculation based on aspects"""
    # Test unaspected house
    assert house_analyzer._calculate_aspect_strength(1, []) == 50
    
    # Test beneficial aspect
    jupiter_trine = {
        'planet': 'Jupiter',
        'strength': 80,
        'type': 'trine',
        'is_applying': True
    }
    strength = house_analyzer._calculate_aspect_strength(1, [jupiter_trine])
    assert 60 < strength < 90
    
    # Test malefic aspect
    saturn_square = {
        'planet': 'Saturn',
        'strength': 70,
        'type': 'square',
        'is_applying': False
    }
    strength = house_analyzer._calculate_aspect_strength(1, [saturn_square])
    assert 30 < strength < 50

def test_lord_strength_calculation(house_analyzer):
    """Test strength calculation based on house lord"""
    # Test lord in own house
    lord = {
        'planet': 'Mars',
        'strength': 75,
        'house': 1,
        'dignity': 'own'
    }
    strength = house_analyzer._calculate_lord_strength(1, lord)
    assert 80 < strength <= 100
    
    # Test debilitated lord
    weak_lord = {
        'planet': 'Venus',
        'strength': 40,
        'house': 6,
        'dignity': 'debilitated'
    }
    strength = house_analyzer._calculate_lord_strength(2, weak_lord)
    assert strength < 50

def test_complete_house_analysis(house_analyzer):
    """Test complete house analysis with all components"""
    # Setup test data
    house = 1
    occupants = [{
        'name': 'Sun',
        'strength': 70,
        'dignity': 'own',
        'is_retrograde': False
    }]
    aspects = [{
        'planet': 'Jupiter',
        'strength': 80,
        'type': 'trine',
        'is_applying': True
    }]
    lord = {
        'planet': 'Mars',
        'strength': 75,
        'house': 1,
        'dignity': 'own'
    }
    
    # Perform analysis
    analysis = house_analyzer.analyze_house(
        house=house,
        occupants=occupants,
        aspects=aspects,
        lord=lord
    )
    
    # Verify results
    assert isinstance(analysis, HouseStrength)
    assert analysis.house_number == 1
    assert 60 < analysis.total_strength <= 100
    assert analysis.functional_nature in ['Benefic', 'Malefic', 'Mixed']
    assert len(analysis.significations) > 0

def test_house_relationships(house_analyzer):
    """Test house relationship determination"""
    # Test kendras (angular houses)
    assert house_analyzer._get_house_relationship(1, 4) == 'friend'  # Both kendra houses
    
    # Test own house
    assert house_analyzer._get_house_relationship(1, 1) == 'own'
    
    # Test exaltation
    assert house_analyzer._get_house_relationship(1, 10) == 'exalted'  # Leo lord (Sun) exalted in Aries
    
    # Test enemy relationship (dusthana to non-dusthana)
    assert house_analyzer._get_house_relationship(6, 1) == 'enemy'  # House 6 (dusthana) to house 1 (kendra)
    
    # Test neutral relationship (no special combination)
    assert house_analyzer._get_house_relationship(2, 3) == 'neutral'  # Regular houses
