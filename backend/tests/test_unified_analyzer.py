"""
Test Suite for Unified Chart Analysis System
PGF Protocol: VCI_001
Gate: GATE_3 -> GATE_4 Transition
Version: 1.0.0
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.core.unified_analyzer import UnifiedAnalyzer, ChartAnalysis
from app.core.calculations.planetary_strength import PlanetaryStrength
from app.core.calculations.aspect_analysis import AspectInfluence, AspectType

@pytest.fixture
def unified_analyzer():
    analyzer = UnifiedAnalyzer()
    # Mock ayanamsa calculation to return a fixed value
    analyzer.ayanamsa_calc.calculate_precise_ayanamsa = MagicMock(return_value=23.15)
    
    # Mock Swiss Ephemeris functions
    with patch('swisseph.houses_ex') as mock_houses_ex, \
         patch('swisseph.get_ayanamsa_ut') as mock_ayanamsa, \
         patch('swisseph.calc_ut') as mock_calc_ut, \
         patch('swisseph.set_sid_mode') as mock_sid_mode, \
         patch('swisseph.set_topo') as mock_set_topo:
        
        # Mock house calculation
        mock_houses_ex.return_value = (
            [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],
            [0, 90, 180, 270]
        )
        
        # Mock ayanamsa calculation
        mock_ayanamsa.return_value = 23.15
        
        # Mock planet calculation
        mock_calc_ut.return_value = ([0, 0, 0], [0, 0, 0])
        
        # Mock house cusps calculation
        analyzer.divisional_calc.calculator.calculate_house_cusps = MagicMock(
            return_value={
                'cusps': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
                'ascendant': 0,
                'mc': 270,
                'armc': 270,
                'vertex': 90,
                'equatorial_ascendant': 90,
                'co_ascendant': 30,
                'polar_ascendant': 30,
                'house_system': 'P'
            }
        )
        
        # Mock divisional chart calculation
        analyzer.divisional_calc.calculator.get_ayanamsa = MagicMock(return_value=23.15)
        
        yield analyzer

@pytest.fixture
def sample_birth_data():
    return {
        'birth_time': datetime(1990, 1, 1, 12, 0),
        'latitude': 28.6139,  # New Delhi
        'longitude': 77.2090
    }

@pytest.fixture
def sample_planet_positions():
    """Sample planet positions for testing"""
    return {
        "Sun": {
            "longitude": 120.0,  # In Leo (5th house)
            "latitude": 0.0,
            "speed": 0.98,
            "dignity": "own",
            "strength": 85,
            "is_retrograde": False
        },
        "Moon": {
            "longitude": 90.0,   # In Cancer (4th house)
            "latitude": 0.0,
            "speed": 13.2,
            "dignity": "own",
            "strength": 90,
            "is_retrograde": False
        },
        "Mars": {
            "longitude": 30.0,   # In Taurus (2nd house)
            "latitude": 0.0,
            "speed": 0.5,
            "dignity": "neutral",
            "strength": 65,
            "is_retrograde": False
        },
        "Mercury": {
            "longitude": 150.0,  # In Virgo (6th house)
            "latitude": 0.0,
            "speed": -0.2,
            "dignity": "own",
            "strength": 80,
            "is_retrograde": True
        },
        "Jupiter": {
            "longitude": 270.0,  # In Capricorn (10th house)
            "latitude": 0.0,
            "speed": 0.1,
            "dignity": "exalted",
            "strength": 95,
            "is_retrograde": False
        },
        "Venus": {
            "longitude": 210.0,  # In Libra (7th house)
            "latitude": 0.0,
            "speed": 1.2,
            "dignity": "own",
            "strength": 88,
            "is_retrograde": False
        },
        "Saturn": {
            "longitude": 300.0,  # In Aquarius (11th house)
            "latitude": 0.0,
            "speed": -0.1,
            "dignity": "own",
            "strength": 82,
            "is_retrograde": True
        }
    }

def test_complete_chart_analysis(
    unified_analyzer,
    sample_birth_data,
    sample_planet_positions
):
    """Test complete chart analysis"""
    analysis = unified_analyzer.analyze_chart(
        birth_time=sample_birth_data['birth_time'],
        latitude=sample_birth_data['latitude'],
        longitude=sample_birth_data['longitude'],
        planet_positions=sample_planet_positions
    )
    
    # Verify analysis structure
    assert isinstance(analysis, ChartAnalysis)
    assert isinstance(analysis.ayanamsa_value, float)
    assert len(analysis.divisional_charts) > 0
    assert len(analysis.planetary_strengths) == 7  # 7 classical planets
    assert len(analysis.house_strengths) == 12     # 12 houses
    assert len(analysis.aspects) > 0
    assert len(analysis.yogas) > 0
    assert isinstance(analysis.chart_strength, float)
    assert len(analysis.primary_influences) > 0
    assert len(analysis.recommendations) > 0

def test_house_positions_calculation(unified_analyzer, sample_planet_positions):
    """Test conversion of planet positions to house positions"""
    house_positions = unified_analyzer._get_house_positions(sample_planet_positions)
    
    # Verify house occupancy
    assert "Sun" in house_positions[5]    # Sun in 5th house
    assert "Moon" in house_positions[4]   # Moon in 4th house
    assert "Jupiter" in house_positions[10]  # Jupiter in 10th house
    
    # Verify all houses are present
    assert len(house_positions) == 12
    
    # Verify all planets are placed
    placed_planets = [p for h in house_positions.values() for p in h]
    assert len(placed_planets) == 7  # All classical planets

def test_aspect_calculation(unified_analyzer, sample_planet_positions):
    """Test aspect calculation between planets and houses"""
    # Test aspects to 1st house
    aspects = unified_analyzer._get_aspects_to_house(1, sample_planet_positions)
    
    # Verify aspect count
    assert len(aspects) > 0
    
    # Verify aspect properties
    for aspect in aspects:
        assert 'planet' in aspect
        assert 'strength' in aspect
        assert 'type' in aspect
        assert 'is_applying' in aspect
        assert aspect['type'] in [
            'conjunction', 'opposition', 'trine',
            'square', 'sextile', 'none'
        ]

def test_chart_strength_calculation(
    unified_analyzer,
    sample_planet_positions
):
    """Test overall chart strength calculation"""
    # Get component data
    house_positions = unified_analyzer._get_house_positions(sample_planet_positions)
    
    # Create planetary strengths
    planetary_strengths = {
        planet: PlanetaryStrength(
            shadbala=data['strength'] / 100,
            dignity_score=0.75 if data['dignity'] == 'own' else 0.5,
            positional_strength=0.8,
            temporal_strength=0.7,
            aspect_strength=0.6,
            total_strength=data['strength']
        )
        for planet, data in sample_planet_positions.items()
    }
    
    # Calculate aspects
    aspects = {}
    for house in range(1, 13):
        house_aspects = unified_analyzer._get_aspects_to_house(
            house,
            sample_planet_positions
        )
        for aspect in house_aspects:
            key = (aspect['planet'], house)
            aspects[key] = AspectInfluence(
                aspect_type=AspectType.FULL if aspect['type'] == 'conjunction' else AspectType.HALF,
                strength=0.8 if aspect['type'] == 'conjunction' else 0.5,
                is_beneficial=True,
                special_effects=None
            )
    
    # Get house strengths
    house_strengths = {}
    for house in range(1, 13):
        lord = unified_analyzer._get_house_lord(house, sample_planet_positions)
        house_aspects = unified_analyzer._get_aspects_to_house(
            house,
            sample_planet_positions
        )
        occupants = [
            {'name': p, **d}
            for p, d in sample_planet_positions.items()
            if int(d['longitude'] / 30) + 1 == house
        ]

        analysis = unified_analyzer.house_analyzer.analyze_house(
            house=house,
            occupants=occupants,
            aspects=house_aspects,
            lord=lord
        )
        house_strengths[house] = analysis
    
    # Calculate yogas
    yogas = []
    yogas.extend(unified_analyzer.yoga_calc.calculate_raj_yoga(
        sample_planet_positions,
        house_positions
    ))
    yogas.extend(unified_analyzer.yoga_calc.calculate_dhana_yoga(
        sample_planet_positions,
        house_positions
    ))
    yogas.extend(unified_analyzer.yoga_calc.calculate_mahapurusha_yoga(
        sample_planet_positions
    ))
    
    # Calculate chart strength
    strength = unified_analyzer._calculate_chart_strength(
        planetary_strengths,
        house_strengths,
        aspects,
        yogas
    )
    
    # Verify strength is within expected range
    assert 0 <= strength <= 100
    assert isinstance(strength, float)

def test_recommendation_generation(unified_analyzer, sample_planet_positions):
    """Test recommendation generation"""
    # Get component data for recommendations
    house_positions = unified_analyzer._get_house_positions(sample_planet_positions)
    
    # Create planetary strengths
    planetary_strengths = {
        planet: PlanetaryStrength(
            shadbala=data['strength'] / 100,
            dignity_score=0.75 if data['dignity'] == 'own' else 0.5,
            positional_strength=0.8,
            temporal_strength=0.7,
            aspect_strength=0.6,
            total_strength=data['strength']
        )
        for planet, data in sample_planet_positions.items()
    }
    
    # Get house strengths
    house_strengths = {}
    for house in range(1, 13):
        lord = unified_analyzer._get_house_lord(house, sample_planet_positions)
        house_aspects = unified_analyzer._get_aspects_to_house(
            house,
            sample_planet_positions
        )
        occupants = [
            {'name': p, **d}
            for p, d in sample_planet_positions.items()
            if int(d['longitude'] / 30) + 1 == house
        ]

        analysis = unified_analyzer.house_analyzer.analyze_house(
            house=house,
            occupants=occupants,
            aspects=house_aspects,
            lord=lord
        )
        house_strengths[house] = analysis
    
    # Calculate yogas
    yogas = []
    yogas.extend(unified_analyzer.yoga_calc.calculate_raj_yoga(
        sample_planet_positions,
        house_positions
    ))
    yogas.extend(unified_analyzer.yoga_calc.calculate_dhana_yoga(
        sample_planet_positions,
        house_positions
    ))
    yogas.extend(unified_analyzer.yoga_calc.calculate_mahapurusha_yoga(
        sample_planet_positions
    ))
    
    # Generate recommendations
    recommendations = unified_analyzer._generate_recommendations(
        planetary_strengths,
        house_strengths,
        yogas
    )
    
    # Verify recommendations
    assert len(recommendations) > 0
    assert all(isinstance(r, str) for r in recommendations)
