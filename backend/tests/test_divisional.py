import pytest
from app.core.calculations.divisional import EnhancedDivisionalChartEngine

def test_divisional_chart_engine_initialization():
    engine = EnhancedDivisionalChartEngine()
    assert engine is not None
    assert hasattr(engine, 'zodiac_signs')
    assert hasattr(engine, 'special_divisions')
    assert len(engine.zodiac_signs) == 12

def test_longitude_normalization():
    engine = EnhancedDivisionalChartEngine()
    test_cases = [
        (370.5, 10.5),    # > 360
        (-30.5, 329.5),   # Negative
        (360.0, 0.0),     # Exactly 360
        (180.5, 180.5),   # Normal case
        (720.5, 0.5)      # Multiple of 360
    ]
    
    for input_value, expected in test_cases:
        result = engine._normalize_longitude(input_value)
        assert abs(result - expected) < 0.000001

def test_sign_calculation():
    engine = EnhancedDivisionalChartEngine()
    test_cases = [
        (15.5, 0),    # Aries
        (45.5, 1),    # Taurus
        (75.5, 2),    # Gemini
        (105.5, 3),   # Cancer
        (360.0, 0)    # Full circle
    ]
    
    for longitude, expected_sign in test_cases:
        result = engine._get_sign_from_longitude(longitude)
        assert result == expected_sign

def test_navamsa_calculation():
    engine = EnhancedDivisionalChartEngine()
    
    # Test cases for different elements
    test_cases = [
        (15.0, 135.0),    # Fire sign (Aries) -> 15° in Aries -> Taurus navamsa
        (45.0, 225.0),    # Earth sign (Taurus) -> 15° in Taurus -> Leo navamsa
        (75.0, 315.0),    # Air sign (Gemini) -> 15° in Gemini -> Scorpio navamsa
        (105.0, 45.0)     # Water sign (Cancer) -> 15° in Cancer -> Aquarius navamsa
    ]
    
    for input_long, expected_nav in test_cases:
        result = engine._calculate_navamsa(input_long)
        assert abs(result - expected_nav) < 0.000001

def test_dwadasamsa_calculation():
    engine = EnhancedDivisionalChartEngine()
    
    # Test cases for D12
    test_cases = [
        (15.0, 180.0),    # First dwadasamsa in Aries -> moves to Virgo
        (45.0, 210.0),    # First dwadasamsa in Taurus -> moves to Libra
        (75.0, 240.0),    # First dwadasamsa in Gemini -> moves to Scorpio
        (105.0, 270.0)    # First dwadasamsa in Cancer -> moves to Sagittarius
    ]
    
    for input_long, expected_d12 in test_cases:
        result = engine._calculate_dwadasamsa(input_long)
        assert abs(result - expected_d12) < 0.000001

def test_trimsamsa_calculation():
    engine = EnhancedDivisionalChartEngine()
    
    # Test odd and even signs
    odd_sign_long = 15.0  # Aries (odd)
    even_sign_long = 45.0  # Taurus (even)
    
    odd_result = engine._calculate_trimsamsa(odd_sign_long)
    even_result = engine._calculate_trimsamsa(even_sign_long)
    
    # Results should be different for odd and even signs
    assert odd_result != even_result
    
    # Results should be within valid range
    assert 0 <= odd_result < 360
    assert 0 <= even_result < 360

def test_divisional_chart_calculation():
    engine = EnhancedDivisionalChartEngine()
    
    # Test planetary positions
    test_positions = {
        'Sun': 45.5,
        'Moon': 120.5,
        'Mars': 200.5,
        'Mercury': 300.5
    }
    
    # Test different divisions
    divisions = [1, 2, 3, 4, 7, 9, 12, 16, 20, 24, 27, 30, 40]
    
    for division in divisions:
        result = engine.calculate_divisional_chart(test_positions, division)
        
        # Verify results
        assert isinstance(result, dict)
        assert len(result) == len(test_positions)
        
        # Check value ranges
        for planet, position in result.items():
            assert 0 <= position < 360
            assert isinstance(position, float)

def test_special_divisional_charts():
    engine = EnhancedDivisionalChartEngine()
    test_positions = {
        'Sun': 45.5,
        'Moon': 120.5
    }
    
    # Test D9, D12, and D30 with special rules
    special_divisions = [9, 12, 30]
    
    for division in special_divisions:
        # Test with special rules
        with_rules = engine.calculate_divisional_chart(
            test_positions, division, apply_special_rules=True
        )
        
        # Test without special rules
        without_rules = engine.calculate_divisional_chart(
            test_positions, division, apply_special_rules=False
        )
        
        # Results should be different when using special rules
        assert with_rules != without_rules

def test_invalid_division():
    engine = EnhancedDivisionalChartEngine()
    test_positions = {'Sun': 45.5}
    
    # Test invalid division numbers
    invalid_divisions = [0, -1, 41, 100]
    
    for division in invalid_divisions:
        with pytest.raises(ValueError):
            engine.calculate_divisional_chart(test_positions, division)
