import pytest
from datetime import datetime
from unittest.mock import Mock, patch

# Mock the swisseph dependency
mock_swe = Mock()
mock_swe.calc_ut.return_value = ((45.5, 0, 1.0), 0)  # longitude, latitude, speed
mock_swe.julday.return_value = 2460000.5
mock_swe.sidtime.return_value = 0.0

@pytest.fixture
def mock_imports():
    with patch.dict('sys.modules', {
        'swisseph': mock_swe,
        'pandas': Mock(),
        'numpy': Mock()
    }):
        yield

@pytest.fixture
def test_date():
    return datetime(2024, 1, 1, 12, 0)

@pytest.fixture
def test_location():
    return {"latitude": 13.0827, "longitude": 80.2707}  # Chennai coordinates

def test_strength_calculation(mock_imports):
    """Test strength calculations with mocked dependencies"""
    from app.core.calculations.strength import EnhancedPlanetaryStrengthEngine
    
    strength_engine = EnhancedPlanetaryStrengthEngine()
    
    # Test data
    planet_data = {
        "longitude": 45.5,  # In Taurus
        "latitude": 0,
        "speed": 1.0,
        "house": 1
    }
    
    chart_data = {
        "ascendant": 0.0,  # Aries ascendant
        "planets": {
            "Sun": {"longitude": 45.5, "latitude": 0, "speed": 1.0},
            "Moon": {"longitude": 75.5, "latitude": 0, "speed": 13.0},
            "Mars": {"longitude": 120.5, "latitude": 0, "speed": 0.5}
        },
        "houses": {i: i * 30.0 for i in range(1, 13)},
        "aspects": []
    }
    
    strength = strength_engine.calculate_complete_strengths(
        planet=planet_data,
        chart=chart_data
    )
    
    # Basic validation
    assert isinstance(strength, dict)
    assert "shadbala" in strength
    assert "vimshopaka" in strength
    assert "total" in strength
    assert 0 <= strength["total"] <= 100

def test_aspect_calculation(mock_imports):
    """Test aspect calculations with mocked dependencies"""
    from app.core.calculations.aspects import EnhancedAspectCalculator
    
    aspect_calculator = EnhancedAspectCalculator()
    
    # Test data - planets in significant aspects
    planets = {
        "Sun": {"longitude": 0.0},   # Conjunction
        "Moon": {"longitude": 60.0},  # Sextile
        "Mars": {"longitude": 90.0},  # Square
        "Jupiter": {"longitude": 120.0},  # Trine
        "Saturn": {"longitude": 180.0}    # Opposition
    }
    
    aspects = aspect_calculator.calculate_aspects(planets)
    
    # Validate aspects
    assert isinstance(aspects, list)
    for aspect in aspects:
        assert hasattr(aspect, "planet1")
        assert hasattr(aspect, "planet2")
        assert hasattr(aspect, "aspect")  # Check for aspect object
        assert hasattr(aspect.aspect, "name")  # Check for aspect name
        
        # Validate aspect properties
        assert aspect.planet1 in planets
        assert aspect.planet2 in planets
        assert 0 <= aspect.strength <= 100

def test_strength_special_cases(mock_imports):
    """Test special cases in strength calculations with mocked dependencies"""
    from app.core.calculations.strength import EnhancedPlanetaryStrengthEngine
    
    strength_engine = EnhancedPlanetaryStrengthEngine()
    
    # Test exalted planet
    exalted_sun = {
        "longitude": 20.0,  # Sun exalted in Aries
        "latitude": 0,
        "speed": 1.0,
        "house": 1
    }
    
    chart_data = {
        "ascendant": 0.0,
        "planets": {"Sun": exalted_sun},
        "houses": {i: i * 30.0 for i in range(1, 13)},
        "aspects": []
    }
    
    strength = strength_engine.calculate_complete_strengths(
        planet=exalted_sun,
        chart=chart_data
    )
    
    assert strength["total"] > 50  # Exalted planet should have high strength
    
    # Test debilitated planet
    debilitated_sun = {
        "longitude": 200.0,  # Sun debilitated in Libra
        "latitude": 0,
        "speed": 1.0,
        "house": 7
    }
    
    chart_data["planets"]["Sun"] = debilitated_sun
    
    strength = strength_engine.calculate_complete_strengths(
        planet=debilitated_sun,
        chart=chart_data
    )
    
    assert strength["total"] < 50  # Debilitated planet should have low strength

def test_aspect_special_cases(mock_imports):
    """Test special cases in aspect calculations with mocked dependencies"""
    from app.core.calculations.aspects import EnhancedAspectCalculator
    
    aspect_calculator = EnhancedAspectCalculator()
    
    # Test exact aspects
    planets = {
        "Mars": {"longitude": 0.0},
        "Saturn": {"longitude": 180.0}  # Exact opposition
    }
    
    aspects = aspect_calculator.calculate_aspects(planets)
    
    # Find the Mars-Saturn opposition
    mars_saturn_aspect = next(
        (a for a in aspects 
         if (a.planet1 == "Mars" and a.planet2 == "Saturn") or
            (a.planet1 == "Saturn" and a.planet2 == "Mars")),
        None
    )
    
    assert mars_saturn_aspect is not None
    assert mars_saturn_aspect.strength >= 85  # Exact aspect should have high strength
    
    # Test weak aspects (planets at the edge of orb)
    planets = {
        "Mars": {"longitude": 0.0},
        "Jupiter": {"longitude": 67.0}  # Just barely in sextile orb
    }
    
    aspects = aspect_calculator.calculate_aspects(planets)
    
    # Find the Mars-Jupiter aspect
    mars_jupiter_aspect = next(
        (a for a in aspects 
         if (a.planet1 == "Mars" and a.planet2 == "Jupiter") or
            (a.planet1 == "Jupiter" and a.planet2 == "Mars")),
        None
    )
    
    if mars_jupiter_aspect:
        assert mars_jupiter_aspect.strength < 50  # Wide orb should have low strength

def test_planetary_strength(mock_imports):
    """Test planetary strength calculations"""
    from app.core.calculations.strength import EnhancedPlanetaryStrengthEngine
    
    strength_engine = EnhancedPlanetaryStrengthEngine()
    
    # Test data
    planet_data = {
        "longitude": 45.5,  # In Taurus
        "latitude": 0,
        "speed": 1.0,
        "house": 1
    }
    
    chart_data = {
        "ascendant": 0.0,  # Aries ascendant
        "planets": {
            "Sun": {"longitude": 45.5, "latitude": 0, "speed": 1.0},
            "Moon": {"longitude": 75.5, "latitude": 0, "speed": 13.0},
            "Mars": {"longitude": 120.5, "latitude": 0, "speed": 0.5}
        },
        "houses": {
            1: 0.0,    # House cusps
            2: 30.0,
            3: 60.0,
            4: 90.0,
            5: 120.0,
            6: 150.0,
            7: 180.0,
            8: 210.0,
            9: 240.0,
            10: 270.0,
            11: 300.0,
            12: 330.0
        },
        "aspects": []
    }
    
    strength = strength_engine.calculate_complete_strengths(
        planet=planet_data,
        chart=chart_data
    )
    
    # Basic validation
    assert isinstance(strength, dict)
    assert "shadbala" in strength
    assert "vimshopaka" in strength
    assert "total" in strength
    assert 0 <= strength["total"] <= 100  # Total strength should be normalized

def test_aspect_calculations(mock_imports):
    """Test aspect calculations between planets"""
    from app.core.calculations.aspects import EnhancedAspectCalculator
    
    aspect_calculator = EnhancedAspectCalculator()
    
    # Test data - planets in significant aspects
    planets = {
        "Sun": {"longitude": 0.0},   # Conjunction
        "Moon": {"longitude": 60.0},  # Sextile
        "Mars": {"longitude": 90.0},  # Square
        "Jupiter": {"longitude": 120.0},  # Trine
        "Saturn": {"longitude": 180.0}    # Opposition
    }
    
    aspects = aspect_calculator.calculate_aspects(planets)
    
    # Validate aspects
    assert isinstance(aspects, list)
    for aspect in aspects:
        assert hasattr(aspect, "planet1")
        assert hasattr(aspect, "planet2")
        assert hasattr(aspect, "aspect")  # Check for aspect object
        assert hasattr(aspect.aspect, "name")  # Check for aspect name
        
        # Check for valid aspects
        valid_aspects = [
            "Conjunction", "Opposition", "Trine", "Square", "Sextile",
            "Semisextile", "Quincunx", "Semisquare", "Sesquiquadrate",
            "Quintile", "Biquintile", "Parallel", "Contraparallel"
        ]
        assert aspect.aspect.name in valid_aspects
        
        # Check aspect strength is normalized
        assert 0 <= aspect.strength <= 100
        assert 0 <= aspect.total_influence <= 100

def test_strength_special_cases(mock_imports):
    """Test special cases in planetary strength calculations"""
    from app.core.calculations.strength import EnhancedPlanetaryStrengthEngine
    
    strength_engine = EnhancedPlanetaryStrengthEngine()
    
    # Test exalted planet
    exalted_sun = {
        "longitude": 20.0,  # Sun exalted in Aries
        "latitude": 0,
        "speed": 1.0,
        "house": 1
    }
    
    chart_data = {
        "ascendant": 0.0,
        "planets": {"Sun": exalted_sun},
        "houses": {i: i * 30.0 for i in range(1, 13)},
        "aspects": []
    }
    
    strength = strength_engine.calculate_complete_strengths(
        planet=exalted_sun,
        chart=chart_data
    )
    
    assert strength["total"] > 50  # Exalted planet should have high strength
    
    # Test debilitated planet
    debilitated_sun = {
        "longitude": 200.0,  # Sun debilitated in Libra
        "latitude": 0,
        "speed": 1.0,
        "house": 7
    }
    
    chart_data["planets"]["Sun"] = debilitated_sun
    
    strength = strength_engine.calculate_complete_strengths(
        planet=debilitated_sun,
        chart=chart_data
    )
    
    assert strength["total"] < 50  # Debilitated planet should have low strength

def test_aspect_special_cases(mock_imports):
    """Test special cases in aspect calculations"""
    from app.core.calculations.aspects import EnhancedAspectCalculator
    
    aspect_calculator = EnhancedAspectCalculator()
    
    # Test exact aspects
    planets = {
        "Mars": {"longitude": 0.0},
        "Saturn": {"longitude": 180.0}  # Exact opposition
    }
    
    aspects = aspect_calculator.calculate_aspects(planets)
    
    # Find the Mars-Saturn opposition
    mars_saturn_aspect = next(
        (a for a in aspects 
         if (a.planet1 == "Mars" and a.planet2 == "Saturn") or
            (a.planet1 == "Saturn" and a.planet2 == "Mars")),
        None
    )
    
    assert mars_saturn_aspect is not None
    assert mars_saturn_aspect.strength >= 85  # Exact aspect should have high strength
    
    # Test weak aspects (planets at the edge of orb)
    planets = {
        "Mars": {"longitude": 0.0},
        "Jupiter": {"longitude": 67.0}  # Just barely in sextile orb
    }
    
    aspects = aspect_calculator.calculate_aspects(planets)
    
    # Find the Mars-Jupiter aspect
    mars_jupiter_aspect = next(
        (a for a in aspects 
         if (a.planet1 == "Mars" and a.planet2 == "Jupiter") or
            (a.planet1 == "Jupiter" and a.planet2 == "Mars")),
        None
    )
    
    if mars_jupiter_aspect:
        assert mars_jupiter_aspect.strength < 50  # Wide orb should have low strength
