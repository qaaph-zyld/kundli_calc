"""
Tests for Dasha Yoga calculations
"""
import pytest
from decimal import Decimal
from app.core.calculations.dasha_yoga import DashaYoga

def test_find_active_yogas():
    # Test Raja Yoga
    yogas = DashaYoga.find_active_yogas('Sun', 'Jupiter')
    assert len(yogas) > 0
    assert any(yoga['name'] == 'Raja Yoga' for yoga in yogas)
    
    # Test Dhana Yoga
    yogas = DashaYoga.find_active_yogas('Jupiter', 'Venus')
    assert len(yogas) > 0
    assert any(yoga['name'] == 'Dhana Yoga' for yoga in yogas)
    
    # Test with three planets
    yogas = DashaYoga.find_active_yogas('Sun', 'Jupiter', 'Venus')
    assert len(yogas) > 0
    # Should find both Raja Yoga and Dhana Yoga
    assert len([yoga for yoga in yogas if yoga['name'] in ['Raja Yoga', 'Dhana Yoga']]) == 2
    
    # Test with no yoga combination
    yogas = DashaYoga.find_active_yogas('Mars', 'Rahu')
    assert len(yogas) == 0

def test_yoga_strength():
    # Test basic strength calculation
    planet_positions = {
        'Sun': 120.0,
        'Jupiter': 90.0,
        'Venus': 180.0
    }
    
    strength = DashaYoga.calculate_yoga_strength('Raja Yoga', planet_positions)
    assert isinstance(strength, Decimal)
    assert Decimal('0') <= strength <= Decimal('1')
    
    # Test with empty positions
    strength = DashaYoga.calculate_yoga_strength('Raja Yoga', {})
    assert strength == Decimal('0.5')  # Should return base strength

def test_yoga_predictions():
    active_yogas = [
        {
            'name': 'Raja Yoga',
            'effects': ['Rise in position', 'Success in career'],
            'planets': ['Sun', 'Jupiter']
        }
    ]
    
    planet_positions = {
        'Sun': 120.0,
        'Jupiter': 90.0
    }
    
    predictions = DashaYoga.get_yoga_predictions(active_yogas, planet_positions)
    assert len(predictions) == 1
    
    prediction = predictions[0]
    assert prediction['yoga_name'] == 'Raja Yoga'
    assert isinstance(prediction['strength'], float)
    assert 'timing' in prediction
    assert 'recommendations' in prediction
    assert len(prediction['recommendations']) > 0
    
    # Test with multiple yogas
    active_yogas.append({
        'name': 'Dhana Yoga',
        'effects': ['Financial gains', 'Material success'],
        'planets': ['Jupiter', 'Venus']
    })
    
    predictions = DashaYoga.get_yoga_predictions(active_yogas, planet_positions)
    assert len(predictions) == 2
    
    # Test with empty yogas
    predictions = DashaYoga.get_yoga_predictions([], planet_positions)
    assert len(predictions) == 0

def test_yoga_definitions():
    # Verify all yoga definitions have required fields
    for yoga_name, yoga_info in DashaYoga.yoga_definitions.items():
        assert 'combinations' in yoga_info
        assert 'effects' in yoga_info
        assert isinstance(yoga_info['combinations'], list)
        assert isinstance(yoga_info['effects'], list)
        assert len(yoga_info['combinations']) > 0
        assert len(yoga_info['effects']) > 0
        
        # Verify combination format
        for combo in yoga_info['combinations']:
            assert isinstance(combo, tuple)
            assert len(combo) == 2
            assert all(isinstance(planet, str) for planet in combo)
