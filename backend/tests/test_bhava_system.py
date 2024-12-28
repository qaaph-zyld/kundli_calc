"""
Tests for Bhava Analysis System
"""
import pytest
from decimal import Decimal
from app.core.calculations.bhava_system import BhavaSystem

def test_house_strength():
    # Test data
    planet_positions = {
        'Sun': 30.0,     # In 2nd house
        'Moon': 60.0,    # In 3rd house
        'Mars': 90.0,    # In 4th house
        'Mercury': 120.0, # In 5th house
        'Jupiter': 150.0, # In 6th house
        'Venus': 180.0,  # In 7th house
        'Saturn': 210.0  # In 8th house
    }
    
    aspects = {
        'Jupiter': [1, 5, 7, 9],  # Jupiter's aspects
        'Mars': [4, 7, 8],       # Mars's aspects
        'Saturn': [3, 7, 10]     # Saturn's aspects
    }
    
    # Test normal house
    result = BhavaSystem.calculate_house_strength(1, planet_positions, aspects)
    assert isinstance(result, dict)
    assert 'strength' in result
    assert 'significations' in result
    assert 'occupants' in result
    assert 'aspects' in result
    assert 'lord' in result
    assert isinstance(result['strength'], Decimal)
    assert Decimal('0') <= result['strength'] <= Decimal('1')
    
    # Test house with occupants
    result = BhavaSystem.calculate_house_strength(2, planet_positions, aspects)
    assert 'Sun' in result['occupants']
    
    # Test house with aspects
    result = BhavaSystem.calculate_house_strength(7, planet_positions, aspects)
    assert len(result['aspects']) > 0
    
    # Test invalid house number
    with pytest.raises(ValueError):
        BhavaSystem.calculate_house_strength(13, planet_positions, aspects)

def test_house_lord():
    # Test each house's lord
    lords = {
        1: 'Mars',
        2: 'Venus',
        3: 'Mercury',
        4: 'Moon',
        5: 'Sun',
        6: 'Mercury',
        7: 'Venus',
        8: 'Mars',
        9: 'Jupiter',
        10: 'Saturn',
        11: 'Saturn',
        12: 'Jupiter'
    }
    
    for house, expected_lord in lords.items():
        assert BhavaSystem.get_house_lord(house) == expected_lord
    
    # Test invalid house
    assert BhavaSystem.get_house_lord(13) == ''

def test_lord_placement():
    # Test lord in own house
    strength = BhavaSystem.analyze_lord_placement(1, 1)
    assert strength == Decimal('0.3')
    
    # Test trine placement
    strength = BhavaSystem.analyze_lord_placement(1, 5)
    assert strength == Decimal('0.2')
    
    # Test opposition
    strength = BhavaSystem.analyze_lord_placement(1, 7)
    assert strength == Decimal('-0.2')

def test_house_relationships():
    # Test relationship types
    assert BhavaSystem.get_house_relationship(1, 5) == 'trine'
    assert BhavaSystem.get_house_relationship(1, 4) == 'square'
    assert BhavaSystem.get_house_relationship(1, 7) == 'opposition'
    assert BhavaSystem.get_house_relationship(1, 3) == 'sextile'
    assert BhavaSystem.get_house_relationship(1, 2) == 'neutral'
    
    # Test get_house_relationships
    relationships = BhavaSystem.get_house_relationships(1)
    assert 'trine' in relationships
    assert 'square' in relationships
    assert 'sextile' in relationships
    assert 'opposition' in relationships

def test_bhava_chart_analysis():
    planet_positions = {
        'Sun': 30.0,
        'Moon': 60.0,
        'Mars': 90.0,
        'Mercury': 120.0,
        'Jupiter': 150.0,
        'Venus': 180.0,
        'Saturn': 210.0
    }
    
    aspects = {
        'Jupiter': [1, 5, 7, 9],
        'Mars': [4, 7, 8],
        'Saturn': [3, 7, 10]
    }
    
    result = BhavaSystem.analyze_bhava_chart(planet_positions, aspects)
    
    # Check structure
    assert 'house_analysis' in result
    assert 'strongest_house' in result
    assert 'weakest_house' in result
    assert 'chart_balance' in result
    
    # Check house analysis
    assert len(result['house_analysis']) == 12
    assert all(isinstance(result['house_analysis'][h]['strength'], Decimal) 
              for h in range(1, 13))
    
    # Check balance
    assert Decimal('0') <= result['chart_balance'] <= Decimal('1')
    
    # Test with empty positions
    result = BhavaSystem.analyze_bhava_chart({}, {})
    assert len(result['house_analysis']) == 12
    assert Decimal('0') <= result['chart_balance'] <= Decimal('1')
