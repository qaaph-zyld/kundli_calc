"""
Tests for Prediction Engine calculations
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.calculations.prediction_engine import PredictionEngine

def test_calculate_muhurta():
    # Test data
    test_time = datetime(2024, 12, 27, 8, 0)  # 8:00 AM UTC
    planet_positions = {
        'sun': 270.0,
        'moon': 120.0,
        'mars': 180.0,
        'mercury': 240.0,
        'jupiter': 300.0,
        'venus': 30.0,
        'saturn': 150.0
    }
    planet_strengths = {
        'sun': 0.7,
        'moon': 0.8,
        'mars': 0.6,
        'mercury': 0.75,
        'jupiter': 0.8,
        'venus': 0.7,
        'saturn': 0.5
    }
    
    # Test business muhurta
    result = PredictionEngine.calculate_muhurta(
        test_time,
        'business',
        planet_positions,
        planet_strengths
    )
    
    assert isinstance(result, dict)
    assert 'datetime' in result
    assert 'activity' in result
    assert 'suitability_score' in result
    assert 'is_suitable' in result
    assert 'tithi' in result
    assert 'nakshatra' in result
    assert 'current_muhurta' in result
    assert 'is_auspicious_muhurta' in result
    assert 'planetary_analysis' in result
    assert 'recommended_muhurtas' in result
    
    # Test invalid activity
    with pytest.raises(ValueError):
        PredictionEngine.calculate_muhurta(
            test_time,
            'invalid_activity',
            planet_positions,
            planet_strengths
        )
    
    # Test spiritual muhurta
    result = PredictionEngine.calculate_muhurta(
        test_time,
        'spiritual',
        planet_positions,
        planet_strengths
    )
    assert result['activity'] == 'spiritual'
    assert isinstance(result['suitability_score'], float)
    assert isinstance(result['is_suitable'], bool)

def test_find_next_suitable_time():
    test_time = datetime(2024, 12, 27, 8, 0)
    planet_positions = {
        'sun': 270.0,
        'moon': 120.0,
        'mars': 180.0,
        'mercury': 240.0,
        'jupiter': 300.0,
        'venus': 30.0,
        'saturn': 150.0
    }
    planet_strengths = {
        'sun': 0.7,
        'moon': 0.8,
        'mars': 0.6,
        'mercury': 0.75,
        'jupiter': 0.8,
        'venus': 0.7,
        'saturn': 0.5
    }
    
    result = PredictionEngine.find_next_suitable_time(
        test_time,
        'business',
        planet_positions.copy(),  # Copy to prevent modification
        planet_strengths,
        max_days=1
    )
    
    assert isinstance(result, dict)
    assert datetime.fromisoformat(result['datetime']) >= test_time
    assert datetime.fromisoformat(result['datetime']) <= test_time + timedelta(days=1)
    assert result['is_suitable']
    assert result['is_auspicious_muhurta']

def test_analyze_transit_period():
    start_time = datetime(2024, 12, 27, 8, 0)
    end_time = datetime(2024, 12, 28, 8, 0)
    
    # Test transit positions (time, position)
    transit_positions = [
        (start_time, 0.0),
        (start_time + timedelta(hours=6), 60.0),
        (start_time + timedelta(hours=12), 120.0),
        (start_time + timedelta(hours=18), 180.0),
        (end_time, 240.0)
    ]
    
    result = PredictionEngine.analyze_transit_period(
        start_time,
        end_time,
        'jupiter',
        0.0,  # Natal position
        transit_positions
    )
    
    assert isinstance(result, dict)
    assert 'period' in result
    assert 'planet' in result
    assert 'natal_position' in result
    assert 'aspects' in result
    assert 'strength' in result
    assert 'overall_effect' in result
    
    assert result['planet'] == 'jupiter'
    assert result['natal_position'] == 0.0
    assert isinstance(result['strength'], float)
    assert 0 <= result['strength'] <= 1
    assert isinstance(result['overall_effect'], str)
    
    # Verify aspects
    for aspect in result['aspects']:
        assert 'time' in aspect
        assert 'type' in aspect
        assert 'angle' in aspect
        assert 'effect' in aspect

def test_helper_functions():
    # Test tithi calculation
    tithi = PredictionEngine._calculate_tithi(120.0, 0.0)
    assert 1 <= tithi <= 30
    
    # Test muhurta name
    muhurta = PredictionEngine._get_muhurta_name(0)
    assert isinstance(muhurta, str)
    assert muhurta in [
        'Rudra', 'Brahma', 'Vidya', 'Kala', 'Siddha',
        'Amrita', 'Chara', 'Labha', 'Shubha', 'Mrityu'
    ]
    
    # Test aspect type
    aspect = PredictionEngine._get_aspect_type(60.0)
    assert aspect == 'Sextile'
    
    aspect = PredictionEngine._get_aspect_type(90.0)
    assert aspect == 'Square'
    
    aspect = PredictionEngine._get_aspect_type(45.0)
    assert aspect is None  # No aspect for 45 degrees
    
    # Test aspect effect
    effect = PredictionEngine._get_aspect_effect('Trine', 'jupiter')
    assert isinstance(effect, str)
    assert len(effect) > 0
    
    # Test transit strength calculation
    aspects = [
        {'type': 'Trine', 'angle': 120},
        {'type': 'Square', 'angle': 90}
    ]
    strength = PredictionEngine._calculate_transit_strength(aspects)
    assert 0 <= strength <= 1
    
    # Test period effect
    effect = PredictionEngine._get_period_effect(0.8)
    assert effect == "Highly favorable period"
    
    effect = PredictionEngine._get_period_effect(0.3)
    assert effect == "Some challenges present"
